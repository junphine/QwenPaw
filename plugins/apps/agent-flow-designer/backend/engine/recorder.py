# -*- coding: utf-8 -*-
"""Project a live traversal into the execution-history tables.

:class:`RunRecorder` is the writer half of the execution-history feature;
:mod:`engine.run_db` is the storage half. One recorder belongs to one
execution and is driven by :meth:`engine.runner.WorkflowRunner.run` — the single
choke point every execution path goes through:

  * ``run_workflow_sync`` / ``resume_workflow_sync`` (JSON contract)
  * ``_stream_events`` for both the fresh and the resumed SSE path

The runner calls :meth:`begin` before its first event, :meth:`observe` between
events and :meth:`finish` from a ``finally`` around its own ``yield``. That
placement is what covers the two abnormal exits: a run stopped between nodes is
``cancelled`` by the traversal itself, and an SSE consumer that goes away closes
the runner's generator, which raises ``GeneratorExit`` at its yield and lands in
the same ``finally`` — recorded as ``abandoned``.

The bracket cannot live in a generator *wrapped around* the runner's: closing an
async generator does not propagate to the generators it iterates, so a nested
bracket would leave the run stuck as ``running`` until garbage collection.

Two properties are load-bearing:

* **Never break a run.** Storage is a side effect: every write is submitted to
  one serialized worker and any failure is a warning, not an exception. A
  locked or corrupt history file must not turn a successful workflow into a
  failed request.
* **Never block the event loop.** Writes run on that worker, so the traversal
  does not wait on SQLite. :meth:`RunRecorder.finish` waits a bounded time for
  the queue to drain, which keeps a run's own history durable by the moment its
  response returns without letting contention stall the server.
"""

from __future__ import annotations

import queue
import re
import threading
from dataclasses import dataclass
from typing import Any, Callable, Optional

from . import run_db
from .log_context import (
    current_execution_id,
    execution_log_scope,
    get_logger,
)
from .state import ExecutionState

logger = get_logger(__name__)

#: Statuses that close a run: ``finished_at`` is set for these and only these.
_TERMINAL_STATUSES = frozenset(
    {"completed", "failed", "cancelled", "expired", "abandoned"}
)

#: How long :meth:`RunRecorder.finish` waits for pending writes to land.
_FLUSH_TIMEOUT_SECONDS = 5.0

#: Longest a stored text field may get. History is read from a drawer in a
#: browser; one node emitting a megabyte is not worth the file.
_MAX_FIELD_CHARS = 4_000

_REDACTED = "***"

#: Minimum distance between two retention passes. Sweeping is a full scan of
#: ``execution_runs``, so it belongs on the calendar rather than on a run
#: boundary: the TTL it enforces is measured in days.
_PURGE_MIN_INTERVAL_SECONDS = 3_600.0

#: When the last sweep was queued, or ``None`` until the first run of the
#: process asks for one. Module state, because one writer thread serves every
#: run and a desktop host may stay up for weeks without a restart.
_last_purge_at: Optional[float] = None

#: Credentials that must never reach the file. Matched by shape rather than by
#: field name because a token arrives inside a tool's output, where no schema
#: predicts it. Masked on write: once it is on disk it is out of the owner's
#: control, and the history file carries no per-viewer scope of its own.
_SECRET_PATTERNS = (
    re.compile(
        r"-----BEGIN[A-Z ]*PRIVATE KEY-----.*?-----END[A-Z ]*PRIVATE KEY-----",
        re.DOTALL,
    ),
    re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]+"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(
        r"(?i)\b(?:authorization|x-api-key|api[_-]?key|access[_-]?key|"
        r"secret|password|token)\b\s*[=:]\s*[^\s,;\"']{6,}"
    ),
    re.compile(r"(?i)\b[a-z][a-z0-9+.-]*://[^\s/@:]+:[^\s@]+@"),
)


def _redact_text(value: str) -> str:
    for pattern in _SECRET_PATTERNS:
        value = pattern.sub(_REDACTED, value)
    return value if len(value) <= _MAX_FIELD_CHARS else value[:_MAX_FIELD_CHARS] + "…"


def _scrub(value: Any) -> Any:
    """Redact and bound every string in a JSON-ish value, rebuilding containers.

    Returning new dicts and lists is deliberate: the trace items being stored
    are the same objects the response payload is built from, and the owner is
    still entitled to read their own run's real output in the response.
    """
    if isinstance(value, str):
        return _redact_text(value)
    if isinstance(value, dict):
        return {key: _scrub(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_scrub(item) for item in value]
    return value


@dataclass
class RunMeta:
    """What the API layer knows and the engine cannot derive.

    ``owner_user_id`` is the authenticated principal, not a request field: every
    read path in :mod:`run_db` filters on it, so a run recorded under the wrong
    owner is invisible to the person who ran it — and visible to someone else.
    """

    owner_user_id: str
    trigger_kind: str = "designer"
    workflow_version: Optional[int] = None
    source_text: str = ""


class _Marker:
    """Sentinel carrying a flush signal to the worker."""

    __slots__ = ("done",)

    def __init__(self) -> None:
        self.done = threading.Event()


class _WriteWorker:
    """One daemon thread draining every history write, in submission order."""

    def __init__(self) -> None:
        self._tasks: "queue.SimpleQueue" = queue.SimpleQueue()
        self._thread = threading.Thread(
            target=self._loop, name="afd-history-writer", daemon=True
        )
        self._started = False
        self._start_lock = threading.Lock()

    def submit(self, task: Callable[[], Any]) -> None:
        if not self._started:
            with self._start_lock:
                if not self._started:
                    self._started = True
                    self._thread.start()
        self._tasks.put((task, current_execution_id()))

    def flush(self, timeout: float) -> bool:
        marker = _Marker()
        self.submit(lambda: marker.done.set())
        return marker.done.wait(timeout)

    def _loop(self) -> None:
        while True:
            task, execution_id = self._tasks.get()
            # A thread starts with an empty context, so the run that queued this
            # write comes in with the item: "the history write failed" is the one
            # line that has to say which run it failed for.
            with execution_log_scope(execution_id):
                try:
                    task()
                except Exception as exc:  # noqa: BLE001  (history must never break a run)
                    logger.warning("AFD execution-history write failed: %s", exc)


_worker = _WriteWorker()


def flush_history(timeout: float = _FLUSH_TIMEOUT_SECONDS) -> bool:
    """Block until every submitted history write has landed. ``False`` on timeout."""
    return _worker.flush(timeout)


def schedule_purge() -> bool:
    """Queue one history retention pass, at most once per interval.

    :func:`run_db.purge_expired` has owned the policy — ``_RUN_TTL_SECONDS`` old,
    with a floor of ``_KEEP_PER_WORKFLOW`` newest runs per workflow — since the
    table existed, but nothing ever reached for it: the plugin owns no scheduler,
    and no other code path calls it. So the history file grew without bound while
    every release note described a limit that was in fact never applied.

    A run finishing is the moment the process reliably has. The sweep is queued
    with the policy's own defaults, so applying it cannot silently change it.
    Returns ``True`` when a pass was queued; because it rides the writer thread
    *after* the drain, it can never delay a caller waiting on
    :meth:`RunRecorder.finish`.
    """
    global _last_purge_at

    now = run_db._now()
    if _last_purge_at is not None and now - _last_purge_at < _PURGE_MIN_INTERVAL_SECONDS:
        return False
    _last_purge_at = now
    _worker.submit(lambda: run_db.purge_expired())
    return True


def _token_count(trace: dict, key: str) -> int:
    """Read one usage counter off a trace item.

    Unparsable or negative values become ``0``: these numbers arrive on a host
    event and feed an additive roll-up, so a malformed one must not be able to
    subtract another node's usage or break the write.
    """
    try:
        return max(int(trace.get(key) or 0), 0)
    except (TypeError, ValueError):
        return 0


class RunRecorder:
    """Records one execution into ``execution_runs`` / ``execution_nodes``."""

    def __init__(
        self,
        state: ExecutionState,
        workflow_id: str,
        meta: RunMeta,
    ) -> None:
        self.state = state
        self.workflow_id = workflow_id
        self.meta = meta
        self._record: Optional[run_db.RunRecord] = None
        #: How many trace items have already been written as node rows. Seeded
        #: from the stored row so a resumed run continues the sequence instead
        #: of re-writing the pre-pause nodes.
        self._written = 0

    # ── Lifecycle ───────────────────────────────────────────────────

    def observe(self) -> None:
        """Persist any trace item the traversal has appended since the last call.

        Called between events, so a run that is still going — or one that dies
        with the process — leaves readable detail instead of an empty row.
        """
        self._flush_nodes()

    def begin(self) -> None:
        """Open the run's row so a crashed or abandoned run is still visible."""
        # A resume re-enters through this same call, so everything that *identifies*
        # the run — when it started, what was asked, which published snapshot it
        # runs on, how it was triggered — is taken from the stored row and never
        # from the answer that resumed it.
        prior = self._read_prior() or {}
        now = run_db._now()
        record = run_db.RunRecord(
            execution_id=self.state.execution_id,
            workflow_id=self.workflow_id,
            owner_user_id=self.meta.owner_user_id,
            status="running",
            trigger_kind=prior.get("trigger_kind") or self.meta.trigger_kind,
            workflow_version=prior.get("workflow_version") or self.meta.workflow_version,
            source_text=_redact_text(prior.get("source_text") or self.meta.source_text),
            started_at=prior.get("started_at") or now,
            resumed_count=prior.get("resumed_count", 0) + (1 if prior else 0),
        )
        self._record = record
        self._written = min(prior.get("node_seq", 0), len(self.state.trace_items))
        self._submit(lambda: run_db.upsert_run(record))

    def finish(self) -> None:
        """Close the run and wait a bounded time for its writes to land."""
        if self._record is None:  # begin() never ran — nothing to close
            return
        self._flush_nodes()
        record = self._record
        status = self.state.status
        if status == "running":
            # The traversal stopped without producing an outcome: the only way
            # through the bracket's finally without a terminal state.
            status = "abandoned"
        record.status = status
        record.result_text = _redact_text(self.state.result)
        record.error = _redact_text(self.state.error)
        record.trace_items = _scrub(list(self.state.trace_items))
        record.node_seq = self._written
        record.finished_at = run_db._now() if status in _TERMINAL_STATUSES else None
        self._submit(lambda: run_db.upsert_run(record))
        if not flush_history():
            logger.warning(
                "AFD execution-history writes for %s did not drain within %.1fs",
                record.execution_id,
                _FLUSH_TIMEOUT_SECONDS,
            )
        # After the drain, never before it: this run's own rows are already safe,
        # and a retention pass must not sit in front of anyone's flush.
        schedule_purge()

    # ── Internals ───────────────────────────────────────────────────

    def _flush_nodes(self) -> None:
        """Write detail rows for every trace item not yet persisted.

        ``state.trace_items`` is the source rather than the node events: it is
        the traversal's own ordered record of participation, so it also holds
        the two kinds of node no event stream would produce — a ``skipped`` node
        and the ask node, whose trace item is appended by ``prepare_resume``
        after the paused run was already written.
        """
        record = self._record
        if record is None:
            return
        items = self.state.trace_items
        while self._written < len(items):
            index = self._written
            self._written = index + 1
            node = self._node_row(items[index], self._written)
            self._submit(lambda row=node: run_db.append_node(row))

    def _node_row(self, item: Any, seq: int) -> run_db.NodeRow:
        trace = item if isinstance(item, dict) else {}
        duration_ms = int(trace.get("durationMs") or 0)
        now = run_db._now()
        prompt_tokens = _token_count(trace, "promptTokens")
        completion_tokens = _token_count(trace, "completionTokens")
        # A host turn_usage event always carries the sum, but a caller-shaped
        # trace item may report only the two halves.
        total_tokens = _token_count(trace, "totalTokens") or (
            prompt_tokens + completion_tokens
        )
        return run_db.NodeRow(
            execution_id=self.state.execution_id,
            workflow_id=self.workflow_id,
            seq=seq,
            node_id=str(trace.get("nodeId", "")),
            status=str(trace.get("status") or "completed"),
            node_label=str(trace.get("nodeLabel", "")),
            node_type=str(trace.get("type", "")),
            duration_ms=duration_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            inputs=_scrub(trace.get("inputs")),
            output=_scrub(trace.get("output")),
            message=_redact_text(str(trace.get("message", ""))),
            error=_redact_text(str(trace.get("error", ""))),
            started_at=now - duration_ms / 1000,
            finished_at=now,
        )

    def _read_prior(self) -> Optional[dict]:
        """Existing row for this execution id, i.e. this traversal is a resume."""
        try:
            return run_db.get_run(self.state.execution_id, self.meta.owner_user_id)
        except Exception as exc:  # noqa: BLE001
            logger.warning("AFD execution-history read failed: %s", exc)
            return None

    @staticmethod
    def _submit(task: Callable[[], Any]) -> None:
        try:
            _worker.submit(task)
        except Exception as exc:  # noqa: BLE001  (a dead queue must not kill a run)
            logger.warning("AFD execution-history write could not be queued: %s", exc)
