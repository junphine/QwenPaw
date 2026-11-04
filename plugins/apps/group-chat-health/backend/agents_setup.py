# -*- coding: utf-8 -*-
"""Register the app-owned routing agent used by generic group chats."""

from __future__ import annotations

import logging
from pathlib import Path

from .constants import PLUGIN_DIR, PLUGIN_ID, ROUTER_AGENT_ID

logger = logging.getLogger("qwenpaw.group_chat")


def _router_profile():
    """Build the QwenPaw 2.2 managed-agent handle lazily."""

    from qwenpaw.pawapp.agent import (
        ManagedAgentProfile,
        ManagedAgentProfileSpec,
    )

    return ManagedAgentProfile(
        ManagedAgentProfileSpec(
            app_id=PLUGIN_ID,
            agent_id=ROUTER_AGENT_ID,
            name="群聊路由",
            description="为通用群聊选择最合适的成员，不直接参与用户对话",
            persona_dir=PLUGIN_DIR / "agents" / "message_router",
            plan_enabled=False,
            pinned=False,
        ),
    )


def _claim_legacy_router_if_safe() -> None:
    """Mark the pre-0.3 router as app-owned when its workspace is unchanged.

    Version 0.2 created the same internal router before QwenPaw exposed the
    managed-agent helper. We only migrate the profile when its workspace is the
    plugin-owned default, so a user profile with the same id is never claimed.
    """

    from qwenpaw.config.config import load_agent_config, save_agent_config
    from qwenpaw.config.utils import load_config
    from qwenpaw.constant import WORKING_DIR

    config = load_config()
    ref = config.agents.profiles.get(ROUTER_AGENT_ID)
    if ref is None:
        return

    expected = (Path(WORKING_DIR) / "workspaces" / ROUTER_AGENT_ID).resolve()
    actual = Path(ref.workspace_dir).expanduser().resolve()
    if actual != expected:
        return

    profile = load_agent_config(ROUTER_AGENT_ID)
    if profile.template_id in (None, "", ROUTER_AGENT_ID):
        profile.template_id = f"pawapp:{PLUGIN_ID}"
        save_agent_config(ROUTER_AGENT_ID, profile)
        logger.info("Migrated the legacy group-chat router to PawApp ownership")


def ensure_router_agent_exists() -> None:
    """Create or refresh the hidden routing agent."""

    try:
        _claim_legacy_router_if_safe()
        created = _router_profile().ensure()
        logger.info(
            "Group-chat routing agent %s",
            "created" if created else "refreshed",
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Cannot prepare the group-chat routing agent: %s", exc)


def uninstall_router_agent() -> None:
    """Detach the app-owned router while preserving its workspace data."""

    try:
        detached = _router_profile().detach()
        if detached:
            logger.info("Detached the group-chat routing agent")
    except Exception as exc:  # noqa: BLE001
        logger.warning("Cannot detach the group-chat routing agent: %s", exc)
