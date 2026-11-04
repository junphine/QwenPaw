# -*- coding: utf-8 -*-
"""Read the live QwenPaw agent catalog for group membership."""

from __future__ import annotations

import logging
from collections import Counter

from .constants import ROUTER_AGENT_ID
from .models import AgentInfo

logger = logging.getLogger("qwenpaw.group_chat")


def discover_available_agents() -> list[AgentInfo]:
    """Return enabled QwenPaw agents in the user's configured display order.

    The group-chat router is an implementation detail and is never selectable.
    A failed individual profile load does not hide the rest of the catalog.
    """

    try:
        from qwenpaw.config.config import load_agent_config
        from qwenpaw.config.utils import load_config

        config = load_config()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Cannot read QwenPaw agent catalog: %s", exc)
        return []

    ordered_ids: list[str] = []
    for agent_id in [
        *config.agents.agent_order,
        *config.agents.profiles.keys(),
    ]:
        if agent_id not in ordered_ids:
            ordered_ids.append(agent_id)

    candidates: list[tuple[str, str, str]] = []
    for agent_id in ordered_ids:
        if agent_id == ROUTER_AGENT_ID:
            continue
        ref = config.agents.profiles.get(agent_id)
        if ref is None or not getattr(ref, "enabled", True):
            continue
        name = agent_id
        description = ""
        try:
            profile = load_agent_config(agent_id)
            if (profile.template_id or "").startswith("pawapp:"):
                continue
            name = profile.name.strip() or agent_id
            description = profile.description.strip()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Cannot read QwenPaw agent %s: %s", agent_id, exc)
        candidates.append((agent_id, name, description))

    name_counts = Counter(name for _, name, _ in candidates)
    return [
        AgentInfo(
            id=agent_id,
            name=name,
            description=description,
            mention=name if name_counts[name] == 1 else agent_id,
        )
        for agent_id, name, description in candidates
    ]
