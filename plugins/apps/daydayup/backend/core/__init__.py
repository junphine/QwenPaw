"""
趣学习核心模块
基于 Deep Tutor 架构
"""
from .plugin import DaydayupPlugin
from .config import Config
from .events import EventManager
from .app import Application

__all__ = ["DaydayupPlugin", "Config", "EventManager", "Application"]
