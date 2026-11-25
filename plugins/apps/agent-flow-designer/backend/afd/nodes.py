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
from typing import Any, Dict, List, Optional, Tuple

from engine import (
    EventType,
    ExecutionState,
    NodeRunContext,
    RunEvent,
    WorkflowRunner,
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
from .store import _find_workflow, _load_version_from_disk
from .tools import (
    ToolApprovalRequired,
    _invoke_http_tool,
    _invoke_mcp_tool,
    _invoke_platform_tool,
    _resolve_tool_params,
    _resolve_tool_source,
)
from engine.runner import run_workflow_sync

logger = get_logger(__name__)


# ── Secret reference resolution ───────────────────────────────────────

def _is_secret_ref(value: str) -> bool:
    """Check if a value is a secret reference in the format ``ref:<workspace_id>:<secret_name>:<field>``."""
    return isinstance(value, str) and value.strip().startswith("ref:")


async def _resolve_secret_ref(
    ref: str,
    services: dict,
) -> str:
    """Resolve a secret reference from the platform credential store.

    Format: ``ref:<workspace_id>:<secret_name>:<field>``
    - ``workspace_id``: The workspace identifier (can be empty for current workspace)
    - ``secret_name``: The name of the secret in the credential store
    - ``field``: The field to extract from the secret's values (default: "value")

    Returns the decrypted secret value as a string.
    Raises RuntimeError if the reference is malformed or the secret is not found.
    """
    if not _is_secret_ref(ref):
        raise ValueError(f"Not a valid secret reference: {ref!r}")

    parts = ref.strip()[4:].split(":", 2)  # Remove 'ref:' prefix
    if len(parts) < 2:
        raise ValueError(
            f"Invalid secret reference format: {ref!r}. "
            "Expected: ref:<workspace_id>:<secret_name>[:<field>]"
        )

    workspace_id = parts[0] if parts[0] else None
    secret_name = parts[1]
    field = parts[2] if len(parts) > 2 else "value"

    if not secret_name:
        raise ValueError(f"Secret name cannot be empty in reference: {ref!r}")

    # Get credential store from services
    workspace = services.get("workspace")
    if workspace is None:
        raise RuntimeError(
            f"无法解析密钥引用「{ref}」：当前运行上下文没有可用的工作区，"
            "请先在平台凭证库中创建该密钥"
        )

    # Build the full reference key for the credential store
    # If workspace_id is specified, use it; otherwise use the current workspace
    if workspace_id:
        full_ref = f"{workspace_id}:{secret_name}"
    else:
        # Use current workspace's credential store directly
        from qwenpaw.drivers.credentials.store import AsyncCredentialStore
        from pathlib import Path

        workspace_dir = getattr(workspace, "local_workspace", None)
        if workspace_dir is None:
            raise RuntimeError(
                f"无法解析密钥引用「{ref}」：工作区缺少 local_workspace 属性"
            )
        store = AsyncCredentialStore(Path(workspace_dir) / "credentials.yaml")

        try:
            record = await store.get(secret_name)
        except Exception as exc:
            raise RuntimeError(
                f"平台密钥「{secret_name}」在工作区凭证库中不存在或读取失败；"
                f"已阻止使用未配置的密钥，请先在凭证库中创建该密钥"
            ) from exc

        value = record.values.get(field)
        if not isinstance(value, str) or not value:
            raise RuntimeError(
                f"平台密钥「{secret_name}」缺少字段「{field}」或该字段为空；"
                "已阻止使用无效密钥"
            )
        return value

    # For cross-workspace references, we'd need a different mechanism
    # For now, only support current workspace
    raise NotImplementedError(
        f"跨工作区密钥引用暂不支持：{ref!r}。请仅使用当前工作区的密钥"
    )


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
    services: Optional[dict] = None,
) -> str:
    """Execute an Agent node by calling the real LLM/chat API.

    ``on_token`` (optional) is forwarded to :func:`_call_agent_chat` so a
    streaming caller can observe incremental deltas; it does not change the
    returned text. ``live_predecessors`` restricts the injected context to the
    branches actually taken — see :func:`_build_node_prompt`. ``usage_out``
    receives this call's token counts, for the node's own trace item.
    ``services`` provides access to the credential store for resolving secret
    references in ``agentId``.
    """
    config = node.get("config", {})
    agent_id = config.get("agentId", "")
    extra_prompt = config.get("extraPrompt", "")

    # Resolve secret reference if agentId is a ref
    if _is_secret_ref(agent_id):
        if services is None:
            raise RuntimeError(
                f"无法解析 Agent ID 密钥引用「{agent_id}」：缺少 services 上下文，"
                "请确保工作流运行时传入了正确的服务句柄"
            )
        agent_id = await _resolve_secret_ref(agent_id, services)

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
    {"user_input", "user_attachments", "messages", "messages_count"} | set(SYSTEM_VARIABLE_KEYS)
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
        inputs["user_attachments"] = context.get("user_attachments", [])
        inputs["messages_count"] = len(context.get("messages", []))
        for key in SYSTEM_VARIABLE_KEYS:
            inputs[key] = context.get(key, "")
    elif node_type == "agent":
        config = node.get("config", {})
        agent_id = config.get("agentId", "")
        # Record whether agentId is a secret ref, but never the actual value
        if _is_secret_ref(agent_id):
            inputs["agentIdRef"] = True
            inputs["agentId"] = "ref:***"
        else:
            inputs["agentId"] = agent_id
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
    elif node_type == "code":
        config = node.get("config", {})
        inputs["language"] = config.get("language", "python")
        code_snippet = config.get("code", "")
        inputs["code_length"] = len(code_snippet) if code_snippet else 0
    elif node_type == "llm":
        config = node.get("config", {})
        inputs["model"] = config.get("model", "")
        inputs["temperature"] = config.get("temperature", 0.7)
        inputs["maxTokens"] = config.get("maxTokens", 2000)
        bindings = _binding_refs(config)
        if bindings:
            inputs["inputs"] = [{"name": a, "ref": r} for a, r in bindings]
        if config.get("promptTemplate"):
            inputs["promptTemplate"] = str(config["promptTemplate"])[:200]
    elif node_type == "subflow":
        config = node.get("config", {})
        workflow_id = config.get("workflowId", "")
        # Record workflowId but never expose sensitive details
        inputs["workflowId"] = workflow_id[:100] if workflow_id else ""
        input_mappings = config.get("inputs") or []
        inputs["inputMappings_count"] = len(input_mappings) if isinstance(input_mappings, list) else 0
        output_mapping = config.get("outputMapping") or {}
        inputs["hasOutputMapping"] = bool(output_mapping)
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

_SUBFLOW_META = NodeTypeDef(
    type_id="subflow",
    label="子工作流",
    description="调用另一个已发布的工作流，支持参数传递和结果返回。",
    icon="Workflow",
    color="#F97316",
    bg_color="#fff7ed",
    border_color="#F97316",
    properties=[
        PropertyField(name="label", type="text", label="节点名称", default="子工作流"),
        PropertyField(name="description", type="textarea", label="描述"),
        PropertyField(name="workflowId", type="text", label="工作流 ID", required=True, description="要调用的目标工作流 ID"),
        PropertyField(name="inputs", type="array", label="输入映射", description="将当前工作流的变量传递给子工作流"),
        PropertyField(name="outputMapping", type="object", label="输出映射", description="将子工作流的输出映射到当前工作流的变量"),
    ],
    supports_error_policy=True,
    supports_retry=False,
)

# ── Subflow recursion tracking ───────────────────────────────────────

# Thread-local call stack for detecting recursive subflow calls
import threading
_subflow_call_stack = threading.local()

# Global registry for mock workflows (used by tests)
_SUBFLOW_MOCK_REGISTRY: Dict[str, Dict[str, Any]] = {}


def _register_mock_workflow(workflow_id: str, workflow: Dict[str, Any]) -> None:
    """Register a mock workflow for testing purposes."""
    _SUBFLOW_MOCK_REGISTRY[workflow_id] = workflow


def _unregister_mock_workflow(workflow_id: str) -> None:
    """Unregister a mock workflow."""
    _SUBFLOW_MOCK_REGISTRY.pop(workflow_id, None)


def _clear_mock_registry() -> None:
    """Clear all mock workflows."""
    _SUBFLOW_MOCK_REGISTRY.clear()


def _get_call_stack() -> List[str]:
    """Get the current subflow call stack."""
    if not hasattr(_subflow_call_stack, 'stack'):
        _subflow_call_stack.stack = []
    return _subflow_call_stack.stack


def _push_call(workflow_id: str) -> None:
    """Push a workflow ID onto the call stack."""
    stack = _get_call_stack()
    stack.append(workflow_id)


def _pop_call() -> None:
    """Pop a workflow ID from the call stack."""
    stack = _get_call_stack()
    if stack:
        stack.pop()


def _detect_recursion(target_wf_id: str) -> bool:
    """Check if calling target_wf_id would cause recursion."""
    stack = _get_call_stack()
    return target_wf_id in stack


# ── Workflow loading utilities ───────────────────────────────────────

def _load_subflow_workflow(workflow_id: str) -> Optional[Dict[str, Any]]:
    """Load a workflow by ID, preferring deployed version.
    
    This function searches for workflows in the following order:
    1. Check the global mock registry (for testing)
    2. Load from disk using the store module
    3. Return None if not found
    """
    # First check the global mock registry
    if workflow_id in _SUBFLOW_MOCK_REGISTRY:
        logger.debug(f"Found mock workflow {workflow_id} in global registry")
        return _SUBFLOW_MOCK_REGISTRY[workflow_id]
    
    # Try to load from disk
    try:
        wf = _find_workflow(workflow_id)
        if wf:
            # If deployed, use the deployed version snapshot
            deployed_version_id = wf.get("deployed_version_id")
            if deployed_version_id:
                v = _load_version_from_disk(workflow_id,deployed_version_id)
                if v.get("id") == deployed_version_id:
                    return {
                        "id": workflow_id,
                        "name": v.get("name", ""),
                        "description": v.get("description", ""),
                        "nodes": v.get("nodes", []),
                        "edges": v.get("edges", []),
                        "system_prompt": v.get("system_prompt", ""),
                    }

            return wf
    except Exception as exc:
        logger.debug(f"Failed to load workflow from disk: {exc}")
        pass
    
    logger.warning(f"Workflow {workflow_id} not found in mock registry or disk")
    return None


# ── Context isolation helpers ────────────────────────────────────────

def _build_child_context(
    parent_state,
    inputs_mapping: List[Dict[str, str]],
) -> Dict[str, Any]:
    """Build an isolated context for the child workflow.
    
    Maps parent variables to child inputs based on the mapping configuration.
    The child context starts fresh but includes mapped variables.
    """
    child_context: Dict[str, Any] = {}
    
    # Map parent variables to child inputs
    for mapping in inputs_mapping:
        if not isinstance(mapping, dict):
            continue
        child_var = mapping.get("name", "")
        parent_ref = mapping.get("ref", "") or mapping.get("value", "")
        
        if not child_var or not parent_ref:
            continue
        
        # Resolve the parent reference
        value, found = _resolve_variable_ex(parent_ref, parent_state.context, parent_state.node_outputs)
        if found:
            child_context[child_var] = value
    
    # Always pass through user_input if not explicitly mapped
    if "user_input" not in child_context and "user_input" in parent_state.context:
        child_context["user_input"] = parent_state.context["user_input"]
    
    return child_context


def _apply_output_mapping(
    parent_state,
    child_result: Dict[str, Any],
    output_mapping: Dict[str, str],
) -> None:
    """Apply child workflow outputs back to parent context.
    
    Maps child workflow results to parent variables based on the mapping.
    Supports both direct keys and node_{id}_output references.
    """
    if not isinstance(output_mapping, dict):
        return
    
    for parent_var, child_ref in output_mapping.items():
        if not parent_var or not child_ref:
            continue
        
        # Try to resolve from child result
        value = None
        
        # First try direct key lookup
        if child_ref in child_result:
            value = child_result[child_ref]
        # Then try node_{id}_output pattern: extract node_id and look it up
        elif child_ref.startswith("node_") and child_ref.endswith("_output"):
            node_id = child_ref[5:-7]  # Extract node_id from "node_X_output"
            if node_id in child_result:
                node_out = child_result[node_id]
                # If it's a dict with 'output' key, use that
                if isinstance(node_out, dict) and "output" in node_out:
                    value = node_out["output"]
                else:
                    value = node_out
        
        if value is not None:
            parent_state.context[parent_var] = value
            parent_state.node_outputs[parent_var] = value

_CODE_META = NodeTypeDef(
    type_id="code",
    label="代码",
    description="执行 Python 或 JavaScript 代码片段，支持变量注入和输出捕获。",
    icon="Code",
    color="#6366F1",
    bg_color="#eef2ff",
    border_color="#6366F1",
    properties=[
        PropertyField(name="label", type="text", label="节点名称", default="代码"),
        PropertyField(name="description", type="textarea", label="描述"),
        PropertyField(name="language", type="select", label="语言", default="python", options=[
            {"value": "python", "label": "Python"},
            {"value": "javascript", "label": "JavaScript"},
        ]),
        PropertyField(name="code", type="textarea", label="代码", required=True, description="要执行的代码片段"),
        PropertyField(name="outputSchema", type="textarea", label="输出声明", description="JSON Schema 格式声明输出结构"),
    ],
    supports_error_policy=True,
    supports_retry=True,
)

_LLM_META = NodeTypeDef(
    type_id="llm",
    label="大模型",
    description="直接调用大模型 API，不依赖平台 Agent。",
    icon="Brain",
    color="#14B8A6",
    bg_color="#f0fdfa",
    border_color="#14B8A6",
    properties=[
        PropertyField(name="label", type="text", label="节点名称", default="大模型"),
        PropertyField(name="description", type="textarea", label="描述"),
        PropertyField(name="model", type="text", label="模型 ID", required=True, description="模型标识符（providerId:modelId）"),
        PropertyField(name="systemPrompt", type="textarea", label="系统提示词", description="系统角色设定"),
        PropertyField(name="promptTemplate", type="textarea", label="用户提示词模板", description="支持 {{variable}} 引用"),
        PropertyField(name="temperature", type="number", label="温度", default=0.7, description="0-2 之间"),
        PropertyField(name="maxTokens", type="number", label="最大 Token 数", default=2000),
        PropertyField(name="outputSchema", type="textarea", label="输出声明", description="JSON Schema 格式声明输出结构"),
    ],
    supports_error_policy=True,
    supports_retry=True,
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
                services=ctx.services,  # Pass services for secret resolution
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


@register_node("subflow", metadata=_SUBFLOW_META)
async def _h_subflow(ctx: NodeRunContext):
    """Execute a subflow node by calling another published workflow.
    
    This handler implements the core subflow functionality:
    1. Recursion detection - prevents infinite loops
    2. Context isolation - child workflow has its own isolated context
    3. Input mapping - maps parent variables to child inputs
    4. Output mapping - maps child results back to parent context
    5. Workflow loading - loads deployed version if available
    """
    print(f"_h_subflow CALLED: node_id={ctx.node_id}")
    node = ctx.node
    node_id = ctx.node_id
    node_label = node.get("label", node_id)
    state = ctx.state
    config = node.get("config") or {}
    t0 = datetime.utcnow()
    
    print(f"_h_subflow: config={config}")
    
    # Extract configuration
    target_wf_id = config.get("workflowId", "")
    inputs_mapping = config.get("inputs", []) or []
    output_mapping = config.get("outputMapping", {}) or {}
    
    print(f"DEBUG _h_subflow: node_id={node_id}, target_wf_id={target_wf_id}")
    print(f"DEBUG _h_subflow: config keys={list(config.keys())}")
    
    # Validate workflow ID
    if not target_wf_id:
        yield RunEvent(EventType.NODE_ERROR, node_id, {"trace": {
            "nodeId": node_id,
            "nodeLabel": node_label,
            "type": "subflow",
            "status": "failed",
            "timestamp": t0.isoformat(),
            "durationMs": 0,
            "error": "工作流 ID 不能为空",
            "message": "子工作流节点执行失败: 必须指定目标工作流 ID",
        }})
        return
    
    # Check for recursion
    if _detect_recursion(target_wf_id):
        call_chain = " -> ".join(_get_call_stack() + [target_wf_id])
        yield RunEvent(EventType.NODE_ERROR, node_id, {"trace": {
            "nodeId": node_id,
            "nodeLabel": node_label,
            "type": "subflow",
            "status": "failed",
            "timestamp": t0.isoformat(),
            "durationMs": 0,
            "error": f"检测到递归调用: {call_chain}",
            "message": f"子工作流节点执行失败: 递归调用检测，调用链为 {call_chain}",
        }})
        return
    
    # Load target workflow
    print(f"DEBUG: Loading workflow {target_wf_id}")
    print(f"DEBUG: Registry keys: {list(_SUBFLOW_MOCK_REGISTRY.keys())}")
    target_wf = _load_subflow_workflow(target_wf_id)
    print(f"DEBUG: Loaded workflow: {target_wf is not None}")
    if target_wf is None:
        yield RunEvent(EventType.NODE_ERROR, node_id, {"trace": {
            "nodeId": node_id,
            "nodeLabel": node_label,
            "type": "subflow",
            "status": "failed",
            "timestamp": t0.isoformat(),
            "durationMs": 0,
            "error": f"工作流不存在: {target_wf_id}",
            "message": f"子工作流节点执行失败: 找不到目标工作流 {target_wf_id}",
        }})
        return
    
    # Build isolated child context with input mapping
    child_context = _build_child_context(state, inputs_mapping)
    
    # Push current workflow onto call stack
    _push_call(state.workflow_id)
    _push_call(target_wf_id)
    
    try:
        # Execute child workflow
        result = await run_workflow_sync(
            workflow_id=target_wf_id,
            workflow=target_wf,
            context=child_context,
            services=ctx.services,
        )
        
        duration_ms = int((datetime.utcnow() - t0).total_seconds() * 1000)
        
        # Check if child execution succeeded
        if not result.get("success"):
            error_detail = result.get("detail", "子工作流执行失败")
            yield RunEvent(EventType.NODE_ERROR, node_id, {"trace": {
                "nodeId": node_id,
                "nodeLabel": node_label,
                "type": "subflow",
                "status": "failed",
                "timestamp": t0.isoformat(),
                "durationMs": duration_ms,
                "error": error_detail[:500],
                "message": f"子工作流节点执行失败: {error_detail[:200]}",
            }})
            return
        
        # Extract child workflow result
        child_data = result.get("data", {})
        child_status = child_data.get("status", "")
        
        # Try to extract the last non-start/end node's output from node_outputs
        child_node_outputs = child_data.get("node_outputs", {})
        if child_node_outputs:
            # Filter out start and end nodes, get the last one
            meaningful_outputs = {
                nid: out for nid, out in child_node_outputs.items()
                if not nid.endswith("_start") and not nid.endswith("_end") 
                and nid != "start" and nid != "end"
            }
            if meaningful_outputs:
                # Get the last value (by insertion order)
                child_result_text = list(meaningful_outputs.values())[-1]
                # If it's a dict with 'output' key, use that
                if isinstance(child_result_text, dict) and "output" in child_result_text:
                    child_result_text = child_result_text["output"]
            else:
                # Fallback to formatted result
                child_result_text = child_data.get("result", "")
        else:
            # Fallback to formatted result
            child_result_text = child_data.get("result", "")
        
        # Apply output mapping
        if output_mapping and child_status == "completed":
            # Pass the full child_node_outputs so _apply_output_mapping can resolve references
            _apply_output_mapping(
                state,
                child_node_outputs or {},
                output_mapping,
            )
        
        # Set the subflow node's output to the child's result
        state.node_outputs[node_id] = child_result_text
        state.context[f"node_{node_id}_output"] = child_result_text
        
        # Emit success event
        yield RunEvent(EventType.NODE_DONE, node_id, {"trace": {
            "nodeId": node_id,
            "nodeLabel": node_label,
            "type": "subflow",
            "status": "completed",
            "timestamp": t0.isoformat(),
            "durationMs": duration_ms,
            "inputs": _get_node_inputs("subflow", node, state.context, state.node_outputs),
            "output": child_result_text[:500] if isinstance(child_result_text, str) else str(child_result_text)[:500],
            "message": f"子工作流执行完成 ({duration_ms}ms)",
        }})
        
    finally:
        # Always pop from call stack, even on error
        _pop_call()  # Pop target_wf_id
        _pop_call()  # Pop parent workflow_id


@register_node("code", metadata=_CODE_META)
async def _h_code(ctx: NodeRunContext):
    """Execute user-provided Python or JavaScript code.

    Python code runs in a restricted environment with access only to injected
    variables from upstream nodes. JavaScript support is stubbed for now.
    """
    node = ctx.node
    node_id = ctx.node_id
    node_label = node.get("label", node_id)
    state = ctx.state
    config = node.get("config") or {}
    t0 = datetime.utcnow()

    language = config.get("language", "python").lower()
    code = config.get("code", "")

    if not code.strip():
        yield RunEvent(EventType.NODE_ERROR, node_id, {"trace": {
            "nodeId": node_id,
            "nodeLabel": node_label,
            "type": "code",
            "status": "failed",
            "timestamp": t0.isoformat(),
            "durationMs": 0,
            "error": "代码为空",
            "message": "代码节点执行失败: 代码不能为空",
        }})
        return

    # Build execution context with upstream outputs
    exec_globals = {
        "__builtins__": __builtins__,
        "json": json,
        "datetime": datetime,
    }
    # Inject upstream node outputs as variables
    for nid, output in state.node_outputs.items():
        var_name = f"node_{nid}_output"
        exec_globals[var_name] = output
    # Also inject context variables
    for key, value in state.context.items():
        if key.startswith("node_") or key in SYSTEM_VARIABLE_KEYS:
            exec_globals[key] = value

    output = None
    error = None
    try:
        if language == "python":
            # Execute Python code
            exec(code, exec_globals)
            # Capture output: look for 'result' variable or last expression
            output = exec_globals.get("result", exec_globals.get("output", ""))
        elif language == "javascript":
            # JavaScript execution is not supported yet — fail loudly
            raise NotImplementedError(
                "JavaScript 代码执行暂不支持，请使用 Python"
            )
        else:
            raise ValueError(f"不支持的编程语言: {language}")
    except Exception as exc:  # noqa: BLE001
        error = str(exc) or f"{type(exc).__name__}: 代码执行异常"

    duration_ms = int((datetime.utcnow() - t0).total_seconds() * 1000)

    if error:
        yield RunEvent(EventType.NODE_ERROR, node_id, {"trace": {
            "nodeId": node_id,
            "nodeLabel": node_label,
            "type": "code",
            "status": "failed",
            "timestamp": t0.isoformat(),
            "durationMs": duration_ms,
            "inputs": _get_node_inputs("code", node, state.context, state.node_outputs),
            "error": error[:500],
            "message": f"代码节点执行失败: {error[:200]}",
        }})
        return

    # Validate against output schema if declared
    schema_fields, schema_errors = parse_output_schema(config.get("outputSchema"))
    published: Any = output
    if schema_fields:
        if isinstance(output, str):
            parsed, ok = parse_json_output(output)
            if ok:
                normalized, field_errors = validate_output(parsed, schema_fields)
                if field_errors:
                    yield RunEvent(EventType.NODE_ERROR, node_id, {"trace": {
                        "nodeId": node_id, "nodeLabel": node_label, "type": "code",
                        "status": "failed", "timestamp": t0.isoformat(),
                        "durationMs": duration_ms,
                        "inputs": _get_node_inputs("code", node, state.context, state.node_outputs),
                        "rawOutput": output[:500],
                        "schemaErrors": field_errors,
                        "error": "; ".join(field_errors)[:500],
                        "message": f"代码节点输出不符合声明: {field_errors[0]}",
                    }})
                    return
                published = normalized
            else:
                yield RunEvent(EventType.NODE_ERROR, node_id, {"trace": {
                    "nodeId": node_id, "nodeLabel": node_label, "type": "code",
                    "status": "failed", "timestamp": t0.isoformat(),
                    "durationMs": duration_ms,
                    "inputs": _get_node_inputs("code", node, state.context, state.node_outputs),
                    "rawOutput": output[:500],
                    "schemaErrors": ["输出不是合法 JSON，无法按声明的字段校验"],
                    "error": "输出不是合法 JSON",
                    "message": "代码节点输出不符合声明: 输出不是合法 JSON",
                }})
                return
        else:
            normalized, field_errors = validate_output(output, schema_fields)
            if field_errors:
                yield RunEvent(EventType.NODE_ERROR, node_id, {"trace": {
                    "nodeId": node_id, "nodeLabel": node_label, "type": "code",
                    "status": "failed", "timestamp": t0.isoformat(),
                    "durationMs": duration_ms,
                    "inputs": _get_node_inputs("code", node, state.context, state.node_outputs),
                    "rawOutput": str(output)[:500],
                    "schemaErrors": field_errors,
                    "error": "; ".join(field_errors)[:500],
                    "message": f"代码节点输出不符合声明: {field_errors[0]}",
                }})
                return
            published = normalized

    state.node_outputs[node_id] = published
    state.context[f"node_{node_id}_output"] = published
    state.node_outputs_history.setdefault(node_id, []).append(published)

    yield RunEvent(EventType.NODE_DONE, node_id, {"trace": {
        "nodeId": node_id,
        "nodeLabel": node_label,
        "type": "code",
        "status": "completed",
        "timestamp": t0.isoformat(),
        "durationMs": duration_ms,
        "inputs": _get_node_inputs("code", node, state.context, state.node_outputs),
        "output": str(published)[:500] if published else "",
        "message": f"代码节点执行完成 ({duration_ms}ms)",
    }})


@register_node("llm", metadata=_LLM_META)
async def _h_llm(ctx: NodeRunContext):
    """Call an LLM directly without going through the platform Agent layer.

    Supports configurable model, temperature, max_tokens, system prompt, and
    user prompt template with variable interpolation.
    """
    node = ctx.node
    node_id = ctx.node_id
    node_label = node.get("label", node_id)
    state = ctx.state
    config = node.get("config") or {}
    t0 = datetime.utcnow()

    model = config.get("model", "")
    if not model:
        yield RunEvent(EventType.NODE_ERROR, node_id, {"trace": {
            "nodeId": node_id,
            "nodeLabel": node_label,
            "type": "llm",
            "status": "failed",
            "timestamp": t0.isoformat(),
            "durationMs": 0,
            "error": "模型 ID 未配置",
            "message": "大模型节点执行失败: 必须配置模型 ID（格式：providerId:modelId）",
        }})
        return

    system_prompt = config.get("systemPrompt", "")
    prompt_template = config.get("promptTemplate", "")
    temperature = float(config.get("temperature", 0.7))
    max_tokens = int(config.get("maxTokens", 2000))

    # Build user message from template
    user_input = _build_node_prompt(
        config, state.context, state.node_outputs, ctx.live_predecessors
    )

    # Construct messages
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_input})

    # Call LLM via llm_client
    usage: dict = {}
    try:
        result = await _call_agent_chat(
            model,  # Use model ID directly as agent_id parameter
            messages,
            on_token=None,
            usage_out=usage,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    except Exception as exc:  # noqa: BLE001
        error = str(exc) or f"{type(exc).__name__}: LLM 调用异常"
        yield RunEvent(EventType.NODE_ERROR, node_id, {"trace": {
            "nodeId": node_id,
            "nodeLabel": node_label,
            "type": "llm",
            "status": "failed",
            "timestamp": t0.isoformat(),
            "durationMs": int((datetime.utcnow() - t0).total_seconds() * 1000),
            "inputs": _get_node_inputs("llm", node, state.context, state.node_outputs),
            "error": error[:500],
            "message": f"大模型节点执行失败: {error[:200]}",
        }})
        return

    duration_ms = int((datetime.utcnow() - t0).total_seconds() * 1000)

    # Validate against output schema if declared
    schema_fields, schema_errors = parse_output_schema(config.get("outputSchema"))
    published: Any = result
    if schema_fields:
        parsed, ok = parse_json_output(result)
        if not ok:
            yield RunEvent(EventType.NODE_ERROR, node_id, {"trace": {
                "nodeId": node_id, "nodeLabel": node_label, "type": "llm",
                "status": "failed", "timestamp": t0.isoformat(),
                "durationMs": duration_ms,
                "inputs": _get_node_inputs("llm", node, state.context, state.node_outputs),
                "rawOutput": result[:500],
                "schemaErrors": ["输出不是合法 JSON，无法按声明的字段校验"],
                "error": "输出不是合法 JSON",
                "message": "大模型节点输出不符合声明: 输出不是合法 JSON",
            }})
            return
        normalized, field_errors = validate_output(parsed, schema_fields)
        if field_errors:
            yield RunEvent(EventType.NODE_ERROR, node_id, {"trace": {
                "nodeId": node_id, "nodeLabel": node_label, "type": "llm",
                "status": "failed", "timestamp": t0.isoformat(),
                "durationMs": duration_ms,
                "inputs": _get_node_inputs("llm", node, state.context, state.node_outputs),
                "rawOutput": result[:500],
                "schemaErrors": field_errors,
                "error": "; ".join(field_errors)[:500],
                "message": f"大模型节点输出不符合声明: {field_errors[0]}",
            }})
            return
        published = normalized

    state.node_outputs[node_id] = published
    state.context[f"node_{node_id}_output"] = published
    state.node_outputs_history.setdefault(node_id, []).append(published)

    yield RunEvent(EventType.NODE_DONE, node_id, {"trace": {
        "nodeId": node_id,
        "nodeLabel": node_label,
        "type": "llm",
        "status": "completed",
        "timestamp": t0.isoformat(),
        "durationMs": duration_ms,
        "inputs": _get_node_inputs("llm", node, state.context, state.node_outputs),
        "output": str(published)[:500] if published else "",
        **usage,
        "message": f"大模型节点执行完成 ({duration_ms}ms)",
    }})


# ── Loop container helpers ────────────────────────────────────────────

_LOOP_TEMPLATE_RE = re.compile(r"\{\{\s*([^\{\}]+?)\s*\}\}")


def _extract_loop_body(workflow: Dict[str, Any], loop_node_id: str) -> Tuple[List[dict], List[dict]]:
    """Extract loop body nodes and internal edges for a loop container.

    Loop body nodes are identified by ``parentId == loop_node_id``.
    Internal edges are those whose both endpoints lie inside the loop body.
    """
    nodes = workflow.get("nodes", [])
    edges = workflow.get("edges", [])

    body_nodes = [n for n in nodes if n.get("parentId") == loop_node_id]
    body_node_ids = {n["id"] for n in body_nodes}

    body_edges = []
    for edge in edges:
        if edge.get("source") in body_node_ids and edge.get("target") in body_node_ids:
            body_edges.append(dict(edge))

    return body_nodes, body_edges


def _build_loop_sub_workflow(body_nodes: List[dict], body_edges: List[dict]) -> Dict[str, Any]:
    """Build a sub-workflow with virtual start/end nodes for the loop body.

    Virtual nodes ensure the loop body can be executed by a standalone
    :class:`WorkflowRunner` without relying on the parent runner's
    scheduler state.
    """
    # Copy edges to avoid mutating the caller's list
    edges = list(body_edges)
    body_node_ids = {n["id"] for n in body_nodes}

    # Entry nodes: no incoming edges within the loop body
    incoming_targets = {e["target"] for e in edges}
    entry_nodes = [n for n in body_nodes if n["id"] not in incoming_targets]

    # Exit nodes: no outgoing edges within the loop body
    outgoing_sources = {e["source"] for e in edges}
    exit_nodes = [n for n in body_nodes if n["id"] not in outgoing_sources]

    virtual_start = {"id": "_loop_start", "type": "start", "label": "循环开始"}
    virtual_end = {"id": "_loop_end", "type": "end", "label": "循环结束"}

    for entry in entry_nodes:
        edges.append({"source": virtual_start["id"], "target": entry["id"]})
    for exit_node in exit_nodes:
        edges.append({"source": exit_node["id"], "target": virtual_end["id"]})

    return {
        "nodes": [virtual_start, virtual_end] + body_nodes,
        "edges": edges,
    }


def _evaluate_while_condition(condition: str, context: Dict[str, Any]) -> bool:
    """Evaluate a while loop condition expression.

    Supports ``{{ var_name }}`` substitution (same syntax as prompt templates).
    The expression is evaluated in a restricted ``eval`` sandbox.
    """
    if not condition:
        return False

    def _replace_var(match: Any) -> str:
        var_name = match.group(1).strip()
        value = context.get(var_name, "")
        if isinstance(value, bool):
            return str(value)
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, str):
            return repr(value)
        return repr(value)

    try:
        expr = _LOOP_TEMPLATE_RE.sub(_replace_var, condition)
        return bool(eval(expr, {"__builtins__": {}}, {}))  # noqa: S307
    except Exception:
        return False


# ── Loop container node metadata ──────────────────────────────────────

_FOR_EACH_META = NodeTypeDef(
    type_id="for_each",
    label="For Each",
    description="遍历数组，每次迭代执行内部子图。",
    icon="Repeat",
    color="#10B981",
    bg_color="#ecfdf5",
    border_color="#10B981",
    properties=[
        PropertyField(name="label", type="text", label="节点名称", default="For Each"),
        PropertyField(name="iterateOver", type="text", label="遍历变量", required=True, description="要遍历的数组变量名"),
        PropertyField(name="loopVariable", type="text", label="循环变量", default="item", description="每次迭代中的变量名"),
        PropertyField(name="maxIterations", type="number", label="最大迭代次数", default=100),
    ],
    supports_error_policy=False,
    supports_retry=False,
)

_WHILE_META = NodeTypeDef(
    type_id="while",
    label="While",
    description="条件为真时重复执行内部子图。",
    icon="RotateCcw",
    color="#8B5CF6",
    bg_color="#f5f3ff",
    border_color="#8B5CF6",
    properties=[
        PropertyField(name="label", type="text", label="节点名称", default="While"),
        PropertyField(name="condition", type="textarea", label="条件表达式", required=True, description="返回 true/false 的表达式，例如：{{ count }} < 10"),
        PropertyField(name="maxIterations", type="number", label="最大迭代次数", default=100),
    ],
    supports_error_policy=False,
    supports_retry=False,
)


@register_node("for_each", metadata=_FOR_EACH_META)
async def _h_for_each(ctx: NodeRunContext):
    """Execute a for-each loop node.

    Each iteration runs the loop body as an isolated sub-workflow via a
    child :class:`WorkflowRunner`.  Outputs are prefixed with iteration
    info to avoid key collisions in the parent state.
    """
    node = ctx.node
    node_id = ctx.node_id
    state = ctx.state
    config = node.get("config", {})

    iterate_over = config.get("iterateOver", "")
    loop_var = config.get("loopVariable", "item")
    max_iterations = config.get("maxIterations", 100)

    items = state.context.get(iterate_over, [])
    if not isinstance(items, list):
        items = []

    body_nodes, body_edges = _extract_loop_body(ctx.workflow, node_id)

    if not body_nodes:
        state.node_outputs[node_id] = {"iterations": 0, "lastResult": None}
        yield RunEvent(EventType.NODE_DONE, node_id, {"trace": {
            "nodeId": node_id,
            "nodeLabel": node.get("label", node_id),
            "type": "for_each",
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
            "durationMs": 0,
            "output": state.node_outputs[node_id],
            "message": "For Each 节点执行完成（无循环体）",
        }})
        return

    sub_workflow = _build_loop_sub_workflow(body_nodes, body_edges)

    total_iterations = 0
    last_result = None

    for i, item in enumerate(items[:max_iterations]):
        total_iterations += 1
        state.context[loop_var] = item

        sub_state = ExecutionState(
            execution_id=f"{state.execution_id}_loop_{i}",
            workflow_id=state.workflow_id,
            context=dict(state.context),
        )

        sub_runner = WorkflowRunner(sub_workflow, sub_state, services=ctx.services)

        async for event in sub_runner.run():
            yield event

        # Merge context updates from sub runner back to parent state
        state.context.update(sub_state.context)

        # Merge outputs with iteration prefix to avoid collisions
        for key, value in sub_state.node_outputs.items():
            state.node_outputs[f"{node_id}_{key}_{i}"] = value

        # Merge trace items with prefixed node ids
        for trace_item in sub_state.trace_items:
            prefixed = dict(trace_item)
            prefixed["nodeId"] = f"{node_id}/{prefixed.get('nodeId', '')}"
            prefixed["nodeLabel"] = f"[迭代 {i}] {prefixed.get('nodeLabel', '')}"
            state.trace_items.append(prefixed)

        last_result = sub_state.result

    # Clean up loop variable to avoid polluting downstream nodes
    state.context.pop(loop_var, None)

    state.node_outputs[node_id] = {
        "iterations": total_iterations,
        "lastResult": last_result,
    }

    yield RunEvent(EventType.NODE_DONE, node_id, {"trace": {
        "nodeId": node_id,
        "nodeLabel": node.get("label", node_id),
        "type": "for_each",
        "status": "completed",
        "timestamp": datetime.utcnow().isoformat(),
        "durationMs": 0,
        "output": state.node_outputs[node_id],
        "message": f"For Each 节点执行完成（共 {total_iterations} 次迭代）",
    }})


@register_node("while", metadata=_WHILE_META)
async def _h_while(ctx: NodeRunContext):
    """Execute a while loop node.

    Evaluates the condition before each iteration.  The loop body is run
    as an isolated sub-workflow, exactly like :func:`_h_for_each`.
    """
    node = ctx.node
    node_id = ctx.node_id
    state = ctx.state
    config = node.get("config", {})

    condition = config.get("condition", "")
    max_iterations = config.get("maxIterations", 100)

    body_nodes, body_edges = _extract_loop_body(ctx.workflow, node_id)

    if not body_nodes:
        state.node_outputs[node_id] = {"iterations": 0, "lastResult": None}
        yield RunEvent(EventType.NODE_DONE, node_id, {"trace": {
            "nodeId": node_id,
            "nodeLabel": node.get("label", node_id),
            "type": "while",
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
            "durationMs": 0,
            "output": state.node_outputs[node_id],
            "message": "While 节点执行完成（无循环体）",
        }})
        return

    sub_workflow = _build_loop_sub_workflow(body_nodes, body_edges)

    total_iterations = 0
    last_result = None

    for i in range(max_iterations):
        should_continue = _evaluate_while_condition(condition, state.context)
        if not should_continue:
            break

        total_iterations += 1

        sub_state = ExecutionState(
            execution_id=f"{state.execution_id}_loop_{i}",
            workflow_id=state.workflow_id,
            context=dict(state.context),
        )

        sub_runner = WorkflowRunner(sub_workflow, sub_state, services=ctx.services)

        async for event in sub_runner.run():
            yield event

        # Merge context updates from sub runner back to parent state
        state.context.update(sub_state.context)

        for key, value in sub_state.node_outputs.items():
            state.node_outputs[f"{node_id}_{key}_{i}"] = value

        for trace_item in sub_state.trace_items:
            prefixed = dict(trace_item)
            prefixed["nodeId"] = f"{node_id}/{prefixed.get('nodeId', '')}"
            prefixed["nodeLabel"] = f"[迭代 {i}] {prefixed.get('nodeLabel', '')}"
            state.trace_items.append(prefixed)

        last_result = sub_state.result

    state.node_outputs[node_id] = {
        "iterations": total_iterations,
        "lastResult": last_result,
    }

    yield RunEvent(EventType.NODE_DONE, node_id, {"trace": {
        "nodeId": node_id,
        "nodeLabel": node.get("label", node_id),
        "type": "while",
        "status": "completed",
        "timestamp": datetime.utcnow().isoformat(),
        "durationMs": 0,
        "output": state.node_outputs[node_id],
        "message": f"While 节点执行完成（共 {total_iterations} 次迭代）",
    }})



