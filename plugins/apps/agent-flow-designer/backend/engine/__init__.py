# -*- coding: utf-8 -*-
"""Agent Flow graph execution engine (skeleton).

Public surface:
    EventType, RunEvent           — execution event model
    ExecutionState                — serializable per-run state
    NodeRunContext, register_node, get_handler, registered_types — node registry
    WorkflowRunner(workflow, state, cancel_check=None, services=None),
    run_workflow_sync, assemble_final_result     — traversal + sync facade
    get_logger, execution_log_scope, current_execution_id — execution-scoped logs

``services`` is the channel for live host handles a tool node needs (workspace,
local_workspace, driver_manager, agent config, identity). It is passed to the
Runner per run and injected into every ``NodeRunContext``; it is deliberately
not a field of ``ExecutionState``, so it never reaches the HITL snapshot JSON.

``get_logger`` / ``execution_log_scope`` (from :mod:`engine.log_context`) tag
every record made while a run is on the current task with that run's
``execution_id``, which is what makes a failure attributable in a shared log.
"""

from __future__ import annotations

from .events import EventType, RunEvent
from .log_context import (
    current_execution_id,
    execution_log_scope,
    get_logger,
)
from .registry import NodeRunContext, get_handler, register_node, registered_types
from .retry import (
    RETRY_ENABLED_TYPES,
    RetryPolicy,
    backoff_delay,
    parse_retry_policy,
)
from .run_db import NodeRow, RunRecord
from .runner import (
    ERROR_HANDLE,
    WorkflowRunner,
    assemble_final_result,
    prepare_resume,
    resume_workflow_sync,
    run_workflow_sync,
)
from .state import ExecutionState

__all__ = [
    "EventType",
    "RunEvent",
    "ExecutionState",
    "NodeRunContext",
    "register_node",
    "get_handler",
    "registered_types",
    "RETRY_ENABLED_TYPES",
    "RetryPolicy",
    "backoff_delay",
    "parse_retry_policy",
    "WorkflowRunner",
    "ERROR_HANDLE",
    "run_workflow_sync",
    "resume_workflow_sync",
    "prepare_resume",
    "assemble_final_result",
    "RunRecord",
    "NodeRow",
    "current_execution_id",
    "execution_log_scope",
    "get_logger",
]
