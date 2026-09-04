#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
删除验证房间脚本
运行方式: python delete_verification_rooms.py
"""

import json
import os

# 要删除的房间 ID（从 data.json 中确认）
ROOMS_TO_DELETE = [
    "1ff29bb3c5004fea",  # "技术交流群" - 微信用户创建的验证房间
    # 如果还有其他验证房间，添加到这里
]

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "data.json")

def delete_rooms():
    """删除指定的房间"""
    if not os.path.exists(DATA_FILE):
        print(f"❌ 数据文件不存在: {DATA_FILE}")
        return
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    rooms = data.get("rooms", {})
    messages = data.get("messages", {})
    files = data.get("files", {})
    share_tokens = data.get("share_tokens", {})
    
    deleted = []
    for room_id in ROOMS_TO_DELETE:
        if room_id in rooms:
            room_name = rooms[room_id].get("name", room_id)
            # 删除房间
            del rooms[room_id]
            # 删除消息
            if room_id in messages:
                del messages[room_id]
            # 删除关联文件
            files_to_delete = [f_id for f_id, f in files.items() if f.get("room_id") == room_id]
            for f_id in files_to_delete:
                del files[f_id]
                file_path = os.path.join(os.path.dirname(__file__), "data", "files", f_id)
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass
            # 删除分享链接
            tokens_to_delete = [t for t, s in share_tokens.items() if s.get("room_id") == room_id]
            for t in tokens_to_delete:
                del share_tokens[t]
            
            deleted.append(f"{room_name} ({room_id})")
            print(f"✅ 已删除: {room_name} ({room_id})")
        else:
            print(f"⚠️ 房间不存在: {room_id}")
    
    # 保存数据
    data["rooms"] = rooms
    data["messages"] = messages
    data["files"] = files
    data["share_tokens"] = share_tokens
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 完成! 共删除 {len(deleted)} 个房间:")
    for d in deleted:
        print(f"  - {d}")
    print("\n⚠️ 请重启 QwenPaw 使更改生效")

if __name__ == "__main__":
    delete_rooms()