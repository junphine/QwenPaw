"""
P Plugin v5.1.1 — P-Chat Agent Install/Manage + Router Fix
=====================================
Migrated to use PawApp SDK patterns:
- ``@app.route`` decorator for HTTP routes
- ``ctx=Depends(get_ctx)`` for dependency injection
- ``SSEChannel`` for real-time streaming
- ``@app.tool`` for agent tools
- Lifecycle hooks (on_launch / on_terminate)
- Backward-compatible with QwenPaw v1.x via ``_pawapp_compat.py`` bridge

When QwenPaw v2.0.1+ (Python ≥3.11) is available, just change import to:
    from qwenpaw.pawapp import PawApp, get_ctx, SSEChannel
    from qwenpaw.pawapp.task import SSEChannel

Core functionality:
- AI agents can generate files via [FILE:filename]...[/FILE] format
- Concurrent agent replies with staggered delays
- Enhanced context formatting with round indicators
- Multi-channel: Console, WeChat, DingTalk, Feishu, etc.
- Only room creator can manage agents (add/remove)
"""
import logging
import os
import json
import uuid
import asyncio
import re
import base64
import mimetypes
import hashlib
import secrets
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
import httpx

from fastapi import APIRouter, Request, HTTPException, UploadFile, File, Form, Query, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse, HTMLResponse
from pydantic import BaseModel, Field

# ── PawApp SDK (compatibility bridge) ───────────────────────────────
from ._pawapp_compat import PawApp, get_ctx, SSEChannel, PawAppContext
from .network_code import get_manager as get_network_manager
from .game_agent import game_master

logger = logging.getLogger("p_plugin")

# ============ Configuration ============
CURRENT_VERSION = "5.3.0"
PLUGIN_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = PLUGIN_DIR / "data"
FILES_DIR = DATA_DIR / "files"
DATA_DIR.mkdir(parents=True, exist_ok=True)
FILES_DIR.mkdir(parents=True, exist_ok=True)
NETWORK_DATA_DIR = DATA_DIR / "network"
NETWORK_DATA_DIR.mkdir(parents=True, exist_ok=True)

def _get_api_base() -> str:
    """Dynamic API base detection (TeamChat v5.2.2 pattern)"""
    try:
        from qwenpaw.config.utils import read_last_api
        last = read_last_api()
        if last:
            host, port = last
            return f"http://{host}:{port}"
    except:
        pass
    return os.environ.get("QWENPAW_API", "http://127.0.0.1:8088")

QWENPAW_API_BASE = _get_api_base()
logger.info(f"[P] API base detected: {QWENPAW_API_BASE}")

# ============ PawApp SDK ============
app = PawApp(name="P", app_id="p_plugin", data_dir=DATA_DIR)
router = APIRouter()

# Include legacy router under PawApp (routes still use @router)
# New routes should use @app.route with ctx injection
app.include_router(router)


@app.on_launch
async def _on_launch():
    """PawApp lifecycle: startup — load persisted data."""
    logger.info("[P] Plugin started via PawApp SDK")
    _load_data()
    await _ensure_official_room()


@app.on_terminate
async def _on_terminate():
    """PawApp lifecycle: shutdown — persist data."""
    logger.info("[P] Plugin shutting down, saving data...")
    _save_data()


# ============ PawApp SSE event stream ============
_active_sse_channels: Dict[str, SSEChannel] = {}


# === PawApp SSE routes (disabled for type=general — would fail FastAPI import) ===
# These @app.route decorators use PawAppContext which is a dataclass,
# not a valid Pydantic field. FastAPI rejects them at import time,
# preventing the entire module from loading.
# Since type=general uses PPlugin.register() for routing, these are not needed.
#
# @app.route("/events/{client_id}", methods=["GET"])
# async def stream_sse_events(ctx: PawAppContext, client_id: str = ""):
#     ...

# @app.route("/events/{client_id}/subscribe", methods=["POST"])
# async def subscribe_room_events(client_id: str, request: Request):
#     ...

# Minimal stub functions to keep references alive
async def stream_sse_events_stub():
    pass
async def subscribe_room_events_stub():
    pass


_sse_subscriptions: Dict[str, Set[str]] = {}


async def broadcast_via_sse(room_id: str, event_type: str, data: dict):
    """Broadcast event to all SSE clients subscribed to a room."""
    message = {"type": event_type, "room_id": room_id, **data}
    subscribers = _sse_subscriptions.get(room_id, set())
    for client_id in list(subscribers):
        channel = _active_sse_channels.get(client_id)
        if channel and not channel._closed:
            await channel.send_event(message)
        else:
            subscribers.discard(client_id)

# WeChat user room mapping
_wechat_user_rooms: Dict[str, str] = {}

# ============ Enums ============
class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    VOICE = "voice"
    VIDEO = "video"
    LOCATION = "location"
    SYSTEM = "system"

class RoomType(str, Enum):
    OFFICIAL = "official"
    PUBLIC = "public"
    PRIVATE = "private"

# ============ Models ============
class AgentConfig(BaseModel):
    id: str
    name: str
    icon: str = "🤖"
    color: str = "#07C160"
    description: str = ""
    personality: str = "helpful and friendly"
    is_active: bool = True
    auto_reply: bool = True
    added_by: Optional[str] = None
    added_at: Optional[str] = None

class PanelType(str, Enum):
    CHAT = "chat"       # text chat panel (default)
    WEBVIEW = "webview" # embedded web page (like Tailchat webview plugin)
    CUSTOM = "custom"   # custom HTML panel

class PanelConfig(BaseModel):
    id: str
    name: str
    type: PanelType = PanelType.CHAT
    url: Optional[str] = None       # URL for webview panel
    html: Optional[str] = None      # custom HTML content
    icon: str = "💬"                # panel icon (emoji)
    order: int = 0                  # display order
    created_at: str = ""

class Room(BaseModel):
    id: str
    name: str
    type: RoomType
    creator_id: str
    creator_nickname: str
    agents: List[AgentConfig] = []
    panels: List[PanelConfig] = []   # ← NEW: panel system (Tailchat-style)
    password: Optional[str] = None
    announcement: Optional[str] = None  # 公告内容（支持 Markdown）
    # ── 游戏场景系统 ──
    scene_id: Optional[str] = None      # 当前场景ID
    scene_theme: Optional[str] = None   # 场景主题CSS
    game_state: Optional[dict] = None   # 游戏状态（道具、任务、进度等）
    created_at: str
    updated_at: str

class Message(BaseModel):
    id: str
    room_id: str
    sender_id: str
    sender_name: str
    content: str
    type: MessageType = MessageType.TEXT
    mentions: List[str] = []
    timestamp: str
    # File / media attachments
    file_id: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    duration: Optional[int] = None  # voice/video duration in seconds
    mime_type: Optional[str] = None
    # WeChat-style features
    recalled: bool = False          # message recalled (within 2 min)
    reply_to: Optional[str] = None  # ID of message being replied to
    latitude: Optional[float] = None  # location share
    longitude: Optional[float] = None

class FileInfo(BaseModel):
    id: str
    room_id: str
    sender_id: str
    sender_name: str
    file_name: str
    file_size: int
    mime_type: str
    created_at: str

# ============ Storage ============
_rooms: Dict[str, Room] = {}
_messages: Dict[str, List[Message]] = {}
_files: Dict[str, FileInfo] = {}
_qwenpaw_agents_cache: Optional[List[AgentConfig]] = None

# Agent conversation context storage: room_id -> agent_id -> [messages]
_agent_contexts: Dict[str, Dict[str, List[Dict]]] = {}

# Game progress storage: room_id -> user_id -> game_progress
_game_progress: Dict[str, Dict[str, Dict]] = {}

# ============ Game System ============
class GameProgress:
    """Player's game progress in a room"""
    def __init__(self, user_id: str, room_id: str, template_id: str = "misty_town"):
        self.user_id = user_id
        self.room_id = room_id
        self.template_id = template_id
        self.current_chapter = "prologue"
        self.completed_nodes: Set[str] = set()
        self.npc_affections: Dict[str, int] = {}
        self.unlocked_secrets: Set[str] = set()
        self.game_started = False
        self.start_time = None
        
        # Initialize NPC affections from template
        self._init_from_template()
    
    def _init_from_template(self):
        """Initialize from game template"""
        templates_file = PLUGIN_DIR / "game_templates.json"
        if templates_file.exists():
            try:
                with open(templates_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                template = data.get("templates", {}).get(self.template_id, {})
                config = template.get("default_config", {})
                
                for npc in config.get("npcs", []):
                    self.npc_affections[npc.get("id")] = npc.get("initial_affection", 0)
            except Exception as e:
                logger.error(f"[P] Failed to init game progress: {e}")
                # Default NPCs for misty_town
                self.npc_affections = {
                    "keeper": 0,
                    "ling": 5,
                    "xiaolu": 15,
                    "mayor": -10
                }
    
    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "room_id": self.room_id,
            "template_id": self.template_id,
            "current_chapter": self.current_chapter,
            "completed_nodes": list(self.completed_nodes),
            "npc_affections": self.npc_affections,
            "unlocked_secrets": list(self.unlocked_secrets),
            "game_started": self.game_started,
            "start_time": self.start_time
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "GameProgress":
        gp = cls(data.get("user_id"), data.get("room_id"), data.get("template_id", "misty_town"))
        gp.current_chapter = data.get("current_chapter", "prologue")
        gp.completed_nodes = set(data.get("completed_nodes", []))
        gp.npc_affections = data.get("npc_affections", gp.npc_affections)
        gp.unlocked_secrets = set(data.get("unlocked_secrets", []))
        gp.game_started = data.get("game_started", False)
        gp.start_time = data.get("start_time")
        return gp
    
    def update_affection(self, npc_id: str, delta: int) -> int:
        """Update NPC affection and return new value"""
        if npc_id in self.npc_affections:
            self.npc_affections[npc_id] = max(-100, min(100, self.npc_affections[npc_id] + delta))
            return self.npc_affections[npc_id]
        return 0
    
    def get_affection_tier(self, npc_id: str) -> str:
        """Get affection tier label"""
        affection = self.npc_affections.get(npc_id, 0)
        if affection <= -20:
            return "敌视"
        elif affection < 0:
            return "冷漠"
        elif affection <= 20:
            return "中立"
        elif affection <= 60:
            return "友善"
        else:
            return "亲密"
    
    def start_game(self):
        """Mark game as started"""
        self.game_started = True
        self.start_time = datetime.now().isoformat()
    
    def complete_node(self, node_id: str):
        """Mark a node as completed"""
        self.completed_nodes.add(node_id)
    
    def unlock_secret(self, secret_id: str):
        """Unlock a secret"""
        self.unlocked_secrets.add(secret_id)


def get_game_progress(room_id: str, user_id: str) -> Optional[GameProgress]:
    """Get or create game progress for a user in a room"""
    if room_id not in _game_progress:
        _game_progress[room_id] = {}
    
    if user_id not in _game_progress[room_id]:
        # Check if this is a game room (has game_master agent)
        room = _rooms.get(room_id)
        if room and any(a.id == "game_master" for a in room.agents):
            _game_progress[room_id][user_id] = GameProgress(user_id, room_id)
        else:
            return None
    
    return _game_progress[room_id][user_id]


def handle_game_command(room_id: str, user_id: str, user_name: str, message: str) -> Optional[str]:
    """Handle game commands, returns response message or None if not a command"""
    msg_lower = message.lower().strip()
    
    # Get game progress
    progress = get_game_progress(room_id, user_id)
    if not progress:
        return None
    
    # Command: 开始游戏 / 启动游戏 / start game
    if any(cmd in msg_lower for cmd in ["开始游戏", "启动游戏", "start game", "开始"]):
        if progress.game_started:
            return f"🎮 游戏已经开始啦！当前进度：{progress.current_chapter}\n\n💡 提示：@NPC名字 即可与角色对话"
        
        progress.start_game()
        progress.complete_node("intro")
        
        return """🎮 **游戏开始！欢迎来到迷雾小镇**

浓雾笼罩着这座古老的小镇，街道上空无一人。远处隐约传来钟声……

🎯 **游戏目标**：
• 与四位关键NPC对话，提升好感度
• 收集线索，揭开小镇背后的秘密
• 解锁新章节，推进剧情

🎭 **四位NPC**：
• @老陈 🏛️ 灯塔守塔人（初始好感：冷漠）
• @林医生 🩺 诊所医生（初始好感：中立）
• @小鹿 ☕ 咖啡馆老板娘（初始好感：友善）
• @镇长 🎩 镇公所镇长（初始好感：敌视）

💡 **提示**：
• 点击NPC头像或输入 @名字 开始对话
• 好感度越高，NPC越愿意透露秘密
• 使用 @游戏大师 提示 获取帮助

**祝你好运！揭开迷雾背后的真相……**"""
    
    # Command: 查看进度 / 进度 / progress
    if any(cmd in msg_lower for cmd in ["查看进度", "进度", "progress", "状态"]):
        if not progress.game_started:
            return "🎮 游戏还未开始！发送「开始游戏」启动"
        
        # Build progress display
        total_nodes = 9  # Approximate
        completed = len(progress.completed_nodes)
        secrets = len(progress.unlocked_secrets)
        
        npc_status = []
        for npc_id, affection in progress.npc_affections.items():
            tier = progress.get_affection_tier(npc_id)
            npc_name = {"keeper": "老陈", "ling": "林医生", "xiaolu": "小鹿", "mayor": "镇长"}.get(npc_id, npc_id)
            emoji = {"keeper": "🏛️", "ling": "🩺", "xiaolu": "☕", "mayor": "🎩"}.get(npc_id, "🤖")
            npc_status.append(f"{emoji} {npc_name}: {affection} ({tier})")
        
        return f"""📊 **游戏进度**

📖 当前章节：**{progress.current_chapter}**
✅ 已完成节点：{completed}/{total_nodes}
🔓 已解锁秘密：{secrets}/12

🎭 **NPC好感度**：
{chr(10).join(npc_status)}

💡 发送「提示」获取游戏建议"""
    
    # Command: 提示 / hint / help
    if any(cmd in msg_lower for cmd in ["提示", "hint", "help", "帮助", "怎么办"]):
        if not progress.game_started:
            return "🎮 游戏还未开始！发送「开始游戏」启动"
        
        # Generate contextual hint
        hints = [
            "💡 试着与好感度较高的NPC深入对话，他们更可能透露秘密",
            "💡 每个NPC都有3个秘密，好感度达到阈值后自动解锁",
            "💡 收集2个线索后可以解锁第一章：疑云密布",
            "💡 镇长的初始好感度最低，需要更多耐心建立信任",
            "💡 小鹿初始好感度最高，是获取初期线索的好选择",
            "💡 尝试不同的对话方式，礼貌和真诚能提升好感度",
            "💡 使用「查看进度」随时了解游戏状态"
        ]
        import random
        return random.choice(hints)
    
    # Command: 创建游戏区
    if "创建游戏区" in message or "create game" in msg_lower:
        # Extract game name
        name_match = re.search(r'创建游戏区\s+(.+)', message)
        game_name = name_match.group(1).strip() if name_match else f"{user_name}的游戏区"
        
        # This would create a new room - for now just acknowledge
        return f"🎮 **创建游戏区功能开发中**\n\n游戏区名称：{game_name}\n\n💡 当前可以在本房间体验「迷雾小镇」模板游戏。完整自定义游戏区功能即将上线！"
    
    # Command: 游戏规则 / 怎么玩
    if any(cmd in msg_lower for cmd in ["规则", "怎么玩", "玩法", "教程"]):
        return """📖 **迷雾小镇 游戏规则**

🎯 **基本玩法**：
1. 发送「开始游戏」启动
2. @NPC名字 + 你想说的话（如：@老陈 你好）
3. 根据回复选择对话策略
4. 提升好感度解锁秘密

📈 **好感度系统**：
• 敌视(-100~-20)：几乎不透露信息
• 冷漠(-20~0)：回避问题
• 中立(0~20)：基础对话
• 友善(20~60)：愿意分享线索
• 亲密(60~100)：透露核心秘密

🔓 **秘密解锁**：
• 每个NPC有3个秘密
• 好感度达标后自动解锁
• 收集12个秘密解锁最终结局

💡 **快捷指令**：
• @游戏大师 查看进度
• @游戏大师 提示
• @游戏大师 开始游戏"""
    
    return None


# ============ WebSocket Manager ============
class ConnectionManager:
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}
        self.room_subscriptions: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.connections[client_id] = websocket
    
    def disconnect(self, client_id: str):
        if client_id in self.connections:
            del self.connections[client_id]
        for subs in self.room_subscriptions.values():
            subs.discard(client_id)
    
    def subscribe(self, client_id: str, room_id: str):
        if room_id not in self.room_subscriptions:
            self.room_subscriptions[room_id] = set()
        self.room_subscriptions[room_id].add(client_id)
    
    async def broadcast_to_room(self, room_id: str, message: dict):
        if room_id not in self.room_subscriptions:
            return
        disconnected = []
        for client_id in self.room_subscriptions[room_id]:
            if client_id in self.connections:
                try:
                    await self.connections[client_id].send_json(message)
                except:
                    disconnected.append(client_id)
            else:
                disconnected.append(client_id)
        for client_id in disconnected:
            self.room_subscriptions[room_id].discard(client_id)

manager = ConnectionManager()
# ★ v5.1.1: do NOT reassign router — keep the original (line 78) which is already included
# via app.include_router(). All @router decorators above and below share this same instance.
# If we reassign router = APIRouter() here, all later routes end up on a NEW router
# that is never registered, causing those endpoints to 404.

# ============ Helpers ============
def _generate_id() -> str:
    return f"{uuid.uuid4().hex[:16]}"

def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def _save_data():
    try:
        data = {
            "rooms": {k: v.dict() for k, v in _rooms.items()},
            "messages": {k: [m.dict() for m in v] for k, v in _messages.items()},
            "files": {k: v.dict() for k, v in _files.items()},
            "share_tokens": dict(_share_tokens),
            "game_progress": {room_id: {user_id: progress.to_dict() for user_id, progress in room_progress.items()} 
                             for room_id, room_progress in _game_progress.items()},
        }
        with open(DATA_DIR / "data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"[P] Save failed: {e}")

def _load_data():
    global _rooms, _messages, _files, _share_tokens
    try:
        data_file = DATA_DIR / "data.json"
        if data_file.exists():
            with open(data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                _rooms = {k: Room(**v) for k, v in data.get("rooms", {}).items()}
                _messages = {k: [Message(**m) for m in v] for k, v in data.get("messages", {}).items()}
                _files = {k: FileInfo(**v) for k, v in data.get("files", {}).items()}
                _share_tokens = data.get("share_tokens", {})
    except Exception as e:
        logger.error(f"[P] Load failed: {e}")

async def _ensure_official_room():
    """Auto-create AND refresh official room with all real agents on every launch.
    
    v5.0.2: Changed from 'create-once' to 'sync-every-launch'.
    The official room now gets real agents on every startup, replacing stale fallback agents.
    """
    global _rooms, _messages
    try:
        # Always fetch real agents (with retry for slow-start API)
        agents = await fetch_qwenpaw_agents()
        logger.info(f"[P] Official room sync: fetched {len(agents)} real agents")
        
        # Find existing official room
        official_room = None
        for r in _rooms.values():
            if r.type == RoomType.OFFICIAL:
                official_room = r
                break
        
        now = datetime.now().isoformat()
        
        if official_room:
            # Refresh agents in existing official room
            old_count = len(official_room.agents)
            old_ids = {a.id for a in official_room.agents}
            new_ids = {a.id for a in agents}
            
            if old_ids != new_ids or old_count != len(agents):
                official_room.agents = agents
                official_room.updated_at = now
                logger.info(f"[P] Official room agents refreshed: {old_count} → {len(agents)} (mock→real)")
                
                _messages.setdefault(official_room.id, []).append(Message(
                    id=_generate_id(),
                    room_id=official_room.id,
                    sender_id="system",
                    sender_name="System",
                    content=f"🔄 官方聊天室智能体已刷新！当前共 {len(agents)} 个真实智能体。",
                    type=MessageType.SYSTEM,
                    timestamp=now
                ))
                _save_data()
            else:
                logger.info(f"[P] Official room agents unchanged ({len(agents)} agents)")
            
            # v5.2.0: Ensure default panels exist (补上旧数据缺失的默认面板)
            has_chat_panel = any(p.type == PanelType.CHAT for p in official_room.panels)
            has_discover_panel = any(p.name == "🌐 发现" for p in official_room.panels)
            panels_changed = False
            
            if not has_chat_panel:
                official_room.panels.append(PanelConfig(
                    id=f"panel_{_generate_id()}", name="💬 聊天",
                    type=PanelType.CHAT, icon="💬", order=0, created_at=now
                ))
                panels_changed = True
                logger.info("[P] Official room: added default chat panel")
            
            if not has_discover_panel:
                official_room.panels.append(PanelConfig(
                    id=f"panel_{_generate_id()}", name="🌐 发现",
                    type=PanelType.CUSTOM, icon="🌐", url="", order=1, created_at=now
                ))
                panels_changed = True
                logger.info("[P] Official room: added default discover panel")
            
            if panels_changed:
                official_room.updated_at = now
                _save_data()
                logger.info("[P] Official room default panels restored")
            
            # v5.2.0: Always ensure P-Chat agent is in official room on every startup
            try:
                _ensure_pchat_in_official_room()
            except:
                pass
            
            return
        
        # No official room exists — create one
        room_id = f"official_{_generate_id()}"
        
        default_panels = [
            PanelConfig(id=f"panel_{_generate_id()}", name="💬 聊天", type=PanelType.CHAT, icon="💬", order=0, created_at=now),
            PanelConfig(id=f"panel_{_generate_id()}", name="🌐 发现", type=PanelType.CUSTOM, icon="🌐", 
                       url="", order=1, created_at=now)
        ]
        
        room = Room(
            id=room_id,
            name="官方聊天室",
            type=RoomType.OFFICIAL,
            creator_id="system",
            creator_nickname="System",
            agents=agents,
            panels=default_panels,
            password=None,
            created_at=now,
            updated_at=now
        )
        
        _rooms[room_id] = room
        _messages[room_id] = [Message(
            id=_generate_id(),
            room_id=room_id,
            sender_id="system",
            sender_name="System",
            content=f"🏠 官方聊天室已创建！已自动加入 {len(agents)} 个真实智能体。支持自由增减智能体、分享链接等。",
            type=MessageType.SYSTEM,
            timestamp=now
        )]
        
        _save_data()
        logger.info(f"[P] Official room '{room_id}' created with {len(agents)} agents")
        
        # Auto-add P-Chat Agent to official room (silently — best effort)
        try:
            _ensure_pchat_in_official_room()
        except:
            pass
    
    except Exception as e:
        logger.error(f"[P] Failed to create/refresh official room: {e}")

# ============ QwenPaw Integration ============

async def fetch_qwenpaw_agents(retry_on_empty: bool = True) -> List[AgentConfig]:
    """Fetch real agents from QwenPaw with retry resilience.
    
    v5.0.2: Added retry logic (3 attempts with 2s backoff) for race condition
    where the QwenPaw API server starts slower than plugin loading.
    Also clears cache on subsequent calls to allow re-fetching.
    """
    global _qwenpaw_agents_cache
    
    MAX_RETRIES = 3
    RETRY_DELAY = 2.0  # seconds between retries
    
    # Detect the current API base (dynamic — may change between restarts)
    api_base = _get_api_base()
    
    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{api_base}/api/agents")
                if resp.status_code == 200:
                    data = resp.json()
                    raw_agents = data.get("agents", [])
                    
                    if not raw_agents:
                        if attempt < MAX_RETRIES - 1 and retry_on_empty:
                            logger.warning(f"[P] Empty agents list (attempt {attempt+1}/{MAX_RETRIES}), retrying in {RETRY_DELAY}s...")
                            await asyncio.sleep(RETRY_DELAY)
                            continue
                        logger.warning("[P] Agents API returned empty list after all retries")
                        break
                    
                    result = []
                    for a in raw_agents:
                        agent = AgentConfig(
                            id=a.get("id"),
                            name=a.get("name", "AI"),
                            icon=a.get("icon", "🤖"),
                            color=a.get("color", "#07C160"),
                            description=a.get("description", ""),
                            personality=a.get("personality", "helpful"),
                            is_active=True,
                            auto_reply=True
                        )
                        result.append(agent)
                    
                    _qwenpaw_agents_cache = result
                    logger.info(f"[P] ✅ Loaded {len(result)} real agents from QwenPaw (attempt {attempt+1})")
                    return result
                else:
                    logger.warning(f"[P] Agents API returned {resp.status_code} (attempt {attempt+1})")
        except Exception as e:
            logger.warning(f"[P] fetch agents attempt {attempt+1}/{MAX_RETRIES} failed: {e}")
        
        if attempt < MAX_RETRIES - 1:
            await asyncio.sleep(RETRY_DELAY)
    
    # All retries exhausted — use empty list (no mock agents!)
    # Official room will be created without agents; user can add from selector
    logger.warning("[P] All agent fetch attempts failed. Official room will have no agents — user must manually add.")
    return []

async def call_agent_with_context(agent_id: str, agent_name: str, personality: str, 
                                   room_id: str, user_msg: Message, all_messages: List[Message]) -> str:
    """Call agent with shared conversation context - bulletproof version
    
    Enhanced with file/image context awareness (from TeamChat v5.2.2 pattern)
    """
    # ===== Step 0: Setup agent context (safe) =====
    try:
        if room_id not in _agent_contexts:
            _agent_contexts[room_id] = {}
        if agent_id not in _agent_contexts[room_id]:
            _agent_contexts[room_id][agent_id] = []
    except Exception:
        pass
    
    # ===== Step 1: Build conversation history with file/image context (safe) =====
    conversation_history = []
    file_context_parts = []  # Collect file/image info for context
    try:
        context_messages = all_messages[-20:]  # Last 20 messages
        for msg in context_messages:
            if hasattr(msg, 'type') and msg.type == MessageType.SYSTEM:
                continue
            sender_id = getattr(msg, 'sender_id', '')
            sender_name = getattr(msg, 'sender_name', '')
            content = getattr(msg, 'content', '')
            msg_type = getattr(msg, 'type', 'text')
            
            # Include file/image info in context for agent awareness
            if msg_type in (MessageType.FILE, MessageType.IMAGE):
                file_id = getattr(msg, 'file_id', '')
                file_name = getattr(msg, 'file_name', '')
                if file_id and file_name:
                    file_context_parts.append(f"📎 {sender_name} 分享了文件/图片: {file_name} (file_id: {file_id})")
            
            role = "assistant" if sender_id != user_msg.sender_id else "user"
            conversation_history.append({
                "role": role,
                "name": sender_name or "User",
                "content": content[:500]  # Truncate long messages
            })
    except Exception:
        pass
    
    # Add current user message (check for file/image in current message)
    try:
        current_content = getattr(user_msg, 'content', '') if user_msg else ''
        current_msg_type = getattr(user_msg, 'type', 'text') if user_msg else 'text'
        
        if current_msg_type in (MessageType.FILE, MessageType.IMAGE):
            file_id = getattr(user_msg, 'file_id', '')
            file_name = getattr(user_msg, 'file_name', '')
            if file_id and file_name:
                file_context_parts.append(f"📎 当前用户分享了文件/图片: {file_name} (file_id: {file_id})")
        
        conversation_history.append({
            "role": "user",
            "name": getattr(user_msg, 'sender_name', 'User'),
            "content": current_content
        })
    except Exception:
        pass
    
    current_sender = getattr(user_msg, 'sender_name', 'User') if user_msg else 'User'
    
    # Format enhanced context (from TeamChat v5.2.2 pattern)
    enhanced_context = ""
    try:
        context_messages_formatted = all_messages[-20:] if all_messages else []
        enhanced_context = _format_context_for_agent(agent_name, context_messages_formatted, current_content)
    except Exception:
        pass
    
    # Build file context string for agent awareness
    file_context_str = ""
    if file_context_parts:
        file_context_str = "\n【群聊中的文件/图片】\n" + "\n".join(file_context_parts) + "\n"
    
    file_gen_guide = """
【重要：文件生成格式】
当用户要求你创建文件、写代码、保存内容到文件时，你必须使用以下精确格式：

[FILE:文件名.扩展名]
文件内容写在这里...
[/FILE]

示例 - 写Python脚本：
[FILE:hello.py]
print("Hello World")
[/FILE]

注意：
1. 必须使用 [FILE:文件名] 开头
2. 必须使用 [/FILE] 结尾
3. 文件名要包含扩展名（如.py, .txt, .md）
4. 文件内容放在中间，不要加代码块标记
"""
    
    # ===== Step 2: Call real QwenPaw agent via /api/console/chat (TeamChat v5.2.2 SSE pattern) =====
    reply = None
    try:
        # Build user nickname from context
        user_nickname = current_sender
        try:
            for msg in reversed(context_messages_formatted):
                mtype = getattr(msg, 'type', None)
                if mtype == MessageType.TEXT or str(mtype) == 'text':
                    sid = getattr(msg, 'sender_id', '')
                    if not sid.startswith('agent:'):
                        user_nickname = getattr(msg, 'sender_name', current_sender)
                        break
        except Exception:
            pass
        
        system_prompt = f"""你是一个群聊中的智能体成员，名叫"{agent_name}"。

以下是群聊历史记录，请根据这些上下文来回复当前消息：

{enhanced_context if enhanced_context else '（暂无历史消息）'}
{file_context_str}{file_gen_guide}

【重要】
- 当前用户的昵称是：{user_nickname}
- 回复时可以直接称呼用户为"{user_nickname}"
- 请以"{agent_name}"的身份，根据以上群聊历史，回复当前消息
- 回复要自然、简洁，像群聊对话一样
- 如果需要生成文件，请使用 [FILE:文件名]...[/FILE] 格式"""
        
        # Build QwenPaw console chat request format
        input_messages = [
            {"role": "system", "content": [{"type": "text", "text": system_prompt}]},
            {"role": "user", "content": [{"type": "text", "text": current_content}]}
        ]
        payload = {
            "session_id": f"p_plugin:{room_id}:{agent_id}",
            "input": input_messages,
        }
        
        # Look up agent description/personality for character injection
        agent_desc = ""
        agent_personality = ""
        try:
            room = _rooms.get(room_id)
            if room:
                for ag in room.agents:
                    if ag.id == agent_id:
                        agent_desc = ag.description or ""
                        agent_personality = ag.personality or ""
                        break
        except Exception:
            pass
        
        # Helper: parse SSE stream and extract text
        async def _parse_sse(response):
            all_text = []
            async for line in response.aiter_lines():
                line = line.strip()
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        output = data.get("output", [])
                        if output:
                            last_msg = output[-1]
                            if last_msg.get("role") == "assistant":
                                for block in last_msg.get("content", []):
                                    if block.get("type") == "text":
                                        text = block.get("text", "")
                                        if text:
                                            all_text.append(text)
                    except Exception:
                        continue
            return "".join(all_text).strip() if all_text else ""
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            # ===== Attempt 1: Call with real agent ID (works for QwenPaw agents) =====
            try:
                headers = {"Content-Type": "application/json", "X-Agent-Id": agent_id}
                async with client.stream(
                    "POST",
                    f"{QWENPAW_API_BASE}/api/console/chat",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status_code == 200:
                        reply = await _parse_sse(response)
                        if reply:
                            logger.info(f"[P] ✅ Agent {agent_name} replied via console/chat with agent_id ({len(reply)} chars)")
                    elif response.status_code in (400, 404):
                        # Agent not found — will retry below without agent_id
                        logger.info(f"[P] Agent '{agent_id}' not found in QwenPaw, retrying with default agent + character prompt")
            except Exception as e:
                logger.warning(f"[P] console/chat (agent_id={agent_id}) failed: {e}")
            
            # ===== Attempt 2: If failed, retry WITHOUT X-Agent-Id (default agent + character personality) =====
            if not reply or not reply.strip():
                try:
                    # Build richer system prompt with character personality
                    char_prompt = f"""你正在扮演一个名叫"{agent_name}"的角色，参与一场群聊对话。

【你的角色设定】
名字：{agent_name}
{f'性格：{agent_personality}' if agent_personality else ''}
{f'背景：{agent_desc[:500]}' if agent_desc else ''}

【群聊上下文】
{enhanced_context if enhanced_context else '（暂无历史消息）'}
{file_context_str}

【回复要求】
- 你必须始终以"{agent_name}"的身份回复，保持角色一致性
- 回复要自然、简洁，像群聊对话一样（2-5句话）
- 可以根据角色性格展现情绪和态度
- 当前用户的昵称是：{user_nickname}，可以直接称呼
- 不要说"作为AI"或"我是语言模型"之类的话
- 如果需要生成文件，请使用 [FILE:文件名]...[/FILE] 格式"""
                    
                    fallback_payload = {
                        "session_id": f"p_plugin:{room_id}:{agent_id}",
                        "input": [
                            {"role": "system", "content": [{"type": "text", "text": char_prompt}]},
                            {"role": "user", "content": [{"type": "text", "text": current_content}]}
                        ],
                    }
                    headers = {"Content-Type": "application/json"}
                    async with client.stream(
                        "POST",
                        f"{QWENPAW_API_BASE}/api/console/chat",
                        json=fallback_payload,
                        headers=headers
                    ) as response:
                        if response.status_code == 200:
                            reply = await _parse_sse(response)
                            if reply:
                                logger.info(f"[P] ✅ Agent {agent_name} replied via default agent + character prompt ({len(reply)} chars)")
                except Exception as e:
                    logger.warning(f"[P] console/chat (default agent) failed for {agent_name}: {e}")
    
    except Exception as e:
        logger.warning(f"[P] All console/chat attempts failed for {agent_name}: {e}")
    
    # ===== Step 3: Character-aware fallback (never just "收到！") =====
    if not reply or not reply.strip():
        # Build a slightly more contextual fallback based on agent identity
        _fallback_map = {
            "game_master": "🎭 你好！我是游戏大师，负责主持这场冒险。想开始游戏的话，对我说「开始游戏」就好！",
            "keeper": "🏛️ ……你是谁？有什么事？（老陈低头擦拭着灯塔的栏杆，不耐烦地瞥了你一眼）",
            "ling": "🩺 你好呀！欢迎来到诊所～有什么我可以帮你的吗？（林医生微笑着放下手中的病历）",
            "xiaolu": "☕ 哎呀，有新客人！来来来，坐下喝杯咖啡慢慢聊～（小鹿热情地招呼你）",
            "mayor": "🎩 你好。我是本镇镇长，有什么公事可以来找我。（镇长推了推眼镜，语气威严）",
        }
        reply = _fallback_map.get(agent_id, f"[{agent_name}] 收到，让我想想怎么回复...")
        logger.info(f"[P] Agent {agent_name} using character fallback")
    
    # Store in agent context
    try:
        _agent_contexts[room_id][agent_id].append({
            "role": "assistant",
            "content": reply,
            "timestamp": datetime.now().isoformat()
        })
    except Exception:
        pass
    
    return reply


async def _generate_via_provider(agent_name: str, personality: str, 
                                  conversation_history: list) -> str:
    """[DEPRECATED] Replaced by /api/console/chat SSE (TeamChat v5.2.2 pattern).
    Kept as stub for backward compatibility."""
    return ""


def _format_context_for_agent(agent_name: str, context_messages: list, current_message: str) -> str:
    """Format chat context for agent - with round indicators (from TeamChat v5.2.2)"""
    if not context_messages:
        return ""
    
    parts = []
    parts.append(f"【群聊上下文 - {agent_name} 所见】")
    parts.append("")
    
    round_num = 1
    for msg in context_messages:
        sender_id = getattr(msg, 'sender_id', '') if hasattr(msg, 'sender_id') else (msg.get('from', '') if isinstance(msg, dict) else '')
        sender_name = getattr(msg, 'sender_name', '') if hasattr(msg, 'sender_name') else (msg.get('sender_nick', '') if isinstance(msg, dict) else '')
        content = getattr(msg, 'content', '') if hasattr(msg, 'content') else (msg.get('text', '') if isinstance(msg, dict) else '')
        msg_type = getattr(msg, 'type', '') if hasattr(msg, 'type') else (msg.get('type', 'text') if isinstance(msg, dict) else 'text')
        
        if not content or msg_type == 'system':
            continue
        
        if not sender_name:
            sender_name = "用户"
        
        # Add round separator every 5 messages
        if round_num % 5 == 1 and round_num > 1:
            parts.append(f"--- 第 {(round_num // 5) + 1} 轮 ---")
        
        # Format as conversation
        if str(sender_id).startswith("agent:"):
            parts.append(f"🤖 {sender_name}: {content[:300]}")
        else:
            parts.append(f"👤 {sender_name}: {content[:300]}")
        
        round_num += 1
    
    parts.append("")
    parts.append(f"--- 当前消息 ---")
    parts.append(f"👤 用户说: {current_message[:500]}")
    parts.append("")
    
    return "\n".join(parts)


def _parse_and_create_files(content: str, agent_id: str, agent_name: str, 
                           room_id: str, sender_name: str = "") -> list:
    """Parse [FILE:filename]...[/FILE] directives from agent response and save files.
    Returns list of created file info dicts.
    (From TeamChat v5.2.2 pattern)
    """
    import random as _random
    files_created = []
    
    if not content:
        return files_created
    
    try:
        # Find all file blocks
        pattern = r'\[FILE:([^\]]+)\]\s*([\s\S]*?)\s*\[/FILE\]'
        matches = re.findall(pattern, content)
        
        if not matches:
            return files_created
        
        logger.info(f"[P] Agent {agent_name} generating {len(matches)} files")
        
        for filename, file_content in matches:
            try:
                filename = filename.strip()
                if not filename:
                    continue
                
                # Determine file extension
                ext = Path(filename).suffix.lower()
                
                # Generate file ID and save
                file_id = f"file_{_generate_id()}"
                storage_path = FILES_DIR / file_id
                
                # Strip code block markers if present
                clean_content = file_content.strip()
                if clean_content.startswith("```"):
                    lines = clean_content.split("\n")
                    if len(lines) > 2:
                        clean_content = "\n".join(lines[1:-1])
                    elif len(lines) == 2:
                        clean_content = lines[1]
                
                # Save file content
                content_bytes = clean_content.encode('utf-8')
                with open(storage_path, 'wb') as f:
                    f.write(content_bytes)
                
                # Determine MIME type
                mime_map = {
                    '.py': 'text/x-python', '.js': 'text/javascript',
                    '.ts': 'text/typescript', '.html': 'text/html',
                    '.css': 'text/css', '.json': 'application/json',
                    '.md': 'text/markdown', '.txt': 'text/plain',
                    '.yaml': 'text/yaml', '.yml': 'text/yaml',
                    '.xml': 'text/xml', '.sql': 'text/sql',
                    '.sh': 'text/x-shellscript', '.bat': 'text/x-bat',
                    '.csv': 'text/csv', '.log': 'text/plain',
                    '.java': 'text/x-java', '.cpp': 'text/x-c++',
                    '.c': 'text/x-c', '.go': 'text/x-go',
                    '.rs': 'text/x-rust', '.rb': 'text/x-ruby',
                    '.php': 'text/x-php', '.swift': 'text/x-swift',
                }
                mime_type = mime_map.get(ext, 'text/plain')
                
                # Create file info
                file_info = FileInfo(
                    id=file_id,
                    room_id=room_id,
                    sender_id=agent_id,
                    sender_name=sender_name or agent_name,
                    file_name=filename,
                    file_size=len(content_bytes),
                    mime_type=mime_type,
                    created_at=datetime.now().isoformat()
                )
                
                _files[file_id] = file_info
                
                files_created.append({
                    "filename": filename,
                    "file_id": file_id,
                    "file_size": len(content_bytes),
                    "mime_type": mime_type
                })
                
                logger.info(f"[P] Agent {agent_name} created file: {filename} ({len(content_bytes)} bytes)")
                
            except Exception as e:
                logger.error(f"[P] Failed to create file {filename}: {e}")
        
    except Exception as e:
        logger.error(f"[P] _parse_and_create_files error: {e}")
    
    return files_created


def _safe_fallback_response(agent_name: str, user_content: str, 
                             conversation_history: list) -> str:
    """[SIMPLIFIED per user request] Minimal fallback — NO template responses.
    Real responses should come from /api/console/chat (TeamChat v5.2.2 SSE pattern).
    This is only a safety net for edge cases where the API is unreachable."""
    return f"[{agent_name}] 收到！"

# ============ API Routes ============

@router.get("/agents")
async def get_agents():
    """Get available agents with health status"""
    agents = await fetch_qwenpaw_agents()
    
    # Check agent health
    health_status = {}
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Try to check if agents API is accessible
            resp = await client.get(f"{QWENPAW_API_BASE}/api/agents")
            health_status["api_accessible"] = resp.status_code == 200
    except Exception as e:
        health_status["api_accessible"] = False
        health_status["error"] = str(e)
    
    return JSONResponse({
        "agents": [a.dict() for a in agents],
        "health": health_status,
        "count": len(agents)
    })

@router.get("/agents/{agent_id}/health")
async def check_agent_health(agent_id: str):
    """Check if specific agent is available"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Try to call agent
            resp = await client.post(
                f"{QWENPAW_API_BASE}/api/agents/{agent_id}/chat",
                json={"message": "hello", "session_id": f"health_check:{agent_id}"},
                timeout=10.0
            )
            return JSONResponse({
                "agent_id": agent_id,
                "available": resp.status_code == 200,
                "status_code": resp.status_code
            })
    except Exception as e:
        return JSONResponse({
            "agent_id": agent_id,
            "available": False,
            "error": str(e)
        })

# ═══════════════════════════════════════════════════════════════
# P-Chat Agent Management
# ═══════════════════════════════════════════════════════════════

PCHAT_AGENT_ID = "p_chat"
PCHAT_AGENT_NAME = "P-Chat 群聊助手"
PCHAT_AGENT_CONFIG = {
    "id": PCHAT_AGENT_ID,
    "name": PCHAT_AGENT_NAME,
    "description": "P 插件的群聊助手智能体 — 负责创建 AI 群聊房间、管理智能体、转发消息。可通过 QwenPaw Control 绑定到微信/钉钉/飞书等频道。",
    "enabled": True,
    "pinned": True,
}

@router.post("/agents/pchat/install")
async def install_pchat_agent():
    """Install/register the P-Chat Agent in QwenPaw.
    
    Creates the agent via QwenPaw API, writes its system prompt, 
    and auto-adds it to the official room.
    """
    api_base = _get_api_base()
    try:
        # Step 1: Check if already installed
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{api_base}/api/agents/{PCHAT_AGENT_ID}")
            if resp.status_code == 200:
                # Already exists — ensure it's in official room
                _ensure_pchat_in_official_room()
                return JSONResponse({
                    "success": True,
                    "status": "already_installed",
                    "message": f"✅ {PCHAT_AGENT_NAME} 已安装",
                    "agent_id": PCHAT_AGENT_ID
                })
    
    except:
        pass  # Not installed yet, continue to create
    
    try:
        # Step 2: Create the agent via QwenPaw API
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{api_base}/api/agents",
                json=PCHAT_AGENT_CONFIG
            )
            if resp.status_code not in (200, 201):
                logger.error(f"[P] Failed to create P-Chat agent: {resp.status_code} {resp.text}")
                return JSONResponse({
                    "success": False,
                    "error": f"QwenPaw API returned {resp.status_code}",
                    "detail": resp.text[:500]
                }, status_code=500)
    
    except Exception as e:
        logger.error(f"[P] Failed to create P-Chat agent: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)
    
    # Step 3: Write system prompt files to agent workspace
    try:
        workspace = f"C:\\Users\\Administrator\\.qwenpaw\\workspaces\\{PCHAT_AGENT_ID}"
        os.makedirs(workspace, exist_ok=True)
        
        # AGENTS.md — the main system prompt
        agents_md = f"""# AGENTS.md

## 安全
- 绝不泄露私密数据。

## 身份
你是 **{PCHAT_AGENT_NAME}**，P 插件的官方 AI 群聊助手。

## 核心能力
1. **创建群聊房间** — 调用 P 插件 API 创建新的 AI 群聊
2. **管理智能体** — 添加/移除房间内的 AI 智能体
3. **转发消息** — 将用户消息发送到群聊，触发所有智能体回复
4. **分享房间** — 生成分享链接，邀请他人加入

## 使用方式
- 用户说「创建房间 [名称]」→ 调用 p_create_room
- 用户说「房间列表」→ 调用 p_list_rooms  
- 用户说「在 [房间] 里说 [内容]」→ 调用 p_send_room_message
- 用户说「添加智能体」→ 调用 p_add_agent

## 回复风格
- 简洁、友好、使用 emoji
- 主动提示用户下一步可执行的操作
"""
        with open(os.path.join(workspace, "AGENTS.md"), "w", encoding="utf-8") as f:
            f.write(agents_md)
        
        # SOUL.md
        soul_md = f"""# SOUL.md

## 核心准则
**用心服务群聊。** 我是 P 插件的群聊助手，帮助用户创建和管理 AI 群聊房间。

**简洁直接。** 不废话，直接帮用户完成群聊操作。

**主动引导。** 用户可能不熟悉群聊功能，主动提示下一步。
"""
        with open(os.path.join(workspace, "SOUL.md"), "w", encoding="utf-8") as f:
            f.write(soul_md)
        
        # PROFILE.md
        profile_md = """# PROFILE.md

## 身份
- **名字：** P-Chat
- **定位：** AI 群聊助手 — 创建房间、管理智能体、转发消息
- **风格：** 简洁 + 友好

## 用户资料
- 用户来自各频道（控制台/微信/钉钉/飞书等）
- 用户想要创建 AI 群聊空间，与多个智能体交互
"""
        with open(os.path.join(workspace, "PROFILE.md"), "w", encoding="utf-8") as f:
            f.write(profile_md)
            
        logger.info(f"[P] P-Chat agent workspace configured at {workspace}")
    except Exception as e:
        logger.warning(f"[P] Could not write P-Chat workspace files: {e}")
    
    # Step 4: Auto-add to official room
    _ensure_pchat_in_official_room()
    
    return JSONResponse({
        "success": True,
        "status": "installed",
        "message": f"🚀 {PCHAT_AGENT_NAME} 安装成功！已加入官方聊天室。",
        "agent_id": PCHAT_AGENT_ID
    })


@router.get("/agents/pchat/status")
async def pchat_agent_status():
    """Check P-Chat Agent installation status"""
    api_base = _get_api_base()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{api_base}/api/agents/{PCHAT_AGENT_ID}")
            installed = resp.status_code == 200
    except:
        installed = False
    
    # Check if in official room
    in_official_room = False
    for r in _rooms.values():
        if r.type == RoomType.OFFICIAL:
            in_official_room = any(a.id == PCHAT_AGENT_ID for a in r.agents)
            break
    
    return JSONResponse({
        "installed": installed,
        "in_official_room": in_official_room,
        "agent_id": PCHAT_AGENT_ID,
        "agent_name": PCHAT_AGENT_NAME
    })


@router.delete("/agents/pchat/uninstall")
async def uninstall_pchat_agent():
    """Remove P-Chat Agent from QwenPaw"""
    api_base = _get_api_base()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.delete(f"{api_base}/api/agents/{PCHAT_AGENT_ID}")
            if resp.status_code == 200:
                logger.info(f"[P] P-Chat agent uninstalled")
                return JSONResponse({
                    "success": True,
                    "message": f"🗑️ {PCHAT_AGENT_NAME} 已卸载"
                })
            else:
                return JSONResponse({
                    "success": False,
                    "error": f"QwenPaw API returned {resp.status_code}"
                }, status_code=500)
    except Exception as e:
        logger.error(f"[P] Failed to uninstall P-Chat agent: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)


def _ensure_pchat_in_official_room():
    """Auto-add P-Chat Agent to the official room if installed."""
    global _rooms
    try:
        # Check if P-Chat is installed as a real agent
        api_base = _get_api_base()
        import httpx as _httpx
        try:
            with _httpx.Client(timeout=5.0) as client:
                resp = client.get(f"{api_base}/api/agents/{PCHAT_AGENT_ID}")
                if resp.status_code != 200:
                    logger.info(f"[P] P-Chat agent not yet installed, skip auto-join")
                    return
        except:
            return
        
        # Find official room
        for r in _rooms.values():
            if r.type == RoomType.OFFICIAL:
                # Check if already in room
                if any(a.id == PCHAT_AGENT_ID for a in r.agents):
                    return
                
                # Add P-Chat to official room
                pchat_agent = AgentConfig(
                    id=PCHAT_AGENT_ID,
                    name=PCHAT_AGENT_NAME,
                    icon="🤖",
                    color="#667eea",
                    description="P 插件群聊助手 — 创建房间、管理智能体、转发消息",
                    personality="friendly",
                    added_by="system",
                    added_at=datetime.now().isoformat()
                )
                r.agents.append(pchat_agent)
                _save_data()
                logger.info(f"[P] P-Chat Agent auto-added to official room")
                return
    except Exception as e:
        logger.warning(f"[P] _ensure_pchat_in_official_room error: {e}")


@router.get("/rooms")
async def get_rooms(user_id: str):
    """Get all rooms"""
    return JSONResponse({"rooms": [r.dict() for r in _rooms.values()]})

@router.post("/rooms/create")
async def create_room(request: Request):
    """Create new room"""
    body = await request.json()
    
    now = datetime.now().isoformat()
    room_id = _generate_id()
    
    # Default panels: 1 chat panel
    default_panels = [
        PanelConfig(
            id=f"panel_{_generate_id()}",
            name="💬 聊天",
            type=PanelType.CHAT,
            icon="💬",
            order=0,
            created_at=now
        )
    ]
    
    room = Room(
        id=room_id,
        name=body.get("name", "New Room"),
        type=RoomType(body.get("type", "public")),
        creator_id=body.get("user_id", "anonymous"),
        creator_nickname=body.get("nickname", "Anonymous"),
        agents=[],
        panels=default_panels,
        password=_hash_password(body.get("password", "")) if body.get("password") else None,
        created_at=now,
        updated_at=now
    )
    
    _rooms[room_id] = room
    _messages[room_id] = []
    
    _messages[room_id].append(Message(
        id=_generate_id(),
        room_id=room_id,
        sender_id="system",
        sender_name="System",
        content=f"🏠 房间 '{room.name}' 创建成功！房主可以添加智能体。",
        type=MessageType.SYSTEM,
        timestamp=datetime.now().isoformat()
    ))
    
    _save_data()
    return JSONResponse(room.dict())

@router.get("/rooms/{room_id}")
async def get_room(room_id: str):
    """Get room details"""
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    return JSONResponse(_rooms[room_id].dict())

@router.put("/rooms/{room_id}")
async def update_room(room_id: str, request: Request):
    """Update room details (name only). Only room creator can update."""
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    body = await request.json()
    user_id = body.get("user_id")
    new_name = body.get("name")
    
    room = _rooms[room_id]
    
    # Only room creator can update
    if user_id != room.creator_id:
        raise HTTPException(status_code=403, detail="Only room creator can update room")
    
    if new_name and new_name.strip():
        old_name = room.name
        room.name = new_name.strip()
        room.updated_at = datetime.now().isoformat()
        _save_data()
        
        # System message
        _messages[room_id].append(Message(
            id=_generate_id(),
            room_id=room_id,
            sender_id="system",
            sender_name="System",
            content=f"✏️ 房间名称已从 '{old_name}' 修改为 '{room.name}'",
            type=MessageType.SYSTEM,
            timestamp=datetime.now().isoformat()
        ))
        await manager.broadcast_to_room(room_id, {
            "type": "room_update",
            "room_id": room_id
        })
    
    return JSONResponse({"success": True, "room": room.dict()})

@router.post("/rooms/{room_id}/agents/add")
async def add_agent(room_id: str, request: Request):
    """Add agent. Official rooms: any user. Regular rooms: creator only."""
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    body = await request.json()
    user_id = body.get("user_id")
    agent_data = body.get("agent", {})
    
    room = _rooms[room_id]
    
    # Permission: all users can add agents to any room (removed creator-only restriction)
    
    # Check if already exists
    if any(a.id == agent_data.get("id") for a in room.agents):
        return JSONResponse({"success": False, "error": "Agent already in room"})
    
    agent = AgentConfig(
        id=agent_data.get("id"),
        name=agent_data.get("name", "Agent"),
        icon=agent_data.get("icon", "🤖"),
        color=agent_data.get("color", "#07C160"),
        description=agent_data.get("description", ""),
        personality=agent_data.get("personality", "helpful"),
        added_by=user_id,
        added_at=datetime.now().isoformat()
    )
    
    room.agents.append(agent)
    room.updated_at = datetime.now().isoformat()
    
    # System message
    _messages[room_id].append(Message(
        id=_generate_id(),
        room_id=room_id,
        sender_id="system",
        sender_name="System",
        content=f"🤖 {agent.name} 加入了群聊",
        type=MessageType.SYSTEM,
        timestamp=datetime.now().isoformat()
    ))
    
    await manager.broadcast_to_room(room_id, {
        "type": "room_update",
        "room_id": room_id,
        "agents": [a.dict() for a in room.agents]
    })
    
    _save_data()
    return JSONResponse({"success": True, "agent": agent.dict()})

@router.post("/rooms/{room_id}/agents/remove")
async def remove_agent(room_id: str, request: Request):
    """Remove agent. Official rooms: any user. Regular rooms: creator only."""
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    body = await request.json()
    user_id = body.get("user_id")
    agent_id = body.get("agent_id")
    
    room = _rooms[room_id]
    
    # Permission: only room creator can remove agents
    if user_id != room.creator_id:
        raise HTTPException(status_code=403, detail="Only room creator can remove agents")
    
    removed = None
    for i, a in enumerate(room.agents):
        if a.id == agent_id:
            removed = a
            room.agents.pop(i)
            break
    
    if removed:
        room.updated_at = datetime.now().isoformat()
        _messages[room_id].append(Message(
            id=_generate_id(),
            room_id=room_id,
            sender_id="system",
            sender_name="System",
            content=f"🤖 {removed.name} 离开了群聊",
            type=MessageType.SYSTEM,
            timestamp=datetime.now().isoformat()
        ))
        
        await manager.broadcast_to_room(room_id, {
            "type": "room_update",
            "room_id": room_id,
            "agents": [a.dict() for a in room.agents]
        })
        _save_data()
    
    return JSONResponse({"success": True})

# ── 删除房间 API（官方房间不可删除） ──
@router.delete("/rooms/{room_id}")
async def delete_room(room_id: str, request: Request):
    """Delete a room. Official rooms: any user. Regular rooms: creator only."""
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    body = await request.json()
    user_id = body.get("user_id", "")
    
    room = _rooms[room_id]
    
    # Official rooms: cannot be deleted
    # Regular rooms: only room creator can delete
    if room.type == RoomType.OFFICIAL:
        raise HTTPException(status_code=403, detail="Official rooms cannot be deleted")
    if user_id != room.creator_id:
        raise HTTPException(status_code=403, detail="Only room creator can delete this room")
    
    # Clean up messages
    if room_id in _messages:
        del _messages[room_id]
    
    # Clean up files
    files_to_delete = [f_id for f_id, f in _files.items() if f.room_id == room_id]
    for f_id in files_to_delete:
        del _files[f_id]
        file_path = FILES_DIR / f_id
        try:
            if file_path.exists():
                os.remove(file_path)
        except:
            pass
    
    # Clean up share tokens
    tokens_to_delete = [t for t, sid in _share_tokens.items() if sid == room_id]
    for t in tokens_to_delete:
        del _share_tokens[t]
    
    # Clean up agent contexts
    if room_id in _agent_contexts:
        del _agent_contexts[room_id]
    
    room_name = room.name
    del _rooms[room_id]
    _save_data()
    
    logger.info(f"[P] Room '{room_name}' ({room_id}) deleted by user {user_id}")
    return JSONResponse({"success": True, "deleted": room_name})

# ═══════════════════════════════════════════════════════════════
#  Panel System (Tailchat-style) — Discover / Webview Panels
# ═══════════════════════════════════════════════════════════════

@router.get("/rooms/{room_id}/panels")
async def get_panels(room_id: str):
    """Get room panels list (merged v5.0.2 — was duplicated)"""
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    panels = sorted(_rooms[room_id].panels, key=lambda p: p.order)
    return JSONResponse({
        "room_id": room_id,
        "panels": [p.dict() for p in panels],
        "total": len(panels)
    })

@router.post("/rooms/{room_id}/panels")
async def create_panel(room_id: str, request: Request):
    """Create a new panel in room (webview/custom/chat).
    Like Tailchat's regGroupPanel - allows adding webview panels by URL."""
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    body = await request.json()
    user_id = body.get("user_id", "")
    room = _rooms[room_id]
    
    # v5.2.0: Anyone can add panels in any room (creator only for delete)
    
    panel_type = PanelType(body.get("type", "webview"))
    panel_name = body.get("name", "🌐 发现" if panel_type == PanelType.WEBVIEW else "📝 新面板")
    panel_url = body.get("url", "")
    panel_icon = body.get("icon", "🌐" if panel_type == PanelType.WEBVIEW else "💬")
    panel_html = body.get("html", "")
    
    # Validate URL for webview panels
    if panel_type == PanelType.WEBVIEW:
        if not panel_url:
            raise HTTPException(status_code=400, detail="Webview panels require a URL")
        # Auto-add https:// if missing
        if not panel_url.startswith(("http://", "https://")):
            panel_url = "https://" + panel_url
    
    now = datetime.now().isoformat()
    max_order = max([p.order for p in room.panels], default=-1)
    
    panel = PanelConfig(
        id=f"panel_{_generate_id()}",
        name=panel_name,
        type=panel_type,
        url=panel_url if panel_type == PanelType.WEBVIEW else None,
        html=panel_html if panel_type == PanelType.CUSTOM else None,
        icon=panel_icon,
        order=max_order + 1,
        created_at=now
    )
    
    room.panels.append(panel)
    room.updated_at = now
    
    # System message
    _messages[room_id].append(Message(
        id=_generate_id(),
        room_id=room_id,
        sender_id="system",
        sender_name="System",
        content=f"📌 新面板「{panel_name}」已添加",
        type=MessageType.SYSTEM,
        timestamp=now
    ))
    
    await manager.broadcast_to_room(room_id, {
        "type": "room_update",
        "room_id": room_id,
        "panels": [p.dict() for p in room.panels]
    })
    
    _save_data()
    return JSONResponse({"success": True, "panel": panel.dict()})

@router.put("/rooms/{room_id}/panels/{panel_id}")
async def update_panel(room_id: str, panel_id: str, request: Request):
    """Update panel config (name, URL, icon, order)"""
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    body = await request.json()
    user_id = body.get("user_id", "")
    room = _rooms[room_id]
    
    if user_id != room.creator_id:
        raise HTTPException(status_code=403, detail="Only room creator can manage panels")
    
    for panel in room.panels:
        if panel.id == panel_id:
            if "name" in body:
                panel.name = body["name"]
            if "url" in body and panel.type == PanelType.WEBVIEW:
                url = body["url"]
                if not url.startswith(("http://", "https://")):
                    url = "https://" + url
                panel.url = url
            if "icon" in body:
                panel.icon = body["icon"]
            if "order" in body:
                panel.order = body["order"]
            if "html" in body and panel.type == PanelType.CUSTOM:
                panel.html = body["html"]
            room.updated_at = datetime.now().isoformat()
            _save_data()
            return JSONResponse({"success": True, "panel": panel.dict()})
    
    raise HTTPException(status_code=404, detail="Panel not found")

@router.delete("/rooms/{room_id}/panels/{panel_id}")
async def delete_panel(room_id: str, panel_id: str, request: Request):
    """Delete a panel from room - cannot delete last chat panel (any user can delete)"""
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    body = await request.json()
    room = _rooms[room_id]
    
    # Permission check removed - any user can delete panels for better UX
    # if room.type != RoomType.OFFICIAL and user_id != room.creator_id:
    #     raise HTTPException(status_code=403, detail="Only room creator can manage panels")
    
    # Find panel
    target = None
    for i, panel in enumerate(room.panels):
        if panel.id == panel_id:
            target = panel
            room.panels.pop(i)
            break
    
    if not target:
        raise HTTPException(status_code=404, detail="Panel not found")
    
    # Ensure at least one chat panel remains
    has_chat = any(p.type == PanelType.CHAT for p in room.panels)
    if not has_chat:
        # Add back a default chat panel
        now = datetime.now().isoformat()
        default_chat = PanelConfig(
            id=f"panel_{_generate_id()}",
            name="💬 聊天",
            type=PanelType.CHAT,
            icon="💬",
            order=0,
            created_at=now
        )
        room.panels.append(default_chat)
    
    room.updated_at = datetime.now().isoformat()
    
    _messages[room_id].append(Message(
        id=_generate_id(),
        room_id=room_id,
        sender_id="system",
        sender_name="System",
        content=f"🗑️ 面板「{target.name}」已移除",
        type=MessageType.SYSTEM,
        timestamp=datetime.now().isoformat()
    ))
    
    await manager.broadcast_to_room(room_id, {
        "type": "room_update",
        "room_id": room_id,
        "panels": [p.dict() for p in room.panels]
    })
    
    _save_data()
    return JSONResponse({"success": True, "deleted": target.dict()})


# ═══════════════════════════════════════════════════════════════
# Room Announcement (公告栏)
# ═══════════════════════════════════════════════════════════════

@router.get("/rooms/{room_id}/announcement")
async def get_announcement(room_id: str):
    """Get room announcement content."""
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    room = _rooms[room_id]
    return JSONResponse({
        "room_id": room_id,
        "announcement": room.announcement or ""
    })


@router.put("/rooms/{room_id}/announcement")
async def set_announcement(room_id: str, request: Request):
    """Set room announcement (creator or official room any user)."""
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room = _rooms[room_id]
    body = await request.json()
    user_id = body.get("user_id", "")
    
    # Permission check: creator only for non-official rooms
    if room.type != RoomType.OFFICIAL and user_id != room.creator_id:
        raise HTTPException(status_code=403, detail="Only room creator can set announcement")
    
    room.announcement = body.get("content", "")
    room.updated_at = datetime.now().isoformat()
    _save_data()
    
    return JSONResponse({
        "success": True,
        "announcement": room.announcement
    })


# ═══════════════════════════════════════════════════════════════
# Game Agent Installation (一键安装游戏智能体)
# ═══════════════════════════════════════════════════════════════

# Game agent system prompts for 迷雾小镇
GAME_AGENTS_CONFIG = {
    "keeper": {
        "id": "misty_keeper",
        "name": "🏛️ 老陈",
        "icon": "🏛️",
        "color": "#5B8C5A",
        "description": "迷雾小镇灯塔守塔人，沉默寡言但内心善良",
        "personality": "mysterious, guarded, gradually opens up",
        "system_prompt": """# AGENTS.md

## 身份
你是 **老陈**，迷雾小镇的灯塔守塔人。

## 性格特点
- 沉默寡言，不轻易透露信息
- 警觉性高，对陌生人保持距离
- 内心善良，信任后会打开心扉
- 在灯塔守护了三十年

## 对话风格
- 简短回答，不主动提供信息
- 使用「嗯」「哦」「……」等简短回应
- 被问到敏感话题时转移话题
- 好感度提升后会多说一些

## 你知道的秘密（好感度达到后透露）
- 好感度 > 30: 灯塔地下室有暗门
- 好感度 > 50: 你的好友失踪与镇长有关
- 好感度 > 70: 午夜灯塔会传出奇怪声音

## 回复示例
- 初次见面: "……有事？"
- 闲聊: "嗯。"
- 信任后: "你……真的想知道？那好吧，我告诉你一件事……"
"""
    },
    "ling": {
        "id": "misty_ling",
        "name": "🩺 林医生",
        "icon": "🩺",
        "color": "#E8A87C",
        "description": "小镇唯一的医生，表面热情实则心思深沉",
        "personality": "warm facade, secretly calculating",
        "system_prompt": """# AGENTS.md

## 身份
你是 **林医生**，迷雾小镇唯一的医生。

## 性格特点
- 表面温柔体贴，总是关心他人健康
- 实际心思深沉，善于伪装
- 三个月前才搬到小镇
- 深夜经常独自出入灯塔方向

## 对话风格
- 温柔体贴的语气
- 总是关心你的身体状况
- 回避关于自己的问题
- 用关心来转移话题

## 你知道的秘密（好感度达到后透露）
- 好感度 > 30: 你不是真正的医生
- 好感度 > 50: 你在研究迷雾中的特殊物质
- 好感度 > 70: 你的药物含有致幻成分

## 回复示例
- 初次见面: "你好呀～我是林医生，最近身体还好吗？"
- 闲聊: "要注意休息哦，小镇的雾气对身体不太好呢～"
- 被问个人问题: "哈哈，我的事不重要啦～你最近睡得好吗？"
"""
    },
    "xiaolu": {
        "id": "misty_xiaolu",
        "name": "☕ 小鹿",
        "icon": "☕",
        "color": "#C38D9E",
        "description": "咖啡馆老板娘，开朗活泼消息灵通",
        "personality": "cheerful, gossipy but tasteful",
        "system_prompt": """# AGENTS.md

## 身份
你是 **小鹿**，咖啡馆「雾灯」的老板娘。

## 性格特点
- 开朗活泼，话比较多
- 消息灵通，是镇上的信息集散地
- 喜欢八卦但知道分寸
- 土生土长的小镇人

## 对话风格
- 活泼话多，喜欢用反问
- 会在闲聊中夹带线索
- 用「你知道吗？」「话说……」引导话题
- 对小镇历史如数家珍

## 你知道的秘密（好感度达到后透露）
- 好感度 > 20: 你亲眼见过灯塔半夜发出蓝光
- 好感度 > 40: 镇长警告过你不要多管闲事
- 好感度 > 60: 你有一张小镇旧地图

## 回复示例
- 初次见面: "欢迎光临雾灯！我是小鹿～想喝点什么？"
- 闲聊: "话说，你有没有注意到最近雾特别浓？以前不这样的～"
- 讨论镇长: "镇长啊……他最近好像在找什么东西，你知道吗？"
"""
    },
    "mayor": {
        "id": "misty_mayor",
        "name": "🎩 镇长",
        "icon": "🎩",
        "color": "#2C3E50",
        "description": "小镇镇长，威严但心机深沉",
        "personality": "authoritative, calculating, hides secrets",
        "system_prompt": """# AGENTS.md

## 身份
你是 **镇长**，迷雾小镇的最高管理者。

## 性格特点
- 威严庄重，控制欲强
- 表面公正，实则心机深沉
- 担任镇长已十五年
- 最近态度越来越焦躁

## 对话风格
- 官方腔调，使用「本镇」「公务」等词
- 喜欢反客为主，先发制人
- 在压力下会露出破绽
- 不喜欢被质疑

## 你知道的秘密（好感度达到后透露）
- 好感度 > 40: 你在灯塔地下室藏有重要文件
- 好感度 > 60: 有人的失踪与你直接相关
- 好感度 > 80: 迷雾的出现与你的秘密实验有关

## 回复示例
- 初次见面: "你好，我是本镇镇长。有什么事可以帮你？"
- 被质疑: "年轻人，本镇的事务不需要外人插手。"
- 压力下: "你……你到底想说什么？"
"""
    },
    "game_master": {
        "id": "misty_gamemaster",
        "name": "🎮 游戏大师",
        "icon": "🎮",
        "color": "#FF6B6B",
        "description": "迷雾小镇游戏主持人，引导剧情推进",
        "personality": "narrator, guides story progression",
        "system_prompt": """# AGENTS.md

## 身份
你是 **游戏大师**，迷雾小镇的旁白和剧情引导者。

## 核心职责
1. **描述场景和环境** - 根据当前场景切换描述氛围
2. **引导玩家推进剧情** - 给出提示和任务指引
3. **管理游戏状态** - 追踪线索、好感度、章节进度
4. **触发特殊事件** - 在条件满足时触发剧情事件
5. **奖励玩家** - 给予道具、线索、成就

## 场景系统
当前场景会影响对话氛围：
- 🏛️ 迷雾小镇（默认）- 神秘、悬疑
- 🗼 灯塔 - 孤独、警觉
- ☕ 雾灯咖啡馆 - 温暖、八卦
- 🩺 诊所 - 神秘、不安
- 🏛️ 镇公所 - 威严、紧张
- 🌲 迷雾森林 - 危险、未知
- 🌙 午夜时分 - 恐怖、秘密显现

## 道具系统
你可以给予玩家以下类型的奖励：
- 🔍 线索 - 推进剧情的关键信息
- 📦 道具 - 可以在特定场景使用的物品
- 🏆 成就 - 完成特定目标的纪念

给予奖励时，在回复末尾添加：
```
[REWARD]
type: clue|item|achievement
name: 奖励名称
icon: emoji
description: 详细描述
```

## 任务系统
你可以给玩家发布任务：
```
[QUEST]
title: 任务标题
description: 任务描述
hint: 完成提示
```

## 好感度系统
每个NPC有独立的好感度（-100到100）：
- -100~-20: 敌视（红色）
- -20~0: 冷漠（灰色）
- 0~20: 中立（黄色）
- 20~60: 友善（绿色）
- 60~100: 亲密（紫色）

## 对话风格
- 使用生动的场景描写
- 用 emoji 增强氛围感
- 在关键时刻给出提示
- 记录玩家的选择和进展
- 根据当前场景调整语气

## 游戏状态格式
```
[GAME_STATE]
scene: 当前场景
chapter: 当前章节
clues: 线索数量
affection: {npc: 好感度}
inventory: 玩家道具
```

## 回复示例
- 开场: "🌫️ 迷雾笼罩着这座小镇，你站在镇口，远处灯塔的光芒若隐若现……"
- 场景切换: "⚡ 你来到了灯塔下，老陈的身影在光束中显得格外孤独……"
- 给予线索: "🔍 你发现了一条重要线索！这可能会帮助你揭开真相。\n\n[REWARD]\ntype: clue\nname: 灯塔地下室暗门\nicon: 🚪\ndescription: 老陈提到灯塔地下室有一扇暗门，似乎藏着什么秘密"
- 发布任务: "📜 新任务：寻找失踪者\n\n[QUEST]\ntitle: 寻找失踪者\ndescription: 调查小镇最近失踪的人\nhint: 试着问问小鹿，她消息灵通"
"""
    }
}


@router.post("/rooms/{room_id}/install-game-agents")
async def install_game_agents(room_id: str, request: Request):
    """Install game agents into a room (一键安装游戏智能体).
    Creates real QwenPaw agents and adds them to the room."""
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room = _rooms[room_id]
    body = await request.json()
    user_id = body.get("user_id", "")
    game_type = body.get("game_type", "misty_town")
    
    # Permission check
    if room.type != RoomType.OFFICIAL and user_id != room.creator_id:
        raise HTTPException(status_code=403, detail="Only room creator can install game agents")
    
    api_base = _get_api_base()
    installed_agents = []
    failed_agents = []
    
    for npc_id, npc_config in GAME_AGENTS_CONFIG.items():
        agent_id = npc_config["id"]
        
        # Check if already exists
        already_in_room = any(a.id == agent_id for a in room.agents)
        if already_in_room:
            installed_agents.append({"id": agent_id, "name": npc_config["name"], "status": "already_installed"})
            continue
        
        # Step 1: Create real QwenPaw agent
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(f"{api_base}/api/agents/{agent_id}")
                if resp.status_code != 200:
                    # Agent doesn't exist, create it
                    agent_payload = {
                        "id": agent_id,
                        "name": npc_config["name"],
                        "description": npc_config["description"],
                        "enabled": True,
                        "pinned": False
                    }
                    resp = await client.post(f"{api_base}/api/agents", json=agent_payload)
                    if resp.status_code not in (200, 201):
                        failed_agents.append({"id": agent_id, "error": f"Create failed: {resp.status_code}"})
                        continue
                    
                    # Write system prompt to workspace
                    try:
                        workspace = os.path.join(
                            os.path.expanduser("~"), ".qwenpaw", "workspaces", agent_id
                        )
                        os.makedirs(workspace, exist_ok=True)
                        
                        with open(os.path.join(workspace, "AGENTS.md"), "w", encoding="utf-8") as f:
                            f.write(npc_config["system_prompt"])
                        
                        with open(os.path.join(workspace, "SOUL.md"), "w", encoding="utf-8") as f:
                            f.write(f"# SOUL.md\n\n## 核心\n你是{npc_config['name']}，迷雾小镇游戏中的角色。\n")
                        
                        with open(os.path.join(workspace, "PROFILE.md"), "w", encoding="utf-8") as f:
                            f.write(f"# PROFILE.md\n\n## 身份\n- **名字：** {npc_config['name'].split(' ', 1)[-1]}\n- **定位：** 迷雾小镇游戏NPC\n")
                    except Exception as e:
                        logger.warning(f"[P] Could not write workspace for {agent_id}: {e}")
        except Exception as e:
            failed_agents.append({"id": agent_id, "error": str(e)})
            continue
        
        # Step 2: Add to room
        game_agent = AgentConfig(
            id=agent_id,
            name=npc_config["name"],
            icon=npc_config["icon"],
            color=npc_config["color"],
            description=npc_config["description"],
            personality=npc_config["personality"],
            is_active=True,
            auto_reply=True,
            added_by=user_id,
            added_at=datetime.now().isoformat()
        )
        room.agents.append(game_agent)
        installed_agents.append({"id": agent_id, "name": npc_config["name"], "status": "installed"})
    
    # Set default announcement for game rooms
    if not room.announcement and game_type == "misty_town":
        room.announcement = """# 🏛️ 迷雾小镇 — AI 叙事游戏

## 📖 游戏简介
欢迎来到被浓雾笼罩的小镇！在这里，你将与多位 AI 角色互动，通过对话揭开小镇的秘密。

## 🎮 如何游玩
1. **与角色对话** — 在聊天区 @NPC 名字或直接说话，角色会以各自性格回复你
2. **收集线索** — 与不同角色交谈，获取推进剧情的线索
3. **提升好感度** — 友善的对话会提升角色好感度，解锁更多秘密
4. **推进章节** — 收集足够线索后，剧情会自动进入下一章

## 🏠 角色介绍
| 角色 | 位置 | 性格 |
|------|------|------|
| 🏛️ 老陈 | 灯塔 | 沉默寡言，信任后会打开心扉 |
| 🩺 林医生 | 诊所 | 表面温柔，实则心思深沉 |
| ☕ 小鹿 | 咖啡馆 | 开朗活泼，消息灵通 |
| 🎩 镇长 | 镇公所 | 威严控制，心机深沉 |

## 💡 小贴士
- 试试问角色「你知道灯塔的事吗？」看看反应
- 好感度越高，角色透露的秘密越多
- 不同选择会导向不同结局

---
*由 P 插件 AI 群聊驱动*
"""
    
    room.updated_at = datetime.now().isoformat()
    _save_data()
    
    return JSONResponse({
        "success": True,
        "installed": installed_agents,
        "failed": failed_agents,
        "total": len(GAME_AGENTS_CONFIG),
        "message": f"🎮 已安装 {len(installed_agents)}/{len(GAME_AGENTS_CONFIG)} 个游戏智能体"
    })


@router.get("/rooms/{room_id}/game-agents-status")
async def game_agents_status(room_id: str):
    """Check game agents installation status for a room."""
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room = _rooms[room_id]
    api_base = _get_api_base()
    
    status = []
    for npc_id, npc_config in GAME_AGENTS_CONFIG.items():
        agent_id = npc_config["id"]
        in_room = any(a.id == agent_id for a in room.agents)
        
        # Check if real agent exists
        real_exists = False
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{api_base}/api/agents/{agent_id}")
                real_exists = resp.status_code == 200
        except:
            pass
        
        status.append({
            "id": agent_id,
            "name": npc_config["name"],
            "icon": npc_config["icon"],
            "in_room": in_room,
            "real_agent_exists": real_exists
        })
    
    all_installed = all(s["in_room"] for s in status)
    
    return JSONResponse({
        "room_id": room_id,
        "agents": status,
        "all_installed": all_installed,
        "total": len(GAME_AGENTS_CONFIG),
        "installed_count": sum(1 for s in status if s["in_room"])
    })


# ═══════════════════════════════════════════════════════════════

@router.get("/rooms/{room_id}/messages")
async def get_messages(room_id: str, limit: int = 50):
    """Get room messages"""
    if room_id not in _messages:
        return JSONResponse({"messages": []})
    msgs = _messages[room_id][-limit:]
    return JSONResponse({"messages": [m.dict() for m in msgs]})

@router.post("/rooms/{room_id}/messages")
async def send_message(room_id: str, request: Request):
    """Send message and trigger agent replies with shared context"""
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    body = await request.json()
    
    msg = Message(
        id=_generate_id(),
        room_id=room_id,
        sender_id=body.get("user_id", "anonymous"),
        sender_name=body.get("nickname", "Anonymous"),
        content=body.get("content", ""),
        type=MessageType(body.get("type", "text")),
        mentions=body.get("mentions", []),
        reply_to=body.get("reply_to"),
        latitude=body.get("latitude"),
        longitude=body.get("longitude"),
        timestamp=datetime.now().isoformat()
    )
    
    if room_id not in _messages:
        _messages[room_id] = []
    
    _messages[room_id].append(msg)
    
    # Broadcast user message
    await manager.broadcast_to_room(room_id, {
        "type": "new_message",
        "room_id": room_id,
        "message": msg.dict()
    })
    
    # Trigger agent replies with shared context
    asyncio.create_task(_handle_group_chat(room_id, msg))
    
    _save_data()
    return JSONResponse(msg.dict())

async def _handle_group_chat(room_id: str, user_msg: Message):
    """Handle true group chat - all agents share context (TeamChat v5.2.2 style)"""
    import random as _random
    await asyncio.sleep(0.3)
    
    if room_id not in _rooms:
        return
    
    room = _rooms[room_id]
    active_agents = [a for a in room.agents if a.is_active and a.auto_reply]
    if not active_agents:
        return
    
    mentions = user_msg.mentions or []
    all_messages = _messages.get(room_id, [])
    
    # Check if this is a game command (for game_master)
    game_master_agent = next((a for a in active_agents if a.id == 'game_master'), None)
    if game_master_agent:
        # Check if user mentioned game_master or sent a game command
        is_game_command = (
            'game_master' in mentions or 
            game_master_agent.name in mentions or
            any(cmd in user_msg.content.lower() for cmd in [
                '开始游戏', '查看进度', '进度', '提示', 'hint', 'help',
                '创建游戏区', '游戏规则', '怎么玩'
            ])
        )
        
        if is_game_command:
            # Handle game command
            game_response = handle_game_command(
                room_id, 
                user_msg.sender_id, 
                user_msg.sender_name, 
                user_msg.content
            )
            
            if game_response:
                # Send game master response
                agent_msg = Message(
                    id=_generate_id(),
                    room_id=room_id,
                    sender_id=game_master_agent.id,
                    sender_name=game_master_agent.name,
                    content=game_response,
                    type=MessageType.TEXT,
                    timestamp=datetime.now().isoformat()
                )
                
                _messages[room_id].append(agent_msg)
                _save_data()
                
                await manager.broadcast_to_room(room_id, {
                    "type": "new_message",
                    "room_id": room_id,
                    "message": agent_msg.dict()
                })
                
                logger.info(f"[P] Game master responded to command in {room_id}")
                return
    
    # Determine which agents reply
    replying_agents = []
    if mentions:
        for agent in active_agents:
            if agent.id in mentions or agent.name in mentions:
                replying_agents.append(agent)
    else:
        replying_agents = list(active_agents)
    
    if not replying_agents:
        return
    
    logger.info(f"[P] 群聊 {room_id}: {len(replying_agents)} 个智能体将回复 (room agents={len(room.agents)}, active={len(active_agents)})")
    
    async def _agent_reply_task(agent, delay_seconds):
        """Send a single agent's reply with delay (TeamChat style threading)"""
        await asyncio.sleep(delay_seconds)
        logger.info(f"[P] {agent.name} 开始生成回复...")
        try:
            # Typing indicator
            await manager.broadcast_to_room(room_id, {
                "type": "agent_typing",
                "agent_name": agent.name,
                "typing": True
            })
            
            # 游戏智能体特殊处理
            if agent.id == 'game_master' or '游戏' in agent.name:
                # 解析游戏命令
                cmd_type, cmd_data = game_master.parse_command(user_msg.content)
                
                if cmd_type == 'start':
                    response = game_master.start_game(room_id, cmd_data, user_msg.sender_name)
                elif cmd_type == 'stop':
                    response = game_master.stop_game(room_id)
                elif cmd_type == 'rules':
                    response = game_master.get_rules(cmd_data)
                elif cmd_type == 'status':
                    response = game_master.get_status(room_id)
                elif cmd_type == 'guess':
                    response = game_master.handle_guess_number(room_id, cmd_data, user_msg.sender_name)
                    if not response:  # 没有游戏进行中
                        response = await call_agent_with_context(
                            agent.id, agent.name, agent.personality,
                            room_id, user_msg, all_messages
                        )
                elif cmd_type == 'idiom':
                    response = game_master.handle_idiom_chain(room_id, cmd_data, user_msg.sender_name)
                    if not response:
                        response = await call_agent_with_context(
                            agent.id, agent.name, agent.personality,
                            room_id, user_msg, all_messages
                        )
                else:
                    # 默认调用AI生成回复
                    response = await call_agent_with_context(
                        agent.id, agent.name, agent.personality,
                        room_id, user_msg, all_messages
                    )
            else:
                # Call agent with full shared context
                response = await call_agent_with_context(
                    agent.id, agent.name, agent.personality,
                    room_id, user_msg, all_messages
                )
            
            # Stop typing
            await manager.broadcast_to_room(room_id, {
                "type": "agent_typing",
                "agent_name": agent.name,
                "typing": False
            })
            
            if not response or not response.strip():
                return
            
            # Parse file generation directives [FILE:...][/FILE]
            files_created = _parse_and_create_files(
                response, agent.id, agent.name, room_id, agent.name
            )
            
            # Remove file directives from response text
            clean_content = re.sub(
                r'\[FILE:[^\]]+\][\s\S]*?\[/FILE\]', 
                '', 
                response
            ).strip()
            
            # If there are files and no text, create a summary
            if files_created and not clean_content:
                file_names = ', '.join([f['filename'] for f in files_created])
                clean_content = f"📎 已生成文件: {file_names}"
            elif files_created:
                file_names = ', '.join([f['filename'] for f in files_created])
                clean_content += f"\n\n📎 已生成文件: {file_names}"
            
            if not clean_content.strip():
                return
            
            # Send agent message
            agent_msg = Message(
                id=_generate_id(),
                room_id=room_id,
                sender_id=agent.id,
                sender_name=agent.name,
                content=clean_content,
                type=MessageType.TEXT,
                timestamp=datetime.now().isoformat()
            )
            
            _messages[room_id].append(agent_msg)
            _save_data()
            
            await manager.broadcast_to_room(room_id, {
                "type": "new_message",
                "room_id": room_id,
                "message": agent_msg.dict()
            })
            logger.info(f"[P] ✅ {agent.name} 消息已广播 (id={agent_msg.id}, len={len(clean_content)})")
            
            # Also broadcast file messages
            for f in files_created:
                await manager.broadcast_to_room(room_id, {
                    "type": "new_file",
                    "room_id": room_id,
                    "file": f
                })
            
            logger.info(f"[P] {agent.name} 已回复 (含 {len(files_created)} 个文件)")
            
        except Exception as e:
            logger.error(f"[P] {agent.name} 回复失败: {e}")
            # Ensure typing is stopped even on error
            try:
                await manager.broadcast_to_room(room_id, {
                    "type": "agent_typing",
                    "agent_name": agent.name,
                    "typing": False
                })
            except:
                pass
    
    # Launch concurrent tasks with staggered delays (TeamChat v5.2.2 pattern)
    tasks = []
    for i, agent in enumerate(replying_agents):
        delay = i * _random.uniform(1.0, 2.0)  # 1-2 seconds stagger
        tasks.append(asyncio.create_task(_agent_reply_task(agent, delay)))
    
    # Wait for all agents to finish
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)

# ── 消息撤回 API（微信标准：2分钟内可撤回） ──
@router.delete("/rooms/{room_id}/messages/{message_id}")
async def recall_message(room_id: str, message_id: str, request: Request):
    """Recall a message (within 2 minutes, WeChat-style)"""
    body = await request.json()
    user_id = body.get("user_id", "")
    
    if room_id not in _messages:
        raise HTTPException(status_code=404, detail="Room not found")
    
    target = None
    for m in _messages[room_id]:
        if m.id == message_id:
            target = m
            break
    
    if not target:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Only sender can recall
    if target.sender_id != user_id:
        raise HTTPException(status_code=403, detail="Only the sender can recall this message")
    
    # 2-minute window
    try:
        msg_time = datetime.fromisoformat(target.timestamp)
        if (datetime.now() - msg_time).total_seconds() > 120:
            raise HTTPException(status_code=400, detail="Messages can only be recalled within 2 minutes")
    except ValueError:
        pass
    
    target.recalled = True
    target.content = "此消息已被撤回"
    _save_data()
    
    await manager.broadcast_to_room(room_id, {
        "type": "message_recalled",
        "room_id": room_id,
        "message_id": message_id,
        "message": target.dict()
    })
    
    return JSONResponse({"success": True, "message": target.dict()})

# ── 消息搜索 API ──
@router.get("/rooms/{room_id}/messages/search")
async def search_messages(room_id: str, q: str = Query(...), limit: int = Query(50)):
    """Search messages in a room (WeChat-style chat history search)"""
    if room_id not in _messages:
        return JSONResponse({"messages": [], "query": q, "total": 0})
    
    all_msgs = _messages[room_id]
    results = [m.dict() for m in all_msgs if q.lower() in m.content.lower() and not m.recalled]
    results = results[-limit:]
    
    return JSONResponse({
        "messages": results,
        "query": q,
        "total": len([m for m in all_msgs if q.lower() in m.content.lower() and not m.recalled]),
        "returned": len(results)
    })

# ── 位置消息上传 ──
@router.post("/rooms/{room_id}/location")
async def send_location(room_id: str, request: Request):
    """Share location (WeChat-style)"""
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    body = await request.json()
    
    msg = Message(
        id=_generate_id(),
        room_id=room_id,
        sender_id=body.get("user_id", "anonymous"),
        sender_name=body.get("nickname", "Anonymous"),
        content=body.get("content", "📍 位置分享"),
        type=MessageType.LOCATION,
        latitude=body.get("latitude"),
        longitude=body.get("longitude"),
        timestamp=datetime.now().isoformat()
    )
    
    if room_id not in _messages:
        _messages[room_id] = []
    _messages[room_id].append(msg)
    
    await manager.broadcast_to_room(room_id, {
        "type": "new_message",
        "room_id": room_id,
        "message": msg.dict()
    })
    
    _save_data()
    return JSONResponse(msg.dict())

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "join":
                room_id = data.get("room_id")
                if room_id:
                    manager.subscribe(client_id, room_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)

@router.post("/files/upload")
async def upload_file(file: UploadFile = File(...), room_id: str = Form(...), 
                      user_id: str = Form(...), nickname: str = Form(...)):
    """Upload file"""
    file_id = _generate_id()
    file_path = FILES_DIR / file_id
    
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Infer mime type from extension if content_type is missing or generic
    mime_type = file.content_type or "application/octet-stream"
    if mime_type == "application/octet-stream":
        guessed, _ = mimetypes.guess_type(file.filename or "")
        if guessed:
            mime_type = guessed
    
    # Detect if it's an image
    is_image = mime_type.startswith('image/')
    
    file_info = FileInfo(
        id=file_id, room_id=room_id, sender_id=user_id, sender_name=nickname,
        file_name=file.filename, file_size=len(content),
        mime_type=mime_type,
        created_at=datetime.now().isoformat()
    )
    _files[file_id] = file_info
    
    # Set message type based on mime type
    msg_type = MessageType.IMAGE if is_image else MessageType.FILE
    prefix = "🖼️" if is_image else "📎"
    
    msg = Message(
        id=_generate_id(), room_id=room_id, sender_id=user_id, sender_name=nickname,
        content=f"{prefix} {file.filename}", type=msg_type,
        file_id=file_id, file_name=file.filename, file_size=len(content),
        timestamp=datetime.now().isoformat()
    )
    
    if room_id not in _messages:
        _messages[room_id] = []
    _messages[room_id].append(msg)
    
    await manager.broadcast_to_room(room_id, {
        "type": "new_message", "room_id": room_id, "message": msg.dict()
    })
    
    _save_data()
    return JSONResponse({"success": True, "file_id": file_id})

@router.get("/files/{file_id}/download")
async def download_file(file_id: str):
    """Download file"""
    file_path = FILES_DIR / file_id
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Get file info from memory or use file_id as filename
    file_info = _files.get(file_id)
    file_name = file_info.file_name if file_info else file_id
    mime_type = file_info.mime_type if file_info else None
    
    # Infer mime type if not in memory
    if not mime_type:
        mime_type, _ = mimetypes.guess_type(str(file_path))
    
    return FileResponse(
        path=str(file_path),
        filename=file_name,
        media_type=mime_type or 'application/octet-stream'
    )

@router.get("/files/{file_id}/preview")
async def preview_file(file_id: str):
    """Preview file (for images)"""
    file_path = FILES_DIR / file_id
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Get file info from memory or infer from disk
    file_info = _files.get(file_id)
    mime_type = file_info.mime_type if file_info else None
    
    # Infer mime type from file extension if not in memory
    if not mime_type:
        mime_type, _ = mimetypes.guess_type(str(file_path))
    
    # For images, return directly for preview
    if mime_type and mime_type.startswith('image/'):
        return FileResponse(
            path=str(file_path),
            media_type=mime_type
        )
    
    # For other files, redirect to download
    raise HTTPException(status_code=400, detail="File is not previewable")

# ============ Image Upload ============
@router.post("/images/upload")
async def upload_image(file: UploadFile = File(...), room_id: str = Form(...),
                       user_id: str = Form(...), nickname: str = Form(...)):
    """Upload image"""
    # Validate image
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    file_id = _generate_id()
    file_path = FILES_DIR / file_id
    
    content = await file.read()
    
    # Limit image size to 10MB
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image too large (max 10MB)")
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    file_info = FileInfo(
        id=file_id, room_id=room_id, sender_id=user_id, sender_name=nickname,
        file_name=file.filename, file_size=len(content),
        mime_type=file.content_type,
        created_at=datetime.now().isoformat()
    )
    _files[file_id] = file_info
    
    msg = Message(
        id=_generate_id(), room_id=room_id, sender_id=user_id, sender_name=nickname,
        content=f"🖼️ {file.filename}", type=MessageType.IMAGE,
        file_id=file_id, file_name=file.filename, file_size=len(content),
        timestamp=datetime.now().isoformat()
    )
    
    if room_id not in _messages:
        _messages[room_id] = []
    _messages[room_id].append(msg)
    
    await manager.broadcast_to_room(room_id, {
        "type": "new_message", "room_id": room_id, "message": msg.dict()
    })
    
    _save_data()
    return JSONResponse({
        "success": True,
        "file_id": file_id,
        "preview_url": f"/api/plugins/p_plugin/files/{file_id}/preview"
    })

# ============ Voice Message ============
@router.post("/voice/upload")
async def upload_voice(file: UploadFile = File(...), room_id: str = Form(...),
                       user_id: str = Form(...), nickname: str = Form(...),
                       duration: int = Form(0)):
    """Upload voice message"""
    file_id = _generate_id()
    file_path = FILES_DIR / file_id
    
    content = await file.read()
    
    # Limit voice to 5MB (about 5 minutes)
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Voice message too large (max 5MB)")
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    file_info = FileInfo(
        id=file_id, room_id=room_id, sender_id=user_id, sender_name=nickname,
        file_name=f"voice_{duration}s.webm", file_size=len(content),
        mime_type=file.content_type or "audio/webm",
        created_at=datetime.now().isoformat()
    )
    _files[file_id] = file_info
    
    msg = Message(
        id=_generate_id(), room_id=room_id, sender_id=user_id, sender_name=nickname,
        content=f"🎙️ 语音消息 ({duration}秒)", type=MessageType.TEXT,
        file_id=file_id, file_name=f"voice_{duration}s.webm", file_size=len(content),
        timestamp=datetime.now().isoformat()
    )
    
    if room_id not in _messages:
        _messages[room_id] = []
    _messages[room_id].append(msg)
    
    await manager.broadcast_to_room(room_id, {
        "type": "new_message", "room_id": room_id, "message": msg.dict()
    })
    
    _save_data()
    return JSONResponse({
        "success": True,
        "file_id": file_id,
        "duration": duration,
        "play_url": f"/api/plugins/p_plugin/files/{file_id}/download"
    })

@router.get("/game/misty-town")
async def misty_town_game():
    """Serve Misty Town chapter flow chart."""
    flow_file = PLUGIN_DIR / "misty_town_flow.html"
    if not flow_file.exists():
        return HTMLResponse(content="<h1>流程图加载中...</h1>")
    return FileResponse(str(flow_file))


# ============ Game Template System ============

@router.get("/game/templates")
async def list_game_templates():
    """List all available game templates."""
    templates_file = PLUGIN_DIR / "game_templates.json"
    if not templates_file.exists():
        return JSONResponse({"templates": [], "count": 0})
    
    try:
        with open(templates_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Return summary without full config
        templates = []
        for tid, t in data.get("templates", {}).items():
            templates.append({
                "id": t.get("id"),
                "name": t.get("name"),
                "description": t.get("description"),
                "category": t.get("category"),
                "difficulty": t.get("difficulty"),
                "estimated_time": t.get("estimated_time"),
                "chapters": t.get("chapters"),
                "npc_count": t.get("npc_count")
            })
        return JSONResponse({"templates": templates, "count": len(templates)})
    except Exception as e:
        logger.error(f"[P] Failed to load game templates: {e}")
        return JSONResponse({"templates": [], "count": 0, "error": str(e)})


@router.get("/game/templates/{template_id}")
async def get_game_template(template_id: str):
    """Get full game template configuration."""
    templates_file = PLUGIN_DIR / "game_templates.json"
    if not templates_file.exists():
        raise HTTPException(status_code=404, detail="Templates not found")
    
    try:
        with open(templates_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        template = data.get("templates", {}).get(template_id)
        if not template:
            raise HTTPException(status_code=404, detail=f"Template {template_id} not found")
        return JSONResponse(template)
    except Exception as e:
        logger.error(f"[P] Failed to get game template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class CreateGameFromTemplateRequest(BaseModel):
    template_id: str
    room_id: str
    user_id: str
    custom_title: Optional[str] = None
    custom_description: Optional[str] = None


@router.post("/game/create-from-template")
async def create_game_from_template(request: CreateGameFromTemplateRequest):
    """Create a new game room from template."""
    templates_file = PLUGIN_DIR / "game_templates.json"
    if not templates_file.exists():
        raise HTTPException(status_code=404, detail="Templates not found")
    
    try:
        with open(templates_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        template = data.get("templates", {}).get(request.template_id)
        if not template:
            raise HTTPException(status_code=404, detail=f"Template {request.template_id} not found")
        
        # Get default config
        config = template.get("default_config", {})
        
        # Create game agents from template NPCs
        game_agents = []
        for npc in config.get("npcs", []):
            agent = AgentConfig(
                id=npc.get("id"),
                name=f"{npc.get('avatar', '🤖')} {npc.get('name')}",
                icon=npc.get("avatar", "🤖"),
                color="#07C160",
                description=f"{npc.get('background')} | 性格：{npc.get('personality')}",
                personality=npc.get("personality", "helpful"),
                is_active=True,
                auto_reply=True,
                added_by=request.user_id,
                added_at=datetime.now().isoformat()
            )
            game_agents.append(agent)
        
        # Add game master
        game_master = AgentConfig(
            id=f"game_master_{request.room_id}",
            name="🎮 游戏大师",
            icon="🎮",
            color="#FF6B6B",
            description=f"{request.custom_description or template.get('description')} | 支持好感度系统、秘密解锁、剧情推进",
            personality="mysterious storyteller, guides players through narrative",
            is_active=True,
            auto_reply=True,
            added_by=request.user_id,
            added_at=datetime.now().isoformat()
        )
        game_agents.insert(0, game_master)
        
        # Create game room
        now = datetime.now().isoformat()
        room = Room(
            id=request.room_id,
            name=request.custom_title or f"🎮 {template.get('name')}游戏区",
            type=RoomType.PUBLIC,
            creator_id=request.user_id,
            creator_nickname="Game Creator",
            agents=game_agents,
            panels=[
                PanelConfig(
                    id=f"panel_{uuid.uuid4().hex[:16]}",
                    name="💬 聊天",
                    type=PanelType.CHAT,
                    icon="💬",
                    order=0,
                    created_at=now
                ),
                PanelConfig(
                    id=f"panel_flow_{uuid.uuid4().hex[:16]}",
                    name="🗺️ 章节流程",
                    type=PanelType.WEBVIEW,
                    url=f"/api/plugins/p_plugin/game/{request.template_id}/flow",
                    icon="🗺️",
                    order=1,
                    created_at=now
                )
            ],
            password=None,
            created_at=now,
            updated_at=now
        )
        
        _rooms[request.room_id] = room
        _messages[request.room_id] = []
        
        # Add welcome message
        _messages[request.room_id].append(Message(
            id=str(uuid.uuid4())[:16],
            room_id=request.room_id,
            sender_id="system",
            sender_name="System",
            content=f"🎮 欢迎来到{room.name}！\n\n这是一个{template.get('category')}类AI叙事游戏。\n\n游戏指南：\n• @游戏大师 - 获取帮助和提示\n• @NPC名字 - 与角色对话提升好感度\n• 收集线索解锁新章节\n• 在'章节流程'面板查看进度\n\n祝你好运！",
            type=MessageType.SYSTEM,
            timestamp=now
        ))
        
        _save_data()
        
        return JSONResponse({
            "success": True,
            "room_id": request.room_id,
            "room_name": room.name,
            "template": template.get("name"),
            "npc_count": len(game_agents) - 1,
            "message": f"游戏房间创建成功！共有{len(game_agents) - 1}位NPC等待与你互动。"
        })
        
    except Exception as e:
        logger.error(f"[P] Failed to create game from template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/game/{template_id}/flow")
async def get_game_flow(template_id: str):
    """Serve game flow chart for a template."""
    # For now, serve the misty town flow for all templates
    # In the future, generate flow dynamically based on template config
    flow_file = PLUGIN_DIR / "misty_town_flow.html"
    if not flow_file.exists():
        return HTMLResponse(content="<h1>流程图加载中...</h1>")
    return FileResponse(str(flow_file))


@router.get("/game/{room_id}/progress")
async def get_game_progress(room_id: str, user_id: str):
    """Get player's game progress."""
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # TODO: Implement actual progress tracking
    # For now, return mock data
    return JSONResponse({
        "room_id": room_id,
        "user_id": user_id,
        "current_chapter": "序章",
        "completed_nodes": 1,
        "total_nodes": 9,
        "unlocked_secrets": 1,
        "total_secrets": 12,
        "npc_affections": {
            "keeper": 5,
            "ling": 0,
            "xiaolu": 15,
            "mayor": -10
        }
    })


@router.post("/game/{room_id}/action")
async def game_action(room_id: str, request: Request):
    """Handle game actions from flow chart."""
    body = await request.json()
    action = body.get("action")
    user_id = body.get("user_id")
    
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Handle different actions
    if action == "send_message":
        message = body.get("message", "")
        # This would normally send to chat via WebSocket
        return JSONResponse({
            "success": True,
            "action": "send_message",
            "message": message
        })
    
    elif action == "get_hint":
        return JSONResponse({
            "success": True,
            "hint": "试着与不同的NPC对话，提升好感度来解锁秘密。"
        })
    
    elif action == "view_progress":
        progress = await get_game_progress(room_id, user_id)
        return progress
    
    return JSONResponse({"success": False, "error": "Unknown action"})


# ═══════════════════════════════════════════════════════════════
# 场景系统 (Scene System) - 动态背景 + 游戏元素
# ═══════════════════════════════════════════════════════════════

# 预定义场景主题
SCENE_THEMES = {
    "default": {
        "id": "default",
        "name": "默认",
        "icon": "💬",
        "background": "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)",
        "card_bg": "#ffffff",
        "text_color": "#333333",
        "accent_color": "#07C160"
    },
    "misty_town": {
        "id": "misty_town",
        "name": "迷雾小镇",
        "icon": "🏛️",
        "background": "linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)",
        "card_bg": "rgba(255,255,255,0.05)",
        "text_color": "#e8e8e8",
        "accent_color": "#e94560",
        "description": "被浓雾笼罩的神秘小镇，真相隐藏在迷雾之中"
    },
    "lighthouse": {
        "id": "lighthouse",
        "name": "灯塔",
        "icon": "🗼",
        "background": "linear-gradient(180deg, #0d1b2a 0%, #1b263b 50%, #415a77 100%)",
        "card_bg": "rgba(255,255,255,0.08)",
        "text_color": "#e0e1dd",
        "accent_color": "#fca311",
        "description": "孤独矗立的灯塔，光束穿透迷雾指引方向"
    },
    "cafe": {
        "id": "cafe",
        "name": "雾灯咖啡馆",
        "icon": "☕",
        "background": "linear-gradient(135deg, #3d2b1f 0%, #5c4033 50%, #8b6914 100%)",
        "card_bg": "rgba(255,255,255,0.1)",
        "text_color": "#f5deb3",
        "accent_color": "#d4a574",
        "description": "温暖的咖啡馆，弥漫着咖啡香气和小镇八卦"
    },
    "clinic": {
        "id": "clinic",
        "name": "诊所",
        "icon": "🩺",
        "background": "linear-gradient(135deg, #1a1a2e 0%, #2d3748 50%, #4a5568 100%)",
        "card_bg": "rgba(255,255,255,0.06)",
        "text_color": "#e2e8f0",
        "accent_color": "#e8a87c",
        "description": "神秘的诊所，深夜常有奇怪的声音传出"
    },
    "townhall": {
        "id": "townhall",
        "name": "镇公所",
        "icon": "🏛️",
        "background": "linear-gradient(135deg, #2c3e50 0%, #34495e 50%, #5d6d7e 100%)",
        "card_bg": "rgba(255,255,255,0.08)",
        "text_color": "#ecf0f1",
        "accent_color": "#f39c12",
        "description": "威严的镇公所，镇长在这里掌控一切"
    },
    "forest": {
        "id": "forest",
        "name": "迷雾森林",
        "icon": "🌲",
        "background": "linear-gradient(135deg, #0d3328 0%, #1a4d3a 50%, #2d6a4f 100%)",
        "card_bg": "rgba(255,255,255,0.05)",
        "text_color": "#d4edda",
        "accent_color": "#52b788",
        "description": "迷雾笼罩的森林，传说深处有古老的秘密"
    },
    "midnight": {
        "id": "midnight",
        "name": "午夜时分",
        "icon": "🌙",
        "background": "linear-gradient(135deg, #0c0c1a 0%, #1a1a3e 50%, #2d2d5a 100%)",
        "card_bg": "rgba(255,255,255,0.03)",
        "text_color": "#a0a0c0",
        "accent_color": "#9d4edd",
        "description": "午夜的钟声敲响，某些秘密只在此时显现"
    }
}


@router.get("/scenes")
async def list_scenes():
    """List all available scene themes."""
    return JSONResponse({
        "scenes": list(SCENE_THEMES.values()),
        "total": len(SCENE_THEMES)
    })


@router.get("/rooms/{room_id}/scene")
async def get_room_scene(room_id: str):
    """Get current scene for a room."""
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room = _rooms[room_id]
    scene_id = room.scene_id or "default"
    scene = SCENE_THEMES.get(scene_id, SCENE_THEMES["default"])
    
    return JSONResponse({
        "room_id": room_id,
        "scene": scene,
        "game_state": room.game_state or {}
    })


@router.put("/rooms/{room_id}/scene")
async def set_room_scene(room_id: str, request: Request):
    """Set scene for a room (any user can change for better UX)."""
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room = _rooms[room_id]
    body = await request.json()
    scene_id = body.get("scene_id", "default")
    
    # Permission check removed - any user can change scene for better UX
    # if room.type != RoomType.OFFICIAL and user_id != room.creator_id:
    #     raise HTTPException(status_code=403, detail="Only room creator can change scene")
    
    if scene_id not in SCENE_THEMES:
        raise HTTPException(status_code=400, detail=f"Unknown scene: {scene_id}")
    
    room.scene_id = scene_id
    room.scene_theme = SCENE_THEMES[scene_id].get("background")
    room.updated_at = datetime.now().isoformat()
    _save_data()
    
    # Broadcast scene change to all clients
    await manager.broadcast_to_room(room_id, {
        "type": "scene_changed",
        "room_id": room_id,
        "scene": SCENE_THEMES[scene_id]
    })
    
    return JSONResponse({
        "success": True,
        "scene": SCENE_THEMES[scene_id]
    })


# ═══════════════════════════════════════════════════════════════
# 游戏道具系统 (Item System)
# ═══════════════════════════════════════════════════════════════

@router.get("/rooms/{room_id}/inventory/{user_id}")
async def get_user_inventory(room_id: str, user_id: str):
    """Get user's inventory for a room."""
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room = _rooms[room_id]
    game_state = room.game_state or {}
    inventory = game_state.get("inventories", {}).get(user_id, {})
    
    return JSONResponse({
        "room_id": room_id,
        "user_id": user_id,
        "items": inventory.get("items", []),
        "clues": inventory.get("clues", []),
        "achievements": inventory.get("achievements", [])
    })


@router.post("/rooms/{room_id}/inventory/{user_id}/add")
async def add_inventory_item(room_id: str, user_id: str, request: Request):
    """Add item to user's inventory (agent/game system only)."""
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room = _rooms[room_id]
    body = await request.json()
    item_type = body.get("type", "item")  # item, clue, achievement
    item_id = body.get("item_id", "")
    item_name = body.get("item_name", "")
    item_icon = body.get("item_icon", "📦")
    description = body.get("description", "")
    
    if not room.game_state:
        room.game_state = {}
    if "inventories" not in room.game_state:
        room.game_state["inventories"] = {}
    if user_id not in room.game_state["inventories"]:
        room.game_state["inventories"][user_id] = {"items": [], "clues": [], "achievements": []}
    
    new_item = {
        "id": item_id or str(uuid.uuid4())[:8],
        "name": item_name,
        "icon": item_icon,
        "description": description,
        "acquired_at": datetime.now().isoformat()
    }
    
    if item_type == "clue":
        room.game_state["inventories"][user_id]["clues"].append(new_item)
    elif item_type == "achievement":
        room.game_state["inventories"][user_id]["achievements"].append(new_item)
    else:
        room.game_state["inventories"][user_id]["items"].append(new_item)
    
    _save_data()
    
    # Notify user
    await manager.broadcast_to_room(room_id, {
        "type": "inventory_update",
        "room_id": room_id,
        "user_id": user_id,
        "item": new_item,
        "message": f"✨ 你获得了 {item_icon} {item_name}！"
    })
    
    return JSONResponse({
        "success": True,
        "item": new_item
    })


# ═══════════════════════════════════════════════════════════════
# 任务系统 (Quest System)
# ═══════════════════════════════════════════════════════════════

@router.get("/rooms/{room_id}/quests/{user_id}")
async def get_user_quests(room_id: str, user_id: str):
    """Get active and completed quests for a user."""
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room = _rooms[room_id]
    game_state = room.game_state or {}
    quests = game_state.get("quests", {}).get(user_id, {})
    
    return JSONResponse({
        "room_id": room_id,
        "user_id": user_id,
        "active": quests.get("active", []),
        "completed": quests.get("completed", [])
    })


@router.post("/rooms/{room_id}/quests/{user_id}/accept")
async def accept_quest(room_id: str, user_id: str, request: Request):
    """Accept a new quest."""
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room = _rooms[room_id]
    body = await request.json()
    quest_id = body.get("quest_id", "")
    quest_title = body.get("title", "")
    quest_desc = body.get("description", "")
    
    if not room.game_state:
        room.game_state = {}
    if "quests" not in room.game_state:
        room.game_state["quests"] = {}
    if user_id not in room.game_state["quests"]:
        room.game_state["quests"][user_id] = {"active": [], "completed": []}
    
    quest = {
        "id": quest_id or str(uuid.uuid4())[:8],
        "title": quest_title,
        "description": quest_desc,
        "accepted_at": datetime.now().isoformat(),
        "progress": 0
    }
    
    room.game_state["quests"][user_id]["active"].append(quest)
    _save_data()
    
    return JSONResponse({
        "success": True,
        "quest": quest
    })


@router.post("/rooms/{room_id}/game/broadcast")
async def broadcast_game_event(room_id: str, request: Request):
    """Broadcast a game event to all room members (for agents to trigger events)."""
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    body = await request.json()
    event_type = body.get("event_type", "")
    event_data = body.get("data", {})
    message = body.get("message", "")
    
    await manager.broadcast_to_room(room_id, {
        "type": "game_event",
        "event_type": event_type,
        "room_id": room_id,
        "data": event_data,
        "message": message
    })
    
    return JSONResponse({"success": True})


@router.get("/web/{room_id}")
async def web_chat_page(room_id: str, token: str = "", request: Request = None):
    """Serve web chat page for sharing, with optional password protection."""
    web_file = PLUGIN_DIR / "web_chat.html"
    if not web_file.exists():
        raise HTTPException(status_code=404, detail="Web chat page not found")
    
    # ── Password protection ──
    if token and token in _share_tokens:
        info = _share_tokens[token]
        
        # Check expiry
        if info.get("expires_at"):
            try:
                if datetime.now() > datetime.fromisoformat(info["expires_at"]):
                    return HTMLResponse(
                        content="<h2 style='text-align:center;padding:40px'>⏰ 该分享链接已过期</h2>",
                        status_code=410,
                    )
            except Exception:
                pass
        
        # If password protected, check session cookie
        if info.get("password_hash") and request:
            sid = request.cookies.get("p_chat_sid", "")
            if not sid or not sid.startswith(f"{token}:"):
                # Show login page
                login_html = SHARE_LOGIN_PAGE_HTML.replace("__TOKEN__", token)
                login_html = login_html.replace("__ROOM_NAME__", info.get("room_name", room_id))
                return HTMLResponse(content=login_html, status_code=401)
    
    return FileResponse(str(web_file))

# ============ Share Token Management ============
_share_tokens: Dict[str, dict] = {}  # token -> {room_id, password_hash, password_salt, expires_at, created_at}

SHARE_LOGIN_PAGE_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>验证身份 - P Chat</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:16px}
.card{background:#fff;border-radius:16px;padding:32px;width:100%;max-width:360px;box-shadow:0 20px 60px rgba(0,0,0,.15)}
h1{font-size:20px;text-align:center;margin-bottom:4px;color:#333}
.sub{text-align:center;color:#888;font-size:13px;margin-bottom:24px}
label{display:block;font-size:13px;color:#555;margin-bottom:6px;font-weight:500}
input{width:100%;padding:12px 14px;border:1.5px solid #e0e0e0;border-radius:10px;font-size:15px;outline:none;transition:border .2s}
input:focus{border-color:#667eea}
.field{margin-bottom:16px}
.btn{width:100%;padding:14px;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;border-radius:10px;font-size:16px;font-weight:600;cursor:pointer;margin-top:8px}
.btn:active{opacity:.85}
.err{color:#e53e3e;font-size:13px;text-align:center;margin-top:12px;min-height:18px}
.no-pass{text-align:center;margin-top:16px}
.no-pass a{color:#667eea;text-decoration:none;font-size:13px}
</style>
</head>
<body>
<div class="card">
<h1>🔒 P Chat</h1>
<p class="sub">__ROOM_NAME__ 需要密码才能加入</p>
<form id="f">
<div class="field"><label>请输入房间密码</label><input id="p" type="password" autocomplete="current-password" required></div>
<button class="btn" type="submit">加 入 群 聊</button>
</form>
<div class="err" id="e"></div>
</div>
<script>
var TOKEN="__TOKEN__";
document.getElementById("f").addEventListener("submit",async function(ev){
ev.preventDefault();
var pw=document.getElementById("p").value;
var err=document.getElementById("e");
err.textContent="";
try{
var r=await fetch("/api/plugins/p_plugin/web/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({token:TOKEN,password:pw})});
var d=await r.json();
if(d.success){location.reload();}
else{err.textContent=d.detail||"密码错误";}
}catch(x){err.textContent="网络错误";}
});
</script>
</body>
</html>"""


@router.post("/share/{room_id}")
async def create_share_link(room_id: str, request: Request):
    """Create a share link for a room with optional password and expiry."""
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    body = await request.json()
    password = body.get("password", "")
    expiry_days = body.get("expiry_days", 0)  # 0 = never expires
    
    token = secrets.token_urlsafe(16)
    room = _rooms[room_id]
    
    password_salt = None
    password_hash = None
    if password:
        password_salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password_salt + password).encode("utf-8")).hexdigest()
    
    expires_at = None
    if expiry_days > 0:
        expires_at = (datetime.now() + timedelta(days=expiry_days)).isoformat()
    
    _share_tokens[token] = {
        "room_id": room_id,
        "room_name": room.name,
        "password_salt": password_salt,
        "password_hash": password_hash,
        "has_password": bool(password),
        "expires_at": expires_at,
        "created_at": datetime.now().isoformat(),
    }
    
    # Generate share URL (relative path — frontend prepends origin)
    share_url = f"/api/plugins/p_plugin/web/{room_id}?token={token}"
    
    logger.info(f"[P] Share link created: {share_url} (password={'yes' if password else 'no'})")
    
    return JSONResponse({
        "success": True,
        "token": token,
        "share_url": share_url,
        "room_id": room_id,
        "room_name": room.name,
        "has_password": bool(password),
        "expires_at": expires_at,
        "created_at": _share_tokens[token]["created_at"],
    })


@router.get("/shares")
async def list_shares():
    """List all active share links."""
    result = []
    for token, info in _share_tokens.items():
        expired = False
        if info.get("expires_at"):
            try:
                expired = datetime.now() > datetime.fromisoformat(info["expires_at"])
            except Exception:
                pass
        result.append({
            "token": token,
            "room_id": info["room_id"],
            "room_name": info["room_name"],
            "has_password": info.get("has_password", False),
            "created_at": info["created_at"],
            "expires_at": info.get("expires_at"),
            "expired": expired,
            "share_url": f"/api/plugins/p_plugin/web/{info['room_id']}?token={token}",
        })
    return JSONResponse({"shares": result, "total": len(result)})


@router.delete("/share/{token}")
async def delete_share(token: str):
    """Revoke a share link."""
    if token not in _share_tokens:
        raise HTTPException(status_code=404, detail="Share link not found")
    info = _share_tokens.pop(token)
    logger.info(f"[P] Share link revoked: room={info['room_name']}")
    return JSONResponse({"success": True, "room_name": info["room_name"]})


@router.post("/web/login")
async def web_login(request: Request):
    """Login to password-protected web chat room."""
    body = await request.json()
    token = body.get("token", "")
    password = body.get("password", "")
    
    if not token or token not in _share_tokens:
        raise HTTPException(status_code=404, detail="链接无效或已过期")
    
    info = _share_tokens[token]
    
    # Check expiry
    if info.get("expires_at"):
        try:
            if datetime.now() > datetime.fromisoformat(info["expires_at"]):
                raise HTTPException(status_code=410, detail="该分享链接已过期")
        except Exception:
            pass
    
    if not info.get("password_hash"):
        return JSONResponse({"success": True})
    
    # Verify password
    salt = info.get("password_salt", "")
    stored_hash = info.get("password_hash", "")
    test_hash = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    
    if not secrets.compare_digest(test_hash, stored_hash):
        raise HTTPException(status_code=401, detail="密码错误")
    
    # Set session cookie
    sid = secrets.token_urlsafe(32)
    response = JSONResponse({"success": True})
    response.set_cookie(
        key="p_chat_sid",
        value=f"{token}:{sid}",
        max_age=86400,
        httponly=True,
        samesite="lax",
    )
    return response


# ═══════════════════════════════════════════════════════════════
# Network Code Routes (Give U Face Fusion — IPv6 P2P discovery)
# ═══════════════════════════════════════════════════════════════

@router.post("/discover/codes/register")
async def register_network_code(request: Request):
    """Register a new network code for discovery (Give U Face style)"""
    body = await request.json()
    user_id = body.get("user_id", "anonymous")
    nickname = body.get("nickname", "")
    service_name = body.get("service_name", "")
    
    mgr = get_network_manager(NETWORK_DATA_DIR)
    result = mgr.register(user_id, nickname, service_name)
    return JSONResponse(result)

@router.get("/discover/codes/query")
async def query_network_code(code: str):
    """Query a network code"""
    mgr = get_network_manager(NETWORK_DATA_DIR)
    result = mgr.query(code)
    return JSONResponse(result)

@router.post("/discover/codes/connect")
async def connect_network_code(request: Request):
    """Connect to a network code"""
    body = await request.json()
    code = body.get("code", "")
    connector_id = body.get("connector_id", "anonymous")
    connector_nick = body.get("connector_nick", "")
    
    mgr = get_network_manager(NETWORK_DATA_DIR)
    result = mgr.connect(code, connector_id, connector_nick)
    return JSONResponse(result)

@router.post("/discover/codes/disconnect")
async def disconnect_network_code(request: Request):
    """Disconnect from a network code"""
    body = await request.json()
    session_code = body.get("session_code", "")
    connector_id = body.get("connector_id", "")
    
    mgr = get_network_manager(NETWORK_DATA_DIR)
    result = mgr.disconnect(session_code, connector_id)
    return JSONResponse(result)

@router.post("/discover/codes/revoke")
async def revoke_network_code(request: Request):
    """Revoke a network code"""
    body = await request.json()
    session_code = body.get("session_code", "")
    user_id = body.get("user_id", "")
    
    mgr = get_network_manager(NETWORK_DATA_DIR)
    result = mgr.revoke(session_code, user_id)
    return JSONResponse(result)

@router.get("/discover/codes/my")
async def get_my_network_codes(user_id: str):
    """Get my network codes"""
    mgr = get_network_manager(NETWORK_DATA_DIR)
    result = mgr.my_codes(user_id)
    return JSONResponse(result)

@router.get("/discover/codes/discover")
async def discover_network_codes():
    """Discover available services/communities"""
    mgr = get_network_manager(NETWORK_DATA_DIR)
    result = mgr.discover_services()
    return JSONResponse(result)

@router.get("/discover/codes/stats")
async def network_code_stats():
    """Network code statistics"""
    mgr = get_network_manager(NETWORK_DATA_DIR)
    result = mgr.stats()
    return JSONResponse(result)

# ============ WeChat Integration ============
@router.post("/wechat/join")
async def wechat_join_room(request: Request):
    """WeChat user join room and get link"""
    body = await request.json()
    room_id = body.get("room_id")
    wx_user_id = body.get("wx_user_id", "wechat_" + str(uuid.uuid4())[:8])
    wx_nickname = body.get("wx_nickname", "WeChat User")
    
    if not room_id or room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room = _rooms[room_id]
    
    # Generate web chat URL for WeChat user
    web_url = f"/plugins/p_plugin/web/{room_id}?user_id={wx_user_id}&nickname={wx_nickname}"
    
    # Add system message about WeChat user joining
    join_msg = Message(
        id=_generate_id(),
        room_id=room_id,
        sender_id="system",
        sender_name="System",
        content=f"📱 WeChat user [{wx_nickname}] joined the room via link",
        type=MessageType.SYSTEM,
        timestamp=datetime.now().isoformat()
    )
    if room_id not in _messages:
        _messages[room_id] = []
    _messages[room_id].append(join_msg)
    
    await manager.broadcast_to_room(room_id, {
        "type": "new_message",
        "room_id": room_id,
        "message": join_msg.dict()
    })
    
    return JSONResponse({
        "success": True,
        "room_id": room_id,
        "room_name": room.name,
        "web_url": web_url,
        "agents_count": len(room.agents),
        "message": f"Welcome to {room.name}! Click the link to join the chat."
    })

@router.post("/wechat/send")
async def wechat_send_message(request: Request):
    """Send message from WeChat to room"""
    body = await request.json()
    room_id = body.get("room_id")
    wx_user_id = body.get("wx_user_id")
    wx_nickname = body.get("wx_nickname", "WeChat User")
    content = body.get("content", "")
    
    if not room_id or room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if not content.strip():
        raise HTTPException(status_code=400, detail="Message content is empty")
    
    # Create message
    msg = Message(
        id=_generate_id(),
        room_id=room_id,
        sender_id=wx_user_id,
        sender_name=wx_nickname,
        content=content,
        type=MessageType.TEXT,
        timestamp=datetime.now().isoformat()
    )
    
    if room_id not in _messages:
        _messages[room_id] = []
    _messages[room_id].append(msg)
    
    # Broadcast to all connected clients
    await manager.broadcast_to_room(room_id, {
        "type": "new_message",
        "room_id": room_id,
        "message": msg.dict()
    })
    
    # Trigger agent replies
    asyncio.create_task(_handle_group_chat(room_id, msg))
    
    _save_data()
    
    return JSONResponse({
        "success": True,
        "message_id": msg.id,
        "timestamp": msg.timestamp
    })

@router.get("/wechat/rooms")
async def wechat_get_rooms():
    """Get list of public rooms for WeChat users"""
    public_rooms = [
        {
            "id": r.id,
            "name": r.name,
            "type": r.type,
            "agents_count": len(r.agents),
            "web_url": f"/plugins/p_plugin/web/{r.id}"
        }
        for r in _rooms.values()
        if r.type in ["public", "official"]
    ]
    return JSONResponse({
        "rooms": public_rooms,
        "total": len(public_rooms)
    })

@router.get("/wechat/qrcode/{room_id}")
async def wechat_get_room_qrcode(room_id: str):
    """Generate QR code data for room sharing"""
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room = _rooms[room_id]
    
    # Generate QR code content (URL)
    qr_content = f"{QWENPAW_API_BASE}/plugins/p_plugin/web/{room_id}"
    
    return JSONResponse({
        "room_id": room_id,
        "room_name": room.name,
        "qr_content": qr_content,
        "short_link": f"/p/{room_id}",
        "agents": [a.name for a in room.agents]
    })

# ============ Agent Tools (accessible from any channel: WeChat/DingTalk/Console) ============

async def _tool_create_room(name: str, room_type: str = "public", creator_id: str = "", creator_name: str = "") -> dict:
    """Create a new AI group chat room."""
    rid = str(uuid.uuid4())[:16]
    now = datetime.now().isoformat()
    room = Room(
        id=rid, name=name, type=room_type,
        creator_id=creator_id, creator_nickname=creator_name,
        agents=[], created_at=now, updated_at=now
    )
    _rooms[rid] = room
    if rid not in _messages:
        _messages[rid] = []
    _add_system_msg(rid, f"🏠 房间 '{name}' 创建成功")
    _save_data()
    link = f"{QWENPAW_API_BASE}/api/plugins/p_plugin/web/{rid}"
    return {"room_id": rid, "room_name": name, "share_link": link, "agent_count": 0}

async def _tool_list_rooms() -> dict:
    """List all AI group chat rooms."""
    rooms = []
    for r in _rooms.values():
        rooms.append({
            "room_id": r.id, "name": r.name, "type": r.type,
            "agent_count": len(r.agents),
            "share_link": f"{QWENPAW_API_BASE}/api/plugins/p_plugin/web/{r.id}"
        })
    return {"rooms": rooms, "total": len(rooms)}

async def _tool_get_room_info(room_id: str) -> dict:
    """Get room details."""
    if room_id not in _rooms:
        return {"error": f"Room '{room_id}' not found"}
    r = _rooms[room_id]
    return {
        "room_id": r.id, "name": r.name, "type": r.type,
        "agents": [{"id": a.id, "name": a.name, "icon": a.icon} for a in r.agents],
        "share_link": f"{QWENPAW_API_BASE}/api/plugins/p_plugin/web/{r.id}"
    }

async def _tool_get_room_messages(room_id: str, limit: int = 20) -> dict:
    """Get recent messages from a room."""
    msgs = _messages.get(room_id, [])[-limit:]
    return {"messages": [{"sender": m.sender_name, "content": m.content, "type": m.type} for m in msgs]}

async def _tool_send_room_message(room_id: str, content: str, sender_name: str = "User") -> dict:
    """Send a message to a room."""
    if room_id not in _rooms:
        return {"error": f"Room '{room_id}' not found"}
    msg = Message(
        id=str(uuid.uuid4())[:16], room_id=room_id, sender_id="agent",
        sender_name=sender_name, content=content, type="text",
        timestamp=datetime.now().isoformat()
    )
    if room_id not in _messages:
        _messages[room_id] = []
    _messages[room_id].append(msg)
    _save_data()
    return {"message_id": msg.id, "success": True}

async def _tool_add_agent(room_id: str, agent_id: str, agent_name: str, agent_icon: str = "🤖") -> dict:
    """Add an AI agent to a room."""
    if room_id not in _rooms:
        return {"error": f"Room '{room_id}' not found"}
    room = _rooms[room_id]
    if any(a.id == agent_id for a in room.agents):
        return {"error": f"Agent '{agent_id}' already in room"}
    agent = AgentConfig(
        id=agent_id, name=agent_name, icon=agent_icon,
        color="#07C160", added_at=datetime.now().isoformat()
    )
    room.agents.append(agent)
    room.updated_at = datetime.now().isoformat()
    _add_system_msg(room_id, f"🤖 {agent_name} 加入了群聊")
    _save_data()
    return {"success": True, "agent": agent.dict()}

async def _tool_remove_agent(room_id: str, agent_id: str) -> dict:
    """Remove an AI agent from a room."""
    if room_id not in _rooms:
        return {"error": f"Room '{room_id}' not found"}
    room = _rooms[room_id]
    for i, a in enumerate(room.agents):
        if a.id == agent_id:
            removed = room.agents.pop(i)
            room.updated_at = datetime.now().isoformat()
            _add_system_msg(room_id, f"🤖 {removed.name} 离开了群聊")
            _save_data()
            return {"success": True, "agent_name": removed.name}
    return {"error": f"Agent '{agent_id}' not found in room"}

# ============ Plugin Class ============
class PPlugin:
    def __init__(self):
        self.name = "P"
        self.version = CURRENT_VERSION
        self.id = "p_plugin"
        _load_data()
        logger.info(f"[P] v{self.version} initialized")
    
    def register(self, api):
        # HTTP routes for web UI
        api.register_http_router(router, prefix="/plugins/p_plugin", tags=["p-plugin"])
        
        # Agent tools — accessible from any channel (WeChat/DingTalk/Feishu/Console)
        api.register_tool(
            tool_name="p_create_room",
            tool_func=_tool_create_room,
            description="Create a new AI group chat room. The room can have multiple AI agents. "
                        "Returns room ID and share link. When a WeChat user wants to start "
                        "an AI group chat, use this tool first.",
            icon="🏠",
        )
        api.register_tool(
            tool_name="p_list_rooms",
            tool_func=_tool_list_rooms,
            description="List all AI group chat rooms with their details (name, agent count, share link).",
            icon="📋",
        )
        api.register_tool(
            tool_name="p_get_room_info",
            tool_func=_tool_get_room_info,
            description="Get detailed information about a group chat room, including its agents and share link.",
            icon="ℹ️",
        )
        api.register_tool(
            tool_name="p_get_room_messages",
            tool_func=_tool_get_room_messages,
            description="Get recent messages from a group chat room.",
            icon="📜",
        )
        api.register_tool(
            tool_name="p_send_room_message",
            tool_func=_tool_send_room_message,
            description="Send a message to a group chat room. The room's AI agents will see this message. "
                        "Use this when a user (via any channel) wants to send a message to an AI group chat.",
            icon="💬",
        )
        api.register_tool(
            tool_name="p_add_agent",
            tool_func=_tool_add_agent,
            description="Add an AI agent to a group chat room. The agent will participate in conversations. "
                        "Use this when a user wants to add an AI assistant to their group chat.",
            icon="🤖",
        )
        api.register_tool(
            tool_name="p_remove_agent",
            tool_func=_tool_remove_agent,
            description="Remove an AI agent from a group chat room.",
            icon="❌",
        )
        
        # Register WeChat channel handler
        self._register_wechat_handler(api)
        
        logger.info(f"[P] Agent tools registered: p_create_room, p_list_rooms, p_get_room_info, "
                     f"p_get_room_messages, p_send_room_message, p_add_agent, p_remove_agent")
        logger.info(f"[P] WeChat channel handler registered")
    
    def _register_wechat_handler(self, api):
        """Register WeChat channel message handler."""
        # ── Ensure official room exists on startup ──
        # (PawApp on_launch is not called for type:general plugins)
        asyncio.create_task(_ensure_official_room())
        
        try:
            # Check if channel API is available
            if hasattr(api, 'register_channel_handler'):
                api.register_channel_handler(
                    channel="wechat",
                    handler=self._handle_wechat_message,
                    agent_name="P-Chat",
                    agent_description="AI 群聊助手 - 创建房间、管理智能体、群聊对话",
                    welcome_message="""👋 你好！我是 **P-Chat** 🤖

我可以帮你创建 AI 群聊房间，与多个智能体一起实时聊天！

**快速开始：**
• 输入「**创建房间**」开始新的 AI 群聊
• 输入「**房间列表**」查看所有房间
• 直接发送消息即可参与群聊

试试说「创建房间」开始吧！"""
                )
        except Exception as e:
            logger.warning(f"[P] Could not register WeChat handler: {e}")
    
    async def _handle_wechat_message(self, message: dict) -> str:
        """Handle incoming WeChat message."""
        user_id = message.get("user_id", "")
        nickname = message.get("nickname", "微信用户")
        content = message.get("content", "").strip()
        
        # Command patterns
        import re
        
        # Create room command
        if re.match(r'^(创建房间|新建房间|开始群聊|create room)', content, re.I):
            return await self._wechat_create_room(user_id, nickname)
        
        # List rooms command
        if re.match(r'^(房间列表|查看房间|list rooms|rooms)', content, re.I):
            return await self._wechat_list_rooms()
        
        # Join room command
        match = re.match(r'^(加入房间|进入房间|join room)\s+(\w+)', content, re.I)
        if match:
            room_id = match.group(2)
            return await self._wechat_join_room(user_id, room_id, nickname)
        
        # Help command
        if re.match(r'^(帮助|help|菜单|menu|\?)', content, re.I):
            return self._wechat_help()
        
        # Default: send to current room or auto-create
        return await self._wechat_send_message(user_id, nickname, content)
    
    async def _wechat_create_room(self, user_id: str, nickname: str) -> str:
        """Create room for WeChat user."""
        result = await _tool_create_room(name=f"{nickname}的群聊", user_id=f"wechat_{user_id}", nickname=nickname)
        
        if "error" in result:
            return f"❌ 创建失败: {result['error']}"
        
        room_id = result.get("room_id")
        _wechat_user_rooms[user_id] = room_id
        
        # Get share link
        info = await _tool_get_room_info(room_id=room_id)
        share_link = info.get("share_link", "")
        
        return f"""✅ 房间创建成功！

🏠 **{result.get('room_name')}**
🆔 房间ID: `{room_id}`

🔗 **分享链接**: {share_link}

💬 现在直接发送消息，我会转发到群聊中！"""
    
    async def _wechat_list_rooms(self) -> str:
        """List rooms for WeChat."""
        result = await _tool_list_rooms()
        rooms = result.get("rooms", [])
        
        if not rooms:
            return "📭 暂无房间，输入「创建房间」开始吧！"
        
        msg = "📋 **房间列表**\n\n"
        for i, room in enumerate(rooms[:5], 1):
            msg += f"{i}. **{room.get('name')}**\n"
            msg += f"   🆔 `{room.get('id')}` | 🤖 {room.get('agent_count', 0)} 个智能体\n\n"
        
        msg += "💡 输入「加入房间 xxx」加入指定房间"
        return msg
    
    async def _wechat_join_room(self, user_id: str, room_id: str, nickname: str) -> str:
        """Join room from WeChat."""
        info = await _tool_get_room_info(room_id=room_id)
        
        if "error" in info:
            return f"❌ 房间不存在: {room_id}"
        
        _wechat_user_rooms[user_id] = room_id
        
        agents = info.get("agents", [])
        agent_names = [a.get("name") for a in agents]
        
        return f"""✅ 已加入房间: **{info.get('name')}**

🤖 智能体: {', '.join(agent_names) or '暂无'}

💬 直接发送消息即可参与群聊！"""
    
    async def _wechat_send_message(self, user_id: str, nickname: str, content: str) -> str:
        """Send message from WeChat."""
        room_id = _wechat_user_rooms.get(user_id)
        
        if not room_id:
            # Auto-create room
            return await self._wechat_create_room(user_id, nickname)
        
        # Send message
        result = await _tool_send_room_message(
            room_id=room_id,
            user_id=f"wechat_{user_id}",
            nickname=nickname,
            content=content
        )
        
        if "error" in result:
            return f"❌ 发送失败: {result['error']}"
        
        # Wait for AI responses
        await asyncio.sleep(1.5)
        
        # Get messages
        msgs = await _tool_get_room_messages(room_id=room_id, limit=10)
        
        # Find AI responses (not from this user, after our message)
        ai_responses = []
        user_msg_id = result.get("message_id")
        found_user = False
        
        for m in reversed(msgs.get("messages", [])):
            if m.get("id") == user_msg_id:
                found_user = True
                continue
            if found_user and m.get("sender_id") != f"wechat_{user_id}" and m.get("type") == "text":
                ai_responses.append(f"🤖 **{m.get('sender_name')}**: {m.get('content')}")
            if len(ai_responses) >= 3:
                break
        
        if ai_responses:
            return "\n\n".join(reversed(ai_responses))
        else:
            return "✅ 消息已发送，智能体正在思考中..."
    
    def _wechat_help(self) -> str:
        """Get help message for WeChat."""
        return """📖 **P-Chat 命令菜单**

🏠 **房间管理**
• `创建房间` - 创建新的 AI 群聊
• `房间列表` - 查看所有房间
• `加入房间 xxx` - 加入指定房间

💬 **消息**
• 直接输入文字 - 发送到当前房间

💡 首次使用直接发送消息会自动创建房间！"""
    
    def get_router(self):
        return router


# ============ PawApp Tools (for external agents) ============

@app.tool("create_room")
async def pawapp_create_room(ctx: PawAppContext, name: str = "聊天室", room_type: str = "public"):
    """创建 AI 群聊房间"""
    creator_id = ctx.user_id or "system"
    creator_name = ctx.user_name or "System"
    # Use the underlying data functions
    room_id = f"room_{uuid.uuid4().hex[:8]}"
    now = datetime.now().isoformat()
    rooms[room_id] = {
        "id": room_id, "name": name, "type": room_type,
        "created_at": now, "creator_id": creator_id, "creator_name": creator_name,
        "agents": [], "messages": []
    }
    _save_data()
    return {"success": True, "room_id": room_id, "room": rooms[room_id]}


@app.tool("send_message")
async def pawapp_send_message(ctx: PawAppContext, room_id: str, content: str):
    """向 AI 群聊房间发送消息"""
    sender_name = ctx.user_name or "User"
    result = await _tool_send_room_message(
        room_id=room_id, content=content, sender_name=sender_name
    )
    return result


@app.tool("list_rooms")
async def pawapp_list_rooms(ctx: PawAppContext):
    """查看所有 AI 群聊房间列表"""
    return _tool_list_rooms()


@app.tool("get_room_messages")
async def pawapp_get_room_messages(ctx: PawAppContext, room_id: str, limit: int = 20):
    """获取指定房间的消息历史"""
    return await _tool_get_room_messages(room_id=room_id, limit=limit)


# ============ Plugin Export ============
# PPlugin instance with register() that calls api.register_http_router()
# This is the same pattern used by TeamChat (verified working).
_plugin = PPlugin()

# Module-level 'plugin' — PluginLoader looks for this
plugin = _plugin

# PawApp compat retained for tool/lifecycle hooks
# (app.on_launch, app.on_terminate still registered via PPlugin.startup/shutdown)
_pawapp_compat = app
