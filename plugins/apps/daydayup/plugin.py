"""
趣学习 (Daydayup) - AI 学习伴侣 v2.0
基于 Deep Tutor 架构，适配 QwenPaw 环境

完整的八大核心功能：
1. Home - 主页学习空间
2. Partners - AI 学习伙伴
3. My Agents - 我的智能体
4. Co-Writer - 协同写作
5. Book - 交互式书本
6. Learning Space - 学习空间
7. Memory - 三层记忆系统
8. Knowledge Center - 知识中心

作者：0+1+2≠3 Team 115886
版本：2.0.0
"""

__version__ = "2.0.0"

import logging
import sys
from pathlib import Path
from typing import Optional

# 添加插件目录到 Python 路径
plugin_dir = Path(__file__).parent
if str(plugin_dir) not in sys.path:
    sys.path.insert(0, str(plugin_dir))

# 导入核心插件
try:
    from backend.core.plugin import DaydayupPlugin
except ImportError as e:
    logging.error(f"[Daydayup] Failed to import DaydayupPlugin: {e}")
    # 创建一个空的插件类作为 fallback
    class DaydayupPlugin:
        def __init__(self):
            self.name = "趣学习"
            self.version = "2.0.0"
            self.id = "daydayup"
            
        def register(self, api):
            logging.info("[Daydayup] Plugin registered (fallback mode)")
            return None

logger = logging.getLogger("daydayup")

# 创建插件实例
plugin = DaydayupPlugin()


def register(api):
    """
    注册插件到 QwenPaw
    
    同时注册后端服务和前端菜单
    """
    # 注册后端服务
    try:
        app = plugin.register(api)
        logger.info("[Daydayup] Backend registered successfully")
    except Exception as e:
        logger.error(f"[Daydayup] Backend registration failed: {e}")
        app = None
    
    # 注册前端菜单（如果 API 支持）
    try:
        # 尝试注册侧边栏菜单
        if hasattr(api, 'register_menu_item'):
            api.register_menu_item(
                key="daydayup",
                label="趣学习",
                icon="📚",
                description="AI学习陪伴助手 - 完整学习系统",
                location="sidebar",
                order=100
            )
            logger.info("[Daydayup] Menu item registered via register_menu_item")
        
        # 尝试注册应用
        if hasattr(api, 'register_app'):
            api.register_app(
                app_id="daydayup",
                name="趣学习",
                icon="📚",
                category="education",
                entry_page="/apps/daydayup",
                description="AI学习陪伴助手 - 基于 Deep Tutor 架构的完整学习系统"
            )
            logger.info("[Daydayup] App registered via register_app")
        
        # 尝试注册页面
        if hasattr(api, 'register_page'):
            api.register_page(
                path="/apps/daydayup",
                title="趣学习",
                plugin_id="daydayup",
                component="DaydayupApp"
            )
            logger.info("[Daydayup] Page registered via register_page")
            
    except Exception as e:
        logger.warning(f"[Daydayup] Failed to register menu: {e}")
    
    return app


# 导出插件实例
__all__ = ["plugin", "register", "__version__"]
