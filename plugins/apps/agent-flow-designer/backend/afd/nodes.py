# -*- coding: utf-8 -*-
"""Node type metadata, handlers and prompt construction.

Importing this module registers the six node types (start/router/agent/tool/
end/ask) into the engine registry -- ``import afd.nodes`` plus the engine is a
complete headless runtime, no web layer (main.py) required. Also home to the
prompt helpers (template interpolation, upstream-context collection) and the
agent execution helper.
"""

import asyncio
import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from engine import (
    EventType,
    NodeRunContext,
    RunEvent,
    assemble_final_result,
    get_logger,
    register_node,
)
from engine.registry import NodeTypeDef, PropertyField
from engine.schema import (
    SYSTEM_VARIABLE_KEYS,
    parse_json_output,
    parse_output_schema,
    validate_output,
)

from . import tools
from .llm_client import _call_agent_chat
from .routing import _evaluate_router_detailed_async, _resolve_variable_ex
from .tools import (
    ToolApprovalRequired,
    _invoke_http_tool,
    _invoke_mcp_tool,
    _invoke_platform_tool,
    _resolve_tool_params,
    _resolve_tool_source,
)

logger = get_logger(__name__)


_TEMPLATE_RE = re.compile(r"\{\{\s*([^{}]+?)\s*\}\}")


def _is_router_output(payload: Any) -> bool:
    return isinstance(payload, dict) and (
        "branchId" in payload or "selected_branch" in payload
    )


def _render_node_output(node_id: str, payload: Any) -> str:
    """Render one node output as a prompt chunk (empty string when unusable)."""
    if _is_router_output(payload):
        return "\n".join([
            f"[路由结果 - {node_id}]",
            f"命中分支: {payload.get('branch_name', '')}",
            f"分支ID: {payload.get('selected_branch', '')}",
            f"路由类型: {payload.get('routeType', '')}",
            f"路由原因: {payload.get('routeReason', '')}",
        ])
    if payload and isinstance(payload, dict):
        return f"[上游节点输出 - {node_id}]\n{json.dumps(payload, ensure_ascii=False, indent=2)}"
    if payload and isinstance(payload, str) and payload.strip():
        return f"[上游节点输出 - {node_id}]\n{payload}"
    return ""


def _collect_upstream_context(
    node_outputs: Dict[str, Any],
    predecessor_ids: Optional[List[str]],
) -> List[str]:
    """Render the outputs of the nodes that actually fed this node.

    ``predecessor_ids`` comes from the runner's live-edge bookkeeping, so a
    branch the router did not select never contributes to the prompt. Passing
    ``None`` keeps the legacy "everything accumulated so far" behaviour for
    callers outside the runner.
    """
    ids = list(node_outputs) if predecessor_ids is None else list(predecessor_ids)
    chunks: List[str] = []
    seen = set()
    for prev_id in ids:
        if prev_id in seen or prev_id not in node_outputs:
            continue
        seen.add(prev_id)
        chunk = _render_node_output(prev_id, node_outputs[prev_id])
        if chunk:
            chunks.append(chunk)
    return chunks


def _binding_refs(config: dict) -> List[tuple[str, str]]:
    """Return ``(alias, reference)`` pairs declared on a node's ``inputs``."""
    pairs: List[tuple[str, str]] = []
    for binding in config.get("inputs") or []:
        if not isinstance(binding, dict):
            continue
        ref = str(binding.get("ref") or binding.get("value") or "").strip()
        if not ref:
            continue
        alias = str(binding.get("name") or "").strip() or ref
        pairs.append((alias, ref))
    return pairs


def _interpolate_template(
    template: str,
    context: dict,
    node_outputs: Optional[Dict[str, Any]],
    aliases: Optional[Dict[str, str]] = None,
) -> str:
    """Replace ``{{ref}}`` placeholders, reporting references that do not resolve."""
    missing: List[str] = []

    def _substitute(match: "re.Match[str]") -> str:
        raw = match.group(1).strip()
        ref = (aliases or {}).get(raw, raw)
        value, found = _resolve_variable_ex(ref, context, node_outputs)
        if not found:
            missing.append(raw)
            return ""
        return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)

    text = _TEMPLATE_RE.sub(_substitute, template)
    if missing:
        logger.warning(
            "[Prompt template] 以下变量引用未能解析: %s", ", ".join(sorted(set(missing)))
        )
    return text


# Circular-avoidance seam: tools must not import nodes (nodes imports tools),
# and _invoke_http_tool looks _interpolate_template up in tools' globals at
# call time -- so nodes owns the wiring. Importing afd.nodes alone fully wires
# the http tool path, headless-safe.
tools._interpolate_template = _interpolate_template


def _build_node_prompt(
    config: dict,
    context: dict,
    node_outputs: Dict[str, Any],
    predecessor_ids: Optional[List[str]],
) -> str:
    """Assemble the user prompt for an agent / tool node.

    Priority: explicit ``promptTemplate`` → declared ``inputs`` bindings →
    upstream outputs on the taken path. The old behaviour of concatenating
    every accumulated output is gone: it leaked unselected branches into the
    prompt and grew token cost with workflow size.
    """
    aliases = dict(_binding_refs(config))
    template = config.get("promptTemplate") or ""
    if template:
        return _interpolate_template(template, context, node_outputs, aliases)

    user_input = context.get("user_input", "")
    bindings = _binding_refs(config)
    if bindings:
        chunks = []
        for alias, ref in bindings:
            value, found = _resolve_variable_ex(ref, context, node_outputs)
            rendered = value if found else "（未解析）"
            chunks.append(f"[{alias}] ({ref})\n{rendered}")
        context_text = "\n\n".join(chunks)
        return f"{context_text}\n\n[当前输入]\n{user_input}"

    upstream = _collect_upstream_context(node_outputs, predecessor_ids)
    if upstream:
        return "\n\n".join(upstream) + f"\n\n[当前输入]\n{user_input}"
    return user_input


async def _execute_agent_node(
    node: dict,
    context: dict,
    node_outputs: dict,
    on_token=None,
    live_predecessors: Optional[List[str]] = None,
    usage_out: Optional[dict] = None,
) -> str:
    """Execute an Agent node by calling the real LLM/chat API.

    ``on_token`` (optional) is forwarded to :func:`_call_agent_chat` so a
    streaming caller can observe incremental deltas; it does not change the
    returned text. ``live_predecessors`` restricts the injected context to the
    branches actually taken — see :func:`_build_node_prompt`. ``usage_out``
    receives this call's token counts, for the node's own trace item.
    """
    config = node.get("config", {})
    agent_id = config.get("agentId", "")
    extra_prompt = config.get("extraPrompt", "")

    user_input = _build_node_prompt(config, context, node_outputs, live_predecessors)

    # Add extra prompt from node config
    if extra_prompt:
        user_input = f"{extra_prompt}\n\n{user_input}"

    # Build call_messages from context messages history, preserving attachments
    messages = context.get("messages", [])
    call_messages = []
    # Only pass the last user message to avoid the agent re-summarizing
    # previous conversation history in its response. This prevents the
    # agent from including past Q&A in its current answer.
    if messages:
        last_msg = messages[-1]
        if isinstance(last_msg, dict):
            call_messages.append(last_msg)
        else:
            call_messages.append({"role": "user", "content": str(last_msg)})
    # Ensure the last message carries the latest user_input and any attachments
    if call_messages:
        last = call_messages[-1]
        last["content"] = user_input
    else:
        call_messages = [{"role": "user", "content": user_input}]

    result = await _call_agent_chat(agent_id, call_messages, on_token=on_token, usage_out=usage_out)
    if not result or not result.strip():
        logger.warning("[_execute_agent_node] Agent returned empty response for agent_id=%s", agent_id)
    return result


#: Fields the Start node always exposes — mirrors :func:`_get_node_inputs`, so a
#: reference to one of these always resolves at run time.
_START_OUTPUT_FIELDS = frozenset(
    {"user_input", "messages", "messages_count"} | set(SYSTEM_VARIABLE_KEYS)
)


def _get_node_inputs(
    node_type: str,
    node: dict,
    context: dict,
    node_outputs: dict,
    predecessor_ids: Optional[List[str]] = None,
) -> dict:
    """Build the input-parameters view recorded in a node's trace item."""
    inputs: Dict[str, Any] = {}
    if node_type == "start":
        inputs["user_input"] = context.get("user_input", "")
        inputs["messages_count"] = len(context.get("messages", []))
        for key in SYSTEM_VARIABLE_KEYS:
            inputs[key] = context.get(key, "")
    elif node_type == "agent":
        config = node.get("config", {})
        inputs["agentId"] = config.get("agentId", "")
        inputs["extraPrompt"] = config.get("extraPrompt", "")[:200] if config.get("extraPrompt") else ""
        bindings = _binding_refs(config)
        if bindings:
            inputs["inputs"] = [{"name": a, "ref": r} for a, r in bindings]
        if config.get("promptTemplate"):
            inputs["promptTemplate"] = str(config["promptTemplate"])[:200]
        # Only the branches actually taken reach the prompt, so the trace shows
        # exactly what the model will see.
        upstream_context = _collect_upstream_context(node_outputs, predecessor_ids)
        if upstream_context:
            inputs["upstream_context"] = [chunk[:100] for chunk in upstream_context]
    elif node_type == "tool":
        config = node.get("config", {})
        source = _resolve_tool_source(config)
        # Only what identifies the call and what it references. HTTP headers and
        # any credential value are deliberately absent: this dict is stored in
        # the trace and exported with the workflow.
        inputs["source"] = source
        if source == "platform":
            inputs["toolName"] = config.get("toolName", node.get("label", "未知工具"))
        elif source == "mcp":
            inputs["clientKey"] = config.get("clientKey", "")
            inputs["capabilityId"] = config.get("capabilityId", "")
        elif source == "http":
            inputs["method"] = str(config.get("method") or "GET").strip().upper()
            inputs["url"] = str(config.get("url") or "")[:200]
            env_name = str(config.get("authEnvVar") or "").strip()
            if env_name:
                inputs["authEnvVar"] = env_name
                # 不记"是否已设置"：那是一份不用出网就能逐个探测宿主环境变量
                # 存在性的 oracle，跟这里的白名单是同一个洞的另一半。
        params = config.get("params")
        if isinstance(params, dict):
            inputs["params"] = params
        else:
            inputs["params"] = [
                {"name": p.get("name"), "valueType": p.get("valueType"), "value": p.get("value")}
                for p in (params or [])
                if isinstance(p, dict)
            ]
    elif node_type == "router":
        config = node.get("config", {})
        inputs["branches_count"] = len(config.get("branches", []))
        inputs["defaultBranchId"] = config.get("defaultBranchId", "")
    elif node_type == "end":
        inputs["upstream_outputs_count"] = len(node_outputs)
    return inputs


_START_META = NodeTypeDef(
    type_id="start",
    label="开始",
    description="工作流的入口节点，接收用户输入并启动执行。",
    icon="PlayCircle",
    color="#10B981",
    bg_color="#ecfdf5",
    border_color="#10B981",
    properties=[
        PropertyField(name="label", type="text", label="节点名称", default="开始"),
        PropertyField(name="description", type="textarea", label="描述"),
    ],
    supports_error_policy=False,
    supports_retry=False,
)

_ROUTER_META = NodeTypeDef(
    type_id="router",
    label="路由",
    description="根据条件将执行流导向不同分支。",
    icon="GitBranch",
    color="#8B5CF6",
    bg_color="#f5f3ff",
    border_color="#8B5CF6",
    properties=[
        PropertyField(name="label", type="text", label="节点名称", default="路由"),
        PropertyField(name="description", type="textarea", label="描述"),
    ],
    supports_error_policy=False,
    supports_retry=False,
    custom_renderer="router",
)

_AGENT_META = NodeTypeDef(
    type_id="agent",
    label="Agent",
    description="调用平台 Agent 进行推理并返回结果。",
    icon="Bot",
    color="#3B82F6",
    bg_color="#eff6ff",
    border_color="#3B82F6",
    properties=[
        PropertyField(name="label", type="text", label="节点名称", default="Agent"),
        PropertyField(name="description", type="textarea", label="描述"),
        PropertyField(name="agentId", type="text", label="Agent ID", required=True, description="要调用的平台 Agent ID"),
        PropertyField(name="prompt", type="textarea", label="提示词", description="发送给 Agent 的提示词"),
        PropertyField(name="outputSchema", type="textarea", label="输出声明", description="JSON Schema 格式声明输出结构"),
    ],
    supports_error_policy=True,
    supports_retry=True,
)

_TOOL_META = NodeTypeDef(
    type_id="tool",
    label="工具",
    description="调用平台工具、MCP 工具或 HTTP 接口。",
    icon="Wrench",
    color="#F59E0B",
    bg_color="#fffbeb",
    border_color="#F59E0B",
    properties=[
        PropertyField(name="label", type="text", label="节点名称", default="工具"),
        PropertyField(name="description", type="textarea", label="描述"),
        PropertyField(name="toolSource", type="select", label="工具来源", default="platform", options=[
            {"value": "platform", "label": "平台工具"},
            {"value": "mcp", "label": "MCP 工具"},
            {"value": "http", "label": "HTTP 接口"},
        ]),
        PropertyField(name="toolName", type="text", label="工具名称", required=True),
        PropertyField(name="outputSchema", type="textarea", label="输出声明", description="JSON Schema 格式声明输出结构"),
    ],
    supports_error_policy=True,
    supports_retry=True,
)

_END_META = NodeTypeDef(
    type_id="end",
    label="结束",
    description="工作流的终点，汇总结果并返回。",
    icon="Flag",
    color="#EF4444",
    bg_color="#fef2f2",
    border_color="#EF4444",
    properties=[
        PropertyField(name="label", type="text", label="节点名称", default="结束"),
        PropertyField(name="description", type="textarea", label="描述"),
    ],
    supports_error_policy=False,
    supports_retry=False,
)

_ASK_META = NodeTypeDef(
    type_id="ask",
    label="提问",
    description="暂停执行，等待人工输入后继续。",
    icon="MessageCircleQuestion",
    color="#EC4899",
    bg_color="#fdf2f8",
    border_color="#EC4899",
    properties=[
        PropertyField(name="label", type="text", label="节点名称", default="提问"),
        PropertyField(name="description", type="textarea", label="描述"),
        PropertyField(name="question", type="textarea", label="提问内容", description="向用户展示的问题"),
    ],
    supports_error_policy=False,
    supports_retry=False,
)


@register_node("start", metadata=_START_META)
async def _h_start(ctx: NodeRunContext):
    node = ctx.node
    node_id = ctx.node_id
    node_label = node.get("label", node_id)
    state = ctx.state
    t0 = datetime.utcnow()
    inputs = _get_node_inputs("start", node, state.context, state.node_outputs)
    # The contract advertises start.messages, so the node-scoped reference must
    # resolve. Publish the history in the node output but keep it out of the
    # trace summary, which is persisted and exported with every run.
    start_output = {**inputs, "messages": state.context.get("messages", [])}
    state.node_outputs[node_id] = start_output
    state.context[node_id] = start_output
    state.context["user_input"] = inputs.get("user_input", "")
    state.context["messages_count"] = inputs.get("messages_count", 0)
    trace = {
        "nodeId": node_id,
        "nodeLabel": node_label,
        "type": "start",
        "status": "completed",
        "timestamp": t0.isoformat(),
        "durationMs": 0,
        "inputs": inputs,
        "message": "工作流开始执行",
    }
    yield RunEvent(EventType.NODE_DONE, node_id, {"trace": trace})


@register_node("router", metadata=_ROUTER_META)
async def _h_router(ctx: NodeRunContext):
    node = ctx.node
    node_id = ctx.node_id
    node_label = node.get("label", node_id)
    state = ctx.state
    t0 = datetime.utcnow()
    usage: dict = {}
    router_result = await _evaluate_router_detailed_async(
        node, state.context,
        node_outputs=state.node_outputs, node_outputs_history=state.node_outputs_history,
        usage_out=usage,
    )
    branch_id = router_result["branchId"]
    branch_name = router_result["branchName"]
    matched = router_result["matched"]
    route_type = router_result.get("routeType", "rule")
    route_reason = router_result.get("reason", "")

    flat_conditions = []
    for bc in router_result.get("conditions", []):
        for c in bc.get("conditions", []):
            flat_conditions.append(c)

    undefined_refs = sorted(
        {
            str(c.get("variable", ""))
            for c in flat_conditions
            if not c.get("defined", True)
        }
    )

    duration_ms = int((datetime.utcnow() - t0).total_seconds() * 1000)
    trace_message = f"路由判定 ({route_type}): {'命中分支' if matched else '未命中任何分支'} -> {branch_name}"
    if route_reason:
        trace_message += f" | {route_reason}"

    logs = list(router_result.get("logs", []))
    if undefined_refs:
        warning = (
            f"[规则路由] 警告：{len(undefined_refs)} 个条件引用了未定义变量 "
            f"({', '.join(undefined_refs)})，这些条件按不成立处理"
        )
        logs.append(warning)
        trace_message += f" | {warning}"

    trace = {
        "nodeId": node_id,
        "nodeLabel": node_label,
        "type": "router",
        "status": "completed",
        "branchId": branch_id,
        "branchName": branch_name,
        "matched": matched,
        "routeType": route_type,
        "routeReason": route_reason,
        "timestamp": t0.isoformat(),
        "durationMs": duration_ms,
        "inputs": _get_node_inputs("router", node, state.context, state.node_outputs),
        "conditions": flat_conditions,
        "undefinedRefs": undefined_refs,
        **usage,
        "message": trace_message,
        "logs": logs,
    }
    router_output = {
        "output": f"路由命中分支: {branch_name} (类型: {route_type})",
        "selected_branch": branch_id,
        "branch_name": branch_name,
        "matched": matched,
        "routeType": route_type,
        "routeReason": route_reason,
    }
    state.node_outputs[node_id] = router_output
    state.context[f"node_{node_id}_output"] = router_output

    # ROUTE first so the Runner captures the branch for successor selection.
    yield RunEvent(EventType.ROUTE, node_id, {"branchId": branch_id, "matched": matched})
    yield RunEvent(EventType.NODE_DONE, node_id, {"trace": trace})


@register_node("agent", metadata=_AGENT_META)
async def _h_agent(ctx: NodeRunContext):
    node = ctx.node
    node_id = ctx.node_id
    node_label = node.get("label", node_id)
    state = ctx.state
    t0 = datetime.utcnow()
    inputs = _get_node_inputs(
        "agent", node, state.context, state.node_outputs, ctx.live_predecessors
    )

    # Run the agent call as a background task while streaming its incremental
    # deltas as NODE_TOKEN events. The task pushes each delta onto the queue
    # and, on completion, the final authoritative text (or the raised error).
    # The synchronous path simply discards token events, so its contract is
    # unchanged; only the SSE path forwards them for live rendering.
    queue: "asyncio.Queue" = asyncio.Queue()
    #: This call's token counts, filled from the platform's turn_usage event and
    #: written onto the trace item below. Left out of a failed node's trace: an
    #: interrupted turn has no trustworthy total, and a partial one is worse
    #: than none in a column people add up.
    usage: dict = {}

    def _on_token(delta: str) -> None:
        queue.put_nowait(("token", delta))

    async def _run_agent() -> None:
        try:
            out = await _execute_agent_node(
                node,
                state.context,
                state.node_outputs,
                on_token=_on_token,
                live_predecessors=ctx.live_predecessors,
                usage_out=usage,
            )
            queue.put_nowait(("done", out))
        except Exception as exc:  # noqa: BLE001  (surfaced as a failed trace below)
            queue.put_nowait(("error", exc))
        except BaseException as exc:
            # Cancellation is a BaseException: without this the consumer keeps
            # awaiting an empty queue and the run hangs holding its connection.
            queue.put_nowait(("error", exc))
            raise

    task = asyncio.ensure_future(_run_agent())
    error = None
    output = ""
    try:
        while True:
            kind, val = await queue.get()
            if kind == "token":
                yield RunEvent(EventType.NODE_TOKEN, node_id, {"delta": val})
            elif kind == "done":
                output = val
                break
            else:  # error
                error = val
                break
    finally:
        if not task.done():
            task.cancel()

    duration_ms = int((datetime.utcnow() - t0).total_seconds() * 1000)
    if error is not None:
        # A cancelled task stringifies to "", which reads as a passing test.
        failure = str(error) or f"{type(error).__name__}: Agent 调用任务被取消或异常终止"
        trace = {
            "nodeId": node_id,
            "nodeLabel": node_label,
            "type": "agent",
            "status": "failed",
            "timestamp": t0.isoformat(),
            "durationMs": duration_ms,
            "inputs": inputs,
            "error": failure[:500],
            "message": f"Agent 节点执行失败: {failure[:200]}",
        }
        yield RunEvent(EventType.NODE_ERROR, node_id, {"trace": trace})
        return

    schema_fields, schema_errors = parse_output_schema(
        (node.get("config") or {}).get("outputSchema")
    )
    if schema_errors:
        yield RunEvent(EventType.NODE_ERROR, node_id, {"trace": {
            "nodeId": node_id, "nodeLabel": node_label, "type": "agent",
            "status": "failed", "timestamp": t0.isoformat(),
            "durationMs": duration_ms, "inputs": inputs,
            "rawOutput": output[:500],
            "schemaErrors": schema_errors,
            "error": "; ".join(schema_errors)[:500],
            "message": f"Agent 节点输出声明非法: {schema_errors[0]}",
        }})
        return

    published: Any = output
    if schema_fields:
        parsed, ok = parse_json_output(output)
        if not ok:
            schema_errors = ["输出不是合法 JSON，无法按声明的字段校验"]
            parsed = None
        normalized, field_errors = (
            validate_output(parsed, schema_fields) if ok else (None, schema_errors)
        )
        if field_errors:
            yield RunEvent(EventType.NODE_ERROR, node_id, {"trace": {
                "nodeId": node_id, "nodeLabel": node_label, "type": "agent",
                "status": "failed", "timestamp": t0.isoformat(),
                "durationMs": duration_ms, "inputs": inputs,
                "rawOutput": output[:500],
                "schemaErrors": field_errors,
                "error": "; ".join(field_errors)[:500],
                "message": f"Agent 节点输出不符合声明: {field_errors[0]}",
            }})
            return
        published = normalized

    state.node_outputs[node_id] = published
    state.context[f"node_{node_id}_output"] = published
    state.node_outputs_history.setdefault(node_id, []).append(published)

    trace = {
        "nodeId": node_id,
        "nodeLabel": node_label,
        "type": "agent",
        "status": "completed",
        "timestamp": t0.isoformat(),
        "durationMs": duration_ms,
        "inputs": inputs,
        "output": output[:500] if isinstance(output, str) else str(output)[:500],
        "outputFields": [f.name for f in schema_fields],
        **usage,
        "message": f"Agent 节点执行完成 (耗时 {duration_ms}ms)",
    }
    yield RunEvent(EventType.NODE_DONE, node_id, {"trace": trace})


@register_node("tool", metadata=_TOOL_META)
async def _h_tool(ctx: NodeRunContext):
    """Execute a tool node: one node type, three sources.

    ``platform`` runs through the host governance layer. When policy answers ASK
    the run pauses for a human decision instead of blocking on a chat approval
    card, and the resume re-enters this handler with a one-shot marker in
    ``state.context`` — this handler is the *only* place that reads it, so
    "consume once" has exactly one implementation.
    """
    node = ctx.node
    node_id = ctx.node_id
    node_label = node.get("label", node_id)
    state = ctx.state
    config = node.get("config") or {}
    t0 = datetime.utcnow()

    approval = str(state.context.pop(f"node_{node_id}_approval", "") or "")
    source = _resolve_tool_source(config)

    def _trace(status: str, **extra: Any) -> dict:
        item = {
            "nodeId": node_id,
            "nodeLabel": node_label,
            "type": "tool",
            "status": status,
            "timestamp": t0.isoformat(),
            "durationMs": int((datetime.utcnow() - t0).total_seconds() * 1000),
            "inputs": _get_node_inputs(
                "tool", node, state.context, state.node_outputs, ctx.live_predecessors
            ),
        }
        item.update(extra)
        return item

    if approval == "deny":
        yield RunEvent(
            EventType.NODE_ERROR,
            node_id,
            {"trace": _trace(
                "failed",
                error="用户拒绝了该工具调用，节点未执行",
                message="工具节点执行失败: 用户拒绝了该工具调用，节点未执行",
            )},
        )
        return

    schema_fields, schema_errors = parse_output_schema(config.get("outputSchema"))
    capture: Optional[dict] = {} if schema_fields else None

    try:
        params = _resolve_tool_params(config, state.context, state.node_outputs)
        if source == "platform":
            output = await _invoke_platform_tool(
                config, params, ctx.services, state,
                approval_granted=(approval == "approve"),
                parsed_out=capture,
            )
        elif source == "mcp":
            output = await _invoke_mcp_tool(
                config, params, ctx.services, state, parsed_out=capture
            )
        elif source == "http":
            output = await _invoke_http_tool(
                config, state.context, state.node_outputs,
                parsed_out=capture, services=ctx.services,
            )
        else:
            raise ValueError(
                f"未知的工具来源「{source}」，可选：platform / mcp / http"
            )
    except ToolApprovalRequired as exc:
        yield RunEvent(
            EventType.WF_PAUSE,
            node_id,
            {
                "question": exc.question or str(exc),
                "resumeMode": "requeue",
                "pauseKind": "tool_approval",
            },
        )
        return
    except Exception as exc:  # noqa: BLE001
        failure = str(exc) or f"{type(exc).__name__}: 工具节点执行异常"
        yield RunEvent(
            EventType.NODE_ERROR,
            node_id,
            {"trace": _trace(
                "failed",
                error=failure[:500],
                message=f"工具节点执行失败: {failure[:200]}",
            )},
        )
        return

    if schema_errors:
        yield RunEvent(EventType.NODE_ERROR, node_id, {"trace": _trace(
            "failed",
            rawOutput=output[:500] if isinstance(output, str) else str(output)[:500],
            schemaErrors=schema_errors,
            error="; ".join(schema_errors)[:500],
            message=f"工具节点输出声明非法: {schema_errors[0]}",
        )})
        return

    published: Any = output
    if schema_fields:
        candidate = (capture or {}).get("value")
        if candidate is None:
            candidate, ok = parse_json_output(output)
            if not ok:
                candidate = None
        normalized, field_errors = validate_output(candidate, schema_fields)
        if field_errors:
            yield RunEvent(EventType.NODE_ERROR, node_id, {"trace": _trace(
                "failed",
                rawOutput=output[:500] if isinstance(output, str) else str(output)[:500],
                schemaErrors=field_errors,
                error="; ".join(field_errors)[:500],
                message=f"工具节点输出不符合声明: {field_errors[0]}",
            )})
            return
        published = normalized

    state.node_outputs[node_id] = published
    state.context[f"node_{node_id}_output"] = published
    state.node_outputs_history.setdefault(node_id, []).append(published)
    duration_ms = int((datetime.utcnow() - t0).total_seconds() * 1000)
    yield RunEvent(
        EventType.NODE_DONE,
        node_id,
        {"trace": _trace(
            "completed",
            output=output[:500] if isinstance(output, str) else str(output)[:500],
            message=f"工具节点执行完成 ({duration_ms}ms)",
        )},
    )


@register_node("end", metadata=_END_META)
async def _h_end(ctx: NodeRunContext):
    node = ctx.node
    node_id = ctx.node_id
    node_label = node.get("label", node_id)
    state = ctx.state
    t0 = datetime.utcnow()
    node_map = {n["id"]: n for n in ctx.workflow.get("nodes", []) if "id" in n}
    result_text = assemble_final_result(state.node_outputs, node_map)
    duration_ms = int((datetime.utcnow() - t0).total_seconds() * 1000)
    trace = {
        "nodeId": node_id,
        "nodeLabel": node_label,
        "type": "end",
        "status": "completed",
        "timestamp": t0.isoformat(),
        "durationMs": duration_ms,
        "inputs": _get_node_inputs("end", node, state.context, state.node_outputs),
        "message": "工作流执行结束",
    }
    yield RunEvent(EventType.NODE_DONE, node_id, {"trace": trace})
    yield RunEvent(EventType.WF_DONE, node_id, {"result": result_text})


@register_node("ask", metadata=_ASK_META)
async def _h_ask(ctx: NodeRunContext):
    """Human-in-the-loop: pause the run awaiting a human answer.

    Emits a ``WF_PAUSE`` event carrying the question to show the human. The
    Runner persists the exact resume position (execution_id -> workflow/state)
    and stops traversal. The run is later continued through the
    ``/execute/resume`` endpoints once the human replies. No trace item is
    emitted here, so the ask node is recorded exactly once (as *completed*) in
    ``prepare_resume`` when the answer arrives.
    """
    config = ctx.config
    state = ctx.state
    question = (
        config.get("question", "")
        or config.get("prompt", "")
        or state.context.get("user_input", "")
        or "请提供输入以继续执行。"
    )
    yield RunEvent(EventType.WF_PAUSE, ctx.node_id, {"question": question})
