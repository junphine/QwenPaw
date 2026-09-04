# -*- coding: utf-8 -*-
"""
P Plugin v4.0.0 - PawApp SDK Version
AI Group Chat with Multi-Channel Integration

Migration from FastAPI to PawApp SDK:
- Uses PawApp, get_ctx, SSEChannel
- Lifecycle hooks: @app.on_launch, @app.on_terminate
- Compatible with QwenPaw v2.0.1+
"""
import asyncio
import json
import logging
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field

# PawApp SDK imports
from qwenpaw.pawapp import PawApp, get_ctx
from qwenpaw.pawapp.task import SSEChannel

logger = logging.getLogger("p_plugin")

# ============ Configuration ============
CURRENT_VERSION = "4.0.0"
PLUGIN_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PLUGIN_DIR / "data"
FILES_DIR = DATA_DIR / "files"
DATA_DIR.mkdir(parents=True, exist_ok=True)
FILES_DIR.mkdir(parents=True, exist_ok=True)

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

class Room(BaseModel):
    id: str
    name: str
    type: str = "public"  # public, private, official
    creator_id: str
    creator_nickname: str
    agents: List[AgentConfig] = []
    password: Optional[str] = None
    created_at: str
    updated_at: str

class Message(BaseModel):
    id: str
    room_id: str
    sender_id: str
    sender_name: str
    content: str
    type: str = "text"  # text, image, file, system
    mentions: List[str] = []
    timestamp: str
    file_id: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None

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
_agent_contexts: Dict[str, Dict[str, List[Dict]]] = {}

# ============ WebSocket Manager (PawApp compatible) ============
class ConnectionManager:
    """WebSocket connection manager for real-time updates"""
    def __init__(self):
        self.connections: Dict[str, Any] = {}
        self.room_subscriptions: Dict[str, set] = {}
    
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
                except Exception:
                    disconnected.append(client_id)
            else:
                disconnected.append(client_id)
        for client_id in disconnected:
            self.room_subscriptions[room_id].discard(client_id)

manager = ConnectionManager()

# ============ Helpers ============
def _generate_id() -> str:
    return f"{uuid.uuid4().hex[:16]}"

def _save_data():
    try:
        data = {
            "rooms": {k: v.dict() for k, v in _rooms.items()},
            "messages": {k: [m.dict() for m in v] for k, v in _messages.items()},
            "files": {k: v.dict() for k, v in _files.items()}
        }
        with open(DATA_DIR / "data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"[P] Save failed: {e}")

def _load_data():
    global _rooms, _messages, _files
    try:
        data_file = DATA_DIR / "data.json"
        if data_file.exists():
            with open(data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                _rooms = {k: Room(**v) for k, v in data.get("rooms", {}).items()}
                _messages = {k: [Message(**m) for m in v] for k, v in data.get("messages", {}).items()}
                _files = {k: FileInfo(**v) for k, v in data.get("files", {}).items()}
    except Exception as e:
        logger.error(f"[P] Load failed: {e}")

# ============ Context Formatting (TeamChat style) ============
def _format_context_for_agent(agent_name: str, context_messages: list, current_message: str) -> str:
    """Format chat context for agent - with round indicators"""
    if not context_messages:
        return ""
    
    parts = []
    parts.append(f"【群聊上下文 - {agent_name} 所见】")
    parts.append("")
    
    round_num = 1
    for msg in context_messages:
        sender_id = getattr(msg, 'sender_id', '')
        sender_name = getattr(msg, 'sender_name', '')
        content = getattr(msg, 'content', '')
        msg_type = getattr(msg, 'type', 'text')
        
        if not content or msg_type == 'system':
            continue
        
        if not sender_name:
            sender_name = "用户"
        
        if round_num % 5 == 1 and round_num > 1:
            parts.append(f"--- 第 {(round_num // 5) + 1} 轮 ---")
        
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

# ============ File Generation Parser ============
def _parse_and_create_files(content: str, agent_id: str, agent_name: str, 
                           room_id: str, sender_name: str = "") -> list:
    """Parse [FILE:filename]...[/FILE] directives from agent response"""
    import random as _random
    files_created = []
    
    if not content:
        return files_created
    
    try:
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
                
                ext = Path(filename).suffix.lower()
                file_id = f"file_{_generate_id()}"
                storage_path = FILES_DIR / file_id
                
                # Strip code block markers
                clean_content = file_content.strip()
                if clean_content.startswith("```"):
                    lines = clean_content.split("\n")
                    if len(lines) > 2:
                        clean_content = "\n".join(lines[1:-1])
                    elif len(lines) == 2:
                        clean_content = lines[1]
                
                content_bytes = clean_content.encode('utf-8')
                with open(storage_path, 'wb') as f:
                    f.write(content_bytes)
                
                mime_map = {
                    '.py': 'text/x-python', '.js': 'text/javascript',
                    '.ts': 'text/typescript', '.html': 'text/html',
                    '.css': 'text/css', '.json': 'application/json',
                    '.md': 'text/markdown', '.txt': 'text/plain',
                    '.yaml': 'text/yaml', '.yml': 'text/yaml',
                }
                mime_type = mime_map.get(ext, 'text/plain')
                
                file_info = FileInfo(
                    id=file_id, room_id=room_id, sender_id=agent_id,
                    sender_name=sender_name or agent_name, file_name=filename,
                    file_size=len(content_bytes), mime_type=mime_type,
                    created_at=datetime.now().isoformat()
                )
                _files[file_id] = file_info
                
                files_created.append({
                    "filename": filename, "file_id": file_id,
                    "file_size": len(content_bytes), "mime_type": mime_type
                })
                
            except Exception as e:
                logger.error(f"[P] Failed to create file {filename}: {e}")
        
    except Exception as e:
        logger.error(f"[P] _parse_and_create_files error: {e}")
    
    return files_created

# ============ Agent Calling with PawApp SDK ============
async def call_agent_with_context(ctx, agent_id: str, agent_name: str, personality: str,
                                   room_id: str, user_msg: Message, all_messages: List[Message]) -> str:
    """Call agent with shared conversation context using PawApp SDK"""
    
    # Setup agent context
    try:
        if room_id not in _agent_contexts:
            _agent_contexts[room_id] = {}
        if agent_id not in _agent_contexts[room_id]:
            _agent_contexts[room_id][agent_id] = []
    except Exception:
        pass
    
    # Build conversation history
    conversation_history = []
    try:
        context_messages = all_messages[-20:]
        for msg in context_messages:
            if msg.type == "system":
                continue
            role = "assistant" if msg.sender_id != user_msg.sender_id else "user"
            conversation_history.append({
                "role": role, "name": msg.sender_name or "User",
                "content": msg.content[:500]
            })
    except Exception:
        pass
    
    conversation_history.append({
        "role": "user", "name": user_msg.sender_name,
        "content": user_msg.content
    })
    
    current_content = user_msg.content
    current_sender = user_msg.sender_name
    
    # Format enhanced context
    enhanced_context = _format_context_for_agent(agent_name, context_messages, current_content)
    
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
"""
    
    reply = None
    
    # Step 1: Try ctx.chat_stream (PawApp SDK)
    try:
        prompt = f"""你正在参与一个 AI 群聊。
{enhanced_context}

{file_gen_guide}

请以 {agent_name} 的身份回复当前消息。回复要自然、简洁。
如果需要生成文件，请使用 [FILE:文件名]...[/FILE] 格式。"""
        
        full_response = ""
        async for ev in ctx.chat_stream(prompt, session_id=f"p_plugin:{room_id}:{agent_id}"):
            if hasattr(ev, 'delta') and ev.delta:
                continue
            if hasattr(ev, 'content'):
                content = ev.content
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and item.get('type') == 'text':
                            full_response += item.get('text', '')
                elif isinstance(content, str):
                    full_response += content
        
        if full_response.strip():
            reply = full_response
            logger.info(f"[P] Agent {agent_name} replied via chat_stream")
    except Exception as e:
        logger.debug(f"[P] chat_stream failed for {agent_name}: {e}")
    
    # Step 2: Fallback response
    if not reply or not reply.strip():
        reply = _safe_fallback_response(agent_name, current_content, conversation_history)
    
    # Store in agent context
    try:
        _agent_contexts[room_id][agent_id].append({
            "role": "assistant", "content": reply,
            "timestamp": datetime.now().isoformat()
        })
    except Exception:
        pass
    
    return reply

def _safe_fallback_response(agent_name: str, user_content: str, conversation_history: list) -> str:
    """Generate a contextual response - CANNOT THROW EXCEPTION"""
    import random as _random
    
    lower_content = (user_content or "").lower().strip()
    
    # Greetings
    if any(w in lower_content for w in ["你好", "hello", "hi ", "hey"]):
        greetings = [
            f"你好！我是 {agent_name}，很高兴见到你！",
            f"嗨！{agent_name} 在此，今天想聊点什么呢？",
            f"你好呀！准备好开始今天的交流了！"
        ]
        return _random.choice(greetings)
    
    # Questions
    if "?" in lower_content or "？" in lower_content:
        return f"这是个好问题。让我分享一下我的看法：{user_content[:50]}"
    
    # Thanks
    if any(w in lower_content for w in ["谢谢", "thanks"]):
        return _random.choice(["不客气！", "很高兴能帮到你！", "别客气！"])
    
    # Default
    defaults = [
        f"我理解你的意思。{agent_name} 认为这确实是个值得讨论的话题。",
        f"好的，收到你的消息了。让我思考一下如何回应。",
        f"明白了。在这个群聊中，我想分享一些我的想法。"
    ]
    return _random.choice(defaults)

# ============ Group Chat Handler ============
async def _handle_group_chat(room_id: str, user_msg: Message, ctx):
    """Handle true group chat - all agents share context"""
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
    
    replying_agents = []
    if mentions:
        for agent in active_agents:
            if agent.id in mentions or agent.name in mentions:
                replying_agents.append(agent)
    else:
        replying_agents = list(active_agents)
    
    if not replying_agents:
        return
    
    logger.info(f"[P] 群聊 {room_id}: {len(replying_agents)} 个智能体将回复")
    
    async def _agent_reply_task(agent, delay_seconds):
        await asyncio.sleep(delay_seconds)
        try:
            await manager.broadcast_to_room(room_id, {
                "type": "agent_typing", "agent_name": agent.name, "typing": True
            })
            
            response = await call_agent_with_context(
                ctx, agent.id, agent.name, agent.personality,
                room_id, user_msg, all_messages
            )
            
            await manager.broadcast_to_room(room_id, {
                "type": "agent_typing", "agent_name": agent.name, "typing": False
            })
            
            if not response or not response.strip():
                return
            
            files_created = _parse_and_create_files(response, agent.id, agent.name, room_id, agent.name)
            
            clean_content = re.sub(r'\[FILE:[^\]]+\][\s\S]*?\[/FILE\]', '', response).strip()
            
            if files_created and not clean_content:
                file_names = ', '.join([f['filename'] for f in files_created])
                clean_content = f"📎 已生成文件: {file_names}"
            elif files_created:
                file_names = ', '.join([f['filename'] for f in files_created])
                clean_content += f"\n\n📎 已生成文件: {file_names}"
            
            if not clean_content.strip():
                return
            
            agent_msg = Message(
                id=_generate_id(), room_id=room_id, sender_id=agent.id,
                sender_name=agent.name, content=clean_content, type="text",
                timestamp=datetime.now().isoformat()
            )
            
            _messages[room_id].append(agent_msg)
            _save_data()
            
            await manager.broadcast_to_room(room_id, {
                "type": "new_message", "room_id": room_id, "message": agent_msg.dict()
            })
            
            for f in files_created:
                await manager.broadcast_to_room(room_id, {
                    "type": "new_file", "room_id": room_id, "file": f
                })
            
        except Exception as e:
            logger.error(f"[P] {agent.name} 回复失败: {e}")
            try:
                await manager.broadcast_to_room(room_id, {
                    "type": "agent_typing", "agent_name": agent.name, "typing": False
                })
            except:
                pass
    
    tasks = []
    for i, agent in enumerate(replying_agents):
        delay = i * _random.uniform(1.0, 2.0)
        tasks.append(asyncio.create_task(_agent_reply_task(agent, delay)))
    
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)

# ============ FastAPI Router ============
router = APIRouter()

@router.get("/agents")
async def get_agents(ctx=Depends(get_ctx)):
    """Get available agents"""
    # Get agents from ctx
    try:
        agents_data = await ctx.list_agents() if hasattr(ctx, 'list_agents') else []
        agents = []
        for a in agents_data:
            agents.append(AgentConfig(
                id=a.get('id'), name=a.get('name', 'Agent'),
                icon=a.get('icon', '🤖'), color=a.get('color', '#07C160'),
                description=a.get('description', ''),
                personality=a.get('personality', 'helpful')
            ))
        return {"agents": [a.dict() for a in agents], "count": len(agents)}
    except Exception as e:
        logger.error(f"[P] get_agents error: {e}")
        return {"agents": [], "count": 0}

@router.get("/rooms")
async def get_rooms(user_id: str, ctx=Depends(get_ctx)):
    """Get all rooms"""
    return {"rooms": [r.dict() for r in _rooms.values()]}

@router.post("/rooms/create")
async def create_room(request: dict, ctx=Depends(get_ctx)):
    """Create new room"""
    room_id = _generate_id()
    room = Room(
        id=room_id, name=request.get("name", "New Room"),
        type=request.get("type", "public"),
        creator_id=request.get("user_id", "anonymous"),
        creator_nickname=request.get("nickname", "Anonymous"),
        agents=[], password=request.get("password") or None,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )
    
    _rooms[room_id] = room
    _messages[room_id] = []
    
    _messages[room_id].append(Message(
        id=_generate_id(), room_id=room_id, sender_id="system",
        sender_name="System", content=f"🏠 房间 '{room.name}' 创建成功！",
        type="system", timestamp=datetime.now().isoformat()
    ))
    
    _save_data()
    return room.dict()

@router.get("/rooms/{room_id}")
async def get_room(room_id: str, ctx=Depends(get_ctx)):
    """Get room details"""
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    return _rooms[room_id].dict()

@router.post("/rooms/{room_id}/agents/add")
async def add_agent(room_id: str, request: dict, ctx=Depends(get_ctx)):
    """Add agent to room"""
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    user_id = request.get("user_id")
    agent_data = request.get("agent", {})
    room = _rooms[room_id]
    
    if user_id != room.creator_id:
        raise HTTPException(status_code=403, detail="Only room creator can add agents")
    
    if any(a.id == agent_data.get("id") for a in room.agents):
        return {"success": False, "error": "Agent already in room"}
    
    agent = AgentConfig(
        id=agent_data.get("id"), name=agent_data.get("name", "Agent"),
        icon=agent_data.get("icon", "🤖"), color=agent_data.get("color", "#07C160"),
        description=agent_data.get("description", ""),
        personality=agent_data.get("personality", "helpful"),
        added_by=user_id, added_at=datetime.now().isoformat()
    )
    
    room.agents.append(agent)
    room.updated_at = datetime.now().isoformat()
    
    _messages[room_id].append(Message(
        id=_generate_id(), room_id=room_id, sender_id="system",
        sender_name="System", content=f"🤖 {agent.name} 加入了群聊",
        type="system", timestamp=datetime.now().isoformat()
    ))
    
    await manager.broadcast_to_room(room_id, {
        "type": "room_update", "room_id": room_id,
        "agents": [a.dict() for a in room.agents]
    })
    
    _save_data()
    return {"success": True, "agent": agent.dict()}

@router.post("/rooms/{room_id}/messages")
async def send_message(room_id: str, request: dict, ctx=Depends(get_ctx)):
    """Send message to room"""
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    msg = Message(
        id=_generate_id(), room_id=room_id,
        sender_id=request.get("user_id", "anonymous"),
        sender_name=request.get("nickname", "User"),
        content=request.get("content", ""),
        type=request.get("type", "text"),
        mentions=request.get("mentions", []),
        timestamp=datetime.now().isoformat()
    )
    
    if room_id not in _messages:
        _messages[room_id] = []
    _messages[room_id].append(msg)
    
    await manager.broadcast_to_room(room_id, {
        "type": "new_message", "room_id": room_id, "message": msg.dict()
    })
    
    # Trigger agent replies
    asyncio.create_task(_handle_group_chat(room_id, msg, ctx))
    
    _save_data()
    return msg.dict()

@router.get("/rooms/{room_id}/messages")
async def get_messages(room_id: str, limit: int = 50, ctx=Depends(get_ctx)):
    """Get room messages"""
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    msgs = _messages.get(room_id, [])[-limit:]
    return {"messages": [m.dict() for m in msgs]}

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

# ============ PawApp Definition ============
app = PawApp(name="P", app_id="p_plugin")
app.include_router(router)

@app.on_launch
async def on_launch():
    """Called when plugin is loaded"""
    logger.info("[P] PawApp launched - P Plugin v4.0.0")
    _load_data()
    logger.info(f"[P] Loaded {len(_rooms)} rooms, {len(_files)} files")

@app.on_terminate
async def on_terminate():
    """Called when plugin is unloaded"""
    logger.info("[P] PawApp terminating - saving data")
    _save_data()
    logger.info("[P] Data saved, goodbye!")

# ============ Plugin Export (with explicit route registration) ============
class _PPawAppWrapper:
    """Wrapper around PawApp that ensures routes are registered via api.register_http_router().
    
    The real PawApp SDK's register() may not properly mount include_router'd routes.
    This wrapper intercepts register() and explicitly calls api.register_http_router().
    """
    def __init__(self, pawapp, router):
        self._pawapp = pawapp
        self._router = router
        self._registered = False
    
    def __getattr__(self, name):
        return getattr(self._pawapp, name)
    
    def register(self, api):
        """Intercept PawApp register to ensure routes are explicitly mounted."""
        # First, let the PawApp do its own registration (tools, hooks, lifecycle)
        try:
            result = self._pawapp.register(api) if hasattr(self._pawapp, 'register') else {}
        except Exception as e:
            logger.warning(f"[P] PawApp.register() failed: {e}, falling back to manual registration")
            result = {}
        
        # Explicitly register HTTP routes — this is the critical fix
        try:
            api.register_http_router(self._router, prefix="/api/plugins/p_plugin", tags=["p-plugin"])
            logger.info(f"[P] HTTP routes registered at /api/plugins/p_plugin (v{CURRENT_VERSION})")
            self._registered = True
        except Exception as e:
            logger.error(f"[P] Route registration failed: {e}")
        
        return result

plugin = _PPawAppWrapper(app, router)
