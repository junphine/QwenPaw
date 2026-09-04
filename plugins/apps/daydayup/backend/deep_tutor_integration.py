"""
Deep Tutor 集成模块
将 Deep Tutor 功能集成到趣学习插件
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

# 导入 Deep Tutor Bridge
from .deep_tutor_bridge import (
    DeepTutorAgentBridge,
    DeepTutorMemoryBridge,
    DeepTutorPartnerBridge,
    DeepTutorSkillBridge
)

logger = logging.getLogger("daydayup")


class DeepTutorIntegration:
    """
    Deep Tutor 集成器
    
    管理所有 Deep Tutor 桥接器
    """
    
    def __init__(self, data_dir: Path, config: Dict[str, Any]):
        self.data_dir = data_dir
        self.config = config
        
        # 初始化桥接器
        self.agent_bridge: Optional[DeepTutorAgentBridge] = None
        self.memory_bridge: Optional[DeepTutorMemoryBridge] = None
        self.partner_bridge: Optional[DeepTutorPartnerBridge] = None
        self.skill_bridge: Optional[DeepTutorSkillBridge] = None
        
        self._initialized = False
        
        logger.info("[DeepTutorIntegration] Created")
    
    async def initialize(self):
        """初始化所有桥接器"""
        if self._initialized:
            return
        
        logger.info("[DeepTutorIntegration] Initializing...")
        
        try:
            # 初始化 Agent Bridge
            self.agent_bridge = DeepTutorAgentBridge(
                self.data_dir,
                self.config
            )
            logger.info("[DeepTutorIntegration] Agent bridge initialized")
            
            # 初始化 Memory Bridge
            self.memory_bridge = DeepTutorMemoryBridge(self.data_dir)
            logger.info("[DeepTutorIntegration] Memory bridge initialized")
            
            # 初始化 Partner Bridge (需要 agent_bridge)
            self.partner_bridge = DeepTutorPartnerBridge(
                self.data_dir,
                self.agent_bridge
            )
            logger.info("[DeepTutorIntegration] Partner bridge initialized")
            
            # 初始化 Skill Bridge
            self.skill_bridge = DeepTutorSkillBridge(self.data_dir)
            logger.info("[DeepTutorIntegration] Skill bridge initialized")
            
            self._initialized = True
            logger.info("[DeepTutorIntegration] All bridges initialized")
            
        except Exception as e:
            logger.error(f"[DeepTutorIntegration] Initialization failed: {e}")
            raise
    
    def is_initialized(self) -> bool:
        """检查是否已初始化"""
        return self._initialized
    
    def get_agent_bridge(self) -> Optional[DeepTutorAgentBridge]:
        """获取 Agent Bridge"""
        return self.agent_bridge
    
    def get_memory_bridge(self) -> Optional[DeepTutorMemoryBridge]:
        """获取 Memory Bridge"""
        return self.memory_bridge
    
    def get_partner_bridge(self) -> Optional[DeepTutorPartnerBridge]:
        """获取 Partner Bridge"""
        return self.partner_bridge
    
    def get_skill_bridge(self) -> Optional[DeepTutorSkillBridge]:
        """获取 Skill Bridge"""
        return self.skill_bridge
    
    async def shutdown(self):
        """关闭所有桥接器"""
        logger.info("[DeepTutorIntegration] Shutting down...")
        self._initialized = False
