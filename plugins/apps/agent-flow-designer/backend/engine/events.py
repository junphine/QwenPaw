# -*- coding: utf-8 -*-
"""Execution event model for the Agent Flow graph engine.

A ``RunEvent`` is the atomic unit emitted by node handlers as they execute.
The Runner consumes these events to drive traversal and to build the
execution trace. The same event stream powers both the synchronous
(``run_sync``) and the streaming (SSE) execution paths, which is why the
event abstraction lives at the core of the engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class EventType(str, Enum):
    """Lifecycle event types emitted during a workflow run."""

    WF_START = "wf:start"        # workflow run began
    WF_DONE = "wf:done"          # end node produced the final result
    WF_ERROR = "wf:error"        # unrecoverable error aborted the run
    WF_PAUSE = "wf:pause"        # ask node paused the run awaiting human input (HITL)
    NODE_START = "node:start"    # a node began executing
    NODE_DONE = "node:done"      # a node finished (payload['trace'] holds the trace item)
    NODE_ERROR = "node:error"    # a node failed (payload['trace'] holds a failed trace item)
    NODE_TOKEN = "node:token"    # incremental token chunk from a streaming node (payload['delta'])
    ROUTE = "route"              # router node selected a branch (payload drives successor selection)


@dataclass
class RunEvent:
    """A single event produced by a node handler.

    Attributes:
        type: The :class:`EventType`.
        node_id: The node this event relates to (empty for workflow-level events).
        payload: Arbitrary event data. For node events, ``payload['trace']``
            (when present) is a legacy-compatible trace item dict that the
            Runner appends to the execution trace in order.
    """

    type: EventType
    node_id: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)

    @property
    def trace_item(self) -> Optional[dict]:
        """Return the embedded trace item dict, if any."""
        item = self.payload.get("trace")
        return item if isinstance(item, dict) else None
