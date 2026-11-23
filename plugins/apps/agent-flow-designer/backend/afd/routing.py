# -*- coding: utf-8 -*-
"""Condition, variable and router evaluation.

ReDoS-safe regex matching, condition/delta evaluation, variable resolution
against node outputs, and the router family (rule-based, LLM-assisted and
detailed async dispatch).
"""

import json
import re
from typing import Any, Dict, Optional

from engine import get_logger

from .llm_client import _call_agent_chat, _call_model_directly

logger = get_logger(__name__)


# A router's ``regex`` target is written by whoever drew the workflow, but the
# text it runs against is a runtime value — an LLM answer, a user message. One
# mistyped nested quantifier therefore stalls the whole server, and ``re`` has
# no timeout to fall back on, so the shape has to be judged before matching.
_REGEX_MAX_PATTERN_CHARS = 512
_REGEX_MAX_SUBJECT_CHARS = 20_000


def _regex_skip_class(text: str, i: int) -> int:
    """Return the index just past the ``[...]`` class opening at ``i``."""
    j = i + 1
    if j < len(text) and text[j] == "^":
        j += 1
    while j < len(text) and text[j] != "]":
        if text[j] == "\\":
            j += 1
        j += 1
    return j + 1


def _regex_matching_paren(text: str, start: int) -> int:
    """Index of the ``)`` closing the ``(`` at ``start``, or -1 when unbalanced."""
    depth = 0
    i = start
    while i < len(text):
        c = text[i]
        if c == "\\":
            i += 2
            continue
        if c == "[":
            i = _regex_skip_class(text, i)
            continue
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def _regex_quantifier_at(text: str, i: int) -> tuple[str, int]:
    """Classify the quantifier starting at ``i`` and return where it ends.

    ``unbounded`` can swallow an arbitrary run (``a+``, ``a{2,}``), ``variable``
    a bounded but non-single length (``a{1,3}``), ``fixed`` one of several
    identical copies (``a{3}``) and ``none`` is not a repetition at all — the
    distinction between the last three and the first two is exactly the
    difference between a pattern that can unroll exponentially and one that
    cannot.
    """
    if i >= len(text):
        return "none", i
    c = text[i]
    if c in "+*":
        return "unbounded", i + 1
    if c != "{":
        return "none", i
    end = text.find("}", i)
    if end < 0:
        return "none", i + 1
    low, comma, high = text[i + 1:end].partition(",")
    if comma and not high.strip():
        return "unbounded", end + 1
    try:
        minimum = int(low) if low.strip() else 0
        maximum = int(high) if high.strip() else minimum
    except ValueError:
        return "unbounded", end + 1
    if maximum <= 1:
        return "none", end + 1
    if maximum > minimum:
        return "variable", end + 1
    return "fixed", end + 1


def _regex_body_quantifier(text: str) -> str:
    """The loosest length a group body can match: ``unbounded`` > ``variable`` > the rest."""
    worst = "none"
    i = 0
    while i < len(text):
        c = text[i]
        if c == "\\":
            i += 2
            continue
        if c == "[":
            i = _regex_skip_class(text, i)
            continue
        if c in "+*":
            return "unbounded"
        if c == "{":
            kind, i = _regex_quantifier_at(text, i)
            if kind == "unbounded":
                return "unbounded"
            if kind == "variable" or worst == "none":
                worst = kind
            continue
        i += 1
    return worst


def _regex_branches_overlap(body: str) -> bool:
    """Whether two alternatives of this group can match a common prefix.

    ``(a|aa)+`` is the second catastrophic shape after ``(a+)+``: the engine
    cannot tell which branch consumed a run of ``a`` and retries both. Branches
    starting with different characters, like ``(是|否)+``, have no such ambiguity
    and must stay allowed.
    """
    parts: list[str] = []
    buf: list[str] = []
    depth = 0
    i = 0
    while i < len(body):
        c = body[i]
        if c == "\\":
            buf.append(body[i:i + 2])
            i += 2
            continue
        if c == "[":
            chunk = body[i:_regex_skip_class(body, i)]
            buf.append(chunk)
            i += len(chunk)
            continue
        if c in "({[":
            depth += 1
        elif c in ")}]":
            depth -= 1
        if c == "|" and depth == 0:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(c)
        i += 1
    parts.append("".join(buf))
    for a_idx in range(len(parts)):
        for b_idx in range(a_idx + 1, len(parts)):
            a, b = parts[a_idx], parts[b_idx]
            if a and b and (a.startswith(b) or b.startswith(a)):
                return True
    return False


def _regex_backtrack_risk(pattern: str) -> Optional[str]:
    """Name the catastrophic-backtracking shape in ``pattern``, or ``None``.

    A deliberately crude static check, because Python's ``re`` has no timeout:
    a group that repeats is refused when its own body is unbounded (``(a+)+``),
    or when the group repeats without a cap over a body whose length is
    ambiguous (``(a{1,3})*``, ``(a|aa)+``). Bounded patterns such as
    ``(\\d{1,3}\\.){3}`` stay allowed — refusing them would tax every workflow
    that matches an IP or a version number to protect against nothing.
    """
    i = 0
    while i < len(pattern):
        c = pattern[i]
        if c == "\\":
            i += 2
            continue
        if c == "[":
            i = _regex_skip_class(pattern, i)
            continue
        if c != "(":
            i += 1
            continue
        close = _regex_matching_paren(pattern, i)
        if close < 0:
            return None  # unbalanced: re.error reports it better than we do
        body = pattern[i + 1:close]
        outer, _ = _regex_quantifier_at(pattern, close + 1)
        if outer != "none":
            inner = _regex_body_quantifier(body)
            if inner == "unbounded":
                return "嵌套量词"
            if outer == "unbounded":
                if inner == "variable":
                    return "分支长度不定"
                if _regex_branches_overlap(body):
                    return "分支可重叠"
        i = close + 1
    return None


def _evaluate_regex(var_str: str, target_value: str, detail: str) -> tuple[bool, str]:
    """Run a designer-authored regex against runtime text, or refuse to."""
    if len(target_value) > _REGEX_MAX_PATTERN_CHARS:
        return False, f"正则表达式过长（>{_REGEX_MAX_PATTERN_CHARS} 字符），已拒绝执行"
    if len(var_str) > _REGEX_MAX_SUBJECT_CHARS:
        return False, (
            f"待匹配内容过长（>{_REGEX_MAX_SUBJECT_CHARS} 字符），未执行正则匹配"
        )
    risk = _regex_backtrack_risk(target_value)
    if risk:
        return False, (
            f"正则表达式存在灾难性回溯风险（{risk}），已拒绝执行: {target_value[:80]}"
        )
    try:
        return bool(re.search(target_value, var_str)), detail
    except re.error:
        return False, f"正则表达式错误: {target_value}"


def _evaluate_condition(
    variable_value: Any,
    operator: str,
    target_value: str,
    node_outputs: Optional[Dict[str, Any]] = None,
    node_outputs_history: Optional[Dict[str, Any]] = None,
    condition: Optional[dict] = None,
    defined: bool = True,
) -> tuple[bool, str]:
    """Evaluate a single condition against a variable value.
    
    Returns (matched, detail) where detail is a human-readable evaluation summary.
    ``defined`` tells an *undefined* reference apart from a variable whose value
    happens to be empty, so the trace can name the real cause.
    """
    if variable_value is None:
        if not defined:
            ref = str((condition or {}).get("variable", ""))
            return False, (
                f"变量 '{ref}' 未定义：引用的上游节点可能未执行、不在可达路径上，"
                f"或字段名不存在"
            )
        return False, "变量值为空"
    
    var_str = str(variable_value)
    detail = f"{var_str} {operator} {target_value}"
    
    # ── Delta / Diff operators ──────────────────────────────────────
    if operator in ("delta_gt", "delta_lt", "delta_ge", "delta_le",
                      "change_rate_gt", "change_rate_lt",
                      "text_diff_ratio_gt", "text_diff_contains"):
        matched, delta_detail = _evaluate_delta_condition(
            variable_value, operator, target_value,
            node_outputs, node_outputs_history, condition
        )
        return matched, delta_detail
    
    try:
        if operator == "eq":
            return var_str == target_value, detail
        elif operator == "ne":
            return var_str != target_value, detail
        elif operator == "gt":
            return float(var_str) > float(target_value), detail
        elif operator == "lt":
            return float(var_str) < float(target_value), detail
        elif operator == "ge":
            return float(var_str) >= float(target_value), detail
        elif operator == "le":
            return float(var_str) <= float(target_value), detail
        elif operator == "contains":
            return target_value in var_str, detail
        elif operator == "starts_with":
            return var_str.startswith(target_value), detail
        elif operator == "ends_with":
            return var_str.endswith(target_value), detail
        elif operator == "regex":
            return _evaluate_regex(var_str, target_value, detail)
    except re.error:
        return False, f"正则表达式错误: {target_value}"
    except (ValueError, TypeError) as exc:
        return False, f"条件评估异常 ({operator}): {str(exc)}"
    
    return False, f"未知运算符: {operator}"


def _resolve_delta_baseline(
    condition: dict,
    node_outputs: Optional[Dict[str, Any]],
) -> tuple[Any, str]:
    """Resolve the baseline a delta/diff operator compares against.

    Returns ``(baseline, error)``. A missing baseline is reported instead of
    defaulting to ``0``: that default silently turned "变化量 > 10" into
    "绝对值 > 10", which is the defect this helper exists to prevent.
    """
    mode = condition.get("compareMode") or "custom"
    baseline_node_id = str(condition.get("baselineNodeId") or "").strip()
    baseline_value = condition.get("baselineValue")

    if mode in ("previous", "initial"):
        return None, (
            f"基线模式 '{mode}' 要求同一节点在一次执行内产出多次历史输出，"
            "而引擎每个节点单次执行只运行一次；请改用『固定基准值』或『引用基准节点』"
        )

    if baseline_node_id:
        ref = baseline_node_id if "." in baseline_node_id else f"{baseline_node_id}.output"
        value, found = _resolve_variable_ex(ref, {}, node_outputs)
        if not found:
            return None, f"基准节点 '{baseline_node_id}' 没有可解析的输出字段（{ref}）"
        return value, ""

    if baseline_value is None or str(baseline_value) == "":
        return None, "未配置基线值：请填写固定基准值，或引用一个基准节点作为基线"
    return baseline_value, ""


def _evaluate_delta_condition(
    variable_value: Any,
    operator: str,
    target_value: str,
    node_outputs: Optional[Dict[str, Any]] = None,
    node_outputs_history: Optional[Dict[str, Any]] = None,
    condition: Optional[dict] = None,
) -> tuple[bool, str]:
    """Evaluate delta/diff conditions by comparing current value with baseline.

    Supports numeric delta, change rate, and text diff operations. The baseline
    comes from a fixed value or another node's output — see
    :func:`_resolve_delta_baseline` for why in-run history is not a usable
    baseline. ``node_outputs_history`` is accepted because every node records
    one entry per execution there; a cross-invocation baseline (Phase B) will
    read it from persisted run history.
    """
    condition = condition or {}

    # Resolve current value (numeric or text)
    current_str = str(variable_value)
    try:
        current_num = float(current_str)
    except (ValueError, TypeError):
        current_num = None

    baseline_value, baseline_error = _resolve_delta_baseline(condition, node_outputs)
    if baseline_error:
        return False, f"变化量条件无法评估：{baseline_error}"

    baseline_str = str(baseline_value)
    
    # ── Numeric delta / change rate ──────────────────────────────────
    baseline_num: Optional[float] = None
    if operator in ("delta_gt", "delta_lt", "delta_ge", "delta_le",
                    "change_rate_gt", "change_rate_lt"):
        try:
            baseline_num = float(baseline_str)
        except (ValueError, TypeError):
            return False, f"基准值 '{baseline_str}' 不是有效数值，无法计算变化量"
    
    if operator in ("delta_gt", "delta_lt", "delta_ge", "delta_le"):
        if current_num is None:
            return False, f"当前值 '{current_str}' 不是有效数值，无法计算变化量"
        
        delta = current_num - baseline_num
        threshold = float(target_value)
        
        matched = False
        if operator == "delta_gt":
            matched = delta > threshold
        elif operator == "delta_lt":
            matched = delta < threshold
        elif operator == "delta_ge":
            matched = delta >= threshold
        elif operator == "delta_le":
            matched = delta <= threshold
        
        detail = f"变化量: {delta:.4f} (当前 {current_num} - 基准 {baseline_num}) {'>' if 'gt' in operator else '<'}= {threshold}"
        return matched, detail
    
    # ── Change rate ─────────────────────────────────────────────────
    if operator in ("change_rate_gt", "change_rate_lt"):
        if current_num is None:
            return False, f"当前值 '{current_str}' 不是有效数值，无法计算变化率"
        
        if abs(baseline_num) < 1e-9:
            return False, f"基准值为零，无法计算变化率 (当前={current_num}, 基准={baseline_num})"
        
        rate = (current_num - baseline_num) / abs(baseline_num)
        threshold = float(target_value)
        
        matched = False
        if operator == "change_rate_gt":
            matched = rate > threshold
        elif operator == "change_rate_lt":
            matched = rate < threshold
        
        detail = f"变化率: {rate:.2%} (({current_num} - {baseline_num}) / {abs(baseline_num)}) {'>' if 'gt' in operator else '<'} {threshold}"
        return matched, detail
    
    # ── Text diff ───────────────────────────────────────────────────
    if operator in ("text_diff_ratio_gt", "text_diff_contains"):
        from difflib import SequenceMatcher
        
        current_text = current_str
        baseline_text = baseline_str
        
        if operator == "text_diff_ratio_gt":
            ratio = SequenceMatcher(None, current_text, baseline_text).ratio()
            threshold = float(target_value)
            matched = ratio > threshold
            detail = f"文本相似度: {ratio:.2%} (阈值: {threshold})"
            return matched, detail
        
        elif operator == "text_diff_contains":
            # Check if the text difference contains the target pattern
            # We compute diff lines and check for containment
            diff_lines = []
            import difflib
            diff = list(difflib.unified_diff(
                baseline_text.splitlines(),
                current_text.splitlines(),
                lineterm=""
            ))
            diff_text = "\n".join(diff)
            matched = target_value in diff_text
            detail = f"文本差异中是否包含 '{target_value}': {matched}"
            return matched, detail
    
    return False, "未知的变化量操作符"


def _lookup_node_output(
    parts: list[str], node_outputs: Optional[Dict[str, Any]]
) -> tuple[Any, bool]:
    """Resolve ``nodeId.field`` against accumulated node outputs.

    Returns ``(value, found)``. ``found`` is what lets callers tell an
    *undefined* reference apart from a variable that legitimately holds an
    empty value — the distinction the trace used to blur into "变量值为空".
    """
    if not node_outputs or len(parts) < 2:
        return None, False
    node_output = node_outputs.get(parts[0])
    if node_output is None:
        return None, False
    field_key = ".".join(parts[1:])
    if isinstance(node_output, dict):
        if field_key in node_output:
            return node_output[field_key], True
        aliases = {"input": "user_input"}
        alias = aliases.get(field_key)
        if alias is not None and alias in node_output:
            return node_output[alias], True
        return None, False
    if field_key in ("output", "result", "text", "response"):
        return node_output, True
    return None, False


def _resolve_variable_ex(
    variable_name: str,
    context: dict,
    node_outputs: Optional[Dict[str, Any]] = None,
) -> tuple[Any, bool]:
    """Resolve a dotted variable reference. Returns ``(value, found)``.

    Supports:
    - Direct key lookup: ``user_input``
    - Nested dict lookup: ``user.name`` / ``start-1.input``
    - Node output lookup: ``node_id.field``
    """
    if not variable_name:
        return None, False

    if variable_name in context:
        return context[variable_name], True

    parts = variable_name.split(".")
    value: Any = context
    for part in parts:
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            return _lookup_node_output(parts, node_outputs)
    return value, True


def _resolve_variable(variable_name: str, context: dict, node_outputs: Optional[Dict[str, Any]] = None) -> Any:
    """Resolve a variable from context using dot notation (``None`` when undefined)."""
    value, _found = _resolve_variable_ex(variable_name, context, node_outputs)
    return value


def _eval_router_condition(
    cond: dict,
    context: dict,
    node_outputs: Optional[Dict[str, Any]],
    node_outputs_history: Optional[Dict[str, Any]],
) -> tuple[bool, dict]:
    """Resolve and evaluate one router condition, returning a trace record."""
    variable_name = cond.get("variable", "")
    operator = cond.get("operator", "eq")
    target_value = cond.get("value", "")

    variable_value, defined = _resolve_variable_ex(variable_name, context, node_outputs)
    if isinstance(variable_value,list):
        for variable_value_item in variable_value:
            cond_matched, detail = _evaluate_condition(
                variable_value_item, operator, target_value,
                node_outputs=node_outputs,
                node_outputs_history=node_outputs_history,
                condition=cond,
                defined=defined,
            )
            if cond_matched:
                break
    else:
        cond_matched, detail = _evaluate_condition(
            variable_value, operator, target_value,
            node_outputs=node_outputs,
            node_outputs_history=node_outputs_history,
            condition=cond,
            defined=defined,
        )
    return cond_matched, {
        "variable": variable_name,
        "operator": operator,
        "value": target_value,
        "actualValue": str(variable_value) if variable_value is not None else "",
        "defined": defined,
        "matched": cond_matched,
        "detail": detail,
    }


async def _evaluate_router(
    node: dict,
    context: dict,
    node_outputs: Optional[Dict[str, Any]] = None,
    node_outputs_history: Optional[Dict[str, Any]] = None,
) -> tuple[str, str, bool]:
    """Evaluate router node and return (branch_id, branch_name, matched).
    
    Args:
        node: Router node configuration
        context: Execution context with variables
        node_outputs: Current outputs from all executed nodes
        node_outputs_history: Historical snapshots of node outputs for delta calculations
    """
    result = await _evaluate_router_detailed_async(node, context, node_outputs, node_outputs_history)
    return result["branchId"], result["branchName"], result["matched"]


async def _evaluate_router_llm(
    node: dict,
    context: dict,
    node_outputs: Optional[Dict[str, Any]] = None,
    usage_out: Optional[dict] = None,
) -> dict:
    """Evaluate router node using LLM-based intent recognition.
    
    Builds a prompt with branch descriptions and asks the LLM to classify
    the intent. Returns the selected branch with reasoning. ``usage_out``
    receives the classification call's token counts.
    """
    node_id = node.get("id", "unknown")
    node_config = node.get("config") or {}
    branches = node_config.get("branches", [])
    model = node_config.get("model", "")
    extra_prompt = node_config.get("extraPrompt", "")
    system_prompt = node_config.get("systemPrompt", "")
    logger.info("[Router LLM] node_id=%s, model=%s, branches=%d", node_id, model, len(branches))
    
    # Support merged AI instruction format: extract system prompt from extraPrompt
    # if it contains a [系统级角色定义] marker
    ai_instruction = extra_prompt or ""
    if "[系统级角色定义]" in ai_instruction:
        parts = ai_instruction.split("[系统级角色定义]", 1)
        if len(parts) == 2:
            # The part after the marker until the next section or end
            marker_content = parts[1].strip()
            # Find the next bracket marker or use the rest
            next_marker_idx = len(marker_content)
            for marker in ["[路由决策规则]", "[补充指令]", "["]:
                idx = marker_content.find(marker)
                if idx > 0 and idx < next_marker_idx:
                    next_marker_idx = idx
            extracted_system = marker_content[:next_marker_idx].strip()
            if extracted_system:
                system_prompt = extracted_system
            # Remove the system prompt section from extra_prompt
            extra_prompt = marker_content[next_marker_idx:].strip() if next_marker_idx < len(marker_content) else ""
            # Also remove any leading marker indicators from extra_prompt
            if extra_prompt.startswith("["):
                section_end = extra_prompt.find("]")
                if section_end > 0:
                    extra_prompt = extra_prompt[section_end + 1:].strip()
    
    # Build branch descriptions for the LLM
    branch_descriptions = []
    normal_branches = []
    other_branch = None
    
    for branch in branches:
        if branch.get("branchType") == "other":
            other_branch = branch
            continue
        normal_branches.append(branch)
        desc = branch.get("description", "").strip() or branch.get("name", "")
        if desc:
            branch_descriptions.append(f"- {branch.get('id')}: {desc}")
    
    if other_branch:
        branch_descriptions.append(f"- {other_branch.get('id')}: 其他意图（兜底分支）")
    
    # Resolve input variables from context
    inputs_config = node_config.get("inputs", [])
    input_values = []
    for var_name in inputs_config:
        val = _resolve_variable(var_name, context, node_outputs)
        if val is not None:
            input_values.append(f"{var_name}: {val}")
    
    # Build the classification prompt
    input_section = input_values if input_values else ["（无额外输入）"]
    prompt_parts = [
        "请根据以下输入信息，判断应该路由到哪个分支。",
        "",
        "## 可选分支：",
        *branch_descriptions,
        "",
        "## 输入信息：",
        *input_section,
    ]
    
    if extra_prompt:
        prompt_parts.extend(["", "## 补充指令：", extra_prompt])
    
    prompt_parts.extend([
        "",
        "请返回 JSON 格式：{ \"classificationId\": \"<分支ID>\", \"reason\": \"<理由>\" }",
        "如果无法确定，请返回兜底分支的 ID。",
    ])
    
    classification_prompt = "\n".join(prompt_parts)
    # The prompt body is user content. The run's trace — owner-filtered, and the
    # only place the raw response is still kept — belongs to the caller; the
    # process log is one file shared by every user of the host, so only the
    # prompt's size is worth keeping here.
    logger.info(
        "[Router LLM] node_id=%s prompt built: prompt_chars=%d branches=%d",
        node_id, len(classification_prompt), len(branch_descriptions),
    )
    
    # Call LLM via agent chat API
    messages = [{"role": "user", "content": classification_prompt}]
    if system_prompt:
        messages.insert(0, {"role": "system", "content": system_prompt})
    
    try:
        # Detect direct model call by checking for separator (colon or slash)
        # Format: providerId:modelId (console standard) or providerId/modelId (legacy)
        if model and (":" in model or "/" in model):
            # A direct provider call bypasses the chat channel, so no turn_usage
            # event comes back and the node is recorded at zero.
            llm_response = await _call_model_directly(
                model, messages, timeout=30.0, usage_out=usage_out
            )
        else:
            llm_response = await _call_agent_chat(
                model or "default", messages, timeout=30.0, usage_out=usage_out
            )
        logger.info(
            "[Router LLM] node_id=%s response received: response_chars=%d",
            node_id, len(llm_response) if isinstance(llm_response, str) else len(str(llm_response)),
        )
        
        # Try to extract classificationId from JSON response
        branch_id = None
        reason = ""
        
        # Parse JSON from response
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{[^}]*"classificationId"[^}]*\}', llm_response)
            if json_match:
                parsed = json.loads(json_match.group())
                branch_id = parsed.get("classificationId")
                reason = parsed.get("reason", "")
            else:
                # Try parsing the whole response
                try:
                    parsed = json.loads(llm_response)
                    branch_id = parsed.get("classificationId")
                    reason = parsed.get("reason", "")
                except (json.JSONDecodeError, ValueError):
                    pass
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Validate branch_id exists
        if branch_id:
            matched_branch_name = ""
            for branch in branches:
                if branch.get("id") == branch_id:
                    matched_branch_name = branch.get("name", "")
                    logger.info("[Router LLM] node_id=%s matched branch_id=%s branch_name=%s", node_id, branch_id, matched_branch_name)
                    return {
                        "branchId": branch_id,
                        "branchName": matched_branch_name,
                        "matched": True,
                        "routeType": "llm",
                        "reason": reason or "LLM 意图识别命中",
                        "llmResponse": llm_response[:500],
                        "conditions": [],
                        "logs": [
                            f"[LLM 路由] 模型: {model or 'default'}",
                            f"[LLM 路由] Prompt 长度: {len(classification_prompt)} 字符",
                            f"[LLM 路由] LLM 原始返回 (前 500 字符): {llm_response[:500]}",
                            f"[LLM 路由] 解析到 branch_id: {branch_id}",
                            f"[LLM 路由] 命中分支: {matched_branch_name}",
                        ],
                    }
            logger.warning("[Router LLM] node_id=%s returned invalid branch_id=%s", node_id, branch_id)
        else:
            logger.warning("[Router LLM] node_id=%s no branch_id extracted", node_id)
        
        # LLM returned invalid branch, fall through to default
        return {
            "branchId": "",
            "branchName": "",
            "matched": False,
            "routeType": "llm",
            "reason": f"LLM 返回无效分支 ID: {branch_id}",
            "llmResponse": llm_response[:500],
            "conditions": [],
            "logs": [
                f"[LLM 路由] 模型: {model or 'default'}",
                f"[LLM 路由] Prompt 长度: {len(classification_prompt)} 字符",
                f"[LLM 路由] LLM 原始返回 (前 500 字符): {llm_response[:500]}",
                f"[LLM 路由] 解析到 branch_id: {branch_id}",
                f"[LLM 路由] 失败原因: 返回无效分支 ID",
            ],
        }
    
    except Exception as exc:
        logger.exception("[Router LLM] node_id=%s call failed: %s", node_id, exc)
        return {
            "branchId": "",
            "branchName": "",
            "matched": False,
            "routeType": "llm",
            "reason": f"LLM 调用异常: {str(exc)}",
            "conditions": [],
            "logs": [
                f"[LLM 路由] 模型: {model or 'default'}",
                f"[LLM 路由] 调用异常: {str(exc)}",
            ],
        }


def _evaluate_router_detailed(
    node: dict,
    context: dict,
    node_outputs: Optional[Dict[str, Any]] = None,
    node_outputs_history: Optional[Dict[str, Any]] = None,
) -> dict:
    """Evaluate router node and return detailed trace information.
    
    Supports both rule-based and LLM-based routing modes.
    Returns a dict with:
        - branchId: selected branch id
        - branchName: selected branch name
        - matched: whether any branch matched
        - routeType: 'rule' | 'llm' | 'default' | 'fallback'
        - reason: human-readable reason for the selection
        - conditions: list of condition evaluations per branch
    """
    node_id = node.get("id", "unknown")
    node_config = node.get("config") or {}
    branches = node_config.get("branches", [])
    default_branch_id = node_config.get("defaultBranchId", "")
    route_mode = node_config.get("routeMode", "rule")
    conditions_detail = []
    logger.info("[Router Rule] node_id=%s, route_mode=%s, branches=%d, defaultBranchId=%s",
                node_id, route_mode, len(branches), default_branch_id)
    
    # ── LLM Routing Mode ────────────────────────────────────────────
    if route_mode == "llm":
        # LLM mode is async, caller must handle it
        # For synchronous path, fall through to rule-based
        pass
    
    # ── Rule-based Routing ──────────────────────────────────────────
    for branch in branches:
        branch_conditions = []
        conditions = branch.get("conditions", [])
        branch_type = branch.get("branchType", "normal")
        branch_id = branch.get("id", "")
        
        # "other" intent branches are handled as fallback, skip in normal evaluation
        if branch_type == "other":
            continue
        
        # Empty conditions = match by default (for branches with no rules)
        if not conditions:
            logger.info("[Router Rule] node_id=%s branch_id=%s branch_name=%s has no conditions, matched by default",
                        node_id, branch_id, branch.get("name", ""))
            conditions_detail.append({
                "branchId": branch_id,
                "branchName": branch.get("name", ""),
                "logic": "and",
                "matched": True,
                "conditions": [],
                "reason": "分支无条件，默认命中",
            })
            return {
                "branchId": branch_id,
                "branchName": branch.get("name", ""),
                "matched": True,
                "routeType": "rule",
                "reason": "分支无条件，默认命中",
                "conditions": conditions_detail,
                "logs": [
                    f"[规则路由] 分支 '{branch.get('name', '')}' 无条件，默认命中",
                ],
            }
        
        condition_logic = branch.get("conditionLogic", "and")
        matched = False
        
        if condition_logic == "or":
            # OR: any condition matches
            for cond in conditions:
                cond_matched, record = _eval_router_condition(
                    cond, context, node_outputs, node_outputs_history
                )
                branch_conditions.append(record)
                if cond_matched:
                    matched = True
                    break
        else:
            # AND: all conditions must match
            matched = True
            for cond in conditions:
                cond_matched, record = _eval_router_condition(
                    cond, context, node_outputs, node_outputs_history
                )
                branch_conditions.append(record)
                if not cond_matched:
                    matched = False

        undefined_refs = [
            r["variable"] for r in branch_conditions if not r.get("defined", True)
        ]
        
        conditions_detail.append({
            "branchId": branch_id,
            "branchName": branch.get("name", ""),
            "logic": condition_logic,
            "matched": matched,
            "conditions": branch_conditions,
            "undefinedRefs": undefined_refs,
        })
        
        if matched:
            logger.info("[Router Rule] node_id=%s branch_id=%s matched by rule, conditions=%d",
                        node_id, branch_id, len(branch_conditions))
            return {
                "branchId": branch_id,
                "branchName": branch.get("name", ""),
                "matched": True,
                "routeType": "rule",
                "reason": f"规则命中: {len(branch_conditions)} 个条件满足",
                "conditions": conditions_detail,
                "logs": [
                    f"[规则路由] 分支 '{branch.get('name', '')}' 规则命中，{len(branch_conditions)} 个条件满足",
                ],
            }
    
    # ── Fallback: default branch ──────────────────────────────────
    for branch in branches:
        if branch.get("id") == default_branch_id:
            logger.info("[Router Rule] node_id=%s fallback to default branch %s", node_id, default_branch_id)
            return {
                "branchId": default_branch_id,
                "branchName": branch.get("name", "默认分支"),
                "matched": True,
                "routeType": "default",
                "reason": "未命中任何规则分支，回退到默认分支",
                "conditions": conditions_detail,
                "logs": [
                    "[规则路由] 未命中任何规则分支，回退到默认分支",
                ],
            }
    
    # ── Fallback: "other" intent branch ───────────────────────────
    for branch in branches:
        if branch.get("branchType") == "other":
            logger.info("[Router Rule] node_id=%s fallback to 'other' branch", node_id)
            return {
                "branchId": branch.get("id", ""),
                "branchName": branch.get("name", "其他意图"),
                "matched": True,
                "routeType": "fallback",
                "reason": "未命中任何规则分支，回退到其他意图兜底分支",
                "conditions": conditions_detail,
                "logs": [
                    "[规则路由] 未命中任何规则分支，回退到其他意图兜底分支",
                ],
            }
    
    # ── Last resort: first branch ─────────────────────────────────
    if branches:
        first = branches[0]
        logger.info("[Router Rule] node_id=%s fallback to first branch %s", node_id, first.get("id", ""))
        return {
            "branchId": first.get("id", ""),
            "branchName": first.get("name", ""),
            "matched": True,
            "routeType": "fallback",
            "reason": "未命中任何分支且无默认/兜底分支，回退到第一个分支",
            "conditions": conditions_detail,
            "logs": [
                "[规则路由] 未命中任何分支且无默认/兜底分支，回退到第一个分支",
            ],
        }
    
    return {
        "branchId": "",
        "branchName": "",
        "matched": False,
        "routeType": "none",
        "reason": "无可用分支",
        "conditions": conditions_detail,
    }


async def _evaluate_router_detailed_async(
    node: dict,
    context: dict,
    node_outputs: Optional[Dict[str, Any]] = None,
    node_outputs_history: Optional[Dict[str, Any]] = None,
    usage_out: Optional[dict] = None,
) -> dict:
    """Async wrapper that supports LLM-based routing.

    ``usage_out`` collects tokens from whichever LLM call actually produced the
    answer — a hybrid router that matched on rules never reaches the model and
    stays at zero.
    """
    node_id = node.get("id", "unknown")
    node_config = node.get("config") or {}
    route_mode = node_config.get("routeMode", "rule")
    logger.info("[Router Async] node_id=%s, route_mode=%s", node_id, route_mode)
    
    if route_mode == "llm":
        # Try LLM routing first
        llm_result = await _evaluate_router_llm(node, context, node_outputs, usage_out=usage_out)
        logger.info("[Router Async] node_id=%s, llm_result matched=%s, routeType=%s, reason=%s",
                    node_id, llm_result.get("matched"), llm_result.get("routeType"), llm_result.get("reason", ""))
        if llm_result.get("matched"):
            return llm_result
        
        # LLM routing failed, fall through to rule-based
        logger.warning("[Router Async] node_id=%s LLM routing failed, falling back to rule-based", node_id)
        rule_result = _evaluate_router_detailed(node, context, node_outputs, node_outputs_history)
        rule_result["reason"] = f"LLM 路由失败，回退到规则路由: {rule_result.get('reason', '')}"
        # Merge logs: prepend LLM logs
        merged_logs = llm_result.get("logs", [])[:]
        merged_logs.append(f"[路由调度] LLM 路由失败，回退到规则路由: {rule_result.get('reason', '')}")
        merged_logs.extend(rule_result.get("logs", []))
        rule_result["logs"] = merged_logs
        logger.info("[Router Async] node_id=%s fallback rule_result: branchId=%s, routeType=%s, reason=%s",
                    node_id, rule_result.get("branchId"), rule_result.get("routeType"), rule_result.get("reason", ""))
        return rule_result
    elif route_mode == "hybrid":
        # Hybrid: try rule-based first, then fall back to LLM
        rule_result = _evaluate_router_detailed(node, context, node_outputs, node_outputs_history)
        logger.info("[Router Async] node_id=%s, rule_result matched=%s, routeType=%s, reason=%s",
                    node_id, rule_result.get("matched"), rule_result.get("routeType"), rule_result.get("reason", ""))
        if rule_result.get("matched") and rule_result.get("routeType") not in ("default", "fallback", "none"):
            return rule_result
        
        # Rule-based didn't match, try LLM
        logger.info("[Router Async] node_id=%s rule-based didn't match or hit fallback, trying LLM", node_id)
        llm_result = await _evaluate_router_llm(node, context, node_outputs, usage_out=usage_out)
        if llm_result.get("matched"):
            # Merge logs: prepend rule logs
            merged_logs = rule_result.get("logs", [])[:]
            merged_logs.append("[路由调度] 规则路由未命中，尝试 LLM 路由")
            merged_logs.extend(llm_result.get("logs", []))
            llm_result["logs"] = merged_logs
            return llm_result
        
        # Both failed, return the rule-based result (which includes fallback)
        logger.warning("[Router Async] node_id=%s both rule and LLM failed, returning rule fallback", node_id)
        merged_logs = rule_result.get("logs", [])[:]
        merged_logs.append("[路由调度] 规则路由未命中，LLM 路由也失败，返回规则 fallback")
        merged_logs.extend(llm_result.get("logs", []))
        rule_result["logs"] = merged_logs
        return rule_result
    else:
        # Pure rule-based
        return _evaluate_router_detailed(node, context, node_outputs, node_outputs_history)


#: Operators that compare a value against a baseline, so a missing baseline is
#: a configuration error rather than a comparison against zero.
_DELTA_OPERATORS = frozenset(
    {
        "delta_gt", "delta_lt", "delta_ge", "delta_le",
        "change_rate_gt", "change_rate_lt",
        "text_diff_ratio_gt", "text_diff_contains",
    }
)
