# -*- coding: utf-8 -*-
"""Execution state carried through a workflow run.

``ExecutionState`` consolidates the per-run data that used to be scattered as
local variables inside the old BFS loop (context, node outputs, output
history, per-node status, accumulated trace). Centralizing it makes the state
serializable, which is the prerequisite for checkpointing, resume (HITL) and
streaming — all of which are layered on top of this skeleton without changing
the synchronous execution contract.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ExecutionState:
    """Mutable state for one workflow execution."""

    execution_id: str
    workflow_id: str
    status: str = "running"                       # running | completed | failed | paused
    context: Dict[str, Any] = field(default_factory=dict)
    node_outputs: Dict[str, Any] = field(default_factory=dict)
    node_outputs_history: Dict[str, list] = field(default_factory=dict)
    node_status: Dict[str, str] = field(default_factory=dict)
    #  node -> running/completed/failed/skipped
    trace_items: List[dict] = field(default_factory=list)
    result: str = ""
    error: str = ""
    reached_end: bool = False
    pending_pause: Optional[Dict[str, Any]] = None  # reserved for HITL resume

    def to_json(self) -> Dict[str, Any]:
        """Serialize to a plain dict (used for future checkpointing)."""
        return asdict(self)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "ExecutionState":
        """Reconstruct from a dict, tolerating missing/extra keys."""
        known = {f for f in cls.__dataclass_fields__}  # type: ignore[attr-defined]
        safe = {k: v for k, v in (data or {}).items() if k in known}
        return cls(**safe)
