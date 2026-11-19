# -*- coding: utf-8 -*-
"""SQLite-backed persistence for HITL paused workflow executions.

Replaces the in-memory ``_PAUSED_RUNS`` OrderedDict with an on-disk table so
that paused executions survive process restarts and are visible across multiple
server instances sharing the same data directory (e.g. via a networked file
system or a single node with multiple workers).

Schema
------
paused_executions
  execution_id  TEXT PRIMARY KEY
  workflow_id   TEXT NOT NULL
  workflow_json TEXT NOT NULL   -- JSON-serialised workflow dict
  state_json    TEXT NOT NULL   -- JSON-serialised ExecutionState dict
  created_at    REAL NOT NULL   -- UTC timestamp (seconds since epoch)
  updated_at    REAL NOT NULL   -- UTC timestamp (seconds since epoch)

TTL / cleanup
-------------
* Records older than ``_PAUSED_TTL_SECONDS`` (default 7 days) are considered
  expired and are removed on the next read/write or explicit cleanup call.
* A background cleanup is triggered automatically on every save after a
  configurable interval (default 1 hour) to avoid repeated scans.
"""

from __future__ import annotations

import json
import os
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from .log_context import get_logger

logger = get_logger(__name__)

# ── Configuration ───────────────────────────────────────────────────
_PAUSED_TTL_SECONDS = 7 * 24 * 60 * 60       # 7 days
_CLEANUP_INTERVAL_SECONDS = 60 * 60            # 1 hour between background cleanups

# Module-level path and lock (late-initialised via init_db)
_db_path: Optional[Path] = None
_db_lock = threading.Lock()
_last_cleanup_time: float = 0.0


def _now() -> float:
    return datetime.now(tz=timezone.utc).timestamp()


def _get_conn() -> sqlite3.Connection:
    """Open a connection with sensible defaults."""
    assert _db_path is not None, "init_db() must be called before any DB operation"
    conn = sqlite3.connect(str(_db_path), check_same_thread=False, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def init_db(db_path: Path) -> None:
    """Create the DB file, schema, and indexes if they don't exist."""
    global _db_path
    _db_path = db_path
    _db_path.parent.mkdir(parents=True, exist_ok=True)
    with _get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS paused_executions (
                execution_id TEXT PRIMARY KEY,
                workflow_id  TEXT NOT NULL,
                workflow_json TEXT NOT NULL,
                state_json   TEXT NOT NULL,
                created_at   REAL NOT NULL,
                updated_at   REAL NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_paused_created_at ON paused_executions(created_at)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_paused_workflow_id ON paused_executions(workflow_id)"
        )
        conn.commit()
    logger.info("HITL paused-run DB initialised at %s", _db_path)


# ── TTL helpers ─────────────────────────────────────────────────────

def _maybe_cleanup_expired(conn: sqlite3.Connection) -> None:
    """Remove records older than the TTL, throttled by _CLEANUP_INTERVAL_SECONDS."""
    global _last_cleanup_time
    now = _now()
    if now - _last_cleanup_time < _CLEANUP_INTERVAL_SECONDS:
        return
    cutoff = now - _PAUSED_TTL_SECONDS
    cur = conn.execute("DELETE FROM paused_executions WHERE updated_at < ?", (cutoff,))
    if cur.rowcount:
        logger.debug("Cleaned up %d expired paused execution(s)", cur.rowcount)
    conn.commit()
    _last_cleanup_time = now


# ── Public API ──────────────────────────────────────────────────────

def save_paused_run(
    execution_id: str,
    workflow_id: str,
    workflow: Dict[str, Any],
    state: Dict[str, Any],
) -> None:
    """Persist a paused execution, replacing any existing record."""
    with _db_lock:
        conn = _get_conn()
        try:
            now = _now()
            conn.execute(
                """
                INSERT INTO paused_executions
                    (execution_id, workflow_id, workflow_json, state_json, created_at, updated_at)
                VALUES
                    (?, ?, ?, ?, ?, ?)
                ON CONFLICT(execution_id) DO UPDATE SET
                    workflow_json = excluded.workflow_json,
                    state_json    = excluded.state_json,
                    updated_at    = excluded.updated_at
                """,
                (
                    execution_id,
                    workflow_id,
                    json.dumps(workflow, ensure_ascii=False),
                    json.dumps(state, ensure_ascii=False),
                    now,
                    now,
                ),
            )
            _maybe_cleanup_expired(conn)
            conn.commit()
        finally:
            conn.close()


def get_paused_run(execution_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a paused run by id. Returns ``None`` if not found or expired."""
    with _db_lock:
        conn = _get_conn()
        try:
            cutoff = _now() - _PAUSED_TTL_SECONDS
            row = conn.execute(
                """
                SELECT workflow_json, state_json
                FROM   paused_executions
                WHERE  execution_id = ?
                  AND  updated_at >= ?
                """,
                (execution_id, cutoff),
            ).fetchone()
            if row is None:
                return None
            return {
                "workflow": json.loads(row["workflow_json"]),
                "state": json.loads(row["state_json"]),
            }
        finally:
            conn.close()


def take_paused_run(execution_id: str) -> Optional[Dict[str, Any]]:
    """Read *and* consume a paused run in one transaction.

    A resume has to be single-use. Reading the record and then deleting it in a
    second transaction leaves a window in which two resumes — another request,
    another worker, or a user double-clicking the answer — both read the same
    record before either delete lands, and both then continue the run from the
    same node. ``BEGIN IMMEDIATE`` takes the write lock up front, so the
    winner's delete is committed before the next caller's select starts.

    Returns ``None`` when the record is absent or expired; an expired record is
    left for :func:`cleanup_expired_paused_runs` rather than removed here.
    """
    with _db_lock:
        conn = _get_conn()
        try:
            cutoff = _now() - _PAUSED_TTL_SECONDS
            conn.execute("BEGIN IMMEDIATE")
            try:
                row = conn.execute(
                    """
                    SELECT workflow_json, state_json
                    FROM   paused_executions
                    WHERE  execution_id = ?
                      AND  updated_at >= ?
                    """,
                    (execution_id, cutoff),
                ).fetchone()
                if row is None:
                    conn.rollback()
                    return None
                conn.execute(
                    "DELETE FROM paused_executions WHERE execution_id = ?",
                    (execution_id,),
                )
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            return {
                "workflow": json.loads(row["workflow_json"]),
                "state": json.loads(row["state_json"]),
            }
        finally:
            conn.close()


def cleanup_expired_paused_runs() -> int:
    """Immediately remove all expired paused runs. Returns number of rows deleted."""
    with _db_lock:
        conn = _get_conn()
        try:
            cutoff = _now() - _PAUSED_TTL_SECONDS
            cur = conn.execute(
                "DELETE FROM paused_executions WHERE updated_at < ?",
                (cutoff,),
            )
            conn.commit()
            return cur.rowcount
        finally:
            conn.close()
