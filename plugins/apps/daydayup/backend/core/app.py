"""
应用类
管理插件的应用状态
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from .config import Config
from .events import EventManager

logger = logging.getLogger("daydayup")


class Application:
    """
    应用类
    管理插件的应用状态和生命周期
    """
    
    def __init__(self, plugin, config: Config, events: EventManager, services: Dict[str, Any]):
        self.plugin = plugin
        self.config = config
        self.events = events
        self.services = services
        
        # 应用状态
        self._state: Dict[str, Any] = {
            "initialized": False,
            "started_at": None,
            "active_sessions": {},
            "active_users": set()
        }
        
        # 会话管理
        self._sessions: Dict[str, Dict[str, Any]] = {}
        
        logger.info("[App] Application instance created")
    
    # 状态管理
    def get_state(self) -> Dict[str, Any]:
        """获取应用状态"""
        return self._state.copy()
    
    def update_state(self, key: str, value: Any):
        """更新状态"""
        self._state[key] = value
        logger.debug(f"[App] State updated: {key}")
    
    def is_initialized(self) -> bool:
        """检查是否已初始化"""
        return self._state.get("initialized", False)
    
    def set_initialized(self, initialized: bool = True):
        """设置初始化状态"""
        self._state["initialized"] = initialized
        if initialized:
            self._state["started_at"] = datetime.now().isoformat()
    
    # 会话管理
    def create_session(self, session_id: str, user_id: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """创建会话"""
        session = {
            "id": session_id,
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self._sessions[session_id] = session
        self._state["active_sessions"][session_id] = session
        self._state["active_users"].add(user_id)
        
        logger.info(f"[App] Session created: {session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话"""
        return self._sessions.get(session_id)
    
    def update_session(self, session_id: str, data: Dict[str, Any]):
        """更新会话"""
        if session_id in self._sessions:
            self._sessions[session_id].update(data)
            self._sessions[session_id]["last_activity"] = datetime.now().isoformat()
            self._state["active_sessions"][session_id] = self._sessions[session_id]
    
    def close_session(self, session_id: str):
        """关闭会话"""
        if session_id in self._sessions:
            session = self._sessions[session_id]
            user_id = session.get("user_id")
            del self._sessions[session_id]
            del self._state["active_sessions"][session_id]
            
            # 检查用户是否还有其他会话
            if not any(s.get("user_id") == user_id for s in self._sessions.values()):
                self._state["active_users"].discard(user_id)
            
            logger.info(f"[App] Session closed: {session_id}")
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """获取活跃会话"""
        return list(self._state["active_sessions"].values())
    
    def get_active_users(self) -> List[str]:
        """获取活跃用户"""
        return list(self._state["active_users"])
    
    def get_session_count(self) -> int:
        """获取会话数量"""
        return len(self._sessions)
    
    def get_user_count(self) -> int:
        """获取用户数量"""
        return len(self._state["active_users"])
    
    # 服务访问
    def get_service(self, name: str) -> Optional[Any]:
        """获取服务"""
        return self.services.get(name)
    
    def get_all_services(self) -> Dict[str, Any]:
        """获取所有服务"""
        return self.services.copy()
    
    # 配置访问
    def get_config(self) -> Config:
        """获取配置"""
        return self.config
    
    # 事件访问
    def get_events(self) -> EventManager:
        """获取事件管理器"""
        return self.events
    
    # 统计信息
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "sessions": self.get_session_count(),
            "users": self.get_user_count(),
            "services": list(self.services.keys()),
            "started_at": self._state.get("started_at"),
            "initialized": self.is_initialized()
        }
