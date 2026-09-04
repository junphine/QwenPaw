"""
P Plugin WeChat Channel Adapter
Integrates P Plugin with QwenPaw's WeChat channel

Features:
- Auto-create room for WeChat user on first message
- Forward WeChat messages to AI group chat
- Send AI responses back to WeChat
- Support room management via WeChat commands
"""
import json
import re
from datetime import datetime
from typing import Optional, Dict, Any

# Room mapping: wechat_user_id -> room_id
_wechat_rooms: Dict[str, str] = {}

# Command patterns
CMD_CREATE_ROOM = r'^(创建房间|新建房间|开始群聊|create room)'
CMD_LIST_ROOMS = r'^(房间列表|查看房间|list rooms|rooms)'
CMD_JOIN_ROOM = r'^(加入房间|进入房间|join room)\s+(\w+)'
CMD_SEND_MSG = r'^(发送消息|在.*中说|send to)\s+(.+)'
CMD_ADD_AGENT = r'^(添加智能体|加入智能体|add agent)\s+(\w+)'
CMD_HELP = r'^(帮助|help|菜单|menu|\?)'

class WeChatAdapter:
    """Adapter for WeChat channel integration."""
    
    def __init__(self, p_plugin_api):
        self.api = p_plugin_api
        self.user_rooms: Dict[str, str] = {}  # user_id -> room_id
    
    async def handle_message(self, user_id: str, nickname: str, content: str) -> str:
        """Handle incoming WeChat message."""
        
        # Check for commands
        if re.match(CMD_CREATE_ROOM, content, re.I):
            return await self._create_room_for_user(user_id, nickname)
        
        if re.match(CMD_LIST_ROOMS, content, re.I):
            return await self._list_rooms()
        
        match = re.match(CMD_JOIN_ROOM, content, re.I)
        if match:
            room_id = match.group(2)
            return await self._join_room(user_id, room_id, nickname)
        
        match = re.match(CMD_ADD_AGENT, content, re.I)
        if match:
            agent_id = match.group(2)
            return await self._add_agent_to_user_room(user_id, agent_id)
        
        if re.match(CMD_HELP, content, re.I):
            return self._get_help_message()
        
        # Default: send message to user's current room
        return await self._send_to_room(user_id, nickname, content)
    
    async def _create_room_for_user(self, user_id: str, nickname: str) -> str:
        """Create a new room for WeChat user."""
        try:
            # Call P Plugin's create room tool
            result = await self.api.call_tool("p_create_room", {
                "name": f"{nickname}的群聊",
                "user_id": f"wechat_{user_id}",
                "nickname": nickname
            })
            
            if "error" in result:
                return f"❌ 创建房间失败: {result['error']}"
            
            room_id = result.get("room_id")
            self.user_rooms[user_id] = room_id
            
            # Get room info for share link
            info = await self.api.call_tool("p_get_room_info", {"room_id": room_id})
            share_link = info.get("share_link", "")
            
            return f"""✅ 房间创建成功！

🏠 **{result.get('room_name')}**
🆔 房间ID: `{room_id}`
🤖 智能体: {len(info.get('agents', []))} 个

🔗 **分享链接**:
{share_link}

💡 现在直接发送消息，我会转发到群聊中！
输入「帮助」查看更多命令。"""
            
        except Exception as e:
            return f"❌ 创建房间出错: {str(e)}"
    
    async def _list_rooms(self) -> str:
        """List all available rooms."""
        try:
            result = await self.api.call_tool("p_list_rooms", {})
            rooms = result.get("rooms", [])
            
            if not rooms:
                return "📭 暂无房间，输入「创建房间」开始吧！"
            
            msg = "📋 **房间列表**\n\n"
            for i, room in enumerate(rooms[:10], 1):
                msg += f"{i}. **{room.get('name')}**\n"
                msg += f"   🆔 `{room.get('id')}`\n"
                msg += f"   🤖 {room.get('agent_count', 0)} 个智能体\n"
                msg += f"   👤 {room.get('creator_nickname', '未知')}\n\n"
            
            msg += "💡 输入「加入房间 xxx」加入指定房间"
            return msg
            
        except Exception as e:
            return f"❌ 获取房间列表失败: {str(e)}"
    
    async def _join_room(self, user_id: str, room_id: str, nickname: str) -> str:
        """Join a room."""
        try:
            # Get room info first
            info = await self.api.call_tool("p_get_room_info", {"room_id": room_id})
            
            if "error" in info:
                return f"❌ 房间不存在: {room_id}"
            
            self.user_rooms[user_id] = room_id
            
            # Get recent messages
            msgs = await self.api.call_tool("p_get_room_messages", {
                "room_id": room_id,
                "limit": 5
            })
            
            msg = f"""✅ 已加入房间: **{info.get('name')}**

🤖 智能体: {', '.join([a.get('name') for a in info.get('agents', [])]) or '暂无'}

📜 **最近消息**:
"""
            for m in msgs.get("messages", [])[:5]:
                msg += f"\n{m.get('sender_name')}: {m.get('content')[:50]}"
            
            msg += "\n\n💬 直接发送消息即可参与群聊！"
            return msg
            
        except Exception as e:
            return f"❌ 加入房间失败: {str(e)}"
    
    async def _send_to_room(self, user_id: str, nickname: str, content: str) -> str:
        """Send message to user's current room."""
        room_id = self.user_rooms.get(user_id)
        
        if not room_id:
            # Auto-create room for first-time user
            return await self._create_room_for_user(user_id, nickname)
        
        try:
            # Send message
            result = await self.api.call_tool("p_send_room_message", {
                "room_id": room_id,
                "user_id": f"wechat_{user_id}",
                "nickname": nickname,
                "content": content
            })
            
            if "error" in result:
                return f"❌ 发送失败: {result['error']}"
            
            # Wait a moment for AI responses
            await asyncio.sleep(1)
            
            # Get new messages
            msgs = await self.api.call_tool("p_get_room_messages", {
                "room_id": room_id,
                "limit": 10
            })
            
            # Find AI responses
            ai_responses = []
            for m in reversed(msgs.get("messages", [])):
                if m.get("sender_id") != f"wechat_{user_id}" and m.get("type") == "text":
                    ai_responses.append(f"🤖 **{m.get('sender_name')}**: {m.get('content')}")
                if len(ai_responses) >= 3:
                    break
            
            if ai_responses:
                return "\n\n".join(reversed(ai_responses))
            else:
                return "✅ 消息已发送，智能体正在思考中..."
                
        except Exception as e:
            return f"❌ 发送消息失败: {str(e)}"
    
    async def _add_agent_to_user_room(self, user_id: str, agent_id: str) -> str:
        """Add an agent to user's room."""
        room_id = self.user_rooms.get(user_id)
        
        if not room_id:
            return "❌ 请先创建或加入房间"
        
        try:
            result = await self.api.call_tool("p_add_agent", {
                "room_id": room_id,
                "agent_id": agent_id
            })
            
            if "error" in result:
                return f"❌ 添加失败: {result['error']}"
            
            return f"✅ 智能体 **{result.get('agent', {}).get('name', agent_id)}** 已加入房间！"
            
        except Exception as e:
            return f"❌ 添加智能体失败: {str(e)}"
    
    def _get_help_message(self) -> str:
        """Get help message."""
        return """📖 **P-Chat 命令菜单**

🏠 **房间管理**
• `创建房间` - 创建新的 AI 群聊
• `房间列表` - 查看所有房间
• `加入房间 xxx` - 加入指定房间

💬 **消息发送**
• 直接输入文字 - 发送到当前房间

🤖 **智能体管理**
• `添加智能体 xxx` - 添加 AI 智能体

❓ **帮助**
• `帮助` 或 `?` - 显示此菜单

💡 首次使用时，直接发送消息会自动创建房间！"""


# Global adapter instance
_wechat_adapter: Optional[WeChatAdapter] = None

def init_wechat_adapter(p_plugin_api):
    """Initialize WeChat adapter."""
    global _wechat_adapter
    _wechat_adapter = WeChatAdapter(p_plugin_api)
    return _wechat_adapter

async def handle_wechat_message(user_id: str, nickname: str, content: str) -> str:
    """Entry point for WeChat channel."""
    if not _wechat_adapter:
        return "❌ P-Chat 尚未初始化"
    return await _wechat_adapter.handle_message(user_id, nickname, content)
