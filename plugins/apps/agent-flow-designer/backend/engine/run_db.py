# -*- coding: utf-8 -*-
"""SQLite-backed persistence for workflow execution history.

Companion to :mod:`engine.paused_db` (which owns only the HITL checkpoint) and
the storage half of the "execution history" feature: every run — synchronous,
streaming, resumed or cancelled — lands as one row in ``execution_runs`` plus
one row per traversed node in ``execution_nodes``.

Schema
------
execution_runs (one row per execution_id, updated in place on resume)
  execution_id       TEXT PRIMARY KEY
  workflow_id        TEXT NOT NULL
  owner_user_id      TEXT NOT NULL   -- every read path filters on this
  status             TEXT NOT NULL   -- running|completed|failed|cancelled|paused|expired|abandoned
  trigger_kind       TEXT NOT NULL   -- designer|api|deployed_api|resume
  workflow_version   INTEGER         -- published snapshot version, NULL for drafts
  source_text        TEXT            -- caller input, truncated + redacted
  result_text        TEXT
  error              TEXT
  trace_json         TEXT            -- same items the /execute response returns
  node_seq           INTEGER         -- next node-row sequence number
  prompt_tokens      INTEGER
  completion_tokens  INTEGER
  total_tokens       INTEGER         -- derived: sum of execution_nodes
  resumed_count      INTEGER
  started_at / finished_at / updated_at  REAL  (UTC epoch seconds)

execution_nodes (one row per node the traversal reported)
  PRIMARY KEY (execution_id, seq)    -- idempotent: re-appending a seq is a no-op

Retention
---------
Unlike a paused run (which expires after 7 days), history rows are kept for
``_RUN_TTL_SECONDS`` and additionally capped to the ``_KEEP_PER_WORKFLOW`` most
recent runs so a busy workflow cannot grow the file without bound. Both bounds
must be exceeded for a row to go: the newest ``_KEEP_PER_WORKFLOW`` runs of a
workflow are kept however old they are.

:func:`purge_expired` is the policy; :func:`engine.recorder.schedule_purge` is
the only caller, queued when a run finishes and throttled in-process, since the
plugin has no scheduler of its own.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .log_context import get_logger

logger = get_logger(__name__)

# ── Configuration ───────────────────────────────────────────────────
_RUN_TTL_SECONDS = 30 * 24 * 60 * 60    # 30 days
_KEEP_PER_WORKFLOW = 500                 # most recent runs kept regardless of age
_BUSY_RETRIES = 3

#: Every value ``execution_runs.status`` can hold. The read API validates its
#: filter against this set, so a new status cannot silently become unfilterable.
RUN_STATUSES = frozenset({
    "running", "completed", "failed", "cancelled", "paused", "expired", "abandoned",
})

_db_path: Optional[Path] = None
_db_lock = threading.Lock()


def _now() -> float:
    return datetime.now(tz=timezone.utc).timestamp()


# ── Records ─────────────────────────────────────────────────────────

@dataclass
class RunRecord:
    """One workflow execution, mutable while the run is in flight."""

    execution_id: str
    workflow_id: str
    owner_user_id: str
    status: str = "running"
    trigger_kind: str = "designer"
    workflow_version: Optional[int] = None
    source_text: str = ""
    result_text: str = ""
    error: str = ""
    trace_items: List[dict] = field(default_factory=list)
    node_seq: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    resumed_count: int = 0
    started_at: float = 0.0
    finished_at: Optional[float] = None
    updated_at: float = 0.0

    def to_row(self) -> Dict[str, Any]:
        """Flatten to storage columns (``trace_items`` becomes ``trace_json``)."""
        row = asdict(self)
        row["trace_json"] = json.dumps(self.trace_items, ensure_ascii=False)
        row.pop("trace_items")
        return row


@dataclass
class NodeRow:
    """One node's participation in one execution."""

    execution_id: str
    workflow_id: str
    seq: int
    node_id: str
    status: str = "completed"
    node_label: str = ""
    node_type: str = ""
    duration_ms: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    inputs: Any = None
    output: Any = None
    message: str = ""
    error: str = ""
    started_at: Optional[float] = None
    finished_at: Optional[float] = None

    def to_row(self) -> Dict[str, Any]:
        row = asdict(self)
        row["inputs_json"] = _dump(self.inputs)
        row["output_json"] = _dump(self.output)
        row.pop("inputs")
        row.pop("output")
        return row


def _dump(value: Any) -> Optional[str]:
    """Envelope-encode a node input/output.

    The envelope is what keeps ``"42"`` a string on the way back out: a bare
    ``json.loads`` would decode it to an int and silently change the type of a
    ``delta_*`` baseline.
    """
    if value is None:
        return None
    return json.dumps({"v": value}, ensure_ascii=False, default=str)


# ── Connection ──────────────────────────────────────────────────────

def _get_conn() -> sqlite3.Connection:
    if _db_path is None:
        raise RuntimeError("run_db.init_db() must be called before any DB operation")
    conn = sqlite3.connect(str(_db_path), check_same_thread=False, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def _write_transaction(body: Callable[[sqlite3.Connection], Any]) -> Any:
    """Run one write transaction, retrying while another writer holds the lock.

    The body is re-executed from scratch on each attempt and must therefore be
    idempotent on retry: every statement here is guarded (``INSERT OR IGNORE``
    plus a row-count check, or an ``UPDATE``/``DELETE`` whose effect is only
    recorded once the transaction commits), so a rolled-back attempt contributes
    nothing — notably no token double-counting.

    A persistent lock surfaces as the original :class:`sqlite3.OperationalError`
    rather than a wrapper: the recorder treats every storage failure the same
    way (warn and carry on), and a history of that decision belongs in the logs.
    """
    last_exc: Optional[Exception] = None
    for attempt in range(_BUSY_RETRIES):
        try:
            with _db_lock:
                conn = _get_conn()
                try:
                    conn.execute("BEGIN IMMEDIATE")
                    outcome = body(conn)
                    conn.commit()
                    return outcome
                except Exception:
                    conn.rollback()
                    raise
                finally:
                    conn.close()
        except sqlite3.OperationalError as exc:
            text = str(exc).lower()
            if "locked" not in text and "busy" not in text:
                raise
            last_exc = exc
    assert last_exc is not None
    raise last_exc


# ── Schema ──────────────────────────────────────────────────────────

_SCHEMA = (
    """
    CREATE TABLE IF NOT EXISTS execution_runs (
        execution_id       TEXT PRIMARY KEY,
        workflow_id        TEXT NOT NULL,
        owner_user_id      TEXT NOT NULL,
        status             TEXT NOT NULL,
        trigger_kind       TEXT NOT NULL DEFAULT 'designer',
        workflow_version   INTEGER,
        source_text        TEXT,
        result_text        TEXT,
        error              TEXT,
        trace_json         TEXT NOT NULL DEFAULT '[]',
        node_seq           INTEGER NOT NULL DEFAULT 0,
        prompt_tokens      INTEGER NOT NULL DEFAULT 0,
        completion_tokens  INTEGER NOT NULL DEFAULT 0,
        total_tokens       INTEGER NOT NULL DEFAULT 0,
        resumed_count      INTEGER NOT NULL DEFAULT 0,
        started_at         REAL NOT NULL,
        finished_at        REAL,
        updated_at         REAL NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_runs_wf_time ON execution_runs(workflow_id, started_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_runs_owner ON execution_runs(owner_user_id, started_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_runs_status ON execution_runs(status)",
    """
    CREATE TABLE IF NOT EXISTS execution_nodes (
        seq                INTEGER NOT NULL,
        execution_id       TEXT NOT NULL,
        workflow_id        TEXT NOT NULL,
        node_id            TEXT NOT NULL,
        node_label         TEXT,
        node_type          TEXT,
        status             TEXT NOT NULL,
        duration_ms        INTEGER NOT NULL DEFAULT 0,
        prompt_tokens      INTEGER NOT NULL DEFAULT 0,
        completion_tokens  INTEGER NOT NULL DEFAULT 0,
        total_tokens       INTEGER NOT NULL DEFAULT 0,
        inputs_json        TEXT,
        output_json        TEXT,
        message            TEXT,
        error              TEXT,
        started_at         REAL,
        finished_at        REAL,
        PRIMARY KEY (execution_id, seq)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_nodes_wf_node ON execution_nodes(workflow_id, node_id, finished_at DESC)",
)


def init_db(db_path: Path) -> None:
    """Create the DB file, schema and indexes if they don't exist."""
    global _db_path
    _db_path = Path(db_path)
    _db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = _get_conn()
    try:
        for statement in _SCHEMA:
            conn.execute(statement)
        conn.commit()
    finally:
        conn.close()
    logger.info("AFD execution-history DB initialised at %s", _db_path)


# ── Writes ──────────────────────────────────────────────────────────

_NODE_COLUMNS = (
    "seq", "execution_id", "workflow_id", "node_id", "node_label", "node_type",
    "status", "duration_ms", "prompt_tokens", "completion_tokens", "total_tokens",
    "inputs_json", "output_json", "message", "error", "started_at", "finished_at",
)

#: Accumulator columns: written only by :func:`append_node`, never by a run update.
_TOKEN_COLUMNS = frozenset({"prompt_tokens", "completion_tokens", "total_tokens"})


def append_node(node: NodeRow) -> bool:
    """Insert one node row and roll its tokens into the parent run.

    Idempotent per ``(execution_id, seq)``: a re-delivered sequence number is
    dropped together with its token contribution, so a resumed run replaying
    its stored trace cannot double-count. Returns ``True`` when the row landed.
    Raises ``KeyError`` when the parent run is unknown — that is always a
    recorder bug, and silently losing history is worse.
    """
    row = node.to_row()
    placeholders = ", ".join("?" for _ in _NODE_COLUMNS)

    def _body(conn: sqlite3.Connection) -> bool:
        cur = conn.execute(
            f"INSERT OR IGNORE INTO execution_nodes ({', '.join(_NODE_COLUMNS)}) "
            f"VALUES ({placeholders})",
            tuple(row[c] for c in _NODE_COLUMNS),
        )
        if not cur.rowcount:
            return False
        updated = conn.execute(
            """
            UPDATE execution_runs
            SET prompt_tokens     = prompt_tokens + ?,
                completion_tokens = completion_tokens + ?,
                total_tokens      = total_tokens + ?
            WHERE execution_id = ?
            """,
            (node.prompt_tokens, node.completion_tokens, node.total_tokens,
             node.execution_id),
        )
        if not updated.rowcount:
            raise KeyError(f"unknown execution_id for node row: {node.execution_id}")
        return True

    return _write_transaction(_body)


def upsert_run(record: RunRecord) -> None:
    """Insert or update a run, keyed by ``execution_id`` so resumes stay one row."""
    # An explicit updated_at is honoured (the recorder always leaves it unset);
    # retention is judged on this column, so tests must be able to age a row.
    record.updated_at = record.updated_at or _now()
    row = record.to_row()
    columns = [
        "execution_id", "workflow_id", "owner_user_id", "status", "trigger_kind",
        "workflow_version", "source_text", "result_text", "error", "trace_json",
        "node_seq", "prompt_tokens", "completion_tokens", "total_tokens",
        "resumed_count", "started_at", "finished_at", "updated_at",
    ]
    updates = [c for c in columns if c != "execution_id" and c not in _TOKEN_COLUMNS]
    # The token columns stay out of the update list on purpose. They are
    # accumulators that append_node rolls up from the node rows, while a run
    # row carries its own (zero) copy — so an upsert that wrote them back would
    # erase a finished run's whole usage, and a resumed run's usage from before
    # the pause.
    sql = (
        f"INSERT INTO execution_runs ({', '.join(columns)}) "
        f"VALUES ({', '.join('?' for _ in columns)}) "
        f"ON CONFLICT(execution_id) DO UPDATE SET "
        f"{', '.join(f'{c} = excluded.{c}' for c in updates)}"
    )
    params = tuple(row[c] for c in columns)
    _write_transaction(lambda conn: conn.execute(sql, params))


def purge_expired(
    *,
    now: Optional[float] = None,
    ttl_seconds: float = _RUN_TTL_SECONDS,
    keep_per_workflow: int = _KEEP_PER_WORKFLOW,
) -> int:
    """Drop old history. Returns the number of run rows deleted.

    Two independent rules, both deliberately conservative, and they **intersect**:
    a run is dropped only when it is past the TTL *and* outside the newest
    ``keep_per_workflow`` for its workflow. Also:

    * ``running`` and ``paused`` rows are never candidates — a paused run still
      has a live HITL checkpoint, and deleting its history would make an
      in-flight resume unreportable;
    * the recency guard is absolute, so a workflow that has not been exercised
      recently still keeps what it has.
    """
    now = _now() if now is None else now
    cutoff = now - ttl_seconds
    terminal = ("completed", "failed", "cancelled", "expired", "abandoned")
    placeholders = ", ".join("?" for _ in terminal)
    def _body(conn: sqlite3.Connection) -> int:
        expired = {
            r["execution_id"]
            for r in conn.execute(
                f"SELECT execution_id FROM execution_runs "
                f"WHERE status IN ({placeholders}) AND updated_at < ?",
                (*terminal, cutoff),
            ).fetchall()
        }
        workflows = [
            r["workflow_id"]
            for r in conn.execute(
                "SELECT DISTINCT workflow_id FROM execution_runs"
            ).fetchall()
        ]
        protected: set = set()
        for workflow_id in workflows:
            rows = conn.execute(
                f"SELECT execution_id FROM execution_runs "
                f"WHERE workflow_id = ? AND status IN ({placeholders}) "
                f"ORDER BY started_at DESC",
                (workflow_id, *terminal),
            ).fetchall()
            protected.update(r["execution_id"] for r in rows[:keep_per_workflow])
        doomed = tuple(expired - protected)
        if not doomed:
            return 0
        marks = ", ".join("?" for _ in doomed)
        conn.execute(f"DELETE FROM execution_nodes WHERE execution_id IN ({marks})", doomed)
        conn.execute(f"DELETE FROM execution_runs WHERE execution_id IN ({marks})", doomed)
        logger.debug("Purged %d expired execution run(s)", len(doomed))
        return len(doomed)

    return _write_transaction(_body)


# ── Reads ───────────────────────────────────────────────────────────

def list_nodes(execution_id: str, owner_user_id: str) -> List[Dict[str, Any]]:
    """Node rows of one run in traversal order, scoped to the owner.

    ``inputs_json`` / ``output_json`` are returned decoded as ``inputs`` /
    ``output``: the detail view should not have to know about the envelope.
    """
    conn = _get_conn()
    try:
        rows = conn.execute(
            """
            SELECT n.* FROM execution_nodes n
            JOIN execution_runs r ON r.execution_id = n.execution_id
            WHERE n.execution_id = ? AND r.owner_user_id = ?
            ORDER BY n.seq
            """,
            (execution_id, owner_user_id),
        ).fetchall()
        return [_decode_node(dict(r)) for r in rows]
    finally:
        conn.close()


def _decode_node(row: Dict[str, Any]) -> Dict[str, Any]:
    row["inputs"] = _load(row.pop("inputs_json", None))
    row["output"] = _load(row.pop("output_json", None))
    return row


def query_last_node_output(
    workflow_id: str,
    node_id: str,
    *,
    exclude_execution_id: str,
    owner_user_id: str,
) -> Any:
    """Baseline for the ``delta_*`` / ``change_rate_*`` router operators.

    Answers "what did this node produce the last time this workflow finished?"
    Two constraints make that question well-defined, and both are load-bearing:

    * the **run** must be in a terminal state — a sibling run that is still
      ``running`` or ``paused`` has not produced a comparable result;
    * the **node row** must be ``completed`` — a ``skipped`` branch has no
      output, and a ``failed`` one has a partial one.

    Pass the *current* ``execution_id`` as ``exclude_execution_id`` so a resume
    does not read the pre-pause output of the very run it is continuing.
    Returns ``None`` when there is no such run: the caller must then report the
    missing baseline instead of comparing against zero.
    """
    conn = _get_conn()
    try:
        row = conn.execute(
            """
            SELECT n.output_json FROM execution_nodes n
            JOIN execution_runs r ON r.execution_id = n.execution_id
            WHERE n.workflow_id = ?
              AND n.node_id = ?
              AND r.owner_user_id = ?
              AND r.status IN ('completed', 'failed', 'cancelled', 'expired', 'abandoned')
              AND n.status = 'completed'
              AND n.execution_id <> ?
            ORDER BY COALESCE(r.finished_at, r.started_at) DESC, n.finished_at DESC, n.seq DESC
            LIMIT 1
            """,
            (workflow_id, node_id, owner_user_id, exclude_execution_id),
        ).fetchone()
        if row is None:
            return None
        return _load(row["output_json"])
    finally:
        conn.close()


def _load(raw: Optional[str]) -> Any:
    """Inverse of :func:`_dump`; tolerates a legacy bare-JSON column."""
    if raw is None:
        return None
    try:
        parsed = json.loads(raw)
    except (TypeError, ValueError):
        return raw
    if isinstance(parsed, dict) and set(parsed) == {"v"}:
        return parsed["v"]
    return parsed


def get_run(execution_id: str, owner_user_id: str) -> Optional[Dict[str, Any]]:
    """Fetch one run. Returns ``None`` when it does not exist or is not yours."""
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM execution_runs WHERE execution_id = ? AND owner_user_id = ?",
            (execution_id, owner_user_id),
        ).fetchone()
        if row is None:
            return None
        run = dict(row)
        run["trace_items"] = _load(run.pop("trace_json")) or []
        return run
    finally:
        conn.close()


def list_runs(
    workflow_id: str,
    owner_user_id: str,
    *,
    limit: int = 20,
    offset: int = 0,
    status: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Most recent runs for one workflow, scoped to the owner.

    ``trace_json`` is deliberately not selected: a list page must not pull every
    run's full trace through the response. :func:`get_run` carries it.
    """
    conn = _get_conn()
    try:
        sql = (
            "SELECT execution_id, workflow_id, owner_user_id, status, trigger_kind, "
            "workflow_version, source_text, result_text, error, node_seq, "
            "prompt_tokens, completion_tokens, total_tokens, resumed_count, "
            "started_at, finished_at, updated_at "
            "FROM execution_runs WHERE workflow_id = ? AND owner_user_id = ?"
        )
        params: List[Any] = [workflow_id, owner_user_id]
        if status:
            sql += " AND status = ?"
            params.append(status)
        sql += " ORDER BY started_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        return [dict(r) for r in conn.execute(sql, tuple(params)).fetchall()]
    finally:
        conn.close()
