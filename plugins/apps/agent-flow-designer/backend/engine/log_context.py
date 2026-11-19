# -*- coding: utf-8 -*-
"""Execution-scoped log context.

The plugin writes into a log file shared by every user and every workflow. Two
lines that both read ``[Router LLM] node_id=router-1`` are indistinguishable
there, which is what makes a failed run unreadable after the fact: this module
puts the run's own ``execution_id`` in front of every line emitted while that
run is on the current task.

Design notes:

* The id lives in a :class:`~contextvars.ContextVar`, not a global, because
  concurrent runs are separate asyncio tasks and each task gets its own copy of
  the context. That is the whole mechanism for "this line belongs to that run".
* :func:`execution_log_scope` is bound by the traversal itself
  (``WorkflowRunner.run``), so all four execution paths get it from one place.
* A worker thread does *not* inherit the context, so anything handed to the
  history writer carries its id explicitly (see ``recorder._WriteWorker``).
* Tagging happens on the originating logger via a ``logging.Filter``, because
  the host owns the formatters and the file handler — the plugin can only
  influence the message it hands over.
"""

from __future__ import annotations

import contextlib
import logging
from contextvars import ContextVar
from typing import Iterator

#: Empty means "no execution is running on this task" — the default, and the
#: state every log line outside a run is expected to be in.
_current_execution_id: ContextVar[str] = ContextVar("afd_execution_id", default="")


def current_execution_id() -> str:
    """The execution id bound on this task, or ``""`` outside a run."""
    return _current_execution_id.get()


@contextlib.contextmanager
def execution_log_scope(execution_id: str) -> Iterator[str]:
    """Tag log records made on this task with ``execution_id``.

    Restores the previous binding on exit — including when the body raises and
    when an SSE consumer abandons the generator (``GeneratorExit`` runs through
    the ``finally``).
    """
    token = _current_execution_id.set(execution_id or "")
    try:
        yield execution_id
    finally:
        _current_execution_id.reset(token)


class _ExecutionIdFilter(logging.Filter):
    """Prefix the message with ``[exec=<id>]`` while a run is bound.

    The prefix carries no ``%``, so the record's ``args`` stay aligned. A
    marker attribute keeps a record that reaches a second tagged logger (or a
    reloaded plugin) from being prefixed twice.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        execution_id = _current_execution_id.get()
        if execution_id and not getattr(record, "_afd_exec_tagged", False):
            record.msg = f"[exec={execution_id}] {record.msg}"
            record._afd_exec_tagged = True
        return True


def install_execution_filter(logger: logging.Logger) -> logging.Logger:
    """Attach the tagger to ``logger``. Idempotent, so plugin reloads are safe."""
    for existing in logger.filters:
        if isinstance(existing, _ExecutionIdFilter):
            return logger
    logger.addFilter(_ExecutionIdFilter())
    return logger


def get_logger(name: str) -> logging.Logger:
    """A module logger whose records are tagged while an execution is running.

    Filters only ever run on the *originating* logger, so each plugin module
    needs its own; going through here is what makes that a one-line convention.
    """
    return install_execution_filter(logging.getLogger(name))
