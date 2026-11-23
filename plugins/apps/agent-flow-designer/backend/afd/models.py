# -*- coding: utf-8 -*-
"""Pydantic request/response models and server-owned key contract."""

from typing import Any, Optional

from pydantic import BaseModel, Field


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


class ValidateRequest(BaseModel):
    """An optional inline graph so unsaved edits can be checked too."""

    workflow: Optional[dict] = None


class CancelRequest(BaseModel):
    reason: str = ""
