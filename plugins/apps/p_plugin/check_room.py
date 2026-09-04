import json

with open('data/data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    
for room_id, room in data.get('rooms', {}).items():
    if '115886' in room.get('name', ''):
        print('房间ID:', room_id)
        print('房间名称:', room.get('name'))
        print('创建者ID:', room.get('creator_id'))
        print('场景ID:', room.get('scene_id'))
        print('公告长度:', len(room.get('announcement', '')))
        print('智能体数量:', len(room.get('agents', [])))
        print('面板数量:', len(room.get('panels', [])))
        print('---')
