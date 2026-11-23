# -*- coding: utf-8 -*-
"""LLM calls: agent chat API, direct model calls, SSE parsing, token usage.

``_call_model_directly`` falls back to ``_call_agent_chat`` within this module;
both raise ``AgentCallException`` on irrecoverable failure.
"""

import asyncio
import json
import os
from typing import Any, Optional

from qwenpaw.agents.tools.agent_management import resolve_agent_api_base_url

from engine import get_logger

logger = get_logger(__name__)

# Platform branding — read from environment or use a neutral fallback
_PLATFORM_NAME = os.environ.get("PLATFORM_NAME", "Agent Platform")


def _parse_sse_line(line: str) -> Optional[dict]:
    """Parse a single SSE data line."""
    stripped = line.strip()
    if stripped.startswith("data: "):
        try:
            return json.loads(stripped[6:])
        except json.JSONDecodeError:
            return None
    return None


def _extract_text_from_agent_response(data: dict) -> str:
    """Extract text content from agent response payload (supports multiple formats)."""
    if not isinstance(data, dict):
        return str(data)

    event_data = data
    text = ''
    if event_data.get('output'):
        for item in event_data['output']:
            if item.get('role') == 'assistant':
                for content_item in item.get('content', []):
                    if content_item.get('type') == 'text':
                        text += content_item.get('text', '')
    return text

    # ── Format 1: SSE content delta (streaming chunks)
    # {"object": "content", "delta": true, "msg_id": "...", "index": 0, "text": "..."}
    if data.get("object") == "content" and data.get("delta") is True:
        text = data.get("text", "")
        if isinstance(text, str) and text:
            return text

    # ── Format 2: SSE message completed
    # {"object": "message", "status": "completed", "output": [...]}
    if data.get("object") == "message" and data.get("status") == "completed":
        output = data.get("output", [])
        if output and isinstance(output, list):
            text_parts = []
            for msg in output:
                if isinstance(msg, dict):
                    content = msg.get("content", [])
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and item.get("type") == "text":
                                text_parts.append(item.get("text", ""))
                            elif isinstance(item, str):
                                text_parts.append(item)
                    elif isinstance(content, str):
                        text_parts.append(content)
            result = "\n".join(text_parts).strip()
            if result:
                return result

    # ── Format 3: SSE response object
    # {"object": "response", "output": [{"role": "assistant", "content": [...]}]}
    if data.get("object") in ("response", "message"):
        output = data.get("output", [])
        if output and isinstance(output, list):
            text_parts = []
            for msg in output:
                if isinstance(msg, dict):
                    content = msg.get("content", [])
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and item.get("type") == "text":
                                text_parts.append(item.get("text", ""))
                            elif isinstance(item, str):
                                text_parts.append(item)
                    elif isinstance(content, str):
                        text_parts.append(content)
            result = "\n".join(text_parts).strip()
            if result:
                return result

    # ── Format 4: SSE standard format (legacy)
    # {"output": [{"role": "assistant", "content": [{"type": "text", "text": "..."}]}]}
    try:
        output = data.get("output", [])
        if output and isinstance(output, list):
            last_msg = output[-1]
            if isinstance(last_msg, dict):
                content = last_msg.get("content", [])
                if isinstance(content, list):
                    text_parts = []
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            text_parts.append(item.get("text", ""))
                        elif isinstance(item, str):
                            text_parts.append(item)
                    result = "\n".join(text_parts).strip()
                    if result:
                        return result
    except (KeyError, IndexError, TypeError):
        pass

    # ── Format 5: Simple text/content fields
    for key in ("text", "content", "response", "message", "result", "output"):
        if key in data:
            val = data[key]
            if isinstance(val, str):
                return val
            elif isinstance(val, dict):
                return json.dumps(val, ensure_ascii=False)
            return str(val)

    # ── Format 6: JSON string fallback
    return json.dumps(data, ensure_ascii=False)


class AgentCallException(Exception):
    """Raised when an agent chat API call fails irrecoverably.

    Used to signal upstream that the node execution failed,
    so the executor can mark the node status as ``failed``
    instead of treating the error text as a normal response.
    """


def _as_token_count(value: Any) -> int:
    """Coerce one host token counter, treating anything unusable as zero."""
    try:
        return max(int(value or 0), 0)
    except (TypeError, ValueError):
        return 0


def _turn_usage_tokens(parsed: Any) -> dict:
    """Normalise the platform's ``turn_usage`` event into trace keys.

    This event is the only place the host reports token cost, and it closes a
    chat turn — so it is a property of the one call that just finished, which is
    what makes per-node attribution possible. An empty dict means "nothing was
    measured", and the history records that as zero rather than as a guess.
    """
    usage = parsed.get("usage") if isinstance(parsed, dict) else None
    if not isinstance(usage, dict):
        return {}
    prompt = _as_token_count(usage.get("prompt_tokens"))
    completion = _as_token_count(usage.get("completion_tokens"))
    return {
        "promptTokens": prompt,
        "completionTokens": completion,
        "totalTokens": _as_token_count(usage.get("total_tokens")) or (prompt + completion),
    }


async def _call_agent_chat(agent_id: str, messages: list, timeout: float = 60.0, on_token=None, usage_out=None) -> str:
    """Call the local platform chat API and collect the full response.

    Supports both JSON and SSE streaming responses.
    Also supports message attachments (images/files) via content_parts.

    Args:
        on_token: Optional synchronous callback invoked with each incremental
            text delta as it arrives from the SSE stream. It is purely a
            passthrough for live streaming (token-level) consumers; the final
            return value is assembled exactly as before, so synchronous
            callers see a byte-identical result.
        usage_out: Optional dict filled with the caller's token counts (see
            :func:`_turn_usage_tokens`). A sink rather than a second return
            value because the text is the contract and this is a side note.

    Raises:
        AgentCallException: When the HTTP request fails (connection error,
            timeout, non-2xx status, or unexpected exception).
    """
    import httpx

    # Fallback to default agent if not specified
    effective_agent_id = agent_id.strip() if agent_id and str(agent_id).strip() else "default"

    def _build_content_parts(msg: dict) -> list:
        """Build content parts from message text and attachments.

        Produces platform-native Content shapes:
        - Text: {"type": "text", "text": "..."}
        - Image: {"type": "image", "image_url": "<path or url>"}
        - File: {"type": "file", "file_url": "<path or url>", "filename": "..."}
        """
        parts = []
        text = msg.get("content", "")
        if text:
            parts.append({"type": "text", "text": text})
        for att in msg.get("attachments", []) or []:
            url = att.get("url", "")
            if not url:
                continue
            # Heuristic: treat image/* as image, everything else as file
            att_type = att.get("type", "")
            if att_type and att_type.startswith("image/"):
                parts.append({"type": "image", "image_url": url})
            else:
                parts.append({
                    "type": "file",
                    "file_url": url,
                    "filename": att.get("name", "file"),
                })
        return parts

    payload = {
        "session_id": None,
        "user_id": "workflow-executor",
        "input": [
            {
                "role": msg.get("role", "user"),
                "content": _build_content_parts(msg),
            }
            for msg in messages
        ],
    }

    headers = {"X-Agent-Id": effective_agent_id}
    base_url = resolve_agent_api_base_url()

    # Debug: log request
    logger.debug(
        "[_call_agent_chat] agent_id=%s, messages_count=%d, payload=%s",
        effective_agent_id,
        len(messages),
        json.dumps(payload, ensure_ascii=False, default=str),
    )

    try:
        async with httpx.AsyncClient() as client:
            # Streaming is what makes on_token incremental: a buffered POST
            # would hand us the whole body before the first delta.
            async with client.stream(
                "POST",
                f"{base_url}/api/console/chat",
                json=payload,
                headers=headers,
                timeout=timeout,
            ) as response:
                # A streaming response cannot be re-read after the context exits,
                # so load an error body now — the handler below reports its detail.
                if response.status_code >= 400:
                    await response.aread()
                response.raise_for_status()

                content_type = response.headers.get("content-type", "")
                logger.debug("[_call_agent_chat] response content-type=%s", content_type)

                # Handle SSE stream
                if "text/event-stream" in content_type or payload.get("stream"):
                    text_parts = []
                    sse_event_count = 0
                    async for line in response.aiter_lines():
                        if not line or not line.strip().startswith("data:"):
                            continue
                        parsed = _parse_sse_line(line)
                        if not parsed:
                            continue
                        if parsed.get("type") == "turn_usage":
                            # Filtered out of the text for the same reason it is
                            # filtered here: it is bookkeeping, not an answer.
                            if usage_out is not None:
                                usage_out.update(_turn_usage_tokens(parsed))
                            continue
                        sse_event_count += 1
                        part = _extract_text_from_agent_response(parsed)
                        if part:
                            text_parts.append(part)
                            # Surface true incremental deltas for live streaming.
                            if (
                                on_token is not None
                                and parsed.get("object") == "content"
                                and parsed.get("delta") is True
                            ):
                                try:
                                    on_token(part)
                                except Exception:  # noqa: BLE001  (never break the run for a UI callback)
                                    logger.debug("[_call_agent_chat] on_token callback failed", exc_info=True)
                    result_text = "\n".join(text_parts).strip()
                    logger.debug(
                        "[_call_agent_chat] SSE events=%d, extracted_text_len=%d",
                        sse_event_count,
                        len(result_text),
                    )
                    return result_text

                # Handle JSON response
                await response.aread()
                data = response.json()
                logger.debug("[_call_agent_chat] JSON response=%s", json.dumps(data, ensure_ascii=False, default=str))
                if usage_out is not None:
                    # A buffered JSON reply normally carries no turn_usage block;
                    # the helper returns {} when there is nothing measured.
                    usage_out.update(_turn_usage_tokens(data))
                result = _extract_text_from_agent_response(data)
                logger.debug("[_call_agent_chat] extracted_text_len=%d", len(result))
                return result

    except httpx.ConnectError as exc:
        raise AgentCallException(f"无法连接到 {_PLATFORM_NAME} 服务 ({base_url})") from exc
    except httpx.TimeoutException as exc:
        raise AgentCallException(f"Agent 调用超时 ({timeout}s)") from exc
    except httpx.HTTPStatusError as exc:
        # Extract detailed error from response body if available
        detail = str(exc)
        try:
            error_body = exc.response.json() if exc.response else {}
            if isinstance(error_body, dict) and error_body.get("detail"):
                detail = error_body["detail"]
        except Exception:
            pass
        raise AgentCallException(f"Agent 调用失败 (HTTP {exc.response.status_code}): {detail}") from exc
    except Exception as exc:
        raise AgentCallException(f"Agent 调用异常: {str(exc)}") from exc


async def _call_model_directly(model_key: str, messages: list, timeout: float = 30.0, usage_out=None) -> str:
    """Directly call a specific model by its provider/model identifier.

    Parses ``provider_id/model_id`` (e.g. ``dashscope/qwen3.6-plus``),
    obtains the chat-model instance from the provider manager, and
    invokes it. Falls back to ``_call_agent_chat`` when the provider
    or model is unavailable.

    Args:
        model_key: Provider/model identifier in the form ``provider/model``.
        messages: List of message dicts with ``role`` and ``content`` keys.
        timeout: Maximum time to wait for the model response.
        usage_out: Token counts sink, filled only on the ``_call_agent_chat``
            fallbacks. A provider called directly reports none: the host's
            ``consume_model_response`` returns text and discards the usage
            block, so a direct call is recorded as zero rather than estimated.

    Returns:
        The model's text response, or an error message string.
    """
    # Parse provider_id and model_id from the key
    # Support both colon (":") and slash ("/") separators for compatibility
    separator = ":" if ":" in model_key else ("/" if "/" in model_key else None)
    if separator is None:
        logger.warning("[Router LLM] model_key does not contain ':' or '/', falling back to agent chat: %s", model_key)
        return await _call_agent_chat(model_key, messages, timeout=timeout, usage_out=usage_out)

    provider_id, model_id = model_key.split(separator, 1)
    if not provider_id or not model_id:
        logger.warning("[Router LLM] empty provider_id or model_id in: %s", model_key)
        return await _call_agent_chat(model_key, messages, timeout=timeout, usage_out=usage_out)

    try:
        from qwenpaw.providers.provider_manager import ProviderManager
        from qwenpaw.utils.model_response import consume_model_response
        from agentscope.message import UserMsg, SystemMsg, AssistantMsg

        manager = ProviderManager.get_instance()
        provider = manager.get_provider(provider_id)
        if provider is None:
            logger.warning("[Router LLM] Provider not found: %s", provider_id)
            return await _call_agent_chat(model_key, messages, timeout=timeout, usage_out=usage_out)

        model_instance = provider.get_chat_model_instance(model_id)
        if model_instance is None:
            logger.warning("[Router LLM] Model not found: %s/%s", provider_id, model_id)
            return await _call_agent_chat(model_key, messages, timeout=timeout, usage_out=usage_out)

        # Convert dict messages to agentscope Msg objects
        # Use UserMsg/SystemMsg/AssistantMsg helpers which automatically
        # wrap string content into TextBlock lists.
        msg_objects = []
        for msg in messages:
            role = msg.get("role", "user") if isinstance(msg, dict) else "user"
            content = msg.get("content", "") if isinstance(msg, dict) else str(msg)
            if role == "system":
                msg_objects.append(SystemMsg(name=role, content=content))
            elif role == "assistant":
                msg_objects.append(AssistantMsg(name=role, content=content))
            else:
                msg_objects.append(UserMsg(name=role, content=content))

        logger.debug("[Router LLM] Calling model directly: %s/%s", provider_id, model_id)
        result = await asyncio.wait_for(
            consume_model_response(model_instance, msg_objects),
            timeout=timeout,
        )
        return result or ""
    except asyncio.TimeoutError as exc:
        raise AgentCallException(f"模型调用超时 ({timeout}s): {model_key}") from exc
    except Exception as exc:
        logger.exception("[Router LLM] Direct model call failed for %s", model_key)
        raise AgentCallException(f"模型调用失败: {exc}") from exc
