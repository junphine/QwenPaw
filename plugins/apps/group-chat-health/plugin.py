# -*- coding: utf-8 -*-
"""QwenPaw generic group-chat plugin entry point."""

from __future__ import annotations

import logging

from qwenpaw.plugins.api import PluginApi

from .backend.agents_setup import (
    ensure_router_agent_exists,
    uninstall_router_agent,
)
from .backend.constants import API_PREFIX
from .backend.proactive import ProactiveScheduler
from .backend.router import create_router
from .backend.service import GroupChatService

logger = logging.getLogger("qwenpaw.group_chat")


class GroupChatPlugin:
    """Register the generic group-chat backend and lifecycle hooks."""

    def __init__(self):
        self.service = GroupChatService()
        self.scheduler = ProactiveScheduler(self.service)

    def register(self, api: PluginApi) -> None:
        api.register_http_router(
            create_router(self.service),
            prefix=API_PREFIX,
            tags=["group-chat-health"],
        )
        api.register_startup_hook(
            hook_name="group_chat_health_startup",
            callback=self._startup,
            priority=90,
        )
        api.register_shutdown_hook(
            hook_name="group_chat_health_shutdown",
            callback=self._shutdown,
            priority=110,
        )
        if hasattr(api, "register_uninstall_hook"):
            api.register_uninstall_hook(
                hook_name="group_chat_health_uninstall",
                callback=self._uninstall,
                priority=80,
            )
        logger.info("Group Chat plugin registered")

    def _startup(self) -> None:
        ensure_router_agent_exists()
        self.scheduler.start()
        logger.info("Group Chat plugin startup complete")

    def _shutdown(self) -> None:
        self.scheduler.stop()
        logger.info("Group Chat plugin shutdown complete")

    def _uninstall(self, plugin_id: str, delete_files: bool = False) -> None:
        self.scheduler.stop()
        uninstall_router_agent()
        logger.info(
            "Group Chat plugin uninstall cleanup complete "
            "(plugin_id=%s, delete_files=%s)",
            plugin_id,
            delete_files,
        )


plugin = GroupChatPlugin()
