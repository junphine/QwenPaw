# -*- coding: utf-8 -*-
"""Agent Flow Designer — PawApp backend.

A simplified agent workflow designer for the Agent Platform.

Persistence: a shared JSON file stored in the platform data directory
(``<QZAGENT_HOME>/data/agent-flow-designer/workflows.json`` or
``~/.qzagent/data/agent-flow-designer/workflows.json``).
Legacy data in ``<plugin_dir>/data/workflows.json`` is automatically
migrated on first access.
"""

import asyncio
import ipaddress
import json
import os
import re
import sys
import tempfile
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from qwenpaw.pawapp import PawApp, PawAppContext, get_scoped_ctx
from qwenpaw.agents.tools.agent_management import resolve_agent_api_base_url

# ── Graph execution engine (package lives next to this file) ─────────
_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from engine import (  # noqa: E402
    ERROR_HANDLE,
    EventType,
    ExecutionState,
    NodeRunContext,
    RunEvent,
    WorkflowRunner,
    assemble_final_result,
    get_logger,
    prepare_resume,
    register_node,
    registered_types,
    resume_workflow_sync,
    run_workflow_sync,
)
from engine.registry import (  # noqa: E402
    NodeTypeDef,
    PropertyField,
    list_node_type_defs,
)

#: Tagged with the running execution's id while a run is on this task.
logger = get_logger(__name__)

# Platform branding — read from environment or use a neutral fallback
_PLATFORM_NAME = os.environ.get("PLATFORM_NAME", "Agent Platform")

# ── Storage ─────────────────────────────────────────────────────────

def _resolve_plugin_data_dir() -> Path:
    """Resolve the plugin data directory in the platform data space.

    Priority:
    1. QZAGENT_HOME env var → <QZAGENT_HOME>/data/agent-flow-designer/
    2. Fall back to ~/.qzagent/data/agent-flow-designer/
    """
    qzagent_home = os.environ.get("QZAGENT_HOME")
    if qzagent_home:
        base = Path(qzagent_home)
    else:
        base = Path("~/.qzagent").expanduser()
    return base / "data" / "agent-flow-designer"


# Legacy data path (kept for migration)
_LEGACY_DATA_DIR = _resolve_plugin_data_dir()
_LEGACY_DATA_FILE = _LEGACY_DATA_DIR / "workflows.json"

# New data path in platform data directory
_DATA_DIR = Path(_BACKEND_DIR).parent.parent.parent / "agent-flow-data"

_locks = dict()

def _LOCK(workflow_id):
    lock = _locks.get(workflow_id)
    if lock is None:
        lock = asyncio.Lock()
        _locks[workflow_id] = lock
    return lock

def _DATA_FILE(workflow_id):
    return _DATA_DIR / workflow_id / "workflow.json"

def _VERSIONS_FILE(workflow_id,version):
    return _DATA_DIR / workflow_id / (str(version)+".json")

# ── HITL paused-run SQLite DB ───────────────────────────────────────
# Initialise on import so the DB file and schema exist before any API call.
from engine.paused_db import get_paused_run, init_db as _init_paused_db  # noqa: E402
from engine.recorder import RunMeta, RunRecorder  # noqa: E402
from engine.run_db import (  # noqa: E402
    RUN_STATUSES as _RUN_STATUSES,
    get_run as _get_run,
    init_db as _init_run_db,
    list_nodes as _list_run_nodes,
    list_runs as _list_runs,
)
from engine.schema import (  # noqa: E402
    SYSTEM_VARIABLE_KEYS,
    build_node_contract,
    parse_json_output,
    parse_output_schema,
    validate_output,
)

_PAUSED_DB_PATH = _DATA_DIR / "paused_executions.db"
_init_paused_db(_PAUSED_DB_PATH)

# ── Execution-history SQLite DB ─────────────────────────────────────
_RUN_DB_PATH = _DATA_DIR / "execution_history.db"
_init_run_db(_RUN_DB_PATH)


def _run_meta(
        workflow: Dict[str, Any],
        context: Dict[str, Any],
        user_id: str,
        trigger_kind: str,
) -> RunMeta:
    """Attribution the engine cannot derive about a run that is about to start.

    ``owner_user_id`` is the authenticated principal: history rows are scoped by
    it on every read, so a run recorded under the wrong owner is invisible to
    the person who ran it and readable by someone else. ``workflow_version`` is
    only ever present for a run on a published snapshot.
    """
    return RunMeta(
        owner_user_id=user_id or "default",
        trigger_kind=trigger_kind,
        workflow_version=workflow.get("deployed_version_number"),
        source_text=str(context.get("user_input") or ""),
    )


# ── In-flight runs (cancellation) ───────────────────────────────────
class _ActiveRun(NamedTuple):
    """What one streaming run leaves behind for the cancel endpoint to find.

    ``workflow_id`` is part of the identity, not decoration: a cancel request is
    addressed at ``/workflows/{id}/executions/{execution_id}/cancel``, and a run
    found under a workflow it never belonged to must read as absent — the same
    answer the history read API gives.
    """

    stop: asyncio.Event
    owner: str
    workflow_id: str


#: Only a streaming run is registered: a synchronous request blocks until the
#: end and never learns its own id first.
_ACTIVE_RUNS: Dict[str, _ActiveRun] = {}


def _begin_run(execution_id: str, user_id: str, workflow_id: str) -> asyncio.Event:
    """Register an in-flight run and return the flag that stops it."""
    stop = asyncio.Event()
    _ACTIVE_RUNS[execution_id] = _ActiveRun(stop, user_id, workflow_id)
    return stop


def _end_run(execution_id: str) -> None:
    _ACTIVE_RUNS.pop(execution_id, None)


# In-memory cache for workflows

def _maybe_migrate_legacy_data() -> bool:
    """Migrate data from legacy plugin directory to platform data directory.

    Returns True if migration was performed, False otherwise.
    """
    # Skip if legacy data doesn't exist
    if not _LEGACY_DATA_FILE.exists():
        return False

    try:
        # Read legacy data
        text = _LEGACY_DATA_FILE.read_text(encoding="utf-8")
        if not text.strip():
            return False

        # Ensure new directory exists
        _DATA_DIR.mkdir(parents=True, exist_ok=True)

        # Write to new location (atomic)
        payload = json.loads(text)
        for workflow in payload:
            _persist_to_disk(workflow)

        # Rename legacy file to mark migration (backup)
        backup_file = _LEGACY_DATA_FILE.with_suffix(".json.migrated")
        try:
            _LEGACY_DATA_FILE.rename(backup_file)
        except OSError:
            pass  # Best effort, don't fail if rename fails

        return True
    except (json.JSONDecodeError, OSError):
        return False


class WorkflowStoreError(RuntimeError):
    """A JSON library on disk cannot be parsed.

    This is deliberately *not* "no data yet". Returning ``[]`` for an
    unreadable file lets the next write persist an empty library straight over
    it, turning one bad byte into total data loss.
    """


def _corrupt_store(path: Path, text: str, label: str, reason: str) -> WorkflowStoreError:
    """Quarantine the unreadable bytes and say where they went."""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    backup = path.with_name(f"{path.name}.corrupt-{stamp}")
    try:
        if not backup.exists():
            backup.write_text(text, encoding="utf-8")
        recovery = f"原文已备份到 {backup}"
    except OSError:
        recovery = "备份写入失败"
    logger.error(
        "[%s] 存储文件损坏: path=%s reason=%s backup=%s", label, path, reason, backup
    )
    return WorkflowStoreError(f"{label}文件已损坏（{reason}）。{recovery}，请修复或删除 {path} 后重试")


def _load_json_library(path: Path, label: str) -> Dict[str, Any]:
    """Read one of the plugin's JSON libraries, refusing to guess on damage."""
    if not path.exists():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    if not text.strip():
        return None
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise _corrupt_store(
            path, text, label, f"JSON 解析失败：第 {exc.lineno} 行 {exc.msg}"
        ) from exc
    if not isinstance(data, dict):
        raise _corrupt_store(path, text, label, "顶层结构不是字典")
    return data


def _load_from_disk(path: Path) -> Dict[str, Any]:
    """Load workflows from JSON file. Returns empty list if file doesn't exist.

    Raises:
        WorkflowStoreError: When the file exists but cannot be parsed.
    """
    return _load_json_library(path, "工作流库")


def _persist_to_disk(workflow:Dict[str, Any]) -> None:
    """Persist workflows atomically to disk (temp file + os.replace).

    Atomic replace guarantees every reader sees either the old or the new
    complete file — never a truncated one — even when other processes read
    concurrently.
    """
    id = workflow['id']
    workflow_dir = _DATA_DIR / id
    workflow_dir.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(workflow, ensure_ascii=False, indent=2)
    fd, tmp = tempfile.mkstemp(
        dir=str(_DATA_DIR),
        prefix=".workflow.",
        suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, _DATA_FILE(id))
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _read_all() -> List[Dict[str, Any]]:
    """Read all workflows from disk, surfacing damage as a structured 500."""
    try:
        # Migrate legacy data on first access (idempotent)
        _maybe_migrate_legacy_data()
        workflows = []
        for workflow_dir in _DATA_DIR.iterdir():
            if workflow_dir.is_file():
                continue
            workflow = _load_from_disk(workflow_dir / 'workflow.json')
            if workflow:
                workflows.append(workflow)
        return workflows
    except WorkflowStoreError as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "error_type": "workflow_store_corrupt",
                "message": str(exc),
                "hint": "修复或删除备份文件后重试，切勿在修复前保存工作流",
            },
        ) from exc


def _find_workflow(
        workflow_id: str
) -> Optional[Dict[str, Any]]:
    data = _load_from_disk(_DATA_FILE(workflow_id))
    return data


def _workflow_owner(record: Dict[str, Any]) -> str:
    return str(record.get("created_by") or "")


def _is_visible_to(record: Dict[str, Any], user_id: str) -> bool:
    """Records written before ownership tracking carry no owner.

    They stay shared on purpose: hiding them would make an existing install
    lose its whole workflow library the moment this ships. Only workflows that
    were explicitly created under an account are isolated.
    """
    owner = _workflow_owner(record)
    return not owner or owner == user_id or owner == 'default' or owner == 'public'


def _require_owner(record: Dict[str, Any], user_id: str, action: str) -> None:
    """Reject a write/run on someone else's workflow."""
    if _is_visible_to(record, user_id):
        return
    raise HTTPException(
        status_code=403,
        detail={
            "error_type": "permission_denied",
            "message": (
                f"工作流「{record.get('name') or record.get('id', '')}」由其他用户创建，"
                f"无法{action}"
            ),
            "action": "switch_account",
        },
    )


def _require_paused_owner(execution_id: str, user_id: str) -> None:
    """Reject a HITL resume submitted by an account other than the one that paused.

    The paused record has no owner column, so the run's own ``SYS_USER_ID``
    (stamped from the authenticated principal when it started) is the owner.
    Missing / expired records are left for ``prepare_resume`` to report.
    """
    entry = get_paused_run(execution_id)
    if not entry:
        return
    context = (entry.get("state") or {}).get("context") or {}
    owner = str(context.get("SYS_USER_ID") or "")
    if owner and owner != user_id:
        raise HTTPException(
            status_code=403,
            detail={
                "error_type": "permission_denied",
                "message": "该暂停执行由其他用户发起，无法代为回答",
                "action": "switch_account",
            },
        )


# ── Router ──────────────────────────────────────────────────────────
router = APIRouter()


class Position(BaseModel):
    x: float
    y: float


class FlowNode(BaseModel):
    id: str
    type: str
    position: Position
    label: str
    description: str = ""
    config: dict[str, Any] = Field(default_factory=dict)


class FlowEdge(BaseModel):
    id: str
    source: str
    target: str
    label: Optional[str] = None
    sourceHandle: Optional[str] = None
    #: Canvas geometry only — which edge of the node the line attaches to. The
    #: engine ignores them; storing them keeps a sideways layout stable across
    #: saves. ``top`` | ``right`` | ``bottom`` | ``left``.
    sourceSide: Optional[str] = None
    targetSide: Optional[str] = None


class WorkflowDefinition(BaseModel):
    id: str
    name: str
    description: str = ""
    nodes: list[FlowNode] = Field(default_factory=list)
    edges: list[FlowEdge] = Field(default_factory=list)
    system_prompt: str = ""
    created_at: str = ""
    updated_at: str = ""
    #: Authenticated principal that created this workflow. Enforced by
    #: :func:`_require_owner`; empty on records written before ownership.
    created_by: str = ""
    deployed_version_id: Optional[str] = None
    deployed_at: Optional[str] = None


#: Record keys only publish / deploy / rollback may change. They are restored
#: from the stored record on every edit, which is why the publish pointers are
#: deliberately absent from :class:`WorkflowDefinition`: an editing payload
#: cannot express "unpublish this workflow".
_SERVER_OWNED_KEYS = (
    "published_version_id",
    "published_version",
    "published_at",
    "deployed_version_id",
    "deployed_at",
)


class WorkflowVersion(BaseModel):
    id: str
    workflow_id: str
    version: int
    name: str
    description: str = ""
    nodes: list[FlowNode] = Field(default_factory=list)
    edges: list[FlowEdge] = Field(default_factory=list)
    system_prompt: str = ""
    created_at: str = ""
    published_at: str = ""


class ChatAttachment(BaseModel):
    url: str
    name: str
    type: str = ""
    size: int = 0


class ChatMessage(BaseModel):
    role: str
    content: str
    attachments: list[ChatAttachment] = Field(default_factory=list)


class ExecuteRequest(BaseModel):
    workflow_id: str = ""
    messages: list[ChatMessage]
    stream: bool = True
    # ── Caller-supplied execution variables ─────────────────────────
    # ``user_id`` / ``agent_id`` are *not* accepted here: they are bound to the
    # authenticated principal by ``get_scoped_ctx`` so a run can never claim
    # another user's identity through the request body.
    conversation_id: str = ""
    user_uid: str = ""
    user_name: str = ""
    lang: str = ""


class ResumeRequest(BaseModel):
    """Human answer used to continue a HITL-paused execution."""
    execution_id: str
    answer: str


# ── Router execution helpers ────────────────────────────────────────

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


# ── API Routes ─────────────────────────────────────────────────────

@router.post("/workflows")
async def create_workflow(
        definition: WorkflowDefinition,
        ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """Create a new workflow owned by the authenticated principal."""
    definition.id = definition.id or str(uuid.uuid4())
    # Ensure workflow has a valid name
    if not definition.name or not str(definition.name).strip():
        definition.name = f"未命名工作流 {datetime.utcnow().strftime('%m-%d %H:%M')}"
    now = datetime.utcnow().isoformat()
    definition.created_at = now
    definition.updated_at = now
    definition.created_by = ctx.user_id

    async with _LOCK(definition.id):
        _persist_to_disk(definition.model_dump())

    return {"success": True, "data": definition.model_dump()}


@router.get("/workflows/{workflow_id}")
async def get_workflow(
        workflow_id: str,
        ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """Get a workflow by ID."""
    async with _LOCK(workflow_id):
        wf = _find_workflow(workflow_id)
        if wf is not None:
            _require_owner(wf, ctx.user_id, "查看")
            return {"success": True, "data": wf}
    raise HTTPException(status_code=404, detail="Workflow not found")


@router.put("/workflows/{workflow_id}")
async def update_workflow(
        workflow_id: str,
        definition: WorkflowDefinition,
        ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """Update an existing workflow."""
    # Ensure workflow has a valid name
    if not definition.name or not str(definition.name).strip():
        definition.name = f"未命名工作流 {datetime.utcnow().strftime('%m-%d %H:%M')}"
    async with _LOCK(workflow_id):
        wf = _find_workflow(workflow_id)
        if wf.get("id") == workflow_id:
            _require_owner(wf, ctx.user_id, "修改")
            definition.id = workflow_id
            definition.updated_at = datetime.utcnow().isoformat()
            # Ownership is server-side: a payload that omits ``created_by``
            # must not silently hand the workflow to the first writer.
            definition.created_by = _workflow_owner(wf) or ctx.user_id
            record = definition.model_dump()
            # Publish and deploy pointers are server-owned. The editing
            # client never sends them, so replacing the record outright
            # would silently unpublish the workflow on every autosave — and
            # copying them unconditionally stops a forged payload from
            # claiming a deployment that never happened.
            for key in _SERVER_OWNED_KEYS:
                record[key] = wf.get(key)

            _persist_to_disk(wf)
            return {"success": True, "data": record}

    raise HTTPException(status_code=404, detail="Workflow not found")


@router.get("/workflows")
async def list_workflows(ctx: PawAppContext = Depends(get_scoped_ctx)) -> dict:
    """List the workflows this user may see."""
    workflows = _read_all()
    visible = [wf for wf in workflows if _is_visible_to(wf, ctx.user_id)]
    return {"success": True, "data": visible}


@router.get("/tools-catalog")
async def tools_catalog(ctx: PawAppContext = Depends(get_scoped_ctx)) -> dict:
    """List the tools a node can actually call, for the designer's pickers.

    The platform section comes from the same ``local_workspace.list_tools`` the
    agent loop uses, so the picker can never offer a tool the agent cannot call
    — permission narrowing stays in the host policy, not a second AFD whitelist.
    One unreachable MCP client degrades to nothing instead of failing the whole
    catalog, because a dead server must not make the designer unusable. A missing
    host workspace is different: that is not "no tools", it is "cannot answer",
    so it fails loudly instead of returning an empty list the UI cannot tell apart
    from an agent that legitimately has nothing to call.
    """
    services = await _build_tool_services(ctx)
    if not services:
        raise HTTPException(
            status_code=503,
            detail="工作区未就绪，无法列出工具目录",
        )
    items: List[dict] = []

    local_ws = services.get("local_workspace")
    if local_ws is not None:
        try:
            tools = await local_ws.list_tools(
                agent_config=services.get("agent_config"),
                agent_id=services.get("agent_id") or None,
                request_context={
                    "agent_id": services.get("agent_id", ""),
                    "user_id": services.get("user_id", ""),
                },
            )
            for tool in tools:
                name = str(getattr(tool, "name", "") or "")
                if not name:
                    continue
                items.append({
                    "source": "platform",
                    "id": name,
                    "label": name,
                    "description": str(getattr(tool, "description", "") or "")[:500],
                })
        except Exception as exc:  # noqa: BLE001  (a failed listing is empty, not fatal)
            logger.warning("[tools-catalog] platform listing failed: %s", exc)

    manager = services.get("driver_manager")
    if manager is not None:
        from qwenpaw.app.mcp.config_service import MCPConfigService
        from qwenpaw.drivers.constants import CAPABILITY_KIND_TOOL

        service = None
        clients: List[Any] = []
        try:
            service = MCPConfigService(services.get("workspace"))
            clients = await service.list_clients()
        except Exception as exc:  # noqa: BLE001
            logger.warning("[tools-catalog] MCP client listing failed: %s", exc)
        for client in clients:
            client_key = str(getattr(client, "key", "") or "")
            if not client_key or not getattr(client, "enabled", False) or service is None:
                continue
            try:
                tool_infos = await service.list_tools(client_key)
                # MCPToolInfo carries no capability id; align by tool name with
                # what the driver reports, and drop anything we cannot address.
                caps = await manager.list_driver_capabilities(
                    client_key, kind=CAPABILITY_KIND_TOOL, request_context={},
                )
                ids = {
                    str(getattr(c, "name", "")): str(getattr(c, "capability_id", ""))
                    for c in caps
                }
            except Exception as exc:  # noqa: BLE001  (dead server: skip this client)
                logger.warning(
                    "[tools-catalog] MCP client '%s' unavailable: %s", client_key, exc
                )
                continue
            for info in tool_infos:
                capability_id = ids.get(str(getattr(info, "name", "")), "")
                if not getattr(info, "enabled", False) or not capability_id:
                    continue
                items.append({
                    "source": "mcp",
                    "id": capability_id,
                    "clientKey": client_key,
                    "label": str(getattr(info, "name", "")),
                    "description": str(getattr(info, "description", "") or "")[:500],
                    "inputSchema": getattr(info, "input_schema", {}) or {},
                })

    return {"success": True, "data": items}


@router.get("/node-contract")
async def node_contract(ctx: PawAppContext = Depends(get_scoped_ctx)) -> dict:
    """Field names and types per node type, straight from the engine.

    The designer used to hardcode this table and drifted: it offered two
    fields the runtime can never resolve. Serving it removes the second copy.
    """
    return {"success": True, "data": build_node_contract()}


@router.get("/node-types")
async def get_node_types(ctx: PawAppContext = Depends(get_scoped_ctx)) -> dict:
    """Return registered node type metadata for dynamic designer rendering."""
    defs = list_node_type_defs()
    payload = []
    for meta in defs:
        item = asdict(meta)
        # PropertyField is a dataclass but asdict handles nested dataclasses
        # automatically; no manual conversion needed.
        payload.append(item)
    return {"success": True, "data": payload}


@router.delete("/workflows/{workflow_id}")
async def delete_workflow(
        workflow_id: str,
        ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """Delete a workflow."""
    async with _LOCK(workflow_id):
        target = _find_workflow(workflow_id)
        if target is not None:
            _require_owner(target, ctx.user_id, "删除")

        if target is None:
            raise HTTPException(status_code=404, detail="Workflow not found")
        os.unlink(_DATA_DIR/ workflow_id)
    return {"success": True}


# ── Version storage helpers ─────────────────────────────────────────

def _load_versions(workflow_id) -> List[Dict[str, Any]]:
    """Load workflow versions from JSON file, surfacing damage as a 500."""
    try:
        versions = []
        root = _DATA_DIR / workflow_id
        for ver in root.glob('*.json'):
            if not ver.is_file():
                continue
            if ver.name=='workflow.json':
                continue
            v = _load_json_library(ver, "版本库")
            if v:
                versions.append(v)
        return versions
    except WorkflowStoreError as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "error_type": "workflow_store_corrupt",
                "message": str(exc),
                "hint": "版本历史无法读取时请勿发布，否则会写入一个空的版本列表",
            },
        ) from exc


def _persist_versions(version: Dict[str, Any]) -> None:
    """Persist versions atomically to disk."""
    workflow_id = version['workflow_id']
    ver_id = version['id']
    payload = json.dumps(version, ensure_ascii=False, indent=2)
    fd, tmp = tempfile.mkstemp(
        dir=str(_DATA_DIR),
        prefix=".version.",
        suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, _VERSIONS_FILE(workflow_id,ver_id))
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


# ── Static validation (design time) ─────────────────────────────────

#: Operators that compare a value against a baseline, so a missing baseline is
#: a configuration error rather than a comparison against zero.
_DELTA_OPERATORS = frozenset(
    {
        "delta_gt", "delta_lt", "delta_ge", "delta_le",
        "change_rate_gt", "change_rate_lt",
        "text_diff_ratio_gt", "text_diff_contains",
    }
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


class ValidateRequest(BaseModel):
    """An optional inline graph so unsaved edits can be checked too."""

    workflow: Optional[dict] = None


@router.post("/workflows/{workflow_id}/validate")
async def validate_workflow_route(
    workflow_id: str,
    req: Optional[ValidateRequest] = None,
    ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """Report structural and reference errors before publishing or deploying.

    When ``workflow`` is supplied the unsaved canvas graph is checked instead of
    the stored one, so the designer can validate without saving first.
    """
    inline = (req.workflow if req and req.workflow else None)
    if inline is not None:
        return validate_workflow(inline)

    async with _LOCK(workflow_id):
        wf = _find_workflow(workflow_id)
    if wf is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    _require_owner(wf, ctx.user_id, "校验")
    return validate_workflow(wf)


# ── Publish API Routes ──────────────────────────────────────────────

@router.post("/workflows/{workflow_id}/publish")
async def publish_workflow(
        workflow_id: str,
        ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """Publish a workflow: create an immutable version snapshot.

    The published version is decoupled from the editing state.
    """
    async with _LOCK(workflow_id):
        # Load current workflow
        wf = _find_workflow(workflow_id)
        if wf is None:
            raise HTTPException(status_code=404, detail="Workflow not found")
        _require_owner(wf, ctx.user_id, "发布")
        _raise_if_invalid(wf, "发布")

        # Load existing versions to determine next version number
        workflow_versions = _load_versions(workflow_id)
        next_version = 1
        if workflow_versions:
            next_version = max(v.get("version", 0) for v in workflow_versions) + 1

        now = datetime.utcnow().isoformat()
        version_record = {
            "id": str(uuid.uuid4()),
            "workflow_id": workflow_id,
            "version": next_version,
            "name": wf.get("name", ""),
            "description": wf.get("description", ""),
            "nodes": wf.get("nodes", []),
            "edges": wf.get("edges", []),
            "system_prompt": wf.get("system_prompt", ""),
            "created_at": wf.get("created_at", ""),
            "created_by": _workflow_owner(wf) or ctx.user_id,
            "published_at": now,
        }
        _persist_versions(version_record)
        w = wf
        # Update workflow with publish metadata
        w["published_version_id"] = version_record["id"]
        w["published_version"] = next_version
        w["published_at"] = now
        w["updated_at"] = now
        _persist_to_disk(w)

    return {
        "success": True,
        "data": {
            "version_id": version_record["id"],
            "version": next_version,
            "published_at": now,
        },
    }


@router.get("/workflows/{workflow_id}/versions")
async def list_workflow_versions(
        workflow_id: str,
        ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """List all published versions of a workflow."""
    async with _LOCK(workflow_id):
        wf = _find_workflow(workflow_id)
        if wf is not None:
            _require_owner(wf, ctx.user_id, "查看版本")
        versions = _load_versions(workflow_id)
        workflow_versions = [v for v in versions if v.get("workflow_id") == workflow_id]
        workflow_versions.sort(key=lambda v: v.get("version", 0), reverse=True)
    return {"success": True, "data": workflow_versions}


@router.post("/workflows/{workflow_id}/rollback/{version_id}")
async def rollback_workflow(
        workflow_id: str,
        version_id: str,
        ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """Rollback a workflow to a specific published version.

    The current editing state is overwritten by the published version snapshot.
    """
    async with _LOCK(workflow_id):
        target_version = _load_from_disk(_VERSIONS_FILE(workflow_id,version_id))
        if target_version is None:
            raise HTTPException(status_code=404, detail="Version not found")

        wf = _find_workflow(workflow_id)
        if wf.get("id") == workflow_id:
            _require_owner(wf, ctx.user_id, "回滚")
            wf.update({
                "name": target_version.get("name", ""),
                "description": target_version.get("description", ""),
                "nodes": target_version.get("nodes", []),
                "edges": target_version.get("edges", []),
                "system_prompt": target_version.get("system_prompt", ""),
                "updated_at": datetime.utcnow().isoformat(),
            })
        else:
            raise HTTPException(status_code=404, detail="Workflow not found")
        _persist_to_disk(wf)

    return {"success": True, "data": {"version_id": version_id, "version": target_version.get("version")}}


@router.get("/workflows/{workflow_id}/published")
async def get_published_workflow(
        workflow_id: str,
        ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """Get the latest published version of a workflow.

    Returns 404 if the workflow has never been published.
    """
    async with _LOCK(workflow_id):
        wf = _find_workflow(workflow_id)
        if wf is None:
            raise HTTPException(status_code=404, detail="Workflow not found")
        _require_owner(wf, ctx.user_id, "查看")

        published_version_id = wf.get("published_version_id")
        if not published_version_id:
            raise HTTPException(status_code=404, detail="Workflow has not been published")

        v = _load_from_disk(_VERSIONS_FILE(workflow_id,published_version_id))
        if v:
            if v.get("id") == published_version_id:
                return {"success": True, "data": v}

        raise HTTPException(status_code=404, detail="Published version not found")


# ── Deploy API Routes ───────────────────────────────────────────────

@router.post("/workflows/{workflow_id}/deploy")
async def deploy_workflow(
    workflow_id: str,
    ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """Deploy the latest published version of a workflow.

    Once deployed, the workflow can be executed externally using the
    deployed version snapshot, completely isolated from the editing state.
    """
    async with _LOCK(workflow_id):
        wf = _find_workflow(workflow_id)
        if wf is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_type": "workflow_not_found",
                    "message": "工作流不存在",
                    "action": "请刷新页面或重新选择工作流",
                }
            )
        _require_owner(wf, ctx.user_id, "部署")

        published_version_id = wf.get("published_version_id")
        if not published_version_id:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_type": "workflow_not_published",
                    "message": "工作流尚未发布，无法部署",
                    "action": "请先点击「发布」按钮发布工作流，然后再进行部署",
                }
            )

        # Verify the published version exists
        target_version = _load_from_disk(_VERSIONS_FILE(workflow_id,published_version_id))
        if target_version is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_type": "published_version_not_found",
                    "message": "已发布版本不存在，可能是数据不一致",
                    "action": "请重新发布工作流后再试",
                }
            )

        # The snapshot is what goes live, so it — not the draft — is validated.
        _raise_if_invalid(target_version, "部署")

        now = datetime.utcnow().isoformat()
        wf["deployed_version_id"] = published_version_id
        wf["deployed_at"] = now

        _persist_to_disk(wf)

    return {
        "success": True,
        "data": {
            "version_id": published_version_id,
            "version": target_version.get("version"),
            "deployed_at": now,
        },
    }


@router.post("/workflows/{workflow_id}/undeploy")
async def undeploy_workflow(
    workflow_id: str,
    ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """Undeploy a workflow, removing its external service endpoint."""
    async with _LOCK(workflow_id):
        wf = _find_workflow(workflow_id)
        if wf is None:
            raise HTTPException(status_code=404, detail="Workflow not found")
        _require_owner(wf, ctx.user_id, "下线")

        wf["deployed_version_id"] = None
        wf["deployed_at"] = None

        _persist_to_disk(wf)

    return {"success": True, "data": {"message": "Workflow undeployed"}}


@router.get("/workflows/{workflow_id}/deployed")
async def get_deployed_workflow(
    workflow_id: str,
    ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """Get the currently deployed version of a workflow."""
    async with _LOCK(workflow_id):
        wf = _find_workflow(workflow_id)
        if wf is None:
            raise HTTPException(status_code=404, detail="Workflow not found")
        _require_owner(wf, ctx.user_id, "查看")

        deployed_version_id = wf.get("deployed_version_id")
        if not deployed_version_id:
            raise HTTPException(status_code=404, detail="Workflow is not deployed")

        v = _load_from_disk(_VERSIONS_FILE(workflow_id,deployed_version_id))
        if v:
            if v.get("id") == deployed_version_id:
                return {"success": True, "data": v}

        raise HTTPException(status_code=404, detail="Deployed version not found")


def _parse_sse_line(line: str) -> Optional[dict]:
    """Parse a single SSE data line."""
    stripped = line.strip()
    if stripped.startswith("data: "):
        try:
            return json.loads(stripped[6:])
        except json.JSONDecodeError:
            return None
    return None


def _extract_text_from_agent_response(data: dict) -> str:
    """Extract text content from agent response payload (supports multiple formats)."""
    if not isinstance(data, dict):
        return str(data)

    event_data = data
    text = ''
    if event_data.get('output'):
        for item in event_data['output']:
            if item.get('role') == 'assistant':
                for content_item in item.get('content', []):
                    if content_item.get('type') == 'text':
                        text += content_item.get('text', '')
    return text

    # ── Format 1: SSE content delta (streaming chunks)
    # {"object": "content", "delta": true, "msg_id": "...", "index": 0, "text": "..."}
    if data.get("object") == "content" and data.get("delta") is True:
        text = data.get("text", "")
        if isinstance(text, str) and text:
            return text

    # ── Format 2: SSE message completed
    # {"object": "message", "status": "completed", "output": [...]}
    if data.get("object") == "message" and data.get("status") == "completed":
        output = data.get("output", [])
        if output and isinstance(output, list):
            text_parts = []
            for msg in output:
                if isinstance(msg, dict):
                    content = msg.get("content", [])
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and item.get("type") == "text":
                                text_parts.append(item.get("text", ""))
                            elif isinstance(item, str):
                                text_parts.append(item)
                    elif isinstance(content, str):
                        text_parts.append(content)
            result = "".join(text_parts)
            if result:
                return result

    # ── Format 3: SSE response object
    # {"object": "response", "output": [{"role": "assistant", "content": [...]}]}
    if data.get("object") in ("response", "message"):
        output = data.get("output", [])
        if output and isinstance(output, list):
            text_parts = []
            for msg in output:
                if isinstance(msg, dict):
                    content = msg.get("content", [])
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and item.get("type") == "text":
                                text_parts.append(item.get("text", ""))
                            elif isinstance(item, str):
                                text_parts.append(item)
                    elif isinstance(content, str):
                        text_parts.append(content)
            result = "".join(text_parts).strip()
            if result:
                return result

    # ── Format 4: SSE standard format (legacy)
    # {"output": [{"role": "assistant", "content": [{"type": "text", "text": "..."}]}]}
    try:
        output = data.get("output", [])
        if output and isinstance(output, list):
            last_msg = output[-1]
            if isinstance(last_msg, dict):
                content = last_msg.get("content", [])
                if isinstance(content, list):
                    text_parts = []
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            text_parts.append(item.get("text", ""))
                        elif isinstance(item, str):
                            text_parts.append(item)
                    result = "".join(text_parts)
                    if result:
                        return result
    except (KeyError, IndexError, TypeError):
        pass
    # ── Format 6: No string fallback
    return ''


# ── Tool node: host service resolution ──────────────────────────────


async def _build_tool_services(ctx: Optional[PawAppContext]) -> dict:
    """Resolve the live host handles a tool node needs, once per run.

    Returns ``{}`` when there is no authenticated context or no workspace: a
    platform/mcp tool node then fails with a readable message rather than
    half-working. Re-resolved on resume, because a paused run's handles died
    with the process that paused it (and the snapshot must stay JSON-safe).
    """
    if ctx is None:
        return {}
    workspace = await ctx._get_workspace()  # pylint: disable=protected-access
    if workspace is None:
        return {}
    agent_id = str(getattr(workspace, "agent_id", "") or getattr(ctx, "agent_id", "") or "")
    agent_config = None
    try:
        from qwenpaw.config.config import load_agent_config

        agent_config = load_agent_config(agent_id or "default")
    except Exception:  # noqa: BLE001  (agent-less workspaces still list tools)
        logger.debug("[tool services] agent config unavailable", exc_info=True)
    return {
        "workspace": workspace,
        "local_workspace": getattr(workspace, "local_workspace", None),
        "driver_manager": getattr(workspace, "driver_manager", None),
        "agent_config": agent_config,
        "agent_id": agent_id,
        "user_id": str(getattr(ctx, "user_id", "") or ""),
    }


def _build_tool_request_context(services: dict, state: ExecutionState) -> dict:
    """The request context handed to host tools, attributed to this run.

    ``session_id`` names the workflow execution so an approval card (should the
    host ever escalate inside ``__call__``) has a session to point at.
    """
    return {
        "agent_id": services.get("agent_id", ""),
        "user_id": services.get("user_id", ""),
        "session_id": f"workflow:{state.execution_id}",
        "channel": "workflow",
    }


class AgentCallException(Exception):
    """Raised when an agent chat API call fails irrecoverably.

    Used to signal upstream that the node execution failed,
    so the executor can mark the node status as ``failed``
    instead of treating the error text as a normal response.
    """


class ToolApprovalRequired(Exception):
    """Governance decided ASK for a workflow tool call.

    Carries the question a human must answer. The ``tool`` handler turns it into
    a ``WF_PAUSE`` event, because the blocking chat approval the host uses has
    no place inside a workflow run: it would park the SSE connection on a card
    nobody in the canvas is watching.
    """

    def __init__(self, message: str, *, question: str = "") -> None:
        super().__init__(message)
        self.question = question


def _as_token_count(value: Any) -> int:
    """Coerce one host token counter, treating anything unusable as zero."""
    try:
        return max(int(value or 0), 0)
    except (TypeError, ValueError):
        return 0


def _turn_usage_tokens(parsed: Any) -> dict:
    """Normalise the platform's ``turn_usage`` event into trace keys.

    This event is the only place the host reports token cost, and it closes a
    chat turn — so it is a property of the one call that just finished, which is
    what makes per-node attribution possible. An empty dict means "nothing was
    measured", and the history records that as zero rather than as a guess.
    """
    usage = parsed.get("usage") if isinstance(parsed, dict) else None
    if not isinstance(usage, dict):
        return {}
    prompt = _as_token_count(usage.get("prompt_tokens"))
    completion = _as_token_count(usage.get("completion_tokens"))
    return {
        "promptTokens": prompt,
        "completionTokens": completion,
        "totalTokens": _as_token_count(usage.get("total_tokens")) or (prompt + completion),
    }


async def _call_agent_chat(agent_id: str, messages: list, timeout: float = 60.0, on_token=None, usage_out=None) -> str:
    """Call the local platform chat API and collect the full response.

    Supports both JSON and SSE streaming responses.
    Also supports message attachments (images/files) via content_parts.

    Args:
        on_token: Optional synchronous callback invoked with each incremental
            text delta as it arrives from the SSE stream. It is purely a
            passthrough for live streaming (token-level) consumers; the final
            return value is assembled exactly as before, so synchronous
            callers see a byte-identical result.
        usage_out: Optional dict filled with the caller's token counts (see
            :func:`_turn_usage_tokens`). A sink rather than a second return
            value because the text is the contract and this is a side note.

    Raises:
        AgentCallException: When the HTTP request fails (connection error,
            timeout, non-2xx status, or unexpected exception).
    """
    import httpx

    # Fallback to default agent if not specified
    effective_agent_id = agent_id.strip() if agent_id and str(agent_id).strip() else "default"

    def _build_content_parts(msg: dict) -> list:
        """Build content parts from message text and attachments.

        Produces platform-native Content shapes:
        - Text: {"type": "text", "text": "..."}
        - Image: {"type": "image", "image_url": "<path or url>"}
        - File: {"type": "file", "file_url": "<path or url>", "filename": "..."}
        """
        parts = []
        text = msg.get("content", "")
        if text:
            parts.append({"type": "text", "text": text})
        for att in msg.get("attachments", []) or []:
            url = att.get("url", "")
            if not url:
                continue
            # Heuristic: treat image/* as image, everything else as file
            att_type = att.get("type", "")
            if att_type and att_type.startswith("image/"):
                parts.append({"type": "image", "image_url": url})
            else:
                parts.append({
                    "type": "file",
                    "file_url": url,
                    "filename": att.get("name", "file"),
                })
        return parts

    payload = {
        "session_id": None,
        "user_id": "workflow-executor",
        "input": [
            {
                "role": msg.get("role", "user"),
                "content": _build_content_parts(msg),
            }
            for msg in messages
        ],
    }

    headers = {"X-Agent-Id": effective_agent_id}
    base_url = resolve_agent_api_base_url()

    # Debug: log request
    logger.debug(
        "[_call_agent_chat] agent_id=%s, messages_count=%d, payload=%s",
        effective_agent_id,
        len(messages),
        json.dumps(payload, ensure_ascii=False, default=str),
    )

    try:
        async with httpx.AsyncClient() as client:
            # Streaming is what makes on_token incremental: a buffered POST
            # would hand us the whole body before the first delta.
            async with client.stream(
                "POST",
                f"{base_url}/api/console/chat",
                json=payload,
                headers=headers,
                timeout=timeout,
            ) as response:
                # A streaming response cannot be re-read after the context exits,
                # so load an error body now — the handler below reports its detail.
                if response.status_code >= 400:
                    await response.aread()
                response.raise_for_status()

                content_type = response.headers.get("content-type", "")
                logger.debug("[_call_agent_chat] response content-type=%s", content_type)

                # Handle SSE stream
                if "text/event-stream" in content_type or payload.get("stream"):
                    text_parts = []
                    sse_event_count = 0
                    async for line in response.aiter_lines():
                        if not line or not line.strip().startswith("data:"):
                            continue
                        parsed = _parse_sse_line(line)
                        if not parsed:
                            continue
                        if parsed.get("type") == "turn_usage":
                            # Filtered out of the text for the same reason it is
                            # filtered here: it is bookkeeping, not an answer.
                            if usage_out is not None:
                                usage_out.update(_turn_usage_tokens(parsed))
                            continue
                        sse_event_count += 1

                        part = _extract_text_from_agent_response(parsed)
                        if part:
                            text_parts.append(part)
                            # Surface true incremental deltas for live streaming.
                            if (
                                on_token is not None
                                and parsed.get("object") == "content"
                                and parsed.get("delta") is True
                            ):
                                try:
                                    on_token(part)
                                except Exception:  # noqa: BLE001  (never break the run for a UI callback)
                                    logger.debug("[_call_agent_chat] on_token callback failed", exc_info=True)
                    result_text = "".join(text_parts)
                    logger.debug(
                        "[_call_agent_chat] SSE events=%d, extracted_text_len=%d",
                        sse_event_count,
                        len(result_text),
                    )
                    return result_text

                # Handle JSON response
                await response.aread()
                data = response.json()
                logger.debug("[_call_agent_chat] JSON response=%s", json.dumps(data, ensure_ascii=False, default=str))
                if usage_out is not None:
                    # A buffered JSON reply normally carries no turn_usage block;
                    # the helper returns {} when there is nothing measured.
                    usage_out.update(_turn_usage_tokens(data))
                result = _extract_text_from_agent_response(data)
                logger.debug("[_call_agent_chat] extracted_text_len=%d", len(result))
                return result

    except httpx.ConnectError as exc:
        raise AgentCallException(f"无法连接到 {_PLATFORM_NAME} 服务 ({base_url})") from exc
    except httpx.TimeoutException as exc:
        raise AgentCallException(f"Agent 调用超时 ({timeout}s)") from exc
    except httpx.HTTPStatusError as exc:
        # Extract detailed error from response body if available
        detail = str(exc)
        try:
            error_body = exc.response.json() if exc.response else {}
            if isinstance(error_body, dict) and error_body.get("detail"):
                detail = error_body["detail"]
        except Exception:
            pass
        raise AgentCallException(f"Agent 调用失败 (HTTP {exc.response.status_code}): {detail}") from exc
    except Exception as exc:
        raise AgentCallException(f"Agent 调用异常: {str(exc)}") from exc


async def _call_model_directly(model_key: str, messages: list, timeout: float = 30.0, usage_out=None) -> str:
    """Directly call a specific model by its provider/model identifier.

    Parses ``provider_id/model_id`` (e.g. ``dashscope/qwen3.6-plus``),
    obtains the chat-model instance from the provider manager, and
    invokes it. Falls back to ``_call_agent_chat`` when the provider
    or model is unavailable.

    Args:
        model_key: Provider/model identifier in the form ``provider/model``.
        messages: List of message dicts with ``role`` and ``content`` keys.
        timeout: Maximum time to wait for the model response.
        usage_out: Token counts sink, filled only on the ``_call_agent_chat``
            fallbacks. A provider called directly reports none: the host's
            ``consume_model_response`` returns text and discards the usage
            block, so a direct call is recorded as zero rather than estimated.

    Returns:
        The model's text response, or an error message string.
    """
    # Parse provider_id and model_id from the key
    # Support both colon (":") and slash ("/") separators for compatibility
    separator = ":" if ":" in model_key else ("/" if "/" in model_key else None)
    if separator is None:
        logger.warning("[Router LLM] model_key does not contain ':' or '/', falling back to agent chat: %s", model_key)
        return await _call_agent_chat(model_key, messages, timeout=timeout, usage_out=usage_out)

    provider_id, model_id = model_key.split(separator, 1)
    if not provider_id or not model_id:
        logger.warning("[Router LLM] empty provider_id or model_id in: %s", model_key)
        return await _call_agent_chat(model_key, messages, timeout=timeout, usage_out=usage_out)

    try:
        from qwenpaw.providers.provider_manager import ProviderManager
        from qwenpaw.utils.model_response import consume_model_response
        from agentscope.message import UserMsg, SystemMsg, AssistantMsg

        manager = ProviderManager.get_instance()
        provider = manager.get_provider(provider_id)
        if provider is None:
            logger.warning("[Router LLM] Provider not found: %s", provider_id)
            return await _call_agent_chat(model_key, messages, timeout=timeout, usage_out=usage_out)

        model_instance = provider.get_chat_model_instance(model_id)
        if model_instance is None:
            logger.warning("[Router LLM] Model not found: %s/%s", provider_id, model_id)
            return await _call_agent_chat(model_key, messages, timeout=timeout, usage_out=usage_out)

        # Convert dict messages to agentscope Msg objects
        # Use UserMsg/SystemMsg/AssistantMsg helpers which automatically
        # wrap string content into TextBlock lists.
        msg_objects = []
        for msg in messages:
            role = msg.get("role", "user") if isinstance(msg, dict) else "user"
            content = msg.get("content", "") if isinstance(msg, dict) else str(msg)
            if role == "system":
                msg_objects.append(SystemMsg(name=role, content=content))
            elif role == "assistant":
                msg_objects.append(AssistantMsg(name=role, content=content))
            else:
                msg_objects.append(UserMsg(name=role, content=content))

        logger.debug("[Router LLM] Calling model directly: %s/%s", provider_id, model_id)
        result = await asyncio.wait_for(
            consume_model_response(model_instance, msg_objects),
            timeout=timeout,
        )
        return result or ""
    except asyncio.TimeoutError as exc:
        raise AgentCallException(f"模型调用超时 ({timeout}s): {model_key}") from exc
    except Exception as exc:
        logger.exception("[Router LLM] Direct model call failed for %s", model_key)
        raise AgentCallException(f"模型调用失败: {exc}") from exc


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


# ── Tool node: config resolution ────────────────────────────────────

#: The three worlds a tool node can reach. One node type, not three types.
_TOOL_SOURCES = frozenset({"platform", "mcp", "http"})


def _resolve_tool_source(config: dict) -> str:
    """The tool node's source; legacy configs (only ``toolName``) mean platform."""
    raw = str(config.get("source") or "").strip().lower()
    return raw or "platform"


def _resolve_tool_params(config: dict, context: dict, node_outputs: dict) -> dict:
    """Turn the structured ``params`` bindings into a plain argument dict.

    platform / mcp take typed arguments, so a binding is ``{name, valueType,
    value}`` with ``valueType == "variable"`` resolved through the same
    reference engine the agent nodes use. Old nodes stored a bare mapping of
    literals; that shape is still accepted.
    """
    raw = config.get("params")
    resolved: Dict[str, Any] = {}
    if isinstance(raw, dict):
        resolved.update(raw)
        return resolved
    for item in raw or []:
        if not isinstance(item, dict):
            # R23：坏绑定不能静默丢弃 —— 少一个参数会让工具在几层之外报"缺必填参数"，
            # 与本功能"未知来源/未解析引用/缺环境变量一律显式失败"的规则自相矛盾。
            raise ValueError(f"工具参数绑定不是对象：{item!r}")
        name = str(item.get("name") or "").strip()
        if not name:
            raise ValueError(f"工具参数绑定缺少参数名：{item!r}")
        # R22：与 _resolve_tool_source 对称归一化，导入的工作流 JSON 里 "Variable"
        # 不能被当成字面值，把引用串本身喂给工具。
        value_type = str(item.get("valueType") or "literal").strip().lower()
        if value_type == "variable":
            ref = str(item.get("value") or "").strip()
            value, found = _resolve_variable_ex(ref, context, node_outputs)
            if not found:
                raise ValueError(
                    f"工具参数「{name}」引用的变量未解析：{ref}"
                )
            resolved[name] = value
        else:
            resolved[name] = item.get("value")
    return resolved


def _tool_block_text(block: Any) -> str:
    """One content block's text, regardless of whether it is a dict or a model."""
    if isinstance(block, dict):
        return str(block.get("text") or "")
    return str(getattr(block, "text", "") or "")


def _render_tool_output(value: Any, output_format: str = "") -> str:
    """Render one tool result as the node's text output.

    Host tools return an agentscope ``ToolChunk`` / ``ToolResponse`` (content
    blocks + state), a driver returns an arbitrary value, and HTTP returns text.

    The state check is an **allow-list**, not a deny-list (控制者裁定 R19):
    ``ToolResultState`` is ``success | error | interrupted | denied | running``
    and ``ToolChunk.state`` defaults to ``RUNNING``, so enumerating only the two
    failure states we happened to think of would let a sandbox kill, a user
    cancel, or a partial/incremental chunk become node output. Anything the host
    has not declared ``success`` is a call that did not produce this result.
    A value with no ``state`` (a plain driver dict) is not a tool result at all
    and falls through to the JSON branch.
    """
    if isinstance(value, str):
        text = value
    else:
        state = getattr(value, "state", None)
        state_value = str(getattr(state, "value", state) or "").lower()
        blocks = list(getattr(value, "content", None) or [])
        if state_value and state_value != "success":
            detail = " / ".join(t for t in (_tool_block_text(b) for b in blocks) if t)
            # 只有真被策略拒绝才说"被拒绝"；error / interrupted / running 是执行失败，
            # 说成拒绝会把排查指向治理层（控制者裁定 R21）。
            label = "被拒绝" if state_value == "denied" else "失败"
            raise RuntimeError(f"工具执行{label}（{state_value}）：{detail[:200]}")
        parts: List[str] = []
        for block in blocks:
            block_text = _tool_block_text(block)
            if block_text:
                parts.append(block_text)
                continue
            source = block.get("source") if isinstance(block, dict) else getattr(block, "source", None)
            if source is not None:
                # DataBlock（截图/音频）走占位符，绝不落进下面的 json.dumps ——
                # 那会把整段 base64 写进 node_outputs、暂停快照与导出（控制者裁定 R20）。
                media = str(getattr(source, "media_type", None)
                            or (source.get("media_type") if isinstance(source, dict) else "")
                            or "")
                parts.append(f"[二进制结果{'：' + media if media else ''}]")
        text = "\n".join(parts) if parts else json.dumps(
            value, ensure_ascii=False, default=str
        )

    if output_format == "json":
        parsed = value if isinstance(value, (dict, list)) else None
        if parsed is None:
            try:
                parsed = json.loads(text)
            except Exception:  # noqa: BLE001  (reported, not swallowed)
                raise RuntimeError(f"工具结果不是 JSON，无法按 json 格式输出：{text[:200]}") from None
        return json.dumps(parsed, ensure_ascii=False, indent=2, default=str)
    return text


def _finish_tool_output(
    value: Any, output_format: str, parsed_out: Optional[dict]
) -> str:
    """Render like _render_tool_output, optionally handing back the object.

    A schema-checked tool node needs the parsed object, not a dumps-then-loads
    round trip. The capture is an out-param so _render_tool_output's own
    contract — and the five tests that lock it — stay untouched.
    """
    text = _render_tool_output(value, output_format)
    if parsed_out is not None and output_format == "json":
        parsed_out["value"] = (
            value if isinstance(value, (dict, list)) else json.loads(text)
        )
    return text


async def _invoke_platform_tool(
    config: dict,
    params: dict,
    services: dict,
    state: ExecutionState,
    *,
    approval_granted: bool = False,
    parsed_out: Optional[dict] = None,
) -> str:
    """Call a host built-in tool with governance intact.

    ``check_permissions`` is *not* part of ``PolicyGuardedTool.__call__`` — the
    agentscope permission engine calls it separately. So invoking a listed tool
    directly would skip policy evaluation, audit and sandbox assembly entirely.
    This function reproduces the four steps the agent loop performs and is the
    only place in the plugin that touches those private attributes.

    Its return value is an authoritative *gate*, not a sandbox assembler
    (控制者裁定 R26 第 1 条): anything but ``ALLOW`` fails closed here without
    running the tool. Its ASK branch parks the run on a chat approval card that
    nobody watches on the canvas, and its DENY branch is a human denial — either
    one executed anyway would be a governance bypass.

    Audit exactly once per call: DENY / ASK-not-approved / unrecognised record
    it here (those branches never reach ``check_permissions``); the executing
    branches let the gate record it, except the OFF short-circuit which returns
    before the host's audit — detectable because ``_qp_policy_decision`` is still
    ``None``, and only then do we back-fill one (裁定 R26 第 3 条).
    """
    from agentscope.permission import PermissionBehavior
    from qwenpaw.governance.policy import GovernanceAction
    from qwenpaw.security.tool_guard.execution_level import ToolExecutionLevel

    tool_name = str(config.get("toolName") or "").strip()
    if not tool_name:
        raise ValueError("工具节点未配置 toolName")
    # 三种来源共用同一个 outputFormat 语义：platform 不得比 mcp/http 少一个格式化能力。
    output_format = str(config.get("outputFormat") or "")
    local_ws = services.get("local_workspace")
    if local_ws is None:
        raise RuntimeError("无法访问宿主 Workspace，工具节点未执行任何操作")

    request_context = _build_tool_request_context(services, state)
    tools = await local_ws.list_tools(
        agent_config=services.get("agent_config"),
        agent_id=services.get("agent_id") or None,
        request_context=request_context,
    )
    tool = next((t for t in tools if getattr(t, "name", "") == tool_name), None)
    if tool is None:
        available = ", ".join(sorted(str(getattr(t, "name", "")) for t in tools)[:20])
        raise RuntimeError(
            f"当前 Agent（{services.get('agent_id', '')}）未启用工具「{tool_name}」。"
            f"可选工具：{available or '（无）'}"
        )

    governor = getattr(tool, "_qp_governor", None)
    if governor is None:
        raise RuntimeError(
            f"治理层不可用，工具「{tool_name}」已按 fail-closed 策略拒绝执行"
        )

    # 1) 非阻塞预分类：assert_policy 是同步纯函数，绝不会停在审批等待里。
    #
    # 预分类必须与闸门用同一个**有效级别**，否则第 2 步的 fail-closed 只是把
    # "静默执行"换成"卡在审批卡上"（裁定 R26 第 2 条）。宿主在
    # _policy_tool_check_permissions 里先同步再评估（tool_adapter.py:323-324），
    # 有效级别 = request_context["approval_level"]（会话覆盖）优先 → agent profile
    # 兜底；这里用的是宿主自己的公共枚举同一个解析入口。工作流的请求上下文由
    # _build_tool_request_context 现造、不含 approval_level，所以只需要 agent_config，
    # 而 `agent_config` 缺失或没有 approval_level 时 from_config 按宿主默认 → AUTO。
    # F1 探索模式对工作流不会命中：宿主注册表按用户会话建键，工作流的 session_id
    # 形如 workflow:{execution_id}，因此这里不模仿 :296-303 的强制 STRICT，
    # 也不为此加任何防御代码。
    effective_level = ToolExecutionLevel.from_config(
        getattr(services.get("agent_config"), "approval_level", None)
    )
    tool._qp_raw_params = params          # noqa: SLF001  (spec §4.2 集中耦合)
    spec = tool._build_tc_spec()          # noqa: SLF001
    previous_level = governor.policy.execution_level
    governor.policy.execution_level = effective_level.value
    try:
        decision = governor.assert_policy(spec)
    finally:
        governor.policy.execution_level = previous_level
    action = getattr(decision, "action", None)

    # 2) 按决定行动。
    if action is GovernanceAction.DENY:
        governor.audit(spec, decision)
        raise RuntimeError(f"工具「{tool_name}」被策略拒绝：{decision.reason}")

    if action is GovernanceAction.ASK and not approval_granted:
        governor.audit(spec, decision)
        raise ToolApprovalRequired(
            f"工具「{tool_name}」需要人工审批：{decision.reason}",
            question=(
                f"是否允许执行工具「{tool_name}」？\n"
                f"策略理由：{decision.reason}\n"
                f"调用参数：{json.dumps(params, ensure_ascii=False, default=str)[:400]}\n"
                "（回复 批准 / 同意 / approve 予以放行；其他任何回答按拒绝处理）"
            ),
        )

    # 3) 下面三条路径都会真执行工具，共用同一段闸门逻辑。
    if action is GovernanceAction.ASK:
        # The human approved this exact call. ``approval_level`` in the request
        # context is the host's session-level override, and list_tools hands us a
        # fresh tool object, so setting it short-circuits only this invocation —
        # and only the "ask the user" step. The OFF branch still compiles a
        # sandbox_config for fail-closed tools, so isolation is not weakened.
        # (Recording a rule instead cannot work: a builtin_rules ASK is
        # deliberately not persisted on approval, so the node would pause again.)
        tool._qp_request_context = {**request_context, "approval_level": "off"}  # noqa: SLF001
    elif action not in (GovernanceAction.ALLOW, GovernanceAction.SANDBOX_FALLBACK):
        governor.audit(spec, decision)
        raise RuntimeError(
            f"工具「{tool_name}」的治理决定无法识别（{action}），已按拒绝处理：{decision.reason}"
        )

    # 闸门判定是权威结论，不是沙箱装配的副产品：非 ALLOW 一律 fail-closed，
    # 绝不调用 tool(**params)（裁定 R26 第 1 条）。
    permission = await tool.check_permissions(params, None)  # noqa: SLF001
    behavior = getattr(permission.behavior, "value", permission.behavior)
    if permission.behavior != PermissionBehavior.ALLOW:
        raise RuntimeError(
            f"工具「{tool_name}」的权限闸门判定为 {behavior}，已按 fail-closed 策略拒绝执行："
            f"{permission.message}"
        )
    # 宿主在正常路径先审计再写 _qp_policy_decision（:364/:367），OFF 短路则在写之前就
    # 返回（:311-317）。于是"宿主有没有记这笔账"有机械信号：还写着默认值就是没记，
    # 由我们补一次；否则宿主已记，不得重复（裁定 R26 第 3 条）。
    if getattr(tool, "_qp_policy_decision", None) is None:  # noqa: SLF001
        governor.audit(spec, decision)
    return _finish_tool_output(await tool(**params), output_format, parsed_out)


async def _invoke_mcp_tool(
    config: dict, params: dict, services: dict, state: ExecutionState,
    parsed_out: Optional[dict] = None,
) -> str:
    """Invoke one MCP capability through the host driver layer.

    Credentials stay in the driver card: AFD never sees, stores or forwards a
    key. The invocation returns a result object rather than raising, so a
    transport failure is an ordinary ``ok=False``.
    """
    from qwenpaw.drivers.capabilities import DriverInvocation

    capability_id = str(config.get("capabilityId") or "").strip()
    if not capability_id:
        raise ValueError("MCP 工具节点未配置 capabilityId")
    manager = services.get("driver_manager")
    if manager is None:
        raise RuntimeError("宿主 driver_manager 不可用，MCP 工具节点未执行")

    result = await manager.invoke_capability(
        DriverInvocation(
            capability_id=capability_id,
            payload=params,
            request_context=_build_tool_request_context(services, state),
        )
    )
    if not result.ok:
        raise RuntimeError(
            f"MCP 工具调用失败（{result.error_type}）：{result.message}"
        )
    return _finish_tool_output(result.value, str(config.get("outputFormat") or ""), parsed_out)


#: 一个节点吊住整条 SSE 是可观测的事故，所以超时钳到 120s。
_TOOL_TIMEOUT_MAX = 120.0
_HTTP_METHODS = frozenset({"GET", "POST", "PUT", "PATCH", "DELETE"})
_HTTP_BODY_LIMIT = 200_000

#: 工作流作者能引用的凭证变量只允许落在这个命名空间里。"只存变量名"挡不住
#: 填任意变量名：宿主进程环境里还有模型 Key、数据库口令、对象存储 AK/SK。
_SECRET_ENV_PREFIX = "AFD_HTTP_SECRET_"
_SECRET_ENV_NAME_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,127}")


def _checked_secret_env_name(env_name: str) -> str:
    """Return the name a workflow may read, or refuse before any request goes out."""
    if not _SECRET_ENV_NAME_RE.fullmatch(env_name):
        raise ValueError(
            f"凭证环境变量名「{env_name[:64]}」不合法：只允许字母、数字、下划线，"
            "且不能以数字开头"
        )
    if not env_name.startswith(_SECRET_ENV_PREFIX):
        raise ValueError(
            f"凭证环境变量必须以「{_SECRET_ENV_PREFIX}」开头，当前为「{env_name}」；"
            "宿主进程里的其它环境变量不能被工作流读取"
        )
    return env_name


_SECRET_REF_MAX_LEN = 120
_SECRET_FIELD_MAX_LEN = 64


def _checked_secret_ref(ref: str) -> str:
    """Return the credential ref a workflow may read, or refuse.

    ``env:`` refs are rejected outright: the store's env fallback would read
    any process variable, bypassing the ``AFD_HTTP_SECRET_`` namespace guard.
    """
    if not ref or len(ref) > _SECRET_REF_MAX_LEN:
        raise ValueError(
            f"密钥引用「{ref[:64]}」不合法：长度须在 1–{_SECRET_REF_MAX_LEN} 字符内"
        )
    if any(ch.isspace() for ch in ref):
        raise ValueError(f"密钥引用「{ref[:64]}」不合法：不能包含空白字符")
    if ref.lower().startswith("env:"):
        raise ValueError(
            "密钥引用不支持 env: 前缀；读环境变量请改用 authEnvVar（须以"
            f"「{_SECRET_ENV_PREFIX}」开头）"
        )
    return ref


def _checked_secret_field(field: str) -> str:
    if not field or len(field) > _SECRET_FIELD_MAX_LEN:
        raise ValueError(
            f"密钥字段名「{field[:64]}」不合法：长度须在 1–{_SECRET_FIELD_MAX_LEN} 字符内"
        )
    return field


def _workspace_credential_store(services: Optional[dict]):
    """Build the host per-workspace credential store, or ``None`` when the
    run has no workspace context (callers must fail closed on ``None``)."""
    workspace = (services or {}).get("workspace")
    workspace_dir = getattr(workspace, "workspace_dir", None)
    if not workspace_dir:
        return None
    from qwenpaw.drivers.credentials.store import AsyncCredentialStore

    return AsyncCredentialStore(Path(workspace_dir) / "credentials.yaml")


async def _resolve_host_ips(host: str) -> List[str]:
    """Resolve ``host`` to its address strings. Seam for the SSRF guard so
    tests can drive resolution without touching the network."""
    loop = asyncio.get_event_loop()
    infos = await loop.getaddrinfo(host, None)
    return [info[4][0] for info in infos]


def _ip_is_blocked(ip: "ipaddress.IPvAddress") -> bool:
    mapped = getattr(ip, "ipv4_mapped", None)
    if mapped is not None:
        ip = mapped
    return bool(
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    )


def _url_pinned_to_ip(url: str, ip: str) -> str:
    """Rewrite ``url``'s host to an address already validated, keeping port and userinfo."""
    from urllib.parse import urlparse, urlunparse

    parsed = urlparse(url)
    host = f"[{ip}]" if ":" in ip else ip
    try:
        port = f":{parsed.port}" if parsed.port else ""
    except ValueError:
        port = ""
    split = parsed.netloc.rsplit("@", 1)
    prefix = f"{split[0]}@" if len(split) == 2 else ""
    return urlunparse(parsed._replace(netloc=f"{prefix}{host}{port}"))


async def _checked_http_target(url: str) -> Tuple[str, Optional[str]]:
    """Check the request host and, for a name, pin the URL to the address checked —
    otherwise httpx re-resolves after the check and a second DNS record moves the
    request to an internal address.

    The second element is the original hostname whenever the URL was rewritten; the
    caller must resend it as ``Host`` and as the TLS SNI name. It is ``None`` when
    the URL goes out as written: a literal IP, or a name that failed to resolve.
    Resolution failures still fail open on purpose so reserved hostnames like
    ``*.test`` keep working and httpx reports the real connect error.
    """
    from urllib.parse import urlparse

    host = urlparse(url).hostname
    if not host:
        raise ValueError(f"无法解析请求地址的主机名：{url}")

    try:
        literal = ipaddress.ip_address(host)
    except ValueError:
        literal = None
    if literal is not None:
        if _ip_is_blocked(literal):
            raise ValueError(f"出于安全考虑，禁止访问内网/本机地址：{host}")
        return url, None

    try:
        resolved = await _resolve_host_ips(host)
    except (OSError, ValueError):
        return url, None
    ips: List[ipaddress.IPvAddress] = []
    for item in resolved:
        try:
            ips.append(ipaddress.ip_address(item))
        except ValueError:
            continue
    blocked = next((str(ip) for ip in ips if _ip_is_blocked(ip)), None)
    if blocked is not None:
        raise ValueError(f"出于安全考虑，禁止访问内网/本机地址：{host} 指向 {blocked}")
    if not ips:
        return url, None
    # 绑死一个地址就不能再靠 httpx 逐个试：优先 IPv4，免得只有 v6 记录或
    # v6 不通的机器上，原来能连通的工具节点变成连不上。
    chosen = next((ip for ip in ips if isinstance(ip, ipaddress.IPv4Address)), ips[0])
    return _url_pinned_to_ip(url, str(chosen)), host


async def _invoke_http_tool(
    config: dict,
    context: dict,
    node_outputs: dict,
    timeout_log: Optional[List[float]] = None,
    parsed_out: Optional[dict] = None,
    services: Optional[dict] = None,
) -> str:
    """Call an external HTTP endpoint with ``{{ref}}`` interpolation.

    url / headers / query / body are free-text templates on purpose: this source
    takes untyped HTTP arguments, not a typed parameter table (spec §3.2). The
    credential comes from the platform credential store (``authSecretRef``) or
    an environment variable (``authEnvVar``) **at run time** — the secretRef
    wins when both are configured. Only the reference / variable name is ever
    stored, the name must sit under the ``AFD_HTTP_SECRET_`` namespace for env
    vars, and neither the value nor the assembled header map reaches the trace.
    """
    import httpx

    def _interpolate(template: str) -> str:
        return _interpolate_template(template, context, node_outputs)

    url = _interpolate(str(config.get("url") or "").strip())
    if not url:
        raise ValueError("HTTP 工具节点未配置 url")
    if url.split(":", 1)[0].lower() not in ("http", "https"):
        raise ValueError(
            f"仅允许 http/https 请求，当前 URL 协议为「{url.split(':', 1)[0] or '空'}」"
        )
    method = str(config.get("method") or "GET").strip().upper()
    if method not in _HTTP_METHODS:
        raise ValueError(f"不支持的 HTTP 方法：{method}")

    request_url, pinned_host = await _checked_http_target(url)

    def _interpolated(mapping_key: str) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for key, value in (config.get(mapping_key) or {}).items():
            out[str(key)] = _interpolate(str(value)) if isinstance(value, str) else value
        return out

    headers = _interpolated("headers")
    query = _interpolated("query")
    body = _interpolate(str(config.get("body") or ""))

    def _apply_auth_header(secret: str) -> None:
        auth_header_name = str(config.get("authHeader") or "Authorization")
        for stale in [k for k in headers if str(k).lower() == auth_header_name.lower()]:
            del headers[stale]
        headers[auth_header_name] = secret

    secret_ref = str(config.get("authSecretRef") or "").strip()
    if secret_ref:
        _checked_secret_ref(secret_ref)
        store = _workspace_credential_store(services)
        if store is None:
            raise RuntimeError(
                "无法解析平台密钥：当前运行上下文没有可用的工作区，"
                "已阻止发送无凭证请求"
            )
        field = str(config.get("authSecretField") or "").strip() or "value"
        _checked_secret_field(field)
        from qwenpaw.drivers.errors import CredentialNotFoundError

        try:
            record = await store.get(secret_ref)
        except CredentialNotFoundError as exc:
            raise RuntimeError(
                f"平台密钥「{secret_ref}」在工作区凭证库中不存在；"
                "已阻止发送无凭证请求，请先在凭证库中创建该密钥"
            ) from exc
        value = record.values.get(field)
        if not isinstance(value, str) or not value:
            raise RuntimeError(
                f"平台密钥「{secret_ref}」缺少字段「{field}」或该字段为空；"
                "已阻止发送无凭证请求"
            )
        _apply_auth_header(value)
    else:
        env_name = str(config.get("authEnvVar") or "").strip()
        if env_name:
            secret = os.environ.get(_checked_secret_env_name(env_name), "")
            if not secret:
                raise RuntimeError(
                    f"环境变量 {env_name} 未设置；已阻止发送无凭证请求，"
                    "请设置后重试（凭证值不会写入工作流或执行记录）"
                )
            _apply_auth_header(secret)

    # 已校验过的地址不能被重新解析顶掉；作者显式写过 Host 时尊重作者的选择。
    send_headers = headers
    extensions: Dict[str, Any] = {}
    if pinned_host is not None:
        if not any(str(k).lower() == "host" for k in send_headers):
            send_headers = {**send_headers, "Host": pinned_host}
        extensions["sni_hostname"] = pinned_host

    raw_timeout = config.get("timeoutSec")
    try:
        timeout = float(raw_timeout) if raw_timeout not in (None, "") else 15.0
    except (TypeError, ValueError):
        timeout = 15.0
    timeout = min(max(timeout, 1.0), _TOOL_TIMEOUT_MAX)
    if timeout_log is not None:
        timeout_log.append(timeout)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(
                method,
                request_url,
                headers=send_headers,
                params=query or None,
                content=body.encode("utf-8") if body else None,
                extensions=extensions,
            )
        response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise RuntimeError(f"工具 HTTP 调用超时（{timeout}s）：{url}") from exc
    except httpx.ConnectError as exc:
        raise RuntimeError(f"无法连接到工具服务端：{url}") from exc
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"工具 HTTP 调用失败（HTTP {exc.response.status_code}）："
            f"{(exc.response.text or '')[:200]}"
        ) from exc
    except httpx.HTTPError as exc:
        # 兜底：httpx 的异常家族比这里逐条列出的三个更宽（RemoteProtocolError、
        # TooManyRedirects、InvalidURL…）。漏网的必须仍是中文的 RuntimeError，
        # 但英文原文不能进 state.error 与用户可见 detail —— 只报异常类名和 URL。
        raise RuntimeError(
            f"工具 HTTP 调用失败（{type(exc).__name__}）：{url}"
        ) from exc

    text = response.text or ""
    if len(text) > _HTTP_BODY_LIMIT:
        text = (
            text[:_HTTP_BODY_LIMIT]
            + f"\n…（响应已截断，原始长度 {len(text)} 字符）"
        )
    return _finish_tool_output(text, str(config.get("outputFormat") or ""), parsed_out)


#: Fields the Start node always exposes — mirrors :func:`_get_node_inputs`, so a
#: reference to one of these always resolves at run time.
_START_OUTPUT_FIELDS = frozenset(
    {"user_input", "messages", "messages_count"} | set(SYSTEM_VARIABLE_KEYS)
)


def _build_execution_context(
    req: ExecuteRequest, ctx: Optional[PawAppContext] = None
) -> dict:
    """Build the initial execution context from the request + host identity.

    ``SYS_USER_ID`` and ``AGENT_ID`` are read from the authenticated PawApp
    context rather than the request body, so a run cannot adopt another user's
    identity by crafting a payload.
    """
    user_input = req.messages[-1].content if req.messages else ""
    principal = str(getattr(ctx, "user_id", "") or "default")
    return {
        "messages": [m.model_dump() for m in req.messages],
        "user_input": user_input,
        "SYS_USER_ID": principal,
        "USER_UID": req.user_uid or principal,
        "USER_NAME": req.user_name or principal,
        "USER_LANG": req.lang,
        "AGENT_ID": str(getattr(ctx, "agent_id", "") or "default"),
        "CONVERSATION_ID": req.conversation_id,
        "REQUEST_ID": str(uuid.uuid4()),
        "AGENT_USER_MSG": user_input,
    }


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


async def _resolve_execution_workflow(
    workflow_id: str, preview: bool = False, user_id: str = ""
) -> dict:
    """Load a workflow for execution, honouring deployed-version isolation.

    Shared by the synchronous ``/execute`` endpoint and the streaming
    ``/execute/stream`` endpoint so both resolve the exact same graph. When the
    workflow is deployed and ``preview`` is false, the deployed snapshot is used
    instead of the current editing state. Raises 404 when not found and 403 when
    ``user_id`` is given and the workflow belongs to someone else.
    """
    async with _LOCK(workflow_id):
        workflow = _find_workflow(workflow_id)

        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        if user_id:
            _require_owner(workflow, user_id, "执行")

    # ── Deployed version isolation ──────────────────────────────
    # If deployed and not in preview mode, load the deployed version snapshot
    deployed_version_id = workflow.get("deployed_version_id")
    if deployed_version_id and not preview:
        v = _load_from_disk(_VERSIONS_FILE(workflow_id,deployed_version_id))
        if v and v.get("id") == deployed_version_id:
            # Use the deployed snapshot instead of the editing state
            workflow = {
                "id": workflow_id,
                "name": v.get("name", ""),
                "description": v.get("description", ""),
                "nodes": v.get("nodes", []),
                "edges": v.get("edges", []),
                "system_prompt": v.get("system_prompt", ""),
                "created_at": v.get("created_at", ""),
                "updated_at": v.get("published_at", ""),
                "deployed_version_id": deployed_version_id,
                "deployed_version_number": v.get("version"),
                "deployed_at": workflow.get("deployed_at"),
            }

    return workflow


@router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str,
    req: ExecuteRequest,
    preview: bool = False,
    ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """Execute a workflow with full node data flow support.

    If the workflow is deployed, the execution uses the deployed version snapshot
    instead of the current editing state, ensuring complete isolation between
    the deployed service and ongoing edits.

    When preview=true, the current editing state is used directly, bypassing
    the deployed version snapshot. This is used by the Preview & Debug panel.

    The authenticated principal behind ``ctx`` supplies the system variables the
    Start node exposes, so a run cannot adopt another user's identity.
    """
    workflow = await _resolve_execution_workflow(workflow_id, preview, ctx.user_id)
    return await _execute_workflow_core(
        workflow_id,
        req,
        workflow,
        ctx,
        trigger_kind="designer" if preview else "deployed_api",
    )


# ── Unified External Execution API ────────────────────────────────

@router.post("/workflows/{workflow_id}/run")
async def run_workflow(
    workflow_id: str,
    req: ExecuteRequest,
    ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """Unified external execution endpoint.
    
    Only deployed workflows can be executed via this endpoint.
    Returns 400 if the workflow is not deployed.
    Automatically uses the deployed version snapshot, completely
    isolated from the editing state.
    """
    async with _LOCK(workflow_id):
        workflow = _find_workflow(workflow_id)

        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        _require_owner(workflow, ctx.user_id, "调用")

        # ── Deployment check ───────────────────────────────────────
        deployed_version_id = workflow.get("deployed_version_id")
        if not deployed_version_id:
            raise HTTPException(
                status_code=400,
                detail="Workflow is not deployed. Please deploy before calling this endpoint."
            )

        # Load deployed version snapshot
        deployed_version = _load_from_disk(_VERSIONS_FILE(workflow_id,deployed_version_id))

        if not deployed_version:
            raise HTTPException(status_code=404, detail="Deployed version not found")

        # Use the deployed snapshot
        workflow = {
            "id": workflow_id,
            "name": deployed_version.get("name", ""),
            "description": deployed_version.get("description", ""),
            "nodes": deployed_version.get("nodes", []),
            "edges": deployed_version.get("edges", []),
            "system_prompt": deployed_version.get("system_prompt", ""),
            "created_at": deployed_version.get("created_at", ""),
            "updated_at": deployed_version.get("published_at", ""),
            "deployed_version_id": deployed_version_id,
            "deployed_version_number": deployed_version.get("version"),
            "deployed_at": workflow.get("deployed_at"),
        }

    return await _execute_workflow_core(
        workflow_id, req, workflow, ctx, trigger_kind="api"
    )


# ── Node type metadata (used by the dynamic designer) ──────────────

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


# ── Node handlers (registered into the graph engine registry) ───────
# Each handler reproduces the trace-item shape produced by the previous BFS
# implementation so the synchronous (run_sync) contract stays byte-identical.

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


async def _execute_workflow_core(
    workflow_id: str,
    req: ExecuteRequest,
    workflow: dict,
    ctx: Optional[PawAppContext] = None,
    *,
    trigger_kind: str = "deployed_api",
) -> dict:
    """Execute a workflow via the graph engine (legacy-compatible contract)."""
    context = _build_execution_context(req, ctx)
    services = await _build_tool_services(ctx)
    meta = _run_meta(
        workflow, context, str(getattr(ctx, "user_id", "") or ""), trigger_kind
    )
    return await run_workflow_sync(
        workflow_id, workflow, context, services=services, meta=meta
    )


def _sse(obj: dict) -> str:
    """Serialize one object as an SSE ``data:`` frame."""
    return f"data: {json.dumps(obj, ensure_ascii=False)}\n\n"


async def _stream_events(
    execution_id: str,
    workflow_id: str,
    state: ExecutionState,
    runner: "WorkflowRunner",
):
    """Drive a traversal and yield SSE frames for every engine event.

    Shared by the fresh streaming path and the HITL resume path so both emit
    an identical wire contract:
      wf_start   {executionId, workflowId, resumed}
      node_start {nodeId, nodeLabel, type}
      token      {nodeId, delta}          (agent token-level streaming)
      node       {nodeId, trace}          (trace status completed|failed|skipped)
      route      {nodeId, branchId, matched}
      pause      {executionId, nodeId, question, traceItems}  (HITL)
      wf_done    {executionId, result, traceItems}
      wf_error   {executionId, detail, traceItems}
    """
    if not runner.resumed and not runner.start_nodes():
        yield _sse({"event": "wf_start", "executionId": execution_id, "workflowId": workflow_id, "resumed": False})
        yield _sse({
            "event": "wf_done",
            "executionId": execution_id,
            "result": "工作流执行完成（无开始节点）。",
            "traceItems": [],
        })
        if runner.recorder is not None:
            # Nothing is traversed, so the runner's bracket never opens: the
            # outcome the caller is being handed has to be written explicitly.
            state.status = "completed"
            state.result = "工作流执行完成（无开始节点）。"
            runner.recorder.begin()
            runner.recorder.finish()
        return

    yield _sse({"event": "wf_start", "executionId": execution_id, "workflowId": workflow_id, "resumed": runner.resumed})
    try:
        async for event in runner.run():
            if event.type == EventType.NODE_START:
                yield _sse({
                    "event": "node_start",
                    "nodeId": event.node_id,
                    "nodeLabel": event.payload.get("nodeLabel", event.node_id),
                    "type": event.payload.get("type", ""),
                })
            elif event.type == EventType.NODE_TOKEN:
                yield _sse({
                    "event": "token",
                    "nodeId": event.node_id,
                    "delta": event.payload.get("delta", ""),
                })
            elif event.type in (EventType.NODE_DONE, EventType.NODE_ERROR):
                trace = event.trace_item or {}
                yield _sse({
                    "event": "node",
                    "nodeId": event.node_id,
                    "status": trace.get("status", "completed"),
                    "trace": trace,
                })
            elif event.type == EventType.ROUTE:
                yield _sse({
                    "event": "route",
                    "nodeId": event.node_id,
                    "branchId": event.payload.get("branchId", ""),
                    "matched": event.payload.get("matched", False),
                })
            elif event.type == EventType.WF_PAUSE:
                yield _sse({
                    "event": "pause",
                    "executionId": execution_id,
                    "nodeId": event.node_id,
                    "question": event.payload.get("question", ""),
                    "traceItems": state.trace_items,
                })
            elif event.type == EventType.WF_DONE:
                # handled after loop with full trace items
                pass

        # HITL pause: traversal stopped awaiting a human answer. The ``pause``
        # frame was already emitted; do NOT send wf_done.
        if state.status == "paused":
            return

        # A node failed under onError=abort, or the run was cancelled: report the
        # stop, never a "completed" outcome built from missing upstream output.
        if state.status in ("failed", "cancelled"):
            yield _sse({
                "event": "wf_error",
                "executionId": execution_id,
                "detail": state.error,
                "cancelled": state.status == "cancelled",
                "traceItems": state.trace_items,
            })
            return

        if not state.reached_end:
            state.result = assemble_final_result(state.node_outputs, runner.node_map)

        yield _sse({
            "event": "wf_done",
            "executionId": execution_id,
            "result": state.result.strip(),
            "traceItems": state.trace_items,
        })
    except Exception as exc:  # noqa: BLE001  (mirror run_sync catch-all)
        yield _sse({
            "event": "wf_error",
            "executionId": execution_id,
            "detail": f"执行工作流时发生错误: {str(exc)}",
            "traceItems": state.trace_items,
        })


async def _stream_workflow(
    workflow_id: str,
    workflow: dict,
    context: dict,
    user_id: str = "",
    services: Optional[dict] = None,
    *,
    trigger_kind: str = "designer",
):
    """Yield SSE frames describing a fresh graph execution as it happens."""
    execution_id = str(uuid.uuid4())
    state = ExecutionState(
        execution_id=execution_id,
        workflow_id=workflow_id,
        context=dict(context),
    )
    stop = _begin_run(execution_id, user_id, workflow_id)
    runner = WorkflowRunner(
        workflow,
        state,
        cancel_check=stop.is_set,
        services=services or {},
        recorder=RunRecorder(
            state, workflow_id, _run_meta(workflow, context, user_id, trigger_kind)
        ),
    )
    try:
        async for frame in _stream_events(execution_id, workflow_id, state, runner):
            yield frame
    finally:
        # Reaching this while the traversal is unfinished means the client went
        # away; stop the run instead of leaving it burning tokens unobserved.
        stop.set()
        _end_run(execution_id)


async def _stream_resume_workflow(
    execution_id: str,
    answer: str,
    user_id: str = "",
    services: Optional[dict] = None,
):
    """Continue a HITL-paused execution, streaming the remaining frames.

    Consumes the persisted pause position via :func:`prepare_resume` (which
    removes it from the registry) and drives the traversal from there. If the
    run pauses again on another ask node, a further ``pause`` frame is emitted.
    ``services`` must be re-resolved by the caller: the snapshot on disk holds
    no live handles, the resuming process supplies them.
    """
    prepared = prepare_resume(
        execution_id,
        answer,
        services,
        meta=RunMeta(owner_user_id=user_id or "default", trigger_kind="resume"),
    )
    if prepared is None:
        yield _sse({
            "event": "wf_error",
            "executionId": execution_id,
            "detail": f"暂停中的执行不存在或已过期: {execution_id}",
            "traceItems": [],
        })
        return
    state, runner = prepared
    stop = _begin_run(execution_id, user_id, state.workflow_id)
    runner.cancel_check = stop.is_set
    try:
        async for frame in _stream_events(
            state.execution_id, state.workflow_id, state, runner
        ):
            yield frame
    finally:
        stop.set()
        _end_run(execution_id)


@router.post("/workflows/{workflow_id}/execute/stream")
async def execute_workflow_stream(
    workflow_id: str,
    req: ExecuteRequest,
    preview: bool = False,
    ctx: PawAppContext = Depends(get_scoped_ctx),
):
    """Stream workflow execution progress as Server-Sent Events.

    Uses the same graph engine and deployed-version isolation as ``/execute``,
    but surfaces each node transition live so the canvas can highlight the
    currently executing node. Kept as a separate endpoint (rather than a
    ``req.stream`` flag on ``/execute``) so existing synchronous callers are
    completely unaffected.
    """
    workflow = await _resolve_execution_workflow(workflow_id, preview, ctx.user_id)
    context = _build_execution_context(req, ctx)
    services = await _build_tool_services(ctx)
    return StreamingResponse(
        _stream_workflow(
            workflow_id,
            workflow,
            context,
            ctx.user_id,
            services=services,
            trigger_kind="designer" if preview else "deployed_api",
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/workflows/{workflow_id}/execute/resume")
async def resume_workflow(
    workflow_id: str,
    req: ResumeRequest,
    ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """Continue a HITL-paused execution with the human answer (JSON contract).

    Mirrors ``/execute``: returns the legacy response shape, either the final
    ``completed`` result or a further ``paused`` outcome when the continuation
    reaches another ask node. Returns 404 when the paused execution is unknown
    or has expired.
    """
    _require_paused_owner(req.execution_id, ctx.user_id)
    services = await _build_tool_services(ctx)
    result = await resume_workflow_sync(
        req.execution_id,
        req.answer,
        services=services,
        meta=RunMeta(owner_user_id=ctx.user_id or "default", trigger_kind="resume"),
    )
    if not result.get("success") and "不存在或已过期" in str(result.get("detail", "")):
        raise HTTPException(status_code=404, detail=result.get("detail", "Paused execution not found"))
    return result


@router.post("/workflows/{workflow_id}/execute/resume/stream")
async def resume_workflow_stream(
    workflow_id: str,
    req: ResumeRequest,
    ctx: PawAppContext = Depends(get_scoped_ctx),
):
    """Continue a HITL-paused execution, streaming the remaining SSE frames.

    Uses the same event contract as ``/execute/stream`` so the canvas keeps the
    live execution running from the paused position.
    """
    _require_paused_owner(req.execution_id, ctx.user_id)
    services = await _build_tool_services(ctx)
    return StreamingResponse(
        _stream_resume_workflow(req.execution_id, req.answer, ctx.user_id, services=services),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


class CancelRequest(BaseModel):
    reason: str = ""


@router.post("/workflows/{workflow_id}/executions/{execution_id}/cancel")
async def cancel_execution(
    workflow_id: str,
    execution_id: str,
    req: Optional[CancelRequest] = None,
    ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """Ask a running execution to stop before its next node.

    The flag is polled between nodes, so the node currently in flight finishes
    first — an LLM call is not cut off mid-request. The run reports
    ``cancelled`` and every node that never started is recorded as ``skipped``.
    """
    entry = _ACTIVE_RUNS.get(execution_id)
    if entry is None or entry.workflow_id != workflow_id:
        raise HTTPException(
            status_code=404,
            detail={
                "error_type": "execution_not_found",
                "message": "该执行记录不存在，或不属于当前工作流",
                "action": "refresh",
            },
        )
    if entry.owner and entry.owner != ctx.user_id:
        raise HTTPException(
            status_code=403,
            detail={
                "error_type": "permission_denied",
                "message": "该执行由其他用户发起，无法代为取消",
                "action": "switch_account",
            },
        )
    entry.stop.set()
    return {
        "success": True,
        "data": {
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "status": "cancelling",
            "reason": (req.reason if req else "") or "",
        },
    }


# ── Execution history (read-only) ───────────────────────────────────

#: Largest page the history API will serve: a caller must not be able to ask for
#: the whole table in one request.
_EXECUTION_PAGE_MAX = 100


@router.get("/workflows/{workflow_id}/executions")
async def list_executions(
    workflow_id: str,
    limit: int = 20,
    offset: int = 0,
    status: Optional[str] = None,
    ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """This user's runs of one workflow, newest first.

    ``run_db`` is synchronous sqlite3, so the read runs on a worker thread: the
    same reason the recorder writes there — history must never stall a run.
    """
    if status and status not in _RUN_STATUSES:
        raise HTTPException(
            status_code=422,
            detail={
                "error_type": "invalid_status_filter",
                "message": (
                    f"未知的执行状态「{status}」，"
                    f"可选值：{'、'.join(sorted(_RUN_STATUSES))}"
                ),
                "action": "refresh",
            },
        )
    async with _LOCK(workflow_id):
        wf = _find_workflow(workflow_id)
    if wf is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error_type": "workflow_not_found",
                "message": "工作流不存在",
                "action": "请刷新页面或重新选择工作流",
            },
        )
    _require_owner(wf, ctx.user_id, "查看执行历史")

    rows = await asyncio.to_thread(
        _list_runs,
        workflow_id,
        ctx.user_id or "default",
        limit=min(max(limit, 1), _EXECUTION_PAGE_MAX),
        offset=max(offset, 0),
        status=status,
        )
    return {"success": True, "data": rows}


@router.get("/workflows/{workflow_id}/executions/{execution_id}")
async def get_execution_detail(
    workflow_id: str,
    execution_id: str,
    ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """One run read back whole: the trace plus one row per traversed node.

    A run that is not yours and a run that never happened get the same answer,
    because ``get_run`` cannot tell them apart — and telling them apart would
    confirm which execution ids exist under other owners.
    """
    async with _LOCK(workflow_id):
        wf = _find_workflow(workflow_id)
    if wf is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error_type": "workflow_not_found",
                "message": "工作流不存在",
                "action": "请刷新页面或重新选择工作流",
            },
        )
    _require_owner(wf, ctx.user_id, "查看执行历史")

    owner = ctx.user_id or "default"
    run = await asyncio.to_thread(_get_run, execution_id, owner)
    if run is None or run.get("workflow_id") != workflow_id:
        raise HTTPException(
            status_code=404,
            detail={
                "error_type": "execution_not_found",
                "message": "该执行记录不存在，或不属于当前工作流",
                "action": "refresh",
            },
        )
    run["nodes"] = await asyncio.to_thread(_list_run_nodes, execution_id, owner)
    return {"success": True, "data": run}

