# -*- coding: utf-8 -*-
"""FastAPI router for the generic Group Chat plugin."""

from __future__ import annotations

import json
from typing import Optional

from fastapi import APIRouter, File, Request, UploadFile
from fastapi.responses import FileResponse, StreamingResponse

from .models import (
    ChatDetailResponse,
    CreateGroupChatRequest,
    ProactiveSettingsRequest,
    SendMessageRequest,
    UpdateAgentsRequest,
)
from .service import GroupChatService


def _sse(data: dict) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


def create_router(service: GroupChatService) -> APIRouter:
    """Build the plugin router mounted under /api/group-chat-health."""
    router = APIRouter()

    @router.get("/agents")
    async def list_agents() -> dict:
        return {"agents": service.list_agents()}

    @router.post("/chats")
    async def create_chat(req: CreateGroupChatRequest):
        return await service.create_group_chat(req)

    @router.get("/chats")
    async def list_chats() -> dict:
        return {"chats": service.list_group_chats()}

    @router.get("/chats/{chat_id}", response_model=ChatDetailResponse)
    async def get_chat(chat_id: str) -> ChatDetailResponse:
        return ChatDetailResponse(
            chat=service.get_group_chat(chat_id),
            messages=service.get_messages(chat_id, limit=100),
        )

    @router.put("/chats/{chat_id}/agents")
    async def update_agents(chat_id: str, req: UpdateAgentsRequest):
        chat, notice = await service.update_agents(chat_id, req.agent_ids)
        return {"chat": chat, "message": notice}

    @router.delete("/chats/{chat_id}")
    async def delete_chat(chat_id: str) -> dict:
        await service.delete_group_chat(chat_id)
        return {"success": True}

    @router.post("/upload")
    async def upload_attachment(file: UploadFile = File(...)):
        return await service.save_attachment(file)

    @router.get("/attachments/{attachment_id}")
    async def get_attachment(attachment_id: str):
        attachment, path = service.get_attachment(attachment_id)
        return FileResponse(
            path,
            media_type=attachment.mime_type,
            filename=attachment.filename,
        )

    @router.post("/chats/{chat_id}/messages")
    async def send_message(
        chat_id: str,
        req: SendMessageRequest,
        request: Request,
    ) -> StreamingResponse:
        async def event_generator():
            async for event in service.send_message(chat_id, req):
                if await request.is_disconnected():
                    break
                yield _sse(event)

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    @router.post("/chats/{chat_id}/messages/{message_id}/retry")
    async def retry_message(
        chat_id: str,
        message_id: str,
        request: Request,
    ) -> StreamingResponse:
        async def event_generator():
            async for event in service.retry_message(chat_id, message_id):
                if await request.is_disconnected():
                    break
                yield _sse(event)

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    @router.get("/chats/{chat_id}/messages")
    async def list_messages(
        chat_id: str,
        limit: int = 50,
        before: Optional[str] = None,
    ) -> dict:
        return {
            "messages": service.get_messages(
                chat_id,
                limit=limit,
                before=before,
            ),
        }

    @router.get("/chats/{chat_id}/events")
    async def chat_events(chat_id: str, request: Request) -> StreamingResponse:
        async def event_generator():
            async for event in service.subscribe(chat_id):
                if await request.is_disconnected():
                    break
                yield _sse(event)

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    @router.put("/chats/{chat_id}/proactive")
    async def update_proactive(chat_id: str, req: ProactiveSettingsRequest):
        return await service.update_proactive_settings(chat_id, req)

    @router.get("/chats/{chat_id}/proactive/logs")
    async def proactive_logs(chat_id: str) -> dict:
        return {"logs": service.get_proactive_logs(chat_id)}

    return router
