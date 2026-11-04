# -*- coding: utf-8 -*-
"""Constants for the generic QwenPaw group-chat plugin."""

from __future__ import annotations

from pathlib import Path

# Keep the historical plugin ID and API prefix so existing installations and
# persisted chats upgrade in place. Only the product name and capabilities are
# generalized in 0.3.0.
PLUGIN_ID = "group-chat-health"
API_PREFIX = "/group-chat-health"
DEFAULT_CHAT_NAME = "多智能体协作群"

PLUGIN_DIR = Path(__file__).resolve().parents[1]
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"

ROUTER_AGENT_ID = "gc-message-router"
MAX_CHAIN_DEPTH = 6
MAX_HISTORY_FOR_AGENT = 50
MAX_HISTORY_FOR_ROUTER = 12
MAX_ATTACHMENT_BYTES = 20 * 1024 * 1024
MAX_EXTRACTED_TEXT_CHARS = 3000
