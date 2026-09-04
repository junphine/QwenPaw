"""
API 路由
基于 Deep Tutor 的 API 架构
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger("daydayup")


def create_api_router(plugin) -> APIRouter:
    """
    创建 API 路由
    
    Args:
        plugin: DaydayupPlugin 实例
        
    Returns:
        FastAPI Router
    """
    router = APIRouter()
    
    # 导入各模块路由
    from .home import router as home_router
    from .partners import router as partners_router
    from .agents import router as agents_router
    from .cowriter import router as cowriter_router
    from .book import router as book_router
    from .learning import router as learning_router
    from .memory import router as memory_router
    from .knowledge import router as knowledge_router
    from .deep_tutor import router as deep_tutor_router
    
    # 包含各模块路由
    router.include_router(home_router, prefix="/home", tags=["home"])
    router.include_router(partners_router, prefix="/partners", tags=["partners"])
    router.include_router(agents_router, prefix="/agents", tags=["agents"])
    router.include_router(cowriter_router, prefix="/cowriter", tags=["cowriter"])
    router.include_router(book_router, prefix="/book", tags=["book"])
    router.include_router(learning_router, prefix="/learning", tags=["learning"])
    router.include_router(memory_router, prefix="/memory", tags=["memory"])
    router.include_router(knowledge_router, prefix="/knowledge", tags=["knowledge"])
    router.include_router(deep_tutor_router, prefix="/dt", tags=["deep_tutor"])
    
    # 健康检查
    @router.get("/health")
    async def health_check():
        """健康检查"""
        return {
            "status": "ok",
            "plugin_id": plugin.id,
            "version": plugin.version,
            "initialized": plugin._initialized
        }
    
    # 插件信息
    @router.get("/info")
    async def plugin_info():
        """插件信息"""
        return {
            "id": plugin.id,
            "name": plugin.name,
            "version": plugin.version,
            "description": plugin.description,
            "data_dir": str(plugin.data_dir),
            "services": list(plugin.services.keys()) if plugin.services else [],
            "features": plugin.config.get("features", {}) if plugin.config else {}
        }
    
    # 统计信息
    @router.get("/stats")
    async def plugin_stats():
        """统计信息"""
        if plugin.app:
            return plugin.app.get_stats()
        return {"error": "Plugin not initialized"}
    
    # 配置
    @router.get("/config")
    async def get_config():
        """获取配置"""
        if plugin.config:
            return {
                "main": plugin.config._config,
                "ui": plugin.config.get_ui_config().__dict__ if plugin.config.get_ui_config() else {}
            }
        return {"error": "Config not available"}
    
    @router.post("/config")
    async def update_config(config: Dict[str, Any]):
        """更新配置"""
        if plugin.config:
            for key, value in config.items():
                plugin.config.set(key, value)
            return {"success": True}
        return {"error": "Config not available"}
    
    logger.info("[API] Router created with all modules")
    
    return router
