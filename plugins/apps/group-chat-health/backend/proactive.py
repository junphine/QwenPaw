# -*- coding: utf-8 -*-
"""Conservative opt-in proactive participation for generic group chats."""

# pylint: disable=protected-access

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .models import (
    GroupChat,
    GroupChatMessage,
    GroupChatStatus,
    ProactiveState,
)
from .service import GroupChatService

logger = logging.getLogger("qwenpaw.group_chat")


@dataclass(frozen=True)
class TimeSlot:
    """A daily proactive polling slot."""

    name: str
    label: str
    hour_start: int
    hour_end: int


DEFAULT_TIME_SLOTS: tuple[TimeSlot, ...] = (
    TimeSlot("morning", "上午时段", 9, 10),
    TimeSlot("afternoon", "下午时段", 14, 15),
    TimeSlot("evening", "晚间时段", 19, 20),
)


class ProactiveGuard:
    """Checks that keep proactive pushes restrained."""

    COOLDOWN_SECONDS = 2 * 60 * 60
    USER_ACTIVE_WINDOW_SECONDS = 30 * 60

    def should_skip(
        self,
        chat: GroupChat,
        state: ProactiveState,
        history: list[GroupChatMessage],
    ) -> tuple[bool, str]:
        now = time.time()
        reason = ""
        if not chat.proactive_enabled:
            reason = "proactive disabled"
        elif chat.status != GroupChatStatus.ACTIVE:
            reason = "chat archived"
        elif not history:
            reason = "empty chat"
        else:
            self._reset_daily_if_needed(state)
            if state.daily_push_count >= chat.proactive_daily_limit:
                reason = "daily limit reached"
            elif (
                state.last_push_at
                and now - state.last_push_at < self.COOLDOWN_SECONDS
            ):
                reason = "cooldown"
            else:
                last_user = next(
                    (m for m in reversed(history) if m.role == "user"),
                    None,
                )
                if last_user:
                    state.last_user_message_at = last_user.timestamp
                    if (
                        now - last_user.timestamp
                        < self.USER_ACTIVE_WINDOW_SECONDS
                    ):
                        reason = "user active"
                hour = datetime.now().hour
                if not reason and self._in_quiet_hours(
                    hour,
                    chat.proactive_quiet_start,
                    chat.proactive_quiet_end,
                ):
                    reason = "quiet hours"
        return bool(reason), reason

    @staticmethod
    def _in_quiet_hours(hour: int, start: int, end: int) -> bool:
        if start == end:
            return False
        if start > end:
            return hour >= start or hour < end
        return start <= hour < end

    @staticmethod
    def _reset_daily_if_needed(state: ProactiveState) -> None:
        today = datetime.now().date().isoformat()
        if state.daily_reset_date != today:
            state.daily_reset_date = today
            state.daily_push_count = 0
            state.triggered_slots_today.clear()


class ProactiveScheduler:
    """Periodically polls members for useful, opt-in proactive messages."""

    def __init__(self, service: GroupChatService):
        self._service = service
        self._states: dict[str, ProactiveState] = {}
        self._task: Optional[asyncio.Task] = None
        self._guard = ProactiveGuard()

    def start(self) -> None:
        if self._task and not self._task.done():
            return
        try:
            self._task = asyncio.create_task(self._loop())
            logger.info("Group chat proactive scheduler started")
        except RuntimeError:
            logger.warning(
                "No running event loop; proactive scheduler skipped",
            )

    def stop(self) -> None:
        if self._task and not self._task.done():
            self._task.cancel()
        self._task = None

    async def _loop(self) -> None:
        while True:
            await asyncio.sleep(600)
            slot = self._get_current_slot()
            if not slot:
                continue
            for chat in self._service.list_group_chats():
                await self._try_push(chat, slot)

    @staticmethod
    def _get_current_slot() -> Optional[TimeSlot]:
        hour = datetime.now().hour
        for slot in DEFAULT_TIME_SLOTS:
            if slot.hour_start <= hour < slot.hour_end:
                return slot
        return None

    def _state(self, chat_id: str) -> ProactiveState:
        if chat_id not in self._states:
            self._states[chat_id] = ProactiveState(group_chat_id=chat_id)
        return self._states[chat_id]

    async def _try_push(self, chat: GroupChat, slot: TimeSlot) -> None:
        state = self._state(chat.id)
        ProactiveGuard._reset_daily_if_needed(state)
        if slot.name in state.triggered_slots_today:
            return
        history = self._service.get_messages(chat.id, limit=10)
        should_skip, reason = self._guard.should_skip(chat, state, history)
        state.triggered_slots_today.add(slot.name)
        if should_skip:
            logger.debug("Proactive skipped for %s: %s", chat.id, reason)
            return

        for agent_id in chat.agent_ids:
            result = await self._poll_agent(agent_id, chat.id, history, slot)
            if not result.get("should_push") or not result.get("message"):
                continue
            delivered = await self._service.deliver_proactive_push(
                chat.id,
                agent_id,
                str(result["message"]),
                str(result.get("reason") or slot.label),
            )
            if delivered:
                state.daily_push_count += 1
                state.last_push_at = delivered.timestamp
            break

    async def _poll_agent(
        self,
        agent_id: str,
        group_chat_id: str,
        history: list[GroupChatMessage],
        slot: TimeSlot,
    ) -> dict:
        spec = self._service.get_agent_info(agent_id)
        if spec is None:
            return {"should_push": False, "reason": "agent unavailable"}
        history_text = "\n".join(
            (
                f"[{'用户' if m.role == 'user' else m.agent_name or '成员'}] "
                f"{m.content}"
            )
            for m in history[-10:]
        )
        prompt = f"""你正在以“{spec.name}”的身份参与一个通用群聊。

当前时间槽：{slot.label}

最近对话：
{history_text or "(无)"}

请判断现在是否有必要主动补充一条与最近对话直接相关的消息。
务必克制：没有明确的新价值、只是问候或重复已有内容时返回 should_push=false。

只输出 JSON：
{{"should_push":false,"message":"","reason":"原因"}}
"""
        try:
            raw = await self._service._call_agent_once(
                agent_id,
                prompt,
                timeout=90,
                group_chat_id=group_chat_id,
            )
            data = self._service._parse_json_object(raw)
            if isinstance(data, dict):
                return data
        except Exception as exc:  # noqa: BLE001
            logger.debug("Proactive poll failed for %s: %s", spec.name, exc)
        return {"should_push": False, "reason": "agent unavailable"}
