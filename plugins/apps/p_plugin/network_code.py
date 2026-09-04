# -*- coding: utf-8 -*-
"""
P Plugin — Network Code Manager (adapted from Give U Face v2.6.0)
================================================================
网络识别码管理器 — 支持发现面板、网络连接、跨设备分享。

概念来源: Give U Face F2SP (Face-to-Server-Peer) + NetworkCodeManager
融合到 P Plugin 的「发现」面板中。

API: register(生成12位网络码), query(查询识别码), connect(建立连接),
     disconnect(断开), revoke(撤销)
"""

import json
import hashlib
import logging
import time
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger("p_plugin.network_code")


class NetworkCodeManager:
    """网络识别码管理器 — P Plugin「发现」功能核心"""
    
    CODE_TTL = timedelta(days=7)
    MAX_SESSIONS = 100
    MAX_CONNECTIONS = 10
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.local_sessions: Dict[str, dict] = {}
        self.network_index: Dict[str, str] = {}
        self._load()
        self._cleanup()
    
    def _load(self):
        file = self.data_dir / "network_codes.json"
        if file.exists():
            try:
                self.local_sessions = json.loads(file.read_text(encoding='utf-8'))
                self._rebuild_index()
                logger.info(f"[NetworkCode] 加载 {len(self.local_sessions)} 个会话")
            except Exception as e:
                logger.warning(f"[NetworkCode] 加载失败: {e}")
                self.local_sessions = {}
    
    def _save(self):
        file = self.data_dir / "network_codes.json"
        try:
            file.write_text(json.dumps(self.local_sessions, indent=2, ensure_ascii=False), encoding='utf-8')
        except Exception as e:
            logger.error(f"[NetworkCode] 保存失败: {e}")
    
    def _rebuild_index(self):
        self.network_index = {}
        for code, info in self.local_sessions.items():
            self.network_index[info.get("network_code", "")] = code
            self.network_index[info.get("short_code", "")] = code
    
    def _cleanup(self):
        now = datetime.now()
        expired = [c for c, i in self.local_sessions.items()
                   if datetime.fromisoformat(i.get("expires_at", "2000-01-01T00:00:00")) < now]
        for c in expired:
            del self.local_sessions[c]
        if expired:
            self._rebuild_index()
            self._save()
            logger.info(f"[NetworkCode] 清理 {len(expired)} 个过期会话")
    
    def _gen_codes(self, user_id: str, nickname: str = "") -> tuple:
        """生成网络识别码 (12位长码, 8位短码)"""
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        rnd = random.randint(1000, 9999)
        seed = f"{user_id}_{ts}_{rnd}"
        short = hashlib.md5(seed.encode()).hexdigest()[:8].upper()
        long_code = hashlib.sha256(seed.encode()).hexdigest()[:12].upper()
        return long_code, short
    
    # ── 核心 API ──
    
    def register(self, user_id: str, nickname: str = "", service_name: str = "") -> Dict:
        """注册网络识别码（用于「发现」面板分享）"""
        self._cleanup()
        
        user_sessions = [i for i in self.local_sessions.values() if i.get("user_id") == user_id]
        if len(user_sessions) >= self.MAX_SESSIONS:
            return {"success": False, "error": f"已达到最大数量 ({self.MAX_SESSIONS})"}
        
        long_code, short = self._gen_codes(user_id, nickname)
        code = f"NC_{long_code}"
        
        session = {
            "session_code": code,
            "network_code": long_code,
            "short_code": short,
            "user_id": user_id,
            "nickname": nickname or user_id,
            "service_name": service_name,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + self.CODE_TTL).isoformat(),
            "status": "active",
            "connections": [],
            "connection_count": 0,
            "type": "network"
        }
        
        self.local_sessions[code] = session
        self._rebuild_index()
        self._save()
        
        logger.info(f"[NetworkCode] {user_id} 注册码 {long_code} ({short})")
        
        return {
            "success": True,
            "session_code": code,
            "network_code": long_code,
            "short_code": short,
            "user_id": user_id,
            "nickname": nickname or user_id,
            "share_text": f"P Chat 网络码: {short}",
            "expires_at": session["expires_at"]
        }
    
    def query(self, code: str) -> Dict:
        """查询识别码（发现面板输入码后搜索）"""
        code = code.upper().strip()
        self._cleanup()
        
        session_code = self.network_index.get(code)
        if not session_code:
            return {"success": True, "exists": False, "message": "识别码不存在或已过期"}
        
        info = self.local_sessions.get(session_code)
        if not info:
            return {"success": True, "exists": False, "message": "会话数据丢失"}
        
        return {
            "success": True,
            "exists": True,
            "network_code": info["network_code"],
            "short_code": info["short_code"],
            "user_id": info["user_id"],
            "nickname": info["nickname"],
            "service_name": info.get("service_name", ""),
            "status": info["status"],
            "connection_count": info["connection_count"],
            "created_at": info["created_at"],
            "expires_at": info["expires_at"]
        }
    
    def connect(self, code: str, connector_id: str, connector_nick: str = "") -> Dict:
        """连接到网络码（对方同意后建立连接）"""
        code = code.upper().strip()
        self._cleanup()
        
        session_code = self.network_index.get(code)
        if not session_code:
            return {"success": False, "error": "识别码不存在或已过期"}
        
        info = self.local_sessions.get(session_code)
        if not info:
            return {"success": False, "error": "会话数据丢失"}
        
        if info["status"] != "active":
            return {"success": False, "error": f"会话状态: {info['status']}"}
        
        if len(info["connections"]) >= self.MAX_CONNECTIONS:
            return {"success": False, "error": "连接数量已达上限"}
        
        # Check existing
        existing = next((c for c in info["connections"] if c["connector_id"] == connector_id), None)
        if existing:
            existing["last_seen"] = datetime.now().isoformat()
            self._save()
            return {"success": True, "already_connected": True}
        
        connection = {
            "connector_id": connector_id,
            "connector_nick": connector_nick or connector_id,
            "connected_at": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat()
        }
        info["connections"].append(connection)
        info["connection_count"] = len(info["connections"])
        self._save()
        
        logger.info(f"[NetworkCode] {connector_id} → {info['user_id']}")
        return {"success": True, "connected": True, "owner_nick": info["nickname"]}
    
    def disconnect(self, session_code: str, connector_id: str) -> Dict:
        """断开网络连接"""
        info = self.local_sessions.get(session_code)
        if not info:
            return {"success": False, "error": "会话不存在"}
        
        info["connections"] = [c for c in info["connections"] if c["connector_id"] != connector_id]
        info["connection_count"] = len(info["connections"])
        self._save()
        return {"success": True}
    
    def revoke(self, session_code: str, user_id: str) -> Dict:
        """撤销识别码"""
        info = self.local_sessions.get(session_code)
        if not info:
            return {"success": False, "error": "会话不存在"}
        if info["user_id"] != user_id:
            return {"success": False, "error": "无权限"}
        
        info["status"] = "revoked"
        info["revoked_at"] = datetime.now().isoformat()
        info["connections"] = []
        info["connection_count"] = 0
        self._save()
        self._rebuild_index()
        return {"success": True, "message": "已撤销"}
    
    def my_codes(self, user_id: str) -> Dict:
        """获取我的所有识别码"""
        self._cleanup()
        codes = []
        for code, info in self.local_sessions.items():
            if info.get("user_id") == user_id:
                codes.append({
                    "session_code": code,
                    "network_code": info["network_code"],
                    "short_code": info["short_code"],
                    "nickname": info["nickname"],
                    "status": info["status"],
                    "connection_count": info["connection_count"],
                    "created_at": info["created_at"],
                    "expires_at": info["expires_at"]
                })
        codes.sort(key=lambda x: x["created_at"], reverse=True)
        return {"success": True, "user_id": user_id, "codes": codes, "total": len(codes)}
    
    def stats(self) -> Dict:
        """统计信息"""
        self._cleanup()
        return {
            "success": True,
            "total_sessions": len(self.local_sessions),
            "active_sessions": sum(1 for s in self.local_sessions.values() if s["status"] == "active"),
            "total_connections": sum(s["connection_count"] for s in self.local_sessions.values())
        }
    
    def discover_services(self) -> Dict:
        """发现可用服务（所有公开的活跃网络码）"""
        self._cleanup()
        services = []
        for code, info in self.local_sessions.items():
            if info["status"] == "active":
                services.append({
                    "network_code": info["network_code"],
                    "short_code": info["short_code"],
                    "nickname": info["nickname"],
                    "service_name": info.get("service_name", ""),
                    "connection_count": info["connection_count"],
                    "created_at": info["created_at"]
                })
        services.sort(key=lambda x: x["created_at"], reverse=True)
        return {"success": True, "services": services, "total": len(services)}


# ── 全局单例 ──
_instance: Optional[NetworkCodeManager] = None

def get_manager(data_dir: Path = None) -> NetworkCodeManager:
    global _instance
    if _instance is None:
        _instance = NetworkCodeManager(data_dir or Path(__file__).parent / "data" / "network")
    return _instance