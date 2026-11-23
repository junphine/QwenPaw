# -*- coding: utf-8 -*-
"""Static (design-time) workflow validation.

Graph shape checks (reachability, cycles, start/end shape), variable-reference
and operator-type checking, per-source tool-node gates, retry/timeout config
gates, and the publish/deploy refusal helper.
"""

from typing import Dict, List

from fastapi import HTTPException

from engine import ERROR_HANDLE, registered_types
from engine.schema import parse_output_schema

from .nodes import _START_OUTPUT_FIELDS, _TEMPLATE_RE
from .routing import _DELTA_OPERATORS
from .tools import (
    _HTTP_METHODS,
    _TOOL_SOURCES,
    _checked_secret_env_name,
    _checked_secret_field,
    _checked_secret_ref,
    _resolve_tool_source,
)


#: Node types the designer offers the ``onError`` policy for, and therefore the
#: only ones that render an error port a branch edge can attach to.
_ON_ERROR_NODE_TYPES = frozenset({"agent", "tool"})


def _issue(code: str, message: str, node_id: str = "", node_label: str = "") -> dict:
    return {"code": code, "message": message, "nodeId": node_id, "nodeLabel": node_label}


def _reachable_from_starts(
    start_ids: List[str], adjacency: Dict[str, List[str]]
) -> set:
    seen = set(start_ids)
    frontier = list(start_ids)
    while frontier:
        nid = frontier.pop(0)
        for tgt in adjacency.get(nid, []):
            if tgt not in seen:
                seen.add(tgt)
                frontier.append(tgt)
    return seen


def _ancestors_of(
    node_id: str, reverse: Dict[str, List[str]]
) -> set:
    seen = set()
    frontier = list(reverse.get(node_id, []))
    while frontier:
        nid = frontier.pop(0)
        if nid in seen:
            continue
        seen.add(nid)
        frontier.extend(reverse.get(nid, []))
    return seen


def _has_cycle(adjacency: Dict[str, List[str]]) -> bool:
    """True when the graph contains a cycle.

    The engine tolerates cycles (it drops the back edges) but a loop is almost
    always unintended, so the validator warns about it.
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color: Dict[str, int] = {}
    for root in adjacency:
        if color.get(root, WHITE) != WHITE:
            continue
        stack = [(root, iter(adjacency.get(root, [])))]
        color[root] = GRAY
        while stack:
            nid, children = stack[-1]
            for tgt in children:
                state = color.get(tgt, WHITE)
                if state == GRAY:
                    return True
                if state == WHITE:
                    color[tgt] = GRAY
                    stack.append((tgt, iter(adjacency.get(tgt, []))))
                    break
            else:
                color[nid] = BLACK
                stack.pop()
    return False


def _iter_variable_refs(node: dict) -> List[tuple]:
    """Yield ``(reference, where)`` pairs a node declares, for static checking."""
    config = node.get("config") or {}
    node_type = node.get("type", "")
    refs: List[tuple] = []

    if node_type == "router":
        for branch in config.get("branches") or []:
            for cond in branch.get("conditions") or []:
                ref = str(cond.get("variable") or "").strip()
                if ref:
                    refs.append((ref, f"分支「{branch.get('name') or branch.get('id', '')}」条件"))
            baseline = str(_cond_baseline(branch) or "").strip()
            if baseline:
                refs.append((baseline, f"分支「{branch.get('name') or branch.get('id', '')}」基准"))
        for ref in config.get("inputs") or []:
            if isinstance(ref, str) and ref.strip():
                refs.append((ref.strip(), "路由输入变量"))

    template = str(config.get("promptTemplate") or "")
    if template:
        for match in _TEMPLATE_RE.finditer(template):
            ref = match.group(1).strip()
            if ref:
                refs.append((ref, "提示词模板"))

    for binding in config.get("inputs") or []:
        if isinstance(binding, dict):
            ref = str(binding.get("ref") or binding.get("value") or "").strip()
            if ref:
                refs.append((ref, f"绑定「{binding.get('name') or ref}」"))

    if node_type == "tool":
        for item in config.get("params") or []:
            if isinstance(item, dict) and (
                str(item.get("valueType") or "literal").strip().lower() == "variable"
            ):
                ref = str(item.get("value") or "").strip()
                if ref:
                    refs.append((ref, f"工具参数「{item.get('name') or ref}」"))
        if _resolve_tool_source(config) == "http":
            for field_key in ("url", "body"):
                for match in _TEMPLATE_RE.finditer(str(config.get(field_key) or "")):
                    ref = match.group(1).strip()
                    if ref:
                        refs.append((ref, f"HTTP {field_key}"))
            for map_key in ("headers", "query"):
                for value in (config.get(map_key) or {}).values():
                    if not isinstance(value, str):
                        continue
                    for match in _TEMPLATE_RE.finditer(value):
                        ref = match.group(1).strip()
                        if ref:
                            refs.append((ref, f"HTTP {map_key}"))

    return refs


_STRING_OPERATORS = frozenset({"contains", "starts_with", "ends_with", "regex"})
_NUMERIC_OPERATORS = frozenset({"gt", "lt", "ge", "le"})


def _iter_condition_operators(node: dict) -> List[tuple]:
    """Yield ``(reference, operator)`` for router conditions.

    Kept separate from _iter_variable_refs so that helper's ``(ref, where)``
    contract — and every caller of it — stays as it is.
    """
    pairs: List[tuple] = []
    for branch in (node.get("config") or {}).get("branches") or []:
        for cond in branch.get("conditions") or []:
            ref = str(cond.get("variable") or "").strip()
            operator = str(cond.get("operator") or "").strip()
            if ref and operator:
                pairs.append((ref, operator))
    return pairs


def _cond_baseline(branch: dict) -> str:
    """The baseline reference of a delta condition, when the branch uses one."""
    for cond in branch.get("conditions") or []:
        if cond.get("operator") in _DELTA_OPERATORS and cond.get("compareMode") == "node":
            return cond.get("baselineNodeId") or ""
    return ""


def _validate_tool_node(node: dict, nid: str, label: str) -> tuple:
    """Per-source tool node checks. Returns ``(errors, warnings)``.

    ``_resolve_tool_source`` deliberately does not validate the source, so this
    is the only place that catches a typo before the run; an unknown source must
    still be an error here even though the handler also fails on it.
    """
    errors: List[dict] = []
    warnings: List[dict] = []
    config = node.get("config") or {}
    source = _resolve_tool_source(config)

    if source not in _TOOL_SOURCES:
        errors.append(_issue(
            "tool_source_unknown",
            f"工具节点「{label}」的来源「{source}」不在 platform/mcp/http 之内",
            nid, label,
        ))
        return errors, warnings

    if source == "platform" and not str(config.get("toolName") or "").strip():
        errors.append(_issue(
            "tool_name_required", f"工具节点「{label}」未选择宿主工具", nid, label))

    if source == "mcp" and not (
        str(config.get("capabilityId") or "").strip()
        and str(config.get("clientKey") or "").strip()
    ):
        errors.append(_issue(
            "mcp_capability_required",
            f"工具节点「{label}」未选择 MCP client 或能力（capabilityId 与 clientKey 都必填）",
            nid, label,
        ))

    if source == "http":
        url = str(config.get("url") or "").strip()
        if not url:
            errors.append(_issue(
                "http_url_required", f"工具节点「{label}」未填写 URL", nid, label))
        elif url.split(":", 1)[0].lower() not in ("http", "https"):
            errors.append(_issue(
                "http_url_scheme_invalid",
                f"工具节点「{label}」的 URL 必须以 http:// 或 https:// 开头",
                nid, label,
            ))
        method = str(config.get("method") or "GET").strip().upper()
        if method not in _HTTP_METHODS:
            errors.append(_issue(
                "http_method_unsupported",
                f"工具节点「{label}」的 HTTP 方法「{method}」不支持", nid, label,
            ))
        env_name = str(config.get("authEnvVar") or "").strip()
        if env_name:
            try:
                _checked_secret_env_name(env_name)
            except ValueError as exc:
                errors.append(_issue(
                    "tool_auth_env_var_namespace", str(exc), nid, label))
            else:
                # 值只有运行时才知道，所以这是提醒而不是错误。
                warnings.append(_issue(
                    "tool_auth_env_var_missing",
                    f"工具节点「{label}」从环境变量「{env_name}」取凭证，"
                    "运行时必须已设置该变量（凭证值不会写入工作流）",
                    nid, label,
                ))
        secret_ref = str(config.get("authSecretRef") or "").strip()
        if secret_ref:
            try:
                _checked_secret_ref(secret_ref)
            except ValueError as exc:
                errors.append(_issue(
                    "tool_auth_secret_ref_invalid", str(exc), nid, label))
            field = str(config.get("authSecretField") or "").strip()
            if field:
                try:
                    _checked_secret_field(field)
                except ValueError as exc:
                    errors.append(_issue(
                        "tool_auth_secret_field_invalid", str(exc), nid, label))
            if env_name:
                warnings.append(_issue(
                    "tool_auth_source_priority",
                    f"工具节点「{label}」同时配置了密钥引用与环境变量凭证；"
                    f"运行时以密钥引用「{secret_ref}」为准，环境变量不会生效",
                    nid, label,
                ))
        elif str(config.get("authSecretField") or "").strip():
            errors.append(_issue(
                "tool_auth_secret_field_without_ref",
                f"工具节点「{label}」配置了密钥字段名但未配置密钥引用（authSecretRef）",
                nid, label,
            ))
    return errors, warnings


def _validate_retry_config(config: dict, label: str, nid: str) -> List[dict]:
    """Authoritative static check for the opt-in retry/timeout keys.

    Runtime parse_retry_policy is the fail-safe backstop; this gate is what
    blocks publish/deploy on a graph the engine would silently default.
    """
    issues: List[dict] = []

    def _is_num(v):
        return isinstance(v, (int, float)) and not isinstance(v, bool)

    if "maxRetries" in config:
        v = config["maxRetries"]
        if not isinstance(v, int) or isinstance(v, bool) or v < 0 or v > 10:
            issues.append(_issue(
                "retry_config_invalid",
                f"「{label}」的 maxRetries 必须是 0–10 的整数", nid, label,
            ))

    base = config.get("retryBaseDelaySec")
    if base is not None and (not _is_num(base) or base <= 0):
        issues.append(_issue(
            "retry_config_invalid",
            f"「{label}」的 retryBaseDelaySec 必须是大于 0 的数值", nid, label,
        ))

    maximum = config.get("retryMaxDelaySec")
    if maximum is not None and (not _is_num(maximum) or maximum <= 0):
        issues.append(_issue(
            "retry_config_invalid",
            f"「{label}」的 retryMaxDelaySec 必须是大于 0 的数值", nid, label,
        ))

    if _is_num(base) and _is_num(maximum) and maximum < base:
        issues.append(_issue(
            "retry_config_invalid",
            f"「{label}」的 retryMaxDelaySec 不能小于 retryBaseDelaySec", nid, label,
        ))

    timeout = config.get("nodeTimeoutSec")
    if timeout is not None and (not _is_num(timeout) or timeout <= 0 or timeout > 3600):
        issues.append(_issue(
            "retry_config_invalid",
            f"「{label}」的 nodeTimeoutSec 必须是大于 0 且不超过 3600 的数值", nid, label,
        ))

    return issues


def validate_workflow(workflow: dict) -> dict:
    """Check a workflow for the mistakes the engine can only report at run time.

    Everything here is static: the graph shape, the configured references and
    the failure policies. It is deliberately conservative about ordering —
    only structurally impossible configurations are errors.
    """
    errors: List[dict] = []
    warnings: List[dict] = []

    nodes = workflow.get("nodes") or []
    edges = workflow.get("edges") or []

    node_ids = [str(n.get("id") or "") for n in nodes]
    id_set = {nid for nid in node_ids if nid}
    label_of = {str(n.get("id") or ""): str(n.get("label") or n.get("id") or "") for n in nodes}

    adjacency: Dict[str, List[str]] = {}
    reverse: Dict[str, List[str]] = {}
    for edge in edges:
        src, tgt = str(edge.get("source") or ""), str(edge.get("target") or "")
        if src not in id_set or tgt not in id_set:
            errors.append(_issue(
                "dangling_edge",
                f"连线 {src or '?'} → {tgt or '?'} 引用了不存在的节点",
                src if src in id_set else "",
                label_of.get(src, ""),
            ))
            continue
        adjacency.setdefault(src, []).append(tgt)
        reverse.setdefault(tgt, []).append(src)

    if not nodes:
        errors.append(_issue("empty_workflow", "工作流没有任何节点"))

    # ── Start / end shape ───────────────────────────────────────────
    start_ids = [str(n.get("id") or "") for n in nodes if n.get("type") == "start"]
    if not start_ids:
        errors.append(_issue("no_start", "缺少「开始」节点，工作流无法启动"))
    elif len(start_ids) > 1:
        errors.append(_issue(
            "multiple_start",
            f"存在 {len(start_ids)} 个「开始」节点，只会执行第一个（{start_ids[0]}）",
            start_ids[1],
            label_of.get(start_ids[1], ""),
        ))
    if not any(n.get("type") == "end" for n in nodes):
        warnings.append(_issue("no_end", "没有「结束」节点，最终结果由最后执行的节点输出拼装"))

    reachable = _reachable_from_starts(start_ids, adjacency) if start_ids else set()

    known_types = set(registered_types())
    for node in nodes:
        nid = str(node.get("id") or "")
        label = str(node.get("label") or nid)
        ntype = str(node.get("type") or "")
        config = node.get("config") or {}

        if ntype not in known_types:
            errors.append(_issue("unknown_type", f"节点类型「{ntype or '未填写'}」未注册", nid, label))
            continue

        if nid not in reachable and ntype != "start" and start_ids:
            errors.append(_issue(
                "unreachable_node",
                f"「{label}」从开始节点不可达，永远不会执行",
                nid,
                label,
            ))
        elif not reverse.get(nid) and ntype != "start":
            errors.append(_issue("orphan_node", f"「{label}」没有入边，永远不会执行", nid, label))

        if not adjacency.get(nid) and ntype not in ("end",):
            warnings.append(_issue("dead_end", f"「{label}」没有出边，流程在此中断", nid, label))

        if ntype == "agent" and not str(config.get("agentId") or "").strip():
            errors.append(_issue("missing_agent_id", f"Agent 节点「{label}」未选择 Agent", nid, label))

        if ntype in ("agent", "tool"):
            _fields, declaration_errors = parse_output_schema(config.get("outputSchema"))
            for message in declaration_errors:
                errors.append(_issue(
                    "output_schema_invalid",
                    f"「{label}」的输出声明非法：{message}",
                    nid,
                    label,
                ))
        if ntype in ("agent", "tool", "router"):
            errors.extend(_validate_retry_config(config, label, nid))
        elif any(k in config for k in (
            "maxRetries", "retryBaseDelaySec", "retryMaxDelaySec", "nodeTimeoutSec"
        )):
            errors.append(_issue(
                "retry_config_invalid",
                f"「{label}」不是 agent/tool/router 节点，不能配置重试/超时", nid, label,
            ))

        if ntype == "tool":
            tool_errors, tool_warnings = _validate_tool_node(node, nid, label)
            errors.extend(tool_errors)
            warnings.extend(tool_warnings)

        if ntype == "router":
            branches = config.get("branches") or []
            if not branches:
                errors.append(_issue("router_no_branches", f"路由节点「{label}」没有分支", nid, label))
            for branch in branches:
                if branch.get("branchType") != "other" and not (branch.get("conditions") or []):
                    warnings.append(_issue(
                        "router_empty_branch",
                        f"路由分支「{branch.get('name') or branch.get('id', '')}」没有条件，"
                        "会直接命中并挡住后续分支",
                        nid,
                        label,
                    ))
                for cond in branch.get("conditions") or []:
                    if cond.get("operator") not in _DELTA_OPERATORS:
                        continue
                    mode = cond.get("compareMode") or "custom"
                    if mode in ("previous", "initial"):
                        errors.append(_issue(
                            "delta_legacy_baseline",
                            f"「{label}」的变化量条件仍使用旧的『{mode}』基线模式，运行时会直接失败",
                            nid,
                            label,
                        ))
                    elif mode == "node":
                        if not str(cond.get("baselineNodeId") or "").strip():
                            errors.append(_issue(
                                "delta_no_baseline",
                                f"「{label}」的变化量条件选择了『引用基准节点』但未选择节点",
                                nid,
                                label,
                            ))
                    elif str(cond.get("baselineValue") or "").strip() == "":
                        errors.append(_issue(
                            "delta_no_baseline",
                            f"「{label}」的变化量条件缺少固定基准值，运行时会按失败处理而不是按 0 比较",
                            nid,
                            label,
                        ))

        policy = str(config.get("onError") or "")
        if policy == "branch":
            has_error_edge = any(
                str(e.get("sourceHandle") or "") == ERROR_HANDLE for e in edges
                if str(e.get("source") or "") == nid
            )
            if not has_error_edge:
                issue = _issue(
                    "error_branch_missing",
                    f"「{label}」设置了 onError=branch 但没有『错误』出边，失败时仍会中止",
                    nid,
                    label,
                )
                # Only agent/tool nodes expose the error port in the designer, so
                # a policy set on any other type is a leftover rather than a fixable
                # graph error.
                bucket = errors if ntype in _ON_ERROR_NODE_TYPES else warnings
                bucket.append(issue)

    declared_fields: Dict[str, Dict[str, str]] = {}
    for node in nodes:
        fields, declaration_errors = parse_output_schema(
            (node.get("config") or {}).get("outputSchema")
        )
        if declaration_errors:
            continue  # already reported as output_schema_invalid
        if fields:
            declared_fields[str(node.get("id") or "")] = {
                f.name: f.type for f in fields
            }

    # ── Variable references ─────────────────────────────────────────
    start_id_set = set(start_ids)
    # ``_lookup_node_output`` accepts "input" as an alias of the Start node's
    # "user_input", so a static check that rejected it would be wrong.
    start_fields = _START_OUTPUT_FIELDS | {"input"}
    for node in nodes:
        nid = str(node.get("id") or "")
        label = str(node.get("label") or nid)
        ancestors = _ancestors_of(nid, reverse)
        for ref, where in _iter_variable_refs(node):
            head, _, field = ref.partition(".")
            head = head.strip()
            if not head:
                continue
            if head not in id_set:
                if not field and head in _START_OUTPUT_FIELDS:
                    continue  # a bare Start/context key: user_input, SYS_USER_ID…
                errors.append(_issue(
                    "unknown_ref",
                    f"{where}引用了不存在的节点或变量：{ref}",
                    nid,
                    label,
                ))
                continue
            if head == nid:
                errors.append(_issue(
                    "self_ref",
                    f"{where}引用了本节点自身的输出：{ref}",
                    nid,
                    label,
                ))
                continue
            if field and head in declared_fields:
                declared = declared_fields[head]
                root = field.split(".")[0]
                if root not in declared:
                    names = "、".join(sorted(declared))
                    errors.append(_issue(
                        "unknown_output_field",
                        f"{where}引用了「{label_of.get(head, head)}」未声明的字段：{ref}；"
                        f"该节点已声明：{names}",
                        nid,
                        label,
                    ))
                    continue
            if head in start_id_set and field and field not in start_fields:
                errors.append(_issue(
                    "unknown_start_field",
                    f"{where}引用了开始节点不存在的字段：{ref}",
                    nid,
                    label,
                ))
            elif head not in ancestors:
                warnings.append(_issue(
                    "ref_not_upstream",
                    f"{where}引用的节点不在「{label}」的上游路径上，运行时可能取不到值：{ref}",
                    nid,
                    label,
                ))
        for ref, operator in _iter_condition_operators(node):
            head, _, field = ref.partition(".")
            declared = declared_fields.get(head.strip())
            if not declared or not field:
                continue
            ftype = declared.get(field.strip().split(".")[0])
            if ftype is None:
                continue
            mismatch = (
                ftype in ("number", "integer", "boolean") and operator in _STRING_OPERATORS
            ) or (
                ftype == "string" and operator in _NUMERIC_OPERATORS
            )
            if mismatch:
                warnings.append(_issue(
                    "ref_type_mismatch",
                    f"「{label}」对声明为 {ftype} 的 {ref} 使用了「{operator}」运算符，"
                    "运行时会按字符串或强制转换处理，结果可能不符合预期",
                    nid,
                    label,
                ))

    if _has_cycle(adjacency):
        warnings.append(_issue(
            "cycle",
            "图中存在环路：引擎每个节点单次执行只运行一次，回边不会被再次触发",
        ))

    return {"valid": not errors, "errors": errors, "warnings": warnings}


def _raise_if_invalid(workflow: dict, action: str) -> None:
    """Refuse to freeze a graph the engine cannot run correctly."""
    result = validate_workflow(workflow)
    if result["valid"]:
        return
    lines = [f"- {item['message']}" for item in result["errors"][:10]]
    if len(result["errors"]) > 10:
        lines.append(f"- …另有 {len(result['errors']) - 10} 个问题")
    raise HTTPException(
        status_code=422,
        detail={
            "error_type": "workflow_invalid",
            "message": f"工作流存在 {len(result['errors'])} 个错误，无法{action}",
            "errors": result["errors"],
            "warnings": result["warnings"],
            "summary": "\n".join(lines),
        },
    )
