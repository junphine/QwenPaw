#!/usr/bin/env python3
"""
修复 115886 故事游戏区 - 清理重复面板
"""
import json
from pathlib import Path

DATA_FILE = Path("~/.qwenpaw/plugins/p_plugin/data/data.json")

def fix_panels():
    """清理重复面板"""
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    rooms = data.get("rooms", {})
    
    for room_id, room in rooms.items():
        if "115886" in room.get("name", ""):
            print(f"处理房间: {room['name']} (ID: {room_id})")
            
            panels = room.get("panels", [])
            
            # 找出重复的面板（按名称）
            seen_names = {}
            duplicates = []
            
            for i, panel in enumerate(panels):
                name = panel.get("name", "")
                if name in seen_names:
                    duplicates.append(i)
                    print(f"  发现重复面板: {name} (ID: {panel.get('id')})")
                else:
                    seen_names[name] = i
            
            # 删除重复面板（保留第一个）
            if duplicates:
                # 从后往前删除，避免索引变化
                for i in sorted(duplicates, reverse=True):
                    removed = panels.pop(i)
                    print(f"  已删除重复面板: {removed.get('name')}")
                
                room["panels"] = panels
                print(f"  面板数量: {len(panels)}")
            else:
                print("  没有发现重复面板")
    
    # 保存数据
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("\n✅ 修复完成！")

if __name__ == "__main__":
    fix_panels()
