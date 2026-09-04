"""
游戏智能体 - 聊天室游戏主持人
"""
import random
import re
from typing import Dict, List, Optional, Any
from datetime import datetime

class GameMaster:
    """游戏大师 - 管理聊天室游戏"""
    
    def __init__(self):
        self.games: Dict[str, Any] = {}  # room_id -> game_state
        
    def parse_command(self, content: str) -> tuple:
        """解析游戏命令"""
        content = content.lower().strip()
        
        # 开始游戏
        if match := re.search(r'开始游戏\s+(\w+)', content):
            return ('start', match.group(1))
        
        # 结束游戏
        if '结束游戏' in content or '停止游戏' in content:
            return ('stop', None)
        
        # 游戏规则
        if '游戏规则' in content or '怎么玩' in content:
            return ('rules', None)
        
        # 游戏状态
        if '游戏状态' in content or '进度' in content:
            return ('status', None)
        
        # 猜数字
        if re.match(r'^\d+$', content):
            return ('guess', int(content))
        
        # 成语接龙
        if len(content) >= 4 and self._is_chinese(content):
            return ('idiom', content)
        
        return ('unknown', None)
    
    def _is_chinese(self, text: str) -> bool:
        """检查是否为中文"""
        return bool(re.search(r'[\u4e00-\u9fff]', text))
    
    def start_game(self, room_id: str, game_type: str, player: str) -> str:
        """开始游戏"""
        if room_id in self.games:
            return f"🎮 当前已有游戏进行中：{self.games[room_id]['name']}\n请先结束当前游戏再开始新的！"
        
        if game_type == '猜数字':
            self.games[room_id] = {
                'name': '猜数字',
                'status': 'playing',
                'players': [player],
                'target': random.randint(1, 100),
                'attempts': 0,
                'history': []
            }
            return f"🎮 游戏开始！\n\n我想了一个 **1-100** 之间的数字\n大家来猜吧！\n\n提示：直接发送数字即可"
        
        elif game_type == '成语接龙':
            # 常见成语列表
            idioms = ['一心一意', '意气风发', '发扬光大', '大显身手', '手到擒来']
            start_idiom = random.choice(idioms)
            self.games[room_id] = {
                'name': '成语接龙',
                'status': 'playing',
                'players': [player],
                'last_idiom': start_idiom,
                'used_idioms': [start_idiom],
                'chain_length': 1
            }
            return f"🎮 成语接龙开始！\n\n首个成语：**{start_idiom}**\n\n请接以「{start_idiom[-1]}」开头的成语！"
        
        elif game_type == '真心话大冒险':
            self.games[room_id] = {
                'name': '真心话大冒险',
                'status': 'playing',
                'players': [player],
                'current_player': player,
                'questions': self._get_truth_questions(),
                'dares': self._get_dare_challenges()
            }
            return f"🎮 真心话大冒险开始！\n\n@{player} 请选择：\n1️⃣ 真心话\n2️⃣ 大冒险\n\n回复 1 或 2 做出选择！"
        
        elif game_type == '谁是卧底':
            return "🎮 谁是卧底需要至少3人参与！\n请等待更多玩家加入..."
        
        else:
            return f"🎮 未知游戏：{game_type}\n\n支持的游戏：\n• 猜数字\n• 成语接龙\n• 真心话大冒险\n• 谁是卧底（需3人以上）"
    
    def handle_guess_number(self, room_id: str, guess: int, player: str) -> str:
        """处理猜数字"""
        game = self.games.get(room_id)
        if not game or game['name'] != '猜数字':
            return None
        
        game['attempts'] += 1
        game['history'].append((player, guess))
        
        if guess == game['target']:
            result = f"🎉 **恭喜 @{player} 猜对了！**\n\n答案就是 **{game['target']}**！\n共用了 **{game['attempts']}** 次猜测\n\n游戏结束！"
            del self.games[room_id]
            return result
        elif guess < game['target']:
            return f"📈 **{guess}** 小了！再大一点！"
        else:
            return f"📉 **{guess}** 大了！再小一点！"
    
    def handle_idiom_chain(self, room_id: str, idiom: str, player: str) -> str:
        """处理成语接龙"""
        game = self.games.get(room_id)
        if not game or game['name'] != '成语接龙':
            return None
        
        last_char = game['last_idiom'][-1]
        
        if idiom[0] != last_char:
            return f"❌ 成语必须以「{last_char}」开头！"
        
        if idiom in game['used_idioms']:
            return f"❌ 「{idiom}」已经用过了！"
        
        # 简单检查是否为四字成语
        if len(idiom) != 4:
            return f"❌ 请输入四字成语！"
        
        game['used_idioms'].append(idiom)
        game['last_idiom'] = idiom
        game['chain_length'] += 1
        
        if player not in game['players']:
            game['players'].append(player)
        
        return f"✅ **{idiom}**\n\n当前接龙长度：**{game['chain_length']}**\n请接以「{idiom[-1]}」开头的成语！"
    
    def _get_truth_questions(self) -> List[str]:
        """获取真心话问题"""
        return [
            "你最近最开心的一件事是什么？",
            "如果可以瞬移，你最想去哪里？",
            "你最喜欢的电影是哪部？",
            "你最难忘的童年回忆是什么？",
            "如果可以拥有一种超能力，你希望是什么？"
        ]
    
    def _get_dare_challenges(self) -> List[str]:
        """获取大冒险挑战"""
        return [
            "发一条朋友圈，文字由大家决定",
            "模仿一种动物的叫声",
            "唱一首歌的片段",
            "做一个鬼脸并拍照",
            "说出三个自己的优点"
        ]
    
    def stop_game(self, room_id: str) -> str:
        """结束游戏"""
        if room_id not in self.games:
            return "🎮 当前没有进行中的游戏"
        
        game = self.games.pop(room_id)
        return f"🎮 游戏「{game['name']}」已结束！\n\n感谢大家的参与！"
    
    def get_status(self, room_id: str) -> str:
        """获取游戏状态"""
        if room_id not in self.games:
            return "🎮 当前没有进行中的游戏\n\n发送「@游戏大师 开始游戏 [游戏名]」开始游戏！"
        
        game = self.games[room_id]
        status = f"🎮 当前游戏：**{game['name']}**\n\n"
        status += f"参与玩家：{', '.join(game['players'])}\n"
        status += f"游戏状态：{'进行中' if game['status'] == 'playing' else '已暂停'}\n"
        
        if game['name'] == '猜数字':
            status += f"\n已猜测 **{game['attempts']}** 次"
        elif game['name'] == '成语接龙':
            status += f"\n接龙长度：**{game['chain_length']}**\n"
            status += f"当前成语：**{game['last_idiom']}**"
        
        return status
    
    def get_rules(self, game_type: str = None) -> str:
        """获取游戏规则"""
        rules = {
            '猜数字': """🎮 **猜数字规则**

1. 我想一个 1-100 之间的数字
2. 玩家轮流猜测
3. 我会提示「大了」或「小了」
4. 猜中者获胜！

**提示**：使用二分法可以更快猜中！""",
            
            '成语接龙': """🎮 **成语接龙规则**

1. 我说一个成语作为开始
2. 下一个玩家接以最后一个字开头的成语
3. 不能重复已用过的成语
4. 必须是四字成语

**示例**：
一心一意 → 意气风发 → 发扬光大""",
            
            '真心话大冒险': """🎮 **真心话大冒险规则**

1. 轮流选择「真心话」或「大冒险」
2. 真心话：回答一个问题
3. 大冒险：完成一个挑战
4. 必须诚实回答或完成挑战！

**提示**：问题随机，挑战有趣但不尴尬！"""
        }
        
        if game_type and game_type in rules:
            return rules[game_type]
        
        return """🎮 **游戏列表**

1️⃣ **猜数字** - 猜 1-100 的数字
2️⃣ **成语接龙** - 成语接龙挑战
3️⃣ **真心话大冒险** - 轮流问答挑战
4️⃣ **谁是卧底** - 推理游戏（需3人以上）

发送「@游戏大师 开始游戏 [游戏名]」开始游戏！"""

# 全局游戏大师实例
game_master = GameMaster()
