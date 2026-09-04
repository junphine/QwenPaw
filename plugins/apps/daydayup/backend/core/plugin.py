"""
趣学习核心插件类
基于 Deep Tutor 架构，适配 QwenPaw 插件系统
"""

import logging
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, FastAPI
from contextlib import asynccontextmanager

from .config import Config
from .events import EventManager
from .app import Application

# 导入服务
from ..services.learning_service import LearningService
from ..services.memory_service import MemoryService
from ..services.knowledge_service import KnowledgeService
from ..services.partner_service import PartnerService
from ..services.agent_service import AgentService
from ..services.skill_service import SkillService
from ..services.capability_service import CapabilityService
from ..services.book_service import BookService

# 导入 API
from ..api.router import create_api_router

logger = logging.getLogger("daydayup")


class DaydayupPlugin:
    """
    趣学习主插件类 - 基于 Deep Tutor 完整架构
    
    八大核心功能：
    1. Home - 主页学习空间
    2. Partners - AI 学习伙伴
    3. My Agents - 我的智能体
    4. Co-Writer - 协同写作
    5. Book - 交互式书本
    6. Learning Space - 学习空间
    7. Memory - 三层记忆系统
    8. Knowledge Center - 知识中心
    """
    
    def __init__(self):
        self.name = "趣学习"
        self.version = "2.0.0"
        self.id = "daydayup"
        self.description = "AI学习陪伴助手 - 基于 Deep Tutor 架构"
        
        # 数据目录
        self.data_dir = Path.home() / ".qwenpaw" / "daydayup_data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置
        self.config = Config(self.data_dir)
        
        # 事件管理器
        self.events = EventManager()
        
        # 应用实例
        self.app: Optional[Application] = None
        self.api: Optional[Any] = None
        
        # 服务实例
        self.services: Dict[str, Any] = {}
        
        # 初始化状态
        self._initialized = False
        
        logger.info(f"[{self.id}] Plugin instance created")
    
    def _init_services(self):
        """初始化所有服务"""
        logger.info(f"[{self.id}] Initializing services...")
        
        self.services = {
            "learning": LearningService(self.data_dir, self.config),
            "memory": MemoryService(self.data_dir, self.config),
            "knowledge": KnowledgeService(self.data_dir, self.config),
            "partner": PartnerService(self.data_dir, self.config),
            "agent": AgentService(self.data_dir, self.config),
            "skill": SkillService(self.data_dir, self.config),
            "capability": CapabilityService(self.data_dir, self.config),
            "book": BookService(self.data_dir, self.config),
        }
        
        logger.info(f"[{self.id}] Services initialized: {list(self.services.keys())}")
    
    def register(self, api) -> Optional[Application]:
        """
        注册插件到 QwenPaw
        
        Args:
            api: QwenPaw PluginApi 实例
            
        Returns:
            Application 实例
        """
        logger.info(f"[{self.id}] Registering plugin to QwenPaw...")
        
        self.api = api
        
        try:
            # 初始化服务
            self._init_services()

            # 创建应用
            self.app = Application(
                plugin=self,
                config=self.config,
                events=self.events,
                services=self.services
            )

            # 初始化API服务
            from ..api.book import init_book_service
            init_book_service(self.services["book"], self.config, self.events)
            
            # 创建 API 路由
            router = create_api_router(self)
            
            # 注册 HTTP 路由
            if hasattr(api, 'register_http_router'):
                api.register_http_router(
                    router,
                    prefix="/plugins/daydayup",
                    tags=["daydayup"],
                )
                logger.info(f"[{self.id}] HTTP router registered")
            
            # 注册生命周期钩子
            if hasattr(api, 'register_startup_hook'):
                api.register_startup_hook(f"{self.id}_startup", self._on_startup)
            
            if hasattr(api, 'register_shutdown_hook'):
                api.register_shutdown_hook(f"{self.id}_shutdown", self._on_shutdown)
            
            # 注册事件监听器
            self._register_event_listeners()
            
            self._initialized = True
            
            logger.info(f"[{self.id}] Plugin registered successfully")
            logger.info(f"[{self.id}] Data directory: {self.data_dir}")
            
            return self.app
            
        except Exception as e:
            logger.error(f"[{self.id}] Failed to register plugin: {e}", exc_info=True)
            raise
    
    def _register_event_listeners(self):
        """注册事件监听器"""
        # 学习事件
        self.events.on("learning.started", self._on_learning_started)
        self.events.on("learning.completed", self._on_learning_completed)
        
        # 记忆事件
        self.events.on("memory.saved", self._on_memory_saved)
        self.events.on("memory.recalled", self._on_memory_recalled)
        
        # 知识事件
        self.events.on("knowledge.added", self._on_knowledge_added)
        self.events.on("knowledge.searched", self._on_knowledge_searched)
        
        # 伙伴事件
        self.events.on("partner.chat", self._on_partner_chat)
        
        logger.info(f"[{self.id}] Event listeners registered")
    
    async def _on_startup(self):
        """启动钩子"""
        logger.info(f"[{self.id}] Plugin starting up...")
        
        try:
            # 启动所有服务
            for name, service in self.services.items():
                if hasattr(service, 'startup'):
                    await service.startup()
                    logger.info(f"[{self.id}] Service '{name}' started")
            
            # 触发启动事件
            await self.events.emit("plugin.started", {"plugin_id": self.id})
            
            logger.info(f"[{self.id}] Plugin startup complete")
            
        except Exception as e:
            logger.error(f"[{self.id}] Startup failed: {e}", exc_info=True)
            raise
    
    async def _on_shutdown(self):
        """关闭钩子"""
        logger.info(f"[{self.id}] Plugin shutting down...")
        
        try:
            # 触发关闭事件
            await self.events.emit("plugin.stopping", {"plugin_id": self.id})
            
            # 关闭所有服务
            for name, service in self.services.items():
                if hasattr(service, 'shutdown'):
                    await service.shutdown()
                    logger.info(f"[{self.id}] Service '{name}' stopped")
            
            logger.info(f"[{self.id}] Plugin shutdown complete")
            
        except Exception as e:
            logger.error(f"[{self.id}] Shutdown error: {e}", exc_info=True)
    
    # 事件处理器
    async def _on_learning_started(self, data: Dict[str, Any]):
        """学习开始事件"""
        logger.info(f"[{self.id}] Learning started: {data.get('course_name')}")
    
    async def _on_learning_completed(self, data: Dict[str, Any]):
        """学习完成事件"""
        logger.info(f"[{self.id}] Learning completed: {data.get('course_name')}")
    
    async def _on_memory_saved(self, data: Dict[str, Any]):
        """记忆保存事件"""
        logger.debug(f"[{self.id}] Memory saved to layer {data.get('layer')}")
    
    async def _on_memory_recalled(self, data: Dict[str, Any]):
        """记忆回忆事件"""
        logger.debug(f"[{self.id}] Memory recalled: {data.get('query')}")
    
    async def _on_knowledge_added(self, data: Dict[str, Any]):
        """知识添加事件"""
        logger.info(f"[{self.id}] Knowledge added to base: {data.get('base_id')}")
    
    async def _on_knowledge_searched(self, data: Dict[str, Any]):
        """知识搜索事件"""
        logger.debug(f"[{self.id}] Knowledge searched: {data.get('query')}")
    
    async def _on_partner_chat(self, data: Dict[str, Any]):
        """伙伴聊天事件"""
        logger.debug(f"[{self.id}] Partner chat: {data.get('partner_id')}")
    
    # 公共服务方法
    def get_service(self, name: str) -> Optional[Any]:
        """获取服务实例"""
        return self.services.get(name)
    
    def get_config(self) -> Config:
        """获取配置"""
        return self.config
    
    def get_events(self) -> EventManager:
        """获取事件管理器"""
        return self.events


# 模块级实例
plugin = DaydayupPlugin()
