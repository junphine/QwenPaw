# -*- coding: utf-8 -*-
# pylint: disable=too-many-instance-attributes,too-many-arguments
"""Puter channel: WebSocket event listener + REST API replies."""
from __future__ import annotations

import asyncio
import json
import logging
import re
import uuid
import types
from pathlib import Path
from typing import Any, Dict, Optional, Union

import httpx

from qwenpaw.app.channels.base import (
    AudioContent,
    ContentType,
    FileContent,
    ImageContent,
    TextContent,
    VideoContent,
)
from qwenpaw.schemas import (
    DataContent
)
from qwenpaw.app.channels.utils import file_url_to_local_path
from qwenpaw.config.config import BaseChannelConfig
from qwenpaw.constant import DEFAULT_MEDIA_DIR,WORKING_DIR
from qwenpaw.app.channels.base import (
    BaseChannel,
    OnReplySent,
    OutgoingContentPart,
    ProcessHandler,
)

from .utils import download_file, sync_puter_login,_download_puter_file

from .constants import (
    CONNECTION_TIMEOUT,
    HEARTBEAT_INTERVAL,
    MAX_RECONNECT_ATTEMPTS,
    TEXT_CHUNK_LIMIT,
    PUTER_ORIGIN_URL, PUTER_API_URL, DEFAULT_HTTP_URL
)

logger = logging.getLogger(__name__)

MATTERMOST_POST_CHUNK_SIZE = TEXT_CHUNK_LIMIT  # chars per post (hard limit ~16383)

_DEFAULT_MEDIA_DIR = WORKING_DIR / "media" / "puter"
_TYPING_TIMEOUT_S = 180

_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff"}
_AUDIO_SUFFIXES = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"}
_VIDEO_SUFFIXES = {".mp4", ".mov", ".mkv", ".webm", ".avi"}

TEXT_CONTENT=101 # "文本"
IMAGE_CONTENT=102 # "图片"
AUDIO_CONTENT=103 # "语音"
VIDEO_CONTENT=104 # "视频"
FILE_CONTENT=105 # "文件"
MATERIAL_CONTENT=125 # 素材


class PuterChannelConfig(BaseChannelConfig):
    """Puter channel: Msg protocol via WebSocket."""
    app_id: str = "app id" # puter app_id
    app_password: str = "app password" # puter app password
    url: str = DEFAULT_HTTP_URL
    bot_token: str = "your_access_token" # auth token
    tenant_id: str = "1" # tenant_id
    media_dir: Optional[str] = None
    show_typing: Optional[bool] = None
    thread_follow_without_mention: bool = False


class PuterChannel(BaseChannel):
    """Puter channel: WebSocket listener + REST API replies.

    Session model
    -------------
    - DM  (channel_type == 'D')  → session_id = puter_dm:{mm_channel_id}
    - Group/Channel (threaded)   → session_id = puter_thread:{root_id}

    Native payload format
    ---------------------
    {
        "channel_id":    "puter",        # framework channel type key
        "sender_id":     "<puter user_id>",
        "content_parts": [...],               # TextContent / ImageContent / …
        "meta": {
            "mm_channel_id": "<puter channel id>",
            "root_id":       "<thread root post id or ''>",
            "channel_type":  "D" | "O" | "P" | …,
            "post_id":       "<triggering post id>",
        },
    }
    """

    channel = "puter"
    uses_manager_queue = True

    def __init__(
        self,
        process: ProcessHandler,
        enabled: bool,
        url: str,
        bot_token: str,
        bot_prefix: str = "",
        media_dir: str = "",
        workspace_dir: Path | None = None,
        show_typing: Optional[bool] = None,
        thread_follow_without_mention: bool = False,
        on_reply_sent: OnReplySent = None,
        show_tool_details: bool = True,
        filter_tool_messages: bool = False,
        filter_thinking: bool = False,
        dm_policy: str = "open",
        group_policy: str = "open",
        allow_from: Optional[list] = None,
        deny_message: str = "",
        access_control_dm: bool = False,
        access_control_group: bool = False,
    ):
        super().__init__(
            process,
            on_reply_sent=on_reply_sent,
            show_tool_details=show_tool_details,
            filter_tool_messages=filter_tool_messages,
            filter_thinking=filter_thinking,
            dm_policy=dm_policy,
            group_policy=group_policy,
            allow_from=allow_from,
            deny_message=deny_message,
            access_control_dm=access_control_dm,
            access_control_group=access_control_group,
        )
        self.enabled = enabled
        self.bot_prefix = bot_prefix
        self._url = url.rstrip("/")
        self._bot_token = bot_token
        self._workspace_dir = (
            Path(workspace_dir).expanduser() if workspace_dir else None
        )
        # Use workspace-specific media dir if workspace_dir is provided
        if not media_dir and self._workspace_dir:
            self._media_dir = self._workspace_dir / "media"
        elif media_dir:
            self._media_dir = Path(media_dir).expanduser()
        else:
            self._media_dir = _DEFAULT_MEDIA_DIR
        self._show_typing = show_typing if show_typing is not None else True
        self._thread_follow = thread_follow_without_mention

        # Runtime state
        self._bot_id: int = 0
        self._bot_username: str = ""
        self._tenant_id: str = "1"
        self._task: Optional[asyncio.Task] = None
        self._typing_tasks: dict[str, asyncio.Task] = {}
        self._participated_threads: set[str] = set()
        self._seen_sessions: set[str] = set()

        # Reuse a single HTTP client (BaseChannel._http field)
        # Only Authorization header — Content-Type is set per-request by httpx
        # (json= → application/json, files= → multipart/form-data)
        self._http = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self._bot_token}","Visit-Tenant-Id": self._tenant_id },
            timeout=CONNECTION_TIMEOUT,
            follow_redirects=True,
        )

        if self.enabled and not self._url:
            logger.warning("puter: enabled but url is empty — disabled")
            self.enabled = False
        if self.enabled and not self._bot_token:
            logger.warning(
                "puter: enabled but bot_token is empty — disabled",
            )
            self.enabled = False

        self.materials = {}

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------

    @classmethod
    def from_config(
        cls,
        process: ProcessHandler,
        config: Union[PuterChannelConfig, dict],
        on_reply_sent: OnReplySent = None,
        show_tool_details: bool = True,
        filter_tool_messages: bool = False,
        filter_thinking: bool = False,
        workspace_dir: Path | None = None,
    ) -> "PuterChannel":
        if isinstance(config, dict):
            c = config
        elif hasattr(config, 'model_dump'):
            c = config.model_dump()
        elif isinstance(config, types.SimpleNamespace):
            # 如果确认 SimpleNamespace 的结构和 Pydantic 模型一致，手动转为字典
            c = vars(config)
        else:
            c = config.__dict__

        def _s(key: str) -> str:
            return (c.get(key) or "").strip()

        return cls(
            process=process,
            enabled=bool(c.get("enabled", False)),
            url=_s("url"),
            bot_token=_s("bot_token"),
            bot_prefix=_s("bot_prefix"),
            media_dir=_s("media_dir"),
            workspace_dir=workspace_dir,
            show_typing=c.get("show_typing"),
            thread_follow_without_mention=bool(
                c.get("thread_follow_without_mention", False),
            ),
            on_reply_sent=on_reply_sent,
            show_tool_details=show_tool_details,
            filter_tool_messages=filter_tool_messages,
            filter_thinking=filter_thinking,
            dm_policy=c.get("dm_policy") or "open",
            group_policy=c.get("group_policy") or "open",
            allow_from=c.get("allow_from") or [],
            deny_message=c.get("deny_message") or "",
            access_control_dm=bool(
                c.get("access_control_dm", False),
            ),
            access_control_group=bool(
                c.get("access_control_group", False),
            ),
        )

    @classmethod
    def from_env(
        cls,
        process: ProcessHandler,
        on_reply_sent: OnReplySent = None,
    ) -> "PuterChannel":
        import os

        allow_from_env = os.getenv("PUTER_ALLOW_FROM", "")
        allow_from = (
            [s.strip() for s in allow_from_env.split(",") if s.strip()]
            if allow_from_env
            else []
        )
        return cls(
            process=process,
            enabled=os.getenv("PUTER_CHANNEL_ENABLED", "0") == "1",
            url=os.getenv("PUTER_URL", ""),
            bot_token=os.getenv("PUTER_BOT_TOKEN", ""),
            bot_prefix=os.getenv("PUTER_BOT_PREFIX", ""),
            media_dir=os.getenv("PUTER_MEDIA_DIR", ""),
            show_typing=os.getenv("PUTER_SHOW_TYPING", "1") == "1",
            thread_follow_without_mention=(
                os.getenv("PUTER_THREAD_FOLLOW", "0") == "1"
            ),
            on_reply_sent=on_reply_sent,
            dm_policy=os.getenv("PUTER_DM_POLICY", "open"),
            group_policy=os.getenv("PUTER_GROUP_POLICY", "open"),
            allow_from=allow_from,
            deny_message=os.getenv("PUTER_DENY_MESSAGE", ""),
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def health_check(self) -> Dict[str, Any]:
        """Check Puter WebSocket and bot identity status."""
        if not self.enabled:
            return {
                "channel": self.channel,
                "status": "disabled",
                "detail": "Puter channel is disabled.",
            }
        issues = []
        task_alive = self._task is not None and not self._task.done()
        if not task_alive:
            issues.append("WebSocket task is not running")
        if not self._bot_id:
            issues.append("Bot identity not resolved (bot_id is empty)")
        if issues:
            return {
                "channel": self.channel,
                "status": "unhealthy",
                "detail": "; ".join(issues),
            }
        return {
            "channel": self.channel,
            "status": "healthy",
            "detail": (
                f"Puter bot is connected "
                f"(bot_id={self._bot_id}, "
                f"username={self._bot_username})."
            ),
        }

    async def start(self) -> None:
        if not self.enabled:
            logger.debug("puter: start() skipped (enabled=false)")
            return
        self._task = asyncio.create_task(
            self._run(),
            name="puter_websocket",
        )
        logger.info("puter: channel started (websocket task created)")

    async def stop(self) -> None:
        if not self.enabled:
            return
        for cid in list(self._typing_tasks):
            self._stop_typing(cid)
        if self._task:
            self._task.cancel()
            try:
                await asyncio.wait_for(self._task, timeout=10)
            except (asyncio.CancelledError, asyncio.TimeoutError, Exception):
                pass
            self._task = None
        try:
            await self._http.aclose()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # WebSocket loop
    # ------------------------------------------------------------------

    async def _init_bot_info(self) -> bool:
        """Fetch and cache bot_id / bot_username. Returns True on success."""
        try:
            resp = await self._http.get(f"{self._url}/admin-api/system/oauth2/user/get")
            if resp.status_code == 200:
                data = resp.json().get('data')
                self._bot_id = data.get("id", "")
                self._bot_username = data.get("nickname", data.get("username", ''))
                logger.info(
                    "puter: bot ready — id=%s username=@%s",
                    self._bot_id,
                    self._bot_username,
                )
            else:
                logger.error(
                    "puter: /users/me returned %s — check bot_token",
                    resp.status_code,
                )
                return False

            resp = await self._http.get(f"{self._url}/admin-api/im/friend/list")
            if resp.status_code == 200:
                data: list = resp.json().get('data')
                self._bot_friends = {}
                for fr in data:
                    self._bot_friends[fr["friendUserId"]] = fr["displayName"] or fr["nickname"]

            else:
                logger.error(
                    "puter: /users/friend returned %s — check bot_token",
                    resp.status_code,
                )

        except Exception:
            logger.exception("puter: failed to fetch bot info")
            return False
        return True

    async def _run(self) -> None:
        """Top-level task: fetch bot info, then enter WS reconnect loop."""
        if not await self._init_bot_info():
            logger.error("puter: cannot start — bot info fetch failed")
            return
        await self._websocket_loop()

    async def _websocket_loop(self) -> None:
        """WebSocket listener with exponential backoff reconnect."""
        try:
            import websockets  # type: ignore
        except ImportError:
            logger.error(
                "puter: 'websockets' not installed. "
                "Run: uv pip install websockets",
            )
            return

        # Default WebSocket URL
        # WS_URL = "ws://im.puter.srv.cn:38080/infra/ws"

        ws_url = (
            self._url.replace("http://", "ws://").replace("https://", "wss://")
            + "/infra/ws"
        )
        ws_url_with_token = ws_url+'?token='+self._bot_token
        reconnect_delay = 1

        while True:
            seq = 1
            try:
                async with websockets.connect(
                    ws_url_with_token,
                    ping_interval=HEARTBEAT_INTERVAL,
                    ping_timeout=CONNECTION_TIMEOUT,
                ) as ws:
                    auth_req ={
                        "toUserId": self._bot_id,
                        "text":"QwenPaw connect to Puter IM as user "+self._bot_username}

                    await ws.send("demo-message-send:"+json.dumps(auth_req))
                    reconnect_delay = 1  # reset on successful connect
                    logger.info(
                        "puter: websocket connected and authenticated",
                    )

                    async for raw in ws:
                        msgtype, data = raw.split(':',maxsplit=1)
                        if msgtype == "post":
                            asyncio.create_task(self._on_posted_event(data))
                        elif msgtype == "im-notification":
                            asyncio.create_task(self._on_im_notification_event(data))

            except asyncio.CancelledError:
                logger.debug("puter: websocket loop cancelled")
                return
            except Exception as exc:
                logger.warning(
                    "puter: websocket error: %s — retrying in %ds",
                    exc,
                    reconnect_delay,
                )
            await asyncio.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 2, 60)

    # ------------------------------------------------------------------
    # Message event helper
    # ------------------------------------------------------------------

    def _is_triggered(self, post: dict, channel_type: str) -> bool:
        """Check if the bot should respond to this post."""
        sender_id = post.get("senderId", "")
        receiver_id = post.get("receiverId", self._bot_id)
        if sender_id == self._bot_id or receiver_id != self._bot_id:
            return False

        message_text = post.get("content", "")
        if not message_text:
            return False
        original_root_id = post.get("root_id", "")
        is_dm = channel_type == "D"
        bot_mention = f"@{self._bot_username}"
        if not is_dm:
            is_mentioned = bool(
                self._bot_username and bot_mention.lower() in message_text.lower(),
            )
        is_in_thread = bool(original_root_id)
        thread_followed = (
            self._thread_follow
            and is_in_thread
            and original_root_id in self._participated_threads
        )
        return is_dm or is_mentioned or thread_followed

    async def _get_context_prefix(
        self,
        session_id: str,
        mm_channel_id: str,
        original_root_id: str|int,
        post_id: str|int,
        is_dm: bool,
    ) -> str:
        """Fetch history context if needed."""
        if is_dm:
            if session_id not in self._seen_sessions:
                self._seen_sessions.add(session_id)
                logger.info(
                    "puter: first DM contact on %s — "
                    "fetching channel history",
                    session_id,
                )
                return await self._fetch_channel_history(mm_channel_id)
        elif original_root_id:
            logger.info("puter: fetching thread gap for %s", session_id)
            return await self._fetch_thread_history(
                original_root_id,
                triggering_post_id=post_id,
            )
        else:
            if session_id not in self._seen_sessions:
                self._seen_sessions.add(session_id)
                logger.info(
                    "puter: new thread on %s — "
                    "fetching channel history as background",
                    session_id,
                )
                return await self._fetch_channel_history(
                    mm_channel_id,
                    per_page=10,
                )
        return ""

    async def _process_attachments(self, post: dict) -> list[Any]:
        """Download and wrap attachments."""
        parts = []
        file_ids: list[str] = post.get("file_ids") or []
        # Build filename hints from post metadata when available
        metadata = post.get("metadata") or {}
        file_infos: list[dict] = metadata.get("files") or []
        hint_map: dict[str, str] = {
            fi.get("id", ""): fi.get("name", "")
            for fi in file_infos
            if fi.get("id")
        }
        for fid in file_ids:
            local_path = await self._download_file(
                fid,
                filename_hint=hint_map.get(fid, ""),
            )
            if local_path:
                suffix = Path(local_path).suffix.lower()
                if suffix in _IMAGE_SUFFIXES:
                    parts.append(
                        ImageContent(
                            type=ContentType.IMAGE,
                            image_url=local_path,
                        ),
                    )
                else:
                    parts.append(
                        FileContent(
                            type=ContentType.FILE,
                            file_url=local_path,
                        ),
                    )
        return parts

    # ------------------------------------------------------------------
    # Message event handler
    # ------------------------------------------------------------------

    async def _on_posted_event(self, raw_post: str) -> None:
        """Handle one 'posted' WebSocket event end-to-end."""
        post: dict = json.loads(raw_post)
        channel_type: str = post.get("channel_type", "")

        if not self._is_triggered(post, channel_type):
            return

        sender_id: str = post.get("user_id", "")
        mm_channel_id: str = post.get("channel_id", "")
        post_id: str = post.get("id", "")
        message_text: str = post.get("message", "")
        original_root_id: str = post.get("root_id", "")
        is_dm = channel_type == "D"

        # 3. Determine effective root_id and session_id
        #
        # DM:  session always tied to the DM channel (unified memory).
        #      root_id is preserved so replies land inside the thread when
        #      the user triggered from within one; flat otherwise.
        #
        # Channel: each thread is its own session.
        #      A flat @mention seeds a new thread (root_id = post_id).
        if is_dm:
            target_root_id = (
                original_root_id  # "" for flat DM, non-empty for thread
            )
            session_id = f"puter_dm:{mm_channel_id}"
        else:
            target_root_id = original_root_id if original_root_id else post_id
            session_id = f"puter_thread:{target_root_id}"

        # 4. Start typing indicator loop
        if self._show_typing:
            self._start_typing(mm_channel_id, post_id)

        # 5. Clean @mention from text
        bot_mention = f"@{self._bot_username}"
        clean_text = re.sub(
            re.escape(bot_mention),
            "",
            message_text,
            flags=re.IGNORECASE,
        ).strip()

        # 6. Context fetching
        context_prefix = await self._get_context_prefix(
            session_id,
            mm_channel_id,
            original_root_id,
            post_id,
            is_dm,
        )

        # 7. Build content_parts
        content_parts: list[Any] = []

        if context_prefix:
            content_parts.append(
                TextContent(type=ContentType.TEXT, text=context_prefix),
            )
        if clean_text:
            content_parts.append(
                TextContent(type=ContentType.TEXT, text=clean_text),
            )

        # 8. Download and classify attachments
        content_parts.extend(await self._process_attachments(post))

        if not content_parts:
            content_parts.append(TextContent(type=ContentType.TEXT, text=""))

        # 9. Enqueue native payload
        native = {
            "channel_id": self.channel,  # "puter" — framework key
            "sender_id": sender_id,
            "content_parts": content_parts,
            "meta": {
                "mm_channel_id": mm_channel_id,
                "root_id": target_root_id,
                "channel_type": channel_type,
                "post_id": post_id,
            },
        }
        if self._enqueue is not None:
            self._enqueue(native)
        else:
            logger.warning("puter: _enqueue not set, message dropped")
            self._stop_typing(mm_channel_id)
            return

        # 10. Record thread participation
        if target_root_id:
            self._participated_threads.add(target_root_id)

    async def _on_im_notification_event(self, raw: str) -> None:
        """Handle one 'posted' WebSocket event end-to-end."""
        data: dict = json.loads(raw)
        content_type: str = data.get('contentType')
        conversation_type: int = data.get('conversationType')
        if conversation_type==1:   # PM
            channel_type = 'D'
        elif conversation_type==2: # Group
            channel_type = 'G'
        elif conversation_type==3: # Chanel
            channel_type = 'O'
        else:
            channel_type = 'P'

        post: dict = data.get('payload')
        if not self._is_triggered(post, channel_type):
            return

        content: dict = json.loads(post.get("content", ""))
        sender_id: int = post.get("senderId")
        group_id: int = post.get("groupId")
        channel_id: int = post.get("channelId")
        post_id: str = post.get("id", "")
        message_text: str = content.get("content","")
        original_root_id: int = post.get("rootId")
        if not original_root_id:
            original_root_id = content.get("rootId")
            if not original_root_id and 'quote' in content:
                original_root_id = content.get('quote').get("rootId")

        is_dm = channel_type == "D"

        # 3. Determine effective root_id and session_id
        #
        # DM:  session always tied to the DM channel (unified memory).
        #      root_id is preserved so replies land inside the thread when
        #      the user triggered from within one; flat otherwise.
        #
        # Channel: each thread is its own session.
        #      A flat @mention seeds a new thread (root_id = post_id).
        if is_dm:
            target_root_id = (
                original_root_id  # "" for flat DM, non-empty for thread
            )
            mm_channel_id = f"{sender_id}:{self._bot_id}" if sender_id>self._bot_id else f"{self._bot_id}:{sender_id}"
            session_id = f"puter_dm:{mm_channel_id}"
            mm_channel_id = f"{channel_type}:{mm_channel_id}"
        elif group_id is not None:
            # if original_root_id 群聊选择了话题
            target_root_id = original_root_id if original_root_id else group_id
            mm_channel_id = f"{channel_type}:{group_id}:{original_root_id or 0}"
            session_id = f"puter_group:{group_id}:{original_root_id or 0}"
        else:
            material_id = post.get("materialId",content.get("materialId")) # 频道必须有话题
            mm_channel_id = f"{channel_type}:{channel_id}:{material_id}"
            target_root_id = original_root_id if original_root_id else post_id
            session_id = f"puter_thread:{material_id}:{target_root_id}"

        # 4. Start typing indicator loop
        if self._show_typing:
            self._start_typing(mm_channel_id, post_id)

        # 5. Clean @mention from text
        bot_mention = f"@{self._bot_username}"
        clean_text = re.sub(
            re.escape(bot_mention),
            "",
            message_text,
            flags=re.IGNORECASE,
        ).strip()

        # 6. Context fetching
        context_prefix = await self._get_context_prefix(
            session_id,
            mm_channel_id,
            original_root_id,
            post_id,
            is_dm,
        )

        # 7. Build content_parts
        content_parts: list[Any] = []

        if context_prefix:
            content_parts.append(
                TextContent(type=ContentType.TEXT, text=context_prefix),
            )
        if clean_text:
            content_parts.append(
                TextContent(type=ContentType.TEXT, text=clean_text),
            )
        if content_type==IMAGE_CONTENT:
            image = content
            content_parts.append(
                ImageContent(
                    image_url=image["url"],
                ),
            )
        elif content_type == AUDIO_CONTENT:
            content_parts.append(
                AudioContent(
                    data=content["url"],
                ),
            )
        elif content_type == VIDEO_CONTENT:
            content_parts.append(
                VideoContent(
                    video_url=content["url"]
                ),
            )
        elif content_type == FILE_CONTENT:
            file = content
            content_parts.append(
                FileContent(
                    file_url=file["url"],filename=file["name"]
                ),
            )
        elif content_type == MATERIAL_CONTENT:
            material_content = self._get_material(content['materialId'])
            if material_content:
                content_parts.append(
                    TextContent(type=ContentType.TEXT, text=material_content),
                )
        elif content_type != TEXT_CONTENT:
            content_parts.append(
                DataContent(
                    data=content,
                ),
            )

        # 8. Download and classify attachments
        content_parts.extend(await self._process_attachments(content))

        if not content_parts:
            content_parts.append(TextContent(type=ContentType.TEXT, text=""))

        # 9. Enqueue native payload
        native = {
            "channel_id": self.channel,  # "puter" — framework key
            "sender_id": str(sender_id),
            "content_parts": content_parts,
            "meta": {
                "session_id": session_id,
                "mm_channel_id": mm_channel_id,
                "root_id": original_root_id,
                "user_name": self._bot_friends.get(sender_id,''),
                "post_id": post_id,
                "sender_id": sender_id,
                "question": clean_text if original_root_id else ''
            },
        }
        if self._enqueue is not None:
            self._enqueue(native)
        else:
            logger.warning("puter: _enqueue not set, message dropped")
            self._stop_typing(mm_channel_id)
            return

        # 10. Record thread participation
        if target_root_id:
            self._participated_threads.add(target_root_id)

    # ------------------------------------------------------------------
    # ------------------------------------------------------------------

    def _start_typing(self, mm_channel_id: str, message_id: str = "") -> None:
        """Start (or restart) the typing indicator loop for a channel."""
        self._stop_typing(mm_channel_id)
        self._typing_tasks[mm_channel_id] = asyncio.create_task(
            self._typing_loop(mm_channel_id, message_id),
        )

    def _stop_typing(self, mm_channel_id: str) -> None:
        """Cancel the typing indicator loop for a channel."""
        task = self._typing_tasks.pop(mm_channel_id, None)
        if task and not task.done():
            task.cancel()

    async def _typing_loop(
        self,
        mm_channel_id: str,
        message_id: str = "",
    ) -> None:
        """Send 'typing' status every 4 s until cancelled.

        Puter typing state expires in ~5 s so we refresh at 4 s.
        Safety timeout at _TYPING_TIMEOUT_S to avoid infinite loops.
        """
        try:
            ctype,channel,topic = mm_channel_id.split(':')
            channel = int(channel)
            if ctype=='D':
                receiver_id = channel if channel!=self._bot_id else int(topic)
                api = f"{self._url}/admin-api/im/message/private/read"
                payload={
                    "messageId": message_id,
                    "receiverId": receiver_id
                }
            elif ctype=='G':
                group_id = channel
                api = f"{self._url}/admin-api/im/message/group/read"
                payload={
                    "messageId": message_id,
                    "groupId": group_id,
                }
            else:
                api = f"{self._url}/admin-api/im/channel/message/read"
                payload={
                    "messageId": message_id,
                    "materialId": int(topic),
                    "channelId": channel
                }

            #deadline = asyncio.get_event_loop().time() + _TYPING_TIMEOUT_S
            if True:
                try:
                    await self._http.put(
                        api, params=payload
                    )
                except Exception as e:
                    logger.debug("puter: typing indicator send failed")
                #await asyncio.sleep(4)
                #if asyncio.get_event_loop().time() >= deadline:
                #    break
        except asyncio.CancelledError:
            pass
        finally:
            if self._typing_tasks.get(mm_channel_id) is asyncio.current_task():
                self._typing_tasks.pop(mm_channel_id, None)

    def _get_thread_target_order(
        self,
        posts: list,
        last_bot_idx: int,
    ) -> tuple[list[str], str]:
        """Helper to determine the slice of thread posts to show as context."""
        if last_bot_idx >= 0:
            # Bot has replied before.
            # Walk backwards to find the start of the consecutive bot-reply seq
            bot_seq_start = last_bot_idx
            while bot_seq_start > 0:
                prev_pid = posts[bot_seq_start - 1]
                if prev_pid.get("senderId") != self._bot_id:
                    break
                bot_seq_start -= 1

            # The user trigger that produced this bot reply sequence is
            # the post immediately before it.
            trigger_idx = bot_seq_start - 1

            # Gap = all NON-bot posts after the trigger (inclusive of
            # messages posted during bot processing AND after bot reply).
            if trigger_idx >= 0:
                gap = [
                    pid
                    for pid in posts[trigger_idx + 1 :]
                    if pid.get("senderId") != self._bot_id
                ]
            else:
                # Bot reply sequence starts at the very beginning
                gap = [
                    pid
                    for pid in posts
                    if pid.get("senderId") != self._bot_id
                ]
            return gap, "[Thread context supplement (unprocessed by bot)]"

        # Bot joining this thread for the first time: full history
        return posts, "[Thread history]"

    # ------------------------------------------------------------------
    # History helpers (lazy context — first session contact only)
    # ------------------------------------------------------------------

    async def _fetch_thread_history(
        self,
        root_id: str,
        triggering_post_id: str = "",
    ) -> str:
        """Pull thread posts and return a formatted context prefix.

        Smart fetch strategy:
        - If bot has never replied in this thread: return all posts
          (bot is joining the thread for the first time).
        - If bot has replied before: return only the "unseen" user
          messages — i.e. messages the bot hasn't processed yet.
          This includes messages posted *during* bot processing
          (which land chronologically before the bot reply) as well
          as messages posted after the bot reply.

        In all cases the triggering post itself is excluded (it is sent
        separately as the main user message).
        """
        try:
            resp = await self._http.get(
                f"{self._url}/admin-api/im/channel/message/list?",
                params ={"pageSize": 20, "rootId":root_id}
            )
            if resp.status_code != 200:
                return ""
            data = resp.json().get("data")
            posts: list = data

            # Exclude the triggering post (processed as main message)
            # Find the last bot reply to determine the "gap" start
            last_bot_idx = -1
            for i, p in enumerate(posts):
                if p.get("senderId") == self._bot_id:
                    last_bot_idx = i
                    break

            target_order, label = self._get_thread_target_order(
                posts,
                last_bot_idx,
            )
            # Sort by create_at to guarantee chronological order
            # (thread API order direction may differ across MM versions)
            posts.reverse()

            lines = [label]
            for p in target_order:
                sender = p.get("senderId")
                senderName = self._bot_friends.get(sender,f"User{sender}")
                role = "Bot" if sender == self._bot_id else senderName

                msg = json.loads(p.get("content", "{}"))
                if msg and 'content' in msg:
                    if 'quote' in msg:
                        quote = msg.get('quote')
                        quote_content = json.loads(quote.get('content','{}'))
                        sender = quote.get("senderId")
                        senderName = self._bot_friends.get(sender,f"User{sender}")
                        qrole = "Bot" if sender == self._bot_id else senderName
                        lines.append(f"> {qrole}: {quote_content['content']}")

                    if msg.get("type")==MATERIAL_CONTENT:
                        material_content = self._get_material(msg.get("materialId"))
                        lines.append(f"{role}: {material_content}")
                    else:
                        lines.append(f"{role}: {msg['content']}")

            if len(lines) == 1:
                return ""  # only label, no actual content
            lines.append(
                "[The above is supplementary context, please answer based on existing memory]",
            )
            return "\n".join(lines)
        except Exception as e:
            logger.exception("puter: fetch thread history failed")
        return ""

    async def _fetch_channel_history(
        self,
        mm_channel_id: str,
        per_page: int = 20,
    ) -> str:
        ctype,channel,topic = mm_channel_id.split(':')
        channel = int(channel)

        if ctype=='D':
            user_id = int(topic)
            receiver_id = channel if channel!=self._bot_id else user_id
            api = f"{self._url}/admin-api/im/message/private/list"
            params ={"limit": per_page, "receiverId":receiver_id}
        elif ctype=='G':
            group_id = channel
            api = f"{self._url}/admin-api/im/message/group/list"
            params ={"limit": per_page,"groupId":group_id}
        else:
            material_id = int(topic)
            api = f"{self._url}/admin-api/im/channel/message/list"
            params ={"pageSize": per_page, "materialId":material_id, "channelId":channel}
        """Pull recent DM posts and return a formatted prefix string."""
        try:
            resp = await self._http.get(
                url = api,
                params = params,
            )
            if resp.status_code == 200:
                posts: list = resp.json().get("data")
                if not posts:
                    return ''
                posts.reverse()
                lines = [f"[Recent {per_page} DM context messages]"]
                for p in posts:
                    sender = p.get("senderId")
                    senderName = p.get("creator")
                    if senderName is None:
                        senderName = self._bot_friends.get(sender,f"User{sender}")
                    role = (
                        "Bot" if sender == self._bot_id else senderName
                    )
                    msg = json.loads(p.get("content", "{}"))
                    if msg and 'content' in msg:
                        if msg.get("type")==MATERIAL_CONTENT:
                            material_content = self._get_material(msg.get("materialId"))
                            lines.append(f"{role}: {material_content}")
                        else:
                            lines.append(f"{role}: {msg['content']}")
                lines.append(
                    "[History ended, please answer the following questions based on the above context]",
                )
                return "\n".join(lines)
        except Exception:
            logger.exception("puter: fetch channel history failed")
        return ""

    # ------------------------------------------------------------------
    # File helpers
    # ------------------------------------------------------------------
    async def _get_material(self, id):
        if id not in self.materials:
            resp = await self._http.get(
                f"{self._url}/admin-api/im/channel/material/get",
                params ={"id":id}
            )
            if resp.status_code != 200:
                return ""

            material = resp.json().get("data")
            self.materials[id] = material
        else:
            material = self.materials[id]

        if material and material.get('content'):
            if material.get('url'):
                material_content = f"'> ## [{material.get('title')}]({material.get('url')})\n"
            else:
                material_content = '> ## '+material.get('title')+"\n"
            if material.get('summary'):
                material_content += '> ### summary \n> '+material.get('summary')+"\n"
            if 'content' in material:
                material_content += '> ### body \n> '+material.get('content')+"\n"

        elif material and material.get('url'):
            material_content = f"'> [{material.get('title')}]({material.get('url')})\n"

        return material_content

    async def _download_file(
        self,
        file_id: str,
        filename_hint: str = "",
    ) -> Optional[str]:
        """Download a Puter attachment; return local path or None."""
        return await _download_puter_file(
            http=self._http,
            url=f"{self._url}/admin-api/infra/file/get?id={file_id}",
            file_id=file_id,
            media_dir=self._media_dir,
            filename_hint=filename_hint,
        )

    async def _upload_file(
        self,
        mm_channel_id: str,
        local_path: str,
    ) -> Optional[str]:
        """Upload a local file; return Puter file_id or None.

        Uses multipart/form-data — httpx sets the Content-Type boundary
        automatically when 'files=' is passed, so we do NOT include
        Content-Type: application/json in this request.
        """
        path = Path(local_path)
        if not path.exists():
            logger.warning(
                "puter: upload — file not found: %s",
                local_path,
            )
            return None
        try:
            with open(path, "rb") as fh:
                resp = await self._http.post(
                    f"{self._url}/admin-api/infra/file/upload",
                    params={"directory": mm_channel_id.replace(':','_')},
                    files={"file": (path.name, fh)},
                    # No json= here; httpx handles Content-Type automatically
                )
            if resp.status_code in (200, 201):
                file_url = resp.json().get("data", "")
                if file_url:
                    return file_url
            logger.warning(
                "puter: file upload failed %s: %s",
                resp.status_code,
                resp.text[:200],
            )
        except Exception:
            logger.exception("puter: upload failed for %s", local_path)
        return None

    # ------------------------------------------------------------------
    # Internal post helper
    # ------------------------------------------------------------------

    async def _post_message(
        self,
        mm_channel_id: str,
        text: str,
        meta: dict = {},
        file_url: Optional[str] = None,file_name = None, content_type = TEXT_CONTENT
    ) -> bool:
        root_id: int = meta.get('root_id')
        post_id: int =  meta.get('post_id')
        """Call POST /api/v4/posts. Returns True on success."""
        content: dict[str, Any] = {}
        if file_url:
            content["url"] = file_url
        if file_name:
            content["name"] = file_name
        if text:
            content['content'] = text
        if root_id:
            quote_content = dict(content=meta.get('question',''))
            content['quote'] = dict(messageId=post_id,content=json.dumps(quote_content,ensure_ascii=False),type=TEXT_CONTENT,senderId=meta.get('sender_id'))
        # bot 生成的数据
        content['@bot'] = self._bot_id

        try:
            msg_id = uuid.uuid4().__str__()
            ctype,channel,topic = mm_channel_id.split(':')
            channel = int(channel)
            if ctype=='D':
                user_id = int(topic)
                receiver_id = channel if channel!=self._bot_id else user_id
                api = f"{self._url}/admin-api/im/message/private/send"
                payload={
                    "clientMessageId": msg_id,
                    "rootId": root_id,
                    "receiverId": receiver_id,
                    "type": content_type,
                    "content": json.dumps(content,ensure_ascii=False),
                }
            elif ctype=='G':
                group_id = channel
                api = f"{self._url}/admin-api/im/message/group/send"
                payload={
                    "clientMessageId": msg_id,
                    "rootId": root_id,
                    "groupId": group_id,
                    "type": content_type,
                    "content": json.dumps(content,ensure_ascii=False),
                }
            else:
                api = f"{self._url}/admin-api/im/channel/message/send"
                payload={
                    "clientMessageId": msg_id,
                    "channelId": channel,
                    "materialId": int(topic),
                    "rootId": root_id,
                    "threadId": post_id,
                    "type": content_type,
                    "content": json.dumps(content,ensure_ascii=False),
                }

            resp = await self._http.post(
                api,
                json=payload,
            )
            if resp.status_code == 201 or resp.status_code == 200:
                return True
            logger.error(
                "puter: post failed %s: %s",
                resp.status_code,
                resp.text[:300],
            )
        except Exception as e:
            logger.exception("puter: _post_message error: {}",e)
        return False

    # ------------------------------------------------------------------
    # Send interface
    # ------------------------------------------------------------------

    def _chunk_text(self, text: str) -> list[str]:
        """Split text at boundaries under post size limit."""
        if not text or len(text) <= MATTERMOST_POST_CHUNK_SIZE:
            return [text] if text else []
        chunks: list[str] = []
        rest = text
        while rest:
            if len(rest) <= MATTERMOST_POST_CHUNK_SIZE:
                chunks.append(rest)
                break
            chunk = rest[:MATTERMOST_POST_CHUNK_SIZE]
            last_nl = chunk.rfind("\n")
            if last_nl > MATTERMOST_POST_CHUNK_SIZE // 2:
                chunk = chunk[: last_nl + 1]
            else:
                last_space = chunk.rfind(" ")
                if last_space > MATTERMOST_POST_CHUNK_SIZE // 2:
                    chunk = chunk[: last_space + 1]
            chunks.append(chunk)
            rest = rest[len(chunk) :].lstrip("\n ")
        return chunks

    async def send(
        self,
        to_handle: str,
        text: str,
        meta: Optional[dict] = None,
    ) -> None:
        """Send text reply to Puter.

        to_handle = mm_channel_id (resolved by get_to_handle_from_request).
        root_id from meta guarantees the reply threads correctly.
        """
        if not self.enabled:
            return
        meta = meta or {}
        mm_channel_id = meta.get("mm_channel_id") or to_handle
        root_id: int = meta.get("root_id")
        post_id: int = meta.get("post_id")
        if not mm_channel_id:
            logger.warning(
                "puter send: no mm_channel_id in meta or to_handle",
            )
            return
        self._stop_typing(mm_channel_id)
        for chunk in self._chunk_text(text):
            await self._post_message(mm_channel_id, chunk, meta)

    async def send_media(
        self,
        to_handle: str,
        part: OutgoingContentPart,
        meta: Optional[dict] = None,
    ) -> None:
        """Upload a local file and post it as a Puter attachment."""
        if not self.enabled:
            return
        meta = meta or {}
        mm_channel_id = meta.get("mm_channel_id") or to_handle
        if not mm_channel_id:
            logger.warning("puter send_media: no mm_channel_id")
            return
        self._stop_typing(mm_channel_id)

        part_type = getattr(part, "type", None)
        local_path: Optional[str] = None
        content_type = FILE_CONTENT
        filename = None
        if part_type == ContentType.IMAGE:
            local_path = getattr(part, "image_url", None)
            content_type = IMAGE_CONTENT
        elif part_type == ContentType.VIDEO:
            local_path = getattr(part, "video_url", None)
            content_type = VIDEO_CONTENT
        elif part_type == ContentType.FILE:
            local_path = getattr(part, "file_url", None)
            filename = getattr(part, "filename", None)
            content_type = FILE_CONTENT
        elif part_type == ContentType.AUDIO:
            local_path = getattr(part, "data", None)
            content_type = AUDIO_CONTENT

        if not local_path:
            return
        local_path = file_url_to_local_path(local_path) or local_path

        file_url = await self._upload_file(mm_channel_id, local_path)
        if file_url:
            await self._post_message(mm_channel_id, "", meta, file_url, filename, content_type)
        else:
            # Fallback: send file path as plain text
            await self._post_message(
                mm_channel_id,
                f"[Attachment: {local_path}]",
                meta,
            )

    # ------------------------------------------------------------------
    # BaseChannel interface
    # ------------------------------------------------------------------

    def resolve_session_id(
        self,
        sender_id: str,
        channel_meta: Optional[dict] = None,
    ) -> str:
        """Map meta to session_id.

        DM  → puter_dm:{mm_channel_id}
        Group/Thread → puter_thread:{root_id or post_id}
        """
        meta = channel_meta or {}
        session_id = meta.get("session_id", "")

        if session_id:
            return session_id

        mm_channel_id = meta.get("mm_channel_id", "")
        root_id = meta.get("root_id", "")
        post_id = meta.get("post_id", "")
        ctype,channel,topic = mm_channel_id.split(':')
        if ctype=='D':
            return f"puter_dm:{channel}:{topic}"
        if ctype=='G':
            return f"puter_group:{channel}:{topic}"
        effective_root = root_id if root_id else post_id
        return f"puter_thread:{topic}:{effective_root}"

    def build_agent_request_from_native(self, native_payload: Any) -> Any:
        """Convert Puter native dict → AgentRequest."""
        payload = native_payload if isinstance(native_payload, dict) else {}
        channel_id = payload.get("channel_id") or self.channel
        sender_id = payload.get("sender_id") or ""
        content_parts = payload.get("content_parts") or []
        meta = payload.get("meta") or {}
        session_id = self.resolve_session_id(sender_id, meta)
        request = self.build_agent_request_from_user_content(
            channel_id=channel_id,
            sender_id=sender_id,
            session_id=session_id,
            content_parts=content_parts,
            channel_meta=meta,
        )
        request.user_id = sender_id
        request.channel_meta = meta
        return request

    def get_to_handle_from_request(self, request: Any) -> str:
        """Return mm_channel_id for the send() call."""
        meta = getattr(request, "channel_meta", None) or {}
        mm_channel_id = meta.get("mm_channel_id")
        if mm_channel_id:
            return str(mm_channel_id)
        # Fallback: extract from DM session_id
        sid = getattr(request, "session_id", "")
        uid = getattr(request, "user_id", "")
        if sid.startswith("puter_:"):
            return self.to_handle_from_target(uid,sid)
        return  uid or ""

    def to_handle_from_target(self, *, user_id: str, session_id: str) -> str:
        """Cron/proactive dispatch: resolve send target from session_id."""
        if session_id.startswith("puter_dm:"):
            return 'D:'+session_id.split(":", 1)[-1]
        if session_id.startswith("puter_thread:"):
            # todo@byron this is bug
            return 'O:'+session_id.split(":", 1)[-1]
        if session_id.startswith("puter_group:"):
            return 'G:'+session_id.split(":", 1)[-1]
        return user_id

    def _extract_chat_name(self, payload: Any) -> str:
        """Extract chat name from payload for chat creation.

        Args:
            payload: Message payload (dict or AgentRequest)

        Returns:
            Chat name (truncated to 50 chars)
        """
        if isinstance(payload, dict):
            mm_channel_id = payload['meta'].get('mm_channel_id')
            ctype,channel,topic = mm_channel_id.split(':')
            if ctype=='P':
                material = self.materials.get(int(topic))
                return f"puter_thread:{material['title']}"
            if ctype=='G':
                name = super()._extract_chat_name(payload)
                return f"puter_group:{name}"
            else:
                user_name = payload['meta'].get('user_name','')
                if user_name:
                    return f"puter_dm:{user_name}"
        return super()._extract_chat_name(payload)
