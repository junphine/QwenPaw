# -*- coding: utf-8 -*-
"""Durable service for generic multi-agent group chats."""

from __future__ import annotations

import asyncio
import json
import logging
import mimetypes
import re
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, AsyncGenerator, Callable, Iterable, Optional
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from .agent_catalog import discover_available_agents
from .constants import (
    DEFAULT_CHAT_NAME,
    MAX_ATTACHMENT_BYTES,
    MAX_CHAIN_DEPTH,
    MAX_EXTRACTED_TEXT_CHARS,
    MAX_HISTORY_FOR_AGENT,
    MAX_HISTORY_FOR_ROUTER,
    ROUTER_AGENT_ID,
)
from .models import (
    AgentInfo,
    Attachment,
    CreateGroupChatRequest,
    GroupChat,
    GroupChatMessage,
    MessageQuote,
    ProactiveSettingsRequest,
    RouteDecision,
    SendMessageRequest,
)

logger = logging.getLogger("qwenpaw.group_chat")

_AGENT_SESSION_USER_ID = "group-chat-health"
_AGENT_SESSION_CHANNEL = "console"


@dataclass(frozen=True)
class _AgentTurn:
    agent_id: str
    reason: str
    current_content: str
    mentioned_by: Optional[str] = None


class GroupChatService:
    """Core group-chat service with local, atomic JSON persistence."""

    _STATE_VERSION = 1

    def __init__(
        self,
        storage_dir: Optional[Path] = None,
        agent_provider: Optional[Callable[[], list[AgentInfo]]] = None,
    ):
        self._group_chats: dict[str, GroupChat] = {}
        self._messages: dict[str, list[GroupChatMessage]] = {}
        self._attachments: dict[str, Attachment] = {}
        self._attachment_paths: dict[str, Path] = {}
        self._subscribers: dict[str, set[asyncio.Queue[dict]]] = {}
        self._proactive_logs: dict[str, list[dict]] = {}
        self._lock = asyncio.Lock()
        self._agent_provider = agent_provider or discover_available_agents
        self._storage_dir = storage_dir or self._resolve_storage_dir()
        self._attachments_dir = self._storage_dir / "attachments"
        try:
            self._attachments_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            fallback = (
                Path(tempfile.gettempdir()) / "qwenpaw-group-chat-health"
            )
            logger.warning(
                "Cannot create group-chat storage at %s (%s); using %s",
                self._storage_dir,
                exc,
                fallback,
            )
            self._storage_dir = fallback
            self._attachments_dir = fallback / "attachments"
            self._attachments_dir.mkdir(parents=True, exist_ok=True)
        self._state_file = self._storage_dir / "state.json"
        self._state_load_failed = False
        self._load_state()

    @staticmethod
    def _resolve_storage_dir() -> Path:
        try:
            from qwenpaw.constant import WORKING_DIR

            return Path(WORKING_DIR).expanduser() / "group_chat_health"
        except Exception:  # noqa: BLE001
            return Path.home() / ".qwenpaw" / "group_chat_health"

    def _load_state(self) -> None:
        """Restore chats and messages without making a corrupt file destructive."""

        if not self._state_file.exists():
            return
        try:
            payload = json.loads(self._state_file.read_text(encoding="utf-8"))
            if payload.get("version") != self._STATE_VERSION:
                raise ValueError("unsupported state version")

            chats = {
                item["id"]: GroupChat.model_validate(item)
                for item in payload.get("chats", [])
            }
            messages: dict[str, list[GroupChatMessage]] = {}
            for chat_id, entries in payload.get("messages", {}).items():
                if chat_id not in chats:
                    continue
                messages[chat_id] = [
                    GroupChatMessage.model_validate(item) for item in entries
                ]

            attachments: dict[str, Attachment] = {}
            attachment_paths: dict[str, Path] = {}
            file_names = payload.get("attachment_files", {})
            for item in payload.get("attachments", []):
                attachment = Attachment.model_validate(item)
                stored_name = file_names.get(attachment.id)
                if not stored_name:
                    continue
                path = self._attachments_dir / Path(stored_name).name
                if not path.exists():
                    continue
                attachments[attachment.id] = attachment
                attachment_paths[attachment.id] = path

            self._group_chats = chats
            self._messages = {
                chat_id: messages.get(chat_id, []) for chat_id in chats
            }
            self._attachments = attachments
            self._attachment_paths = attachment_paths
            self._proactive_logs = {
                chat_id: list(entries)[-100:]
                for chat_id, entries in payload.get(
                    "proactive_logs",
                    {},
                ).items()
                if chat_id in chats and isinstance(entries, list)
            }
        except Exception as exc:  # noqa: BLE001
            self._state_load_failed = True
            logger.warning(
                "Cannot load group-chat state from %s: %s",
                self._state_file,
                exc,
            )

    def _persist_state_locked(self) -> None:
        """Atomically save state. Caller must hold ``self._lock``."""

        self._storage_dir.mkdir(parents=True, exist_ok=True)
        if self._state_load_failed and self._state_file.exists():
            backup = self._state_file.with_name(
                f"state.corrupt-{int(time.time())}.json",
            )
            self._state_file.replace(backup)
            self._state_load_failed = False
            logger.warning("Preserved unreadable group-chat state at %s", backup)

        payload = {
            "version": self._STATE_VERSION,
            "chats": [
                chat.model_dump(mode="json")
                for chat in self._group_chats.values()
            ],
            "messages": {
                chat_id: [message.model_dump(mode="json") for message in items]
                for chat_id, items in self._messages.items()
            },
            "attachments": [
                attachment.model_dump(mode="json")
                for attachment in self._attachments.values()
            ],
            "attachment_files": {
                attachment_id: path.name
                for attachment_id, path in self._attachment_paths.items()
            },
            "proactive_logs": self._proactive_logs,
        }
        temp_path = self._state_file.with_suffix(".json.tmp")
        temp_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        temp_path.replace(self._state_file)

    # ── Agents ───────────────────────────────────────────────────────────

    def list_agents(self) -> list[dict]:
        """Return the current enabled QwenPaw agents."""

        return [agent.model_dump() for agent in self._available_agents()]

    def _available_agents(self) -> list[AgentInfo]:
        try:
            return self._agent_provider()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Cannot load the current agent catalog: %s", exc)
            return []

    def _agent_map(self) -> dict[str, AgentInfo]:
        return {agent.id: agent for agent in self._available_agents()}

    def get_agent_info(self, agent_id: str) -> Optional[AgentInfo]:
        """Return live metadata for one selectable agent."""

        return self._agent_map().get(agent_id)

    def _validate_agent_ids(self, agent_ids: Iterable[str]) -> list[str]:
        available = self._agent_map()
        seen: list[str] = []
        for agent_id in agent_ids:
            if agent_id not in available:
                raise HTTPException(
                    status_code=400,
                    detail=f"Agent 不存在或未启用：{agent_id}",
                )
            if agent_id not in seen:
                seen.append(agent_id)
        if not seen:
            raise HTTPException(
                status_code=400,
                detail="至少选择一位群成员",
            )
        return seen

    # ── Group chat CRUD ─────────────────────────────────────────────────

    async def create_group_chat(
        self,
        req: CreateGroupChatRequest,
    ) -> GroupChat:
        agent_ids = self._validate_agent_ids(req.agent_ids)
        now = time.time()
        chat = GroupChat(
            id=f"gch-{uuid4().hex[:12]}",
            name=req.name.strip() or DEFAULT_CHAT_NAME,
            agent_ids=agent_ids,
            created_at=now,
            updated_at=now,
        )
        async with self._lock:
            self._group_chats[chat.id] = chat
            self._messages[chat.id] = []
            self._persist_state_locked()
        return chat

    def list_group_chats(self) -> list[GroupChat]:
        return sorted(
            self._group_chats.values(),
            key=lambda c: c.updated_at,
            reverse=True,
        )

    def get_group_chat(self, group_chat_id: str) -> GroupChat:
        chat = self._group_chats.get(group_chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Group chat not found")
        return chat

    def get_messages(
        self,
        group_chat_id: str,
        limit: int = 50,
        before: Optional[str] = None,
    ) -> list[GroupChatMessage]:
        self.get_group_chat(group_chat_id)
        messages = self._messages.get(group_chat_id, [])
        if before:
            idx = next(
                (i for i, msg in enumerate(messages) if msg.id == before),
                len(messages),
            )
            messages = messages[:idx]
        if limit > 0:
            messages = messages[-limit:]
        return list(messages)

    async def update_agents(
        self,
        group_chat_id: str,
        agent_ids: list[str],
    ) -> tuple[GroupChat, Optional[GroupChatMessage]]:
        chat = self.get_group_chat(group_chat_id)
        next_agent_ids = self._validate_agent_ids(agent_ids)
        added = [
            agent_id
            for agent_id in next_agent_ids
            if agent_id not in chat.agent_ids
        ]
        removed = [
            agent_id
            for agent_id in chat.agent_ids
            if agent_id not in next_agent_ids
        ]
        now = time.time()
        updated = chat.model_copy(
            update={
                "agent_ids": next_agent_ids,
                "updated_at": now,
            },
        )
        async with self._lock:
            self._group_chats[group_chat_id] = updated
            self._persist_state_locked()

        notice: Optional[GroupChatMessage] = None
        notice_content = self._format_member_change_notice(added, removed)
        if notice_content:
            notice = GroupChatMessage(
                id=f"msg-{uuid4().hex[:12]}",
                group_chat_id=group_chat_id,
                role="system",
                content=notice_content,
                timestamp=now,
            )
            await self._append_message(notice)
            updated = self.get_group_chat(group_chat_id)
        return updated, notice

    async def delete_group_chat(self, group_chat_id: str) -> None:
        self.get_group_chat(group_chat_id)
        async with self._lock:
            self._group_chats.pop(group_chat_id, None)
            self._messages.pop(group_chat_id, None)
            self._subscribers.pop(group_chat_id, None)
            self._proactive_logs.pop(group_chat_id, None)
            self._persist_state_locked()

    async def update_proactive_settings(
        self,
        group_chat_id: str,
        req: ProactiveSettingsRequest,
    ) -> GroupChat:
        chat = self.get_group_chat(group_chat_id)
        updated = chat.model_copy(
            update={
                "proactive_enabled": req.enabled,
                "proactive_quiet_start": (
                    req.quiet_start
                    if req.quiet_start is not None
                    else chat.proactive_quiet_start
                ),
                "proactive_quiet_end": (
                    req.quiet_end
                    if req.quiet_end is not None
                    else chat.proactive_quiet_end
                ),
                "proactive_daily_limit": (
                    req.daily_limit
                    if req.daily_limit is not None
                    else chat.proactive_daily_limit
                ),
                "updated_at": time.time(),
            },
        )
        async with self._lock:
            self._group_chats[group_chat_id] = updated
            self._persist_state_locked()
        return updated

    # ── Attachments ─────────────────────────────────────────────────────

    async def save_attachment(self, upload: UploadFile) -> Attachment:
        filename = Path(upload.filename or "attachment.bin").name
        suffix = Path(filename).suffix
        att_id = f"att-{uuid4().hex[:12]}"
        path = self._attachments_dir / f"{att_id}{suffix}"
        total = 0
        chunks: list[bytes] = []
        while True:
            chunk = await upload.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_ATTACHMENT_BYTES:
                raise HTTPException(
                    status_code=413,
                    detail="Attachment exceeds 20MB limit",
                )
            chunks.append(chunk)
        data = b"".join(chunks)
        path.write_bytes(data)
        mime = upload.content_type or mimetypes.guess_type(filename)[0]
        mime = mime or "application/octet-stream"
        extracted = self._extract_text(filename, mime, data)
        attachment = Attachment(
            id=att_id,
            filename=filename,
            mime_type=mime,
            size=total,
            url=f"/api/group-chat-health/attachments/{att_id}",
            thumbnail_url=(
                f"/api/group-chat-health/attachments/{att_id}"
                if mime.startswith("image/")
                else None
            ),
            extracted_text=extracted,
        )
        async with self._lock:
            self._attachments[att_id] = attachment
            self._attachment_paths[att_id] = path
            self._persist_state_locked()
        return attachment

    def get_attachment(self, attachment_id: str) -> tuple[Attachment, Path]:
        attachment = self._attachments.get(attachment_id)
        path = self._attachment_paths.get(attachment_id)
        if not attachment or not path:
            raise HTTPException(status_code=404, detail="Attachment not found")
        return attachment, path

    @staticmethod
    def _extract_text(filename: str, mime: str, data: bytes) -> Optional[str]:
        if mime.startswith("text/") or filename.lower().endswith(
            (".txt", ".csv", ".md"),
        ):
            for encoding in ("utf-8", "gb18030", "latin-1"):
                try:
                    return data.decode(encoding)[:MAX_EXTRACTED_TEXT_CHARS]
                except UnicodeDecodeError:
                    continue
        if filename.lower().endswith(".pdf"):
            return "[PDF 文档已上传。MVP 阶段仅将文件名和类型传给路由，完整解析可在后续版本接入。]"
        if filename.lower().endswith((".docx", ".doc")):
            return "[Word 文档已上传。MVP 阶段仅将文件名和类型传给路由，完整解析可在后续版本接入。]"
        return None

    # ── Messaging ───────────────────────────────────────────────────────

    async def send_message(
        self,
        group_chat_id: str,
        req: SendMessageRequest,
    ) -> AsyncGenerator[dict, None]:
        chat = self.get_group_chat(group_chat_id)
        available = self._agent_map()
        available_member_ids = [
            agent_id for agent_id in chat.agent_ids if agent_id in available
        ]
        if not available_member_ids:
            yield {
                "type": "error",
                "message": "群聊中没有可用成员，请先在群资料中更新成员",
                "recoverable": False,
            }
            return
        content = req.content.strip()
        if not content and not req.attachment_ids:
            yield {"type": "error", "message": "消息内容不能为空"}
            return

        missing_attachments = [
            attachment_id
            for attachment_id in req.attachment_ids
            if attachment_id not in self._attachments
        ]
        if missing_attachments:
            yield {
                "type": "error",
                "message": "部分附件已失效，请重新上传后发送",
            }
            return
        attachments = [
            self._attachments[a]
            for a in req.attachment_ids
        ]
        quote = self._build_quote_snapshot(group_chat_id, req.quote_message_id)
        if req.quote_message_id and not quote:
            yield {"type": "error", "message": "引用的消息不存在或不可引用"}
            return
        mentioned_agent_ids = list(req.mentioned_agent_ids)
        if not mentioned_agent_ids:
            mentioned_agent_ids = self._parse_mentions(
                content,
                available_member_ids,
            )
        mentioned_agent_ids = [
            agent_id
            for idx, agent_id in enumerate(mentioned_agent_ids)
            if agent_id and agent_id not in mentioned_agent_ids[:idx]
        ]
        if any(
            agent_id not in available_member_ids
            for agent_id in mentioned_agent_ids
        ):
            yield {
                "type": "error",
                "message": "被 @ 的 Agent 不在当前群聊中或已停用",
                "recoverable": False,
            }
            return
        mentioned_agent_id = (
            mentioned_agent_ids[0] if mentioned_agent_ids else None
        )

        user_msg = GroupChatMessage(
            id=f"msg-{uuid4().hex[:12]}",
            group_chat_id=group_chat_id,
            role="user",
            content=content,
            quote=quote,
            attachments=attachments,
            mentioned_agent_id=mentioned_agent_id,
            mentioned_agent_ids=mentioned_agent_ids,
            timestamp=time.time(),
        )
        await self._append_message(user_msg)
        yield {"type": "message", "message": user_msg.model_dump()}

        async for event in self._generate_agent_replies(
            chat,
            user_msg,
            mentioned_agent_ids,
        ):
            yield event

    async def retry_message(
        self,
        group_chat_id: str,
        message_id: str,
    ) -> AsyncGenerator[dict, None]:
        """Regenerate replies for an existing user message without duplicating it."""

        chat = self.get_group_chat(group_chat_id)
        source = next(
            (
                message
                for message in self._messages.get(group_chat_id, [])
                if message.id == message_id and message.role == "user"
            ),
            None,
        )
        if source is None:
            yield {
                "type": "error",
                "message": "待重试的消息不存在",
                "recoverable": False,
            }
            return
        mentioned_agent_ids = list(source.mentioned_agent_ids)
        if not mentioned_agent_ids and source.mentioned_agent_id:
            mentioned_agent_ids = [source.mentioned_agent_id]
        if not mentioned_agent_ids:
            mentioned_agent_ids = self._parse_mentions(
                source.content,
                chat.agent_ids,
            )
        yield {"type": "retry_started", "source_message_id": source.id}
        async for event in self._generate_agent_replies(
            chat,
            source,
            mentioned_agent_ids,
        ):
            yield event

    async def _generate_agent_replies(
        self,
        chat: GroupChat,
        source_message: GroupChatMessage,
        mentioned_agent_ids: list[str],
    ) -> AsyncGenerator[dict, None]:
        """Route one stored user message and run bounded Agent hand-offs."""

        agents = self._agent_map()
        available_member_ids = [
            agent_id for agent_id in chat.agent_ids if agent_id in agents
        ]
        if not available_member_ids:
            yield {
                "type": "error",
                "message": "群聊中没有可用成员，请先在群资料中更新成员",
                "source_message_id": source_message.id,
                "recoverable": False,
            }
            return

        unavailable_mentions = [
            agent_id
            for agent_id in mentioned_agent_ids
            if agent_id not in available_member_ids
        ]
        if unavailable_mentions:
            yield {
                "type": "error",
                "message": "被 @ 的 Agent 已停用或已从群聊移除",
                "source_message_id": source_message.id,
                "recoverable": False,
            }
            return

        pending_turns: list[_AgentTurn] = []
        if mentioned_agent_ids:
            pending_turns = [
                _AgentTurn(
                    agent_id=agent_id,
                    reason="用户直接 @ 指定",
                    current_content=source_message.content,
                    mentioned_by="user",
                )
                for agent_id in mentioned_agent_ids
            ]
        else:
            decision = await self._route_message(chat, source_message)
            pending_turns = [
                _AgentTurn(
                    agent_id=agent_id,
                    reason=decision.reason,
                    current_content=source_message.content,
                )
                for agent_id in decision.target_agent_ids
                if agent_id in available_member_ids
            ]

        visited: set[str] = set()
        chain_depth = 0
        while pending_turns and chain_depth < MAX_CHAIN_DEPTH:
            turn = pending_turns.pop(0)
            next_agent = turn.agent_id
            if next_agent in visited or next_agent not in available_member_ids:
                continue
            visited.add(next_agent)
            chain_depth += 1
            spec = agents[next_agent]
            turn_id = f"turn-{uuid4().hex[:10]}"
            yield {
                "type": "routing",
                "agent_id": spec.id,
                "agent_name": spec.name,
                "detail": turn.reason,
                "turn_id": turn_id,
                "source_message_id": source_message.id,
            }
            assistant_content = ""
            try:
                prompt = self._build_agent_prompt(
                    chat=chat,
                    target_agent_id=spec.id,
                    current_content=turn.current_content,
                    attachments=source_message.attachments,
                    reason=turn.reason,
                )
                async for chunk in self._stream_agent_reply(
                    spec.id,
                    prompt,
                    group_chat_id=chat.id,
                ):
                    assistant_content += chunk
                    yield {
                        "type": "chunk",
                        "content": chunk,
                        "turn_id": turn_id,
                        "agent_id": spec.id,
                    }
            except Exception as exc:  # noqa: BLE001
                logger.exception("Agent call failed for %s", spec.id)
                yield {
                    "type": "error",
                    "message": f"{spec.name} 调用失败：{exc}",
                    "agent_id": spec.id,
                    "agent_name": spec.name,
                    "turn_id": turn_id,
                    "source_message_id": source_message.id,
                    "recoverable": True,
                }
                return

            assistant_content = assistant_content.strip()
            if not assistant_content:
                assistant_content = f"{spec.name} 暂时没有返回内容。"

            assistant_msg = GroupChatMessage(
                id=f"msg-{uuid4().hex[:12]}",
                group_chat_id=chat.id,
                role="assistant",
                content=assistant_content,
                agent_id=spec.id,
                agent_name=spec.name,
                mentioned_by=turn.mentioned_by,
                routed_by=turn.reason,
                timestamp=time.time(),
            )
            await self._append_message(assistant_msg)
            yield {
                "type": "done",
                "message": assistant_msg.model_dump(),
                "turn_id": turn_id,
                "source_message_id": source_message.id,
            }

            pending_ids = {item.agent_id for item in pending_turns}
            for mentioned_next in self._parse_mentions(
                assistant_content,
                available_member_ids,
            ):
                if (
                    mentioned_next == spec.id
                    or mentioned_next in visited
                    or mentioned_next in pending_ids
                ):
                    continue
                next_spec = agents[mentioned_next]
                yield {
                    "type": "agent_mention",
                    "from_agent_id": spec.id,
                    "to_agent_id": next_spec.id,
                    "to_agent_name": next_spec.name,
                    "source_message_id": source_message.id,
                }
                pending_turns.append(
                    _AgentTurn(
                        agent_id=mentioned_next,
                        reason=(f"{spec.name} 在回复中 @提及了你，" "请补充你的专业意见"),
                        current_content=assistant_content,
                        mentioned_by=spec.id,
                    ),
                )
                pending_ids.add(mentioned_next)

        if pending_turns:
            yield {
                "type": "chain_stopped",
                "detail": f"已达到 {MAX_CHAIN_DEPTH} 轮协作上限",
                "source_message_id": source_message.id,
            }

    async def _append_message(self, message: GroupChatMessage) -> None:
        async with self._lock:
            self._messages.setdefault(message.group_chat_id, []).append(
                message,
            )
            chat = self._group_chats.get(message.group_chat_id)
            if chat:
                self._group_chats[message.group_chat_id] = chat.model_copy(
                    update={"updated_at": message.timestamp},
                )
            self._persist_state_locked()
        await self._publish(
            message.group_chat_id,
            {"type": "message", "message": message.model_dump()},
        )

    def _parse_mention(
        self,
        content: str,
        available_agent_ids: list[str],
    ) -> Optional[str]:
        mentions = self._parse_mentions(content, available_agent_ids)
        return mentions[0] if mentions else None

    def _parse_mentions(
        self,
        content: str,
        available_agent_ids: list[str],
    ) -> list[str]:
        agents = self._agent_map()
        aliases: dict[str, str] = {}
        for agent_id in available_agent_ids:
            spec = agents.get(agent_id)
            if spec is None:
                continue
            mention = spec.mention or spec.name or spec.id
            aliases[mention] = spec.id
            aliases[spec.id] = spec.id
        if not aliases:
            return []

        alias_pattern = "|".join(
            re.escape(alias)
            for alias in sorted(aliases, key=len, reverse=True)
        )
        pattern = re.compile(
            rf"[@＠]({alias_pattern})(?=$|[^A-Za-z0-9_-])",
        )
        mentions: list[str] = []
        for match in pattern.finditer(content):
            alias = match.group(1)
            agent_id = aliases[alias]
            if agent_id not in mentions:
                mentions.append(agent_id)
        return mentions

    def _build_quote_snapshot(
        self,
        group_chat_id: str,
        message_id: Optional[str],
    ) -> Optional[MessageQuote]:
        if not message_id:
            return None
        for msg in reversed(self._messages.get(group_chat_id, [])):
            if msg.id != message_id or msg.role == "system":
                continue
            speaker = "用户" if msg.role == "user" else (msg.agent_name or "成员")
            content = self._compact_text(msg.content, limit=160)
            if not content and msg.attachments:
                content = " ".join(
                    f"[附件:{att.filename}]" for att in msg.attachments
                )
            return MessageQuote(
                message_id=msg.id,
                role=msg.role,
                speaker=speaker,
                content=content or "(无文本内容)",
                agent_id=msg.agent_id,
            )
        return None

    async def _route_message(
        self,
        chat: GroupChat,
        message: GroupChatMessage,
    ) -> RouteDecision:
        available_ids = list(self._agent_map())
        routable_ids = [
            agent_id for agent_id in chat.agent_ids if agent_id in available_ids
        ]
        prompt = self._build_router_prompt(chat, message)
        try:
            raw = await self._call_agent_once(
                ROUTER_AGENT_ID,
                prompt,
                timeout=90,
                group_chat_id=chat.id,
            )
            parsed = self._parse_json_object(raw)
            decision = RouteDecision.model_validate(parsed)
            valid_ids: list[str] = []
            for agent_id in decision.target_agent_ids:
                if agent_id in routable_ids and agent_id not in valid_ids:
                    valid_ids.append(agent_id)
            if valid_ids:
                return decision.model_copy(
                    update={
                        "target_agent_id": valid_ids[0],
                        "target_agent_ids": valid_ids,
                    },
                )
        except Exception as exc:  # noqa: BLE001
            logger.debug("Router agent unavailable; using fallback: %s", exc)
        return self._fallback_route(routable_ids)

    @staticmethod
    def _fallback_route(available_agent_ids: list[str]) -> RouteDecision:
        if not available_agent_ids:
            raise RuntimeError("No available group-chat members")
        target_ids = [available_agent_ids[0]]
        return RouteDecision(
            target_agent_id=target_ids[0],
            target_agent_ids=target_ids,
            reason="路由 Agent 暂不可用，已交给群内首位可用成员",
            confidence=0.2,
        )

    @staticmethod
    def _parse_json_object(text: str) -> dict:
        stripped = text.strip()
        if stripped.startswith("```"):
            stripped = re.sub(r"^```(?:json)?", "", stripped).strip()
            stripped = re.sub(r"```$", "", stripped).strip()
        match = re.search(r"\{.*\}", stripped, flags=re.S)
        if match:
            stripped = match.group(0)
        return json.loads(stripped)

    def _build_router_prompt(
        self,
        chat: GroupChat,
        message: GroupChatMessage,
    ) -> str:
        agent_map = self._agent_map()
        selected = [
            agent_map[agent_id]
            for agent_id in chat.agent_ids
            if agent_id in agent_map
        ]
        agents = "\n".join(
            f"- {agent.id}（{agent.name}）: "
            f"{agent.description or '未提供角色描述'}"
            for agent in selected
        )
        history = self._format_history(
            self.get_messages(chat.id, limit=MAX_HISTORY_FOR_ROUTER),
            compact=True,
        )
        attachments = self._format_attachments(
            message.attachments,
            include_text=False,
        )
        quote = self._format_quote(message.quote)
        return f"""请分析这条群聊消息应该交给哪些群成员回复。

## 当前消息
{message.content or "(无文本消息)"}

## 附件
{attachments or "(无)"}

## 引用消息
{quote or "(无)"}

## 可选成员
{agents}

## 最近对话摘要
{history or "(无)"}

## 路由要求
- 通常选择 1 位最合适的成员。
- 当用户明确希望“大家/你们都”回复，或消息确实需要多个不同角色协作时，可以选择多位成员。
- 只能使用“可选成员”中出现的 ID，不要发明成员。
- 无法明确判断时选择最可能胜任的一位；不要为了热闹多选。
- target_agent_ids 按回复优先级排序；target_agent_id 必须等于 target_agent_ids 的第一项，用于兼容旧字段。

只输出 JSON：
{{"target_agent_ids":["agent-id"],"target_agent_id":"agent-id","reason":"简短原因","confidence":0.0}}
"""

    def _build_agent_prompt(
        self,
        chat: GroupChat,
        target_agent_id: str,
        current_content: str,
        attachments: list[Attachment],
        reason: str,
    ) -> str:
        agent_map = self._agent_map()
        members = [
            agent_map[agent_id]
            for agent_id in chat.agent_ids
            if agent_id in agent_map
        ]
        target = agent_map.get(target_agent_id)
        if target is None:
            raise RuntimeError(f"Agent is unavailable: {target_agent_id}")
        member_lines = "\n".join(
            f"- @{member.mention or member.name or member.id} "
            f"（{member.name}，ID: {member.id}）"
            for member in members
        )
        history = self._format_history(
            self._history_since_last_reply(chat.id, target_agent_id),
            compact=False,
        )
        attachment_text = self._format_attachments(
            attachments,
            include_text=True,
        )
        return f"""你正在 QwenPaw 的通用群聊中，以“{target.name}”的身份回复。

你原有的人设、系统指令、知识和工具权限继续生效；群聊只为你补充共享上下文，不改变你的专业边界。

系统选择你回复本轮消息，原因：{reason}

## 当前群成员与可用 @ 名称
{member_lines}

## 对话历史
{history or "(无历史)"}

## 当前需要回复的内容
{current_content or "(用户只发送了附件)"}

## 附件
{attachment_text or "(无附件)"}

请直接回应用户，避免复述系统说明。只有当其他成员能提供明显互补价值时，才使用上面列出的精确 @ 名称邀请对方补充；不要代表其他成员发言，也不要 @用户。
"""

    def _history_since_last_reply(
        self,
        group_chat_id: str,
        agent_id: str,
    ) -> list[GroupChatMessage]:
        history = self.get_messages(group_chat_id, limit=0)
        last_idx = -1
        for idx, msg in enumerate(history):
            if msg.agent_id == agent_id:
                last_idx = idx
        start_idx = last_idx + 1
        selected = history[start_idx:] if last_idx >= 0 else history
        return selected[-MAX_HISTORY_FOR_AGENT:]

    @staticmethod
    def _format_history(
        messages: list[GroupChatMessage],
        *,
        compact: bool,
    ) -> str:
        lines: list[str] = []
        for msg in messages:
            if msg.role == "system":
                continue
            speaker = "用户" if msg.role == "user" else (msg.agent_name or "成员")
            text = msg.content.replace("\n", " ").strip()
            if compact and len(text) > 80:
                text = text[:80] + "..."
            if msg.quote:
                text = f"引用「{msg.quote.speaker}: {msg.quote.content}」；{text}"
            att = ""
            if msg.attachments:
                att = " " + " ".join(
                    f"[附件:{a.filename}]" for a in msg.attachments
                )
            lines.append(f"[{speaker}] {text}{att}")
        return "\n".join(lines)

    @staticmethod
    def _format_attachments(
        attachments: list[Attachment],
        *,
        include_text: bool,
    ) -> str:
        parts: list[str] = []
        for att in attachments:
            line = f"- {att.filename} ({att.mime_type}, {att.size} bytes)"
            if include_text and att.extracted_text:
                line += f"\n  提取内容：{att.extracted_text}"
            parts.append(line)
        return "\n".join(parts)

    @staticmethod
    def _format_quote(quote: Optional[MessageQuote]) -> str:
        if not quote:
            return ""
        return f"[{quote.speaker}] {quote.content}"

    @staticmethod
    def _compact_text(text: str, *, limit: int) -> str:
        compact = re.sub(r"\s+", " ", text or "").strip()
        if len(compact) > limit:
            return compact[:limit] + "..."
        return compact

    def _format_member_change_notice(
        self,
        added: list[str],
        removed: list[str],
    ) -> str:
        agents = self._agent_map()
        parts: list[str] = []
        if added:
            names = "、".join(
                agents.get(agent_id, AgentInfo(id=agent_id, name=agent_id)).name
                for agent_id in added
            )
            parts.append(f"已将 {names} 拉入群聊")
        if removed:
            names = "、".join(
                agents.get(agent_id, AgentInfo(id=agent_id, name=agent_id)).name
                for agent_id in removed
            )
            parts.append(f"已将 {names} 移出群聊")
        return "；".join(parts)

    async def _stream_agent_reply(
        self,
        agent_id: str,
        prompt: str,
        *,
        group_chat_id: str,
    ) -> AsyncGenerator[str, None]:
        text = await self._call_agent_once(
            agent_id,
            prompt,
            timeout=300,
            group_chat_id=group_chat_id,
        )
        for chunk in self._chunk_text(text):
            yield chunk
            await asyncio.sleep(0)

    @staticmethod
    def _chunk_text(text: str, size: int = 80) -> Iterable[str]:
        text = text or ""
        for i in range(0, len(text), size):
            end_idx = i + size
            yield text[i:end_idx]

    async def _call_agent_once(
        self,
        agent_id: str,
        prompt: str,
        *,
        timeout: int,
        group_chat_id: str,
    ) -> str:
        from qwenpaw.agents.tools.agent_management import (
            collect_final_agent_chat_response,
            extract_agent_text_content,
        )

        payload = self._build_agent_request_payload(
            agent_id,
            prompt,
            group_chat_id,
        )
        response_data = await asyncio.to_thread(
            collect_final_agent_chat_response,
            None,
            payload,
            agent_id,
            timeout,
        )
        if not response_data:
            raise RuntimeError("No response received from agent")
        text = extract_agent_text_content(response_data)
        return text.strip()

    def _build_agent_request_payload(
        self,
        agent_id: str,
        prompt: str,
        group_chat_id: str,
    ) -> dict[str, Any]:
        from qwenpaw.agents.tools.agent_management import (
            build_agent_chat_request,
        )

        session_id = self._session_id_for_group_chat(group_chat_id)
        _, payload, _ = build_agent_chat_request(
            agent_id,
            prompt,
            session_id=session_id,
            from_agent="group-chat-health",
            root_session_id=session_id,
        )
        payload["user_id"] = _AGENT_SESSION_USER_ID
        payload["channel"] = _AGENT_SESSION_CHANNEL
        payload["session_source"] = "chat"
        payload.setdefault("request_context", {}).update(
            {
                "source": "group-chat-health",
                "group_chat_id": group_chat_id,
            },
        )
        return payload

    @staticmethod
    def _session_id_for_group_chat(group_chat_id: str) -> str:
        return f"group-chat-health:{group_chat_id}"

    # ── Proactive support ───────────────────────────────────────────────

    async def deliver_proactive_push(
        self,
        group_chat_id: str,
        agent_id: str,
        content: str,
        reason: str,
    ) -> Optional[GroupChatMessage]:
        chat = self.get_group_chat(group_chat_id)
        if agent_id not in chat.agent_ids:
            return None
        spec = self.get_agent_info(agent_id)
        if spec is None:
            return None
        message = GroupChatMessage(
            id=f"msg-{uuid4().hex[:12]}",
            group_chat_id=group_chat_id,
            role="assistant",
            content=f"@用户 {content.strip()}",
            agent_id=agent_id,
            agent_name=spec.name,
            routed_by=reason,
            proactive=True,
            timestamp=time.time(),
        )
        await self._append_message(message)
        async with self._lock:
            self._proactive_logs.setdefault(group_chat_id, []).append(
                {
                    "timestamp": message.timestamp,
                    "agent_id": agent_id,
                    "should_push": True,
                    "reason": reason,
                },
            )
            self._proactive_logs[group_chat_id] = self._proactive_logs[
                group_chat_id
            ][-100:]
            self._persist_state_locked()
        await self._publish(
            group_chat_id,
            {"type": "proactive", "message": message.model_dump()},
        )
        return message

    def get_proactive_logs(self, group_chat_id: str) -> list[dict]:
        self.get_group_chat(group_chat_id)
        return self._proactive_logs.get(group_chat_id, [])[-100:]

    async def subscribe(
        self,
        group_chat_id: str,
    ) -> AsyncGenerator[dict, None]:
        self.get_group_chat(group_chat_id)
        queue: asyncio.Queue[dict] = asyncio.Queue(maxsize=100)
        self._subscribers.setdefault(group_chat_id, set()).add(queue)
        try:
            yield {"type": "connected"}
            while True:
                item = await queue.get()
                yield item
        finally:
            self._subscribers.get(group_chat_id, set()).discard(queue)

    async def _publish(self, group_chat_id: str, event: dict) -> None:
        queues = list(self._subscribers.get(group_chat_id, set()))
        for queue in queues:
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                logger.debug("Dropping group-chat event for full subscriber")
