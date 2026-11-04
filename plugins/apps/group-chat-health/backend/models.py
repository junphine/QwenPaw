# -*- coding: utf-8 -*-
"""Pydantic models for the generic group-chat plugin."""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator

from .constants import DEFAULT_CHAT_NAME


class GroupChatStatus(str, Enum):
    """Lifecycle status for a group chat."""

    ACTIVE = "active"
    ARCHIVED = "archived"


class AgentInfo(BaseModel):
    """QwenPaw agent metadata returned to the frontend."""

    id: str
    name: str
    description: str = ""
    avatar: str = ""
    mention: str = ""


class Attachment(BaseModel):
    """Uploaded attachment metadata."""

    id: str
    filename: str
    mime_type: str
    size: int
    url: str
    thumbnail_url: Optional[str] = None
    extracted_text: Optional[str] = Field(default=None, exclude=True)


class MessageQuote(BaseModel):
    """Snapshot of the message being quoted."""

    message_id: str
    role: str
    speaker: str
    content: str
    agent_id: Optional[str] = None


class GroupChat(BaseModel):
    """Group chat instance."""

    id: str
    name: str = DEFAULT_CHAT_NAME
    agent_ids: list[str]
    status: GroupChatStatus = GroupChatStatus.ACTIVE
    proactive_enabled: bool = False
    proactive_quiet_start: int = 21
    proactive_quiet_end: int = 8
    proactive_daily_limit: int = 2
    created_at: float
    updated_at: float


class GroupChatMessage(BaseModel):
    """A message inside a group chat."""

    id: str
    group_chat_id: str
    role: str
    content: str
    quote: Optional[MessageQuote] = None
    attachments: list[Attachment] = Field(default_factory=list)
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    mentioned_agent_id: Optional[str] = None
    mentioned_agent_ids: list[str] = Field(default_factory=list)
    mentioned_by: Optional[str] = None
    routed_by: Optional[str] = None
    proactive: bool = False
    timestamp: float


class CreateGroupChatRequest(BaseModel):
    """Create a new group chat."""

    name: str = DEFAULT_CHAT_NAME
    agent_ids: list[str] = Field(min_length=1)


class UpdateAgentsRequest(BaseModel):
    """Update group chat members."""

    agent_ids: list[str] = Field(min_length=1)


class SendMessageRequest(BaseModel):
    """Send a message to a group chat."""

    content: str = Field(max_length=8000)
    mentioned_agent_id: Optional[str] = None
    mentioned_agent_ids: list[str] = Field(default_factory=list)
    quote_message_id: Optional[str] = None
    attachment_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def normalize_mentions(self) -> "SendMessageRequest":
        """Keep the legacy single target while supporting ordered mentions."""

        normalized: list[str] = []
        for agent_id in [self.mentioned_agent_id, *self.mentioned_agent_ids]:
            if agent_id and agent_id not in normalized:
                normalized.append(agent_id)
        self.mentioned_agent_ids = normalized
        self.mentioned_agent_id = normalized[0] if normalized else None
        return self


class RouteDecision(BaseModel):
    """Router decision output."""

    target_agent_id: Optional[str] = None
    target_agent_ids: list[str] = Field(default_factory=list)
    reason: str
    confidence: float = Field(default=0.0, ge=0, le=1)

    @model_validator(mode="after")
    def normalize_targets(self) -> "RouteDecision":
        """Accept single-target and multi-target router outputs."""

        normalized: list[str] = []
        for agent_id in self.target_agent_ids:
            if agent_id and agent_id not in normalized:
                normalized.append(agent_id)
        if self.target_agent_id and self.target_agent_id not in normalized:
            normalized.insert(0, self.target_agent_id)
        self.target_agent_ids = normalized
        if not self.target_agent_id and normalized:
            self.target_agent_id = normalized[0]
        return self


class ProactiveState(BaseModel):
    """Per-chat proactive push state."""

    group_chat_id: str
    daily_push_count: int = 0
    daily_reset_date: str = ""
    last_push_at: Optional[float] = None
    last_user_message_at: Optional[float] = None
    triggered_slots_today: set[str] = Field(default_factory=set)


class ProactivePollResult(BaseModel):
    """Single advisor proactive poll result."""

    agent_id: str
    should_push: bool
    message: Optional[str] = None
    reason: str = ""


class ProactiveSettingsRequest(BaseModel):
    """Update proactive push settings."""

    enabled: bool
    quiet_start: Optional[int] = Field(default=None, ge=0, le=23)
    quiet_end: Optional[int] = Field(default=None, ge=0, le=23)
    daily_limit: Optional[int] = Field(default=None, ge=0, le=10)


class ChatDetailResponse(BaseModel):
    """Group chat detail plus messages."""

    chat: GroupChat
    messages: list[GroupChatMessage]


class SSEEvent(BaseModel):
    """Server-Sent Event payload shape."""

    type: str
    content: Optional[str] = None
    message: Optional[GroupChatMessage] = None
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    from_agent_id: Optional[str] = None
    to_agent_id: Optional[str] = None
    to_agent_name: Optional[str] = None
    detail: Optional[str] = None
    turn_id: Optional[str] = None
    source_message_id: Optional[str] = None
    recoverable: Optional[bool] = None
    data: Optional[dict[str, Any]] = None
