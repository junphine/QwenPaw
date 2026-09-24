# -*- coding: utf-8 -*-
"""Puter channel module.

Puter is WebOS assistant platform.
This module implements A2A (Agent-to-Agent) protocol support.
"""

from .channel import PuterChannel,PuterChannelConfig
from .media_routes import register_app_routes
__all__ = [
    "PuterChannel",
    "PuterChannelConfig",
    "register_app_routes",
]
