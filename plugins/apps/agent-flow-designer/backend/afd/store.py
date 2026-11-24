# -*- coding: utf-8 -*-
"""Workflow/version JSON storage, ownership checks and DB initialisation.

Importing this module resolves the plugin data directory and initialises the
HITL paused-run and execution-history SQLite databases, so the DB files and
schemas exist before any API call.
"""

import asyncio
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import HTTPException

from engine import get_logger
from engine.paused_db import get_paused_run, init_db as _init_paused_db
from engine.run_db import init_db as _init_run_db

logger = get_logger(__name__)
_WORKING_DIR = Path(os.environ.get("QWENPAW_WORKING_DIR", Path.home() / ".qwenpaw"))

def _resolve_plugin_data_dir() -> Path:
    """Resolve the plugin data directory in the platform data space.

    Priority:
    1. QWENPAW_WORKING_DIR env var → <QWENPAW_WORKING_DIR>/agent-flow-data/
    2. Fall back to ~/.qwenpaw/agent-flow-data/
    """
    return _WORKING_DIR / "agent-flow-data"


# Legacy data path (kept for migration). This module sits one level
# deeper than main.py did (backend/afd/), so the plugin root is three
# parents up — the resolved directory is unchanged.
_LEGACY_DATA_DIR = Path("~/.qzagent/data/agent-flow-designer")
_LEGACY_DATA_FILE = _LEGACY_DATA_DIR / "workflows.json"

# New data path in platform data directory
_DATA_DIR = _resolve_plugin_data_dir()

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
_PAUSED_DB_PATH = _DATA_DIR / "paused_executions.db"
_init_paused_db(_PAUSED_DB_PATH)

# ── Execution-history SQLite DB ─────────────────────────────────────
_RUN_DB_PATH = _DATA_DIR / "execution_history.db"
_init_run_db(_RUN_DB_PATH)


# In-memory cache for workflows

def _maybe_migrate_legacy_data() -> bool:
    """Migrate data from legacy plugin directory to platform data directory.

    Returns True if migration was performed, False otherwise.
    """
    # Skip if new data already exists
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
