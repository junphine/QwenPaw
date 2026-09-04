#!/usr/bin/env python3
"""
修复 115886 故事游戏区 - 添加公告和场景
"""
import json
import os
from pathlib import Path

# 数据文件路径
DATA_FILE = Path("~/.qwenpaw/plugins/p_plugin/data/data.json")

# 游戏公告内容
GAME_ANNOUNCEMENT = """# 🏛️ 迷雾小镇 — AI 叙事游戏

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

## 🎭 场景切换
房主可点击场景标签切换氛围：迷雾小镇、灯塔、咖啡馆、诊所、镇公所、森林、午夜

---
*由 P 插件 AI 群聊驱动*
"""

def fix_room():
    """修复 115886 房间数据"""
    if not DATA_FILE.exists():
        print(f"数据文件不存在: {DATA_FILE}")
        return
    
    # 读取数据
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    rooms = data.get("rooms", {})
    
    # 找到 115886 房间
    for room_id, room in rooms.items():
        if "115886" in room.get("name", ""):
            print(f"找到房间: {room['name']} (ID: {room_id})")
            
            # 设置公告
            if not room.get("announcement"):
                room["announcement"] = GAME_ANNOUNCEMENT
                print("✅ 已添加游戏公告")
            else:
                print("ℹ️ 公告已存在，跳过")
            
            # 设置场景
            if not room.get("scene_id"):
                room["scene_id"] = "misty_town"
                room["scene_theme"] = "linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)"
                print("✅ 已设置场景: 迷雾小镇")
            else:
                print(f"ℹ️ 场景已存在: {room.get('scene_id')}")
            
            # 初始化游戏状态
            if not room.get("game_state"):
                room["game_state"] = {
                    "inventories": {},
                    "quests": {}
                }
                print("✅ 已初始化游戏状态")
            
            break
    
    # 保存数据
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("\n✅ 修复完成！重启 QwenPaw 后生效")

if __name__ == "__main__":
    fix_room()
