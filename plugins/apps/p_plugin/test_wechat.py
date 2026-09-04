"""
P Plugin WeChat Quick Start
Test WeChat integration with P-Chat agent
"""
import asyncio
import sys
sys.path.insert(0, r'C:\Users\Administrator\.qwenpaw\plugins\p_plugin')

from p_plugin_main import plugin, _tool_create_room, _tool_list_rooms, _tool_get_room_info, _tool_send_room_message

async def test_wechat_flow():
    """Test WeChat user flow."""
    print("=" * 50)
    print("🧪 P Plugin WeChat Integration Test")
    print("=" * 50)
    
    # Simulate WeChat user
    user_id = "wx_test_user_001"
    nickname = "测试用户"
    
    print(f"\n👤 模拟微信用户: {nickname} ({user_id})")
    
    # Step 1: Create room
    print("\n📤 用户发送: '创建房间'")
    result = await _tool_create_room(name=f"{nickname}的群聊", user_id=f"wechat_{user_id}", nickname=nickname)
    print(f"📥 回复: {result}")
    
    if "error" in result:
        print("❌ 创建失败")
        return
    
    room_id = result.get("room_id")
    print(f"✅ 房间创建成功: {room_id}")
    
    # Step 2: Get room info
    print(f"\n📤 获取房间信息...")
    info = await _tool_get_room_info(room_id=room_id)
    print(f"📥 房间: {info.get('name')}")
    print(f"🔗 分享链接: {info.get('share_link')}")
    
    # Step 3: Send message
    print(f"\n📤 用户发送: '大家好！'")
    msg_result = await _tool_send_room_message(
        room_id=room_id,
        user_id=f"wechat_{user_id}",
        nickname=nickname,
        content="大家好！"
    )
    print(f"📥 消息发送: {msg_result.get('message_id')}")
    
    # Step 4: List rooms
    print(f"\n📤 用户发送: '房间列表'")
    rooms = await _tool_list_rooms()
    print(f"📥 找到 {len(rooms.get('rooms', []))} 个房间")
    for r in rooms.get('rooms', []):
        print(f"   - {r.get('name')} ({r.get('id')})")
    
    print("\n" + "=" * 50)
    print("✅ 测试完成！")
    print("=" * 50)
    print(f"\n房间ID: {room_id}")
    print(f"分享链接: http://127.0.0.1:8088/api/plugins/p_plugin/web/{room_id}")

if __name__ == "__main__":
    asyncio.run(test_wechat_flow())
