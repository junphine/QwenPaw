"""
双虾汇 - AI辩论平台插件 v2.4.3
"""
import logging
import json
import os
import httpx
import uuid
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

from qwenpaw.plugins.api import PluginApi

logger = logging.getLogger(__name__)
router = APIRouter()


def _get_qwenpaw_api_base():
    """获取 QwenPaw 主服务 API 地址，自动适配端口"""
    host = "127.0.0.1"
    port = None

    # 1) 优先读环境变量
    env_port = os.environ.get("QWENPAW_API_PORT") or os.environ.get("QWENPAW_PORT")
    if env_port:
        try:
            port = int(env_port)
            return f"http://{host}:{port}"
        except ValueError:
            pass

    # 2) 读 QwenPaw 主配置
    config_paths = [
        os.path.expanduser("~/.qwenpaw/config.json"),
        os.path.expanduser("~/.copaw/config.json"),
        os.path.join(os.path.expanduser("~"), ".qwenpaw", "config.json"),
    ]
    for path in config_paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                api_info = config.get("last_api", {})
                if api_info.get("port"):
                    port = api_info["port"]
                    host = api_info.get("host", host)
                    return f"http://{host}:{port}"
            except Exception:
                continue

    # 3) 兜底当前已知端口
    if port is None:
        port = 49739
    return f"http://{host}:{port}"

class DebateConfig(BaseModel):
    topic: str
    pro_agent_id: Optional[str] = None
    con_agent_id: Optional[str] = None
    max_rounds: int = 3

class DebateMessage(BaseModel):
    session_id: str
    agent_id: str
    side: str
    text: str
    debate_topic: str
    history: List[Dict] = []

class DebateJudge(BaseModel):
    session_id: str
    winner: str
    reason: str = ""

_debate_sessions: Dict[str, Dict] = {}

DEBATE_TOPICS = [
    "内卷对社会发展是好事还是坏事？",
    "AI会不会取代人类的工作？",
    "远程办公是否应该成为常态？",
    "社交媒体拉近了还是疏远了人际关系？",
    "高考制度是否应该废除？",
    "社会主义是否是通往奴役之路？",
]

@router.get("/health")
async def health_check():
    return {"status": "ok", "version": "2.2.0", "sessions": len(_debate_sessions)}

@router.get("/agents")
async def list_agents():
    """获取可用智能体列表"""
    agents = []
    api_base = _get_qwenpaw_api_base()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{api_base}/api/agents")
            if response.status_code == 200:
                data = response.json()
                for agent in data.get("agents", []):
                    agents.append({
                        "id": agent.get("id"),
                        "name": agent.get("name", agent.get("id")),
                        "description": agent.get("description", "AI智能体")[:100]
                    })
    except Exception as e:
        logger.error(f"[双虾汇] 获取智能体失败: {e}")
    
    if not agents:
        agents = [{"id": "default", "name": "Default", "description": "默认智能体"}]
    
    return {"agents": agents}

@router.get("/topics")
async def list_topics():
    return {"topics": DEBATE_TOPICS}

@router.post("/debate/start")
async def start_debate(config: DebateConfig):
    """开始辩论"""
    if not config.pro_agent_id or not config.con_agent_id:
        return {"success": False, "error": "必须选择正反方智能体"}
    
    session_id = str(uuid.uuid4())[:8]
    
    _debate_sessions[session_id] = {
        "topic": config.topic,
        "pro_agent_id": config.pro_agent_id,
        "con_agent_id": config.con_agent_id,
        "max_rounds": config.max_rounds,
        "history": [{
            "role": "system",
            "content": f"📢 辩论开始！\n\n辩题：{config.topic}\n\n正方：{config.pro_agent_id}\n反方：{config.con_agent_id}",
            "timestamp": datetime.now().isoformat()
        }]
    }
    
    return {
        "success": True,
        "session_id": session_id,
        "session": _debate_sessions[session_id]
    }

@router.post("/debate/chat")
async def debate_chat(message: DebateMessage):
    """辩论对话"""
    session_id = message.session_id
    agent_id = message.agent_id
    side = message.side
    text = message.text
    debate_topic = message.debate_topic
    
    if not agent_id or not text:
        return {"success": False, "error": "缺少参数"}
    
    session = _debate_sessions.get(session_id)
    if not session:
        return {"success": False, "error": "会话不存在"}
    
    side_name = "正方" if side == "pro" else "反方"
    opponent_name = "反方" if side == "pro" else "正方"
    
    # 小红书风格系统提示
    system_prompt = f"""你是辩论赛的{side_name}辩手。

辩题：{debate_topic}
你的立场：坚定支持{side_name}观点

说话风格（小红书风格）：
1. 分段清晰，每段一个核心观点
2. 适度使用emoji点缀（✨ 💡 🎯）
3. 每段开头有金句总结
4. 有理有据，引用数据案例
5. 必须回应{opponent_name}的观点
6. 字数150-300字

结构：开篇金句→核心论据→反驳回应→小结升华"""

    # 构建消息
    input_messages = [{
        "role": "system",
        "content": [{"type": "text", "text": system_prompt}]
    }]
    
    # 添加历史
    for msg in message.history[-4:]:  # 最近4条
        if msg.get("role") in ["pro", "con"]:
            role = "user" if msg["role"] == side else "assistant"
            input_messages.append({
                "role": role,
                "content": [{"type": "text", "text": msg.get("content", "")}]
            })
    
    input_messages.append({
        "role": "user",
        "content": [{"type": "text", "text": text}]
    })
    
    response_text = None
    is_mock = False
    
    try:
        api_base = _get_qwenpaw_api_base()
        url = f"{api_base}/api/console/chat"
        payload = {
            "session_id": f"shuangxia:{session_id}:{agent_id}",
            "input": input_messages,
        }
        headers = {
            "Content-Type": "application/json",
            "X-Agent-Id": agent_id
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", url, json=payload, headers=headers) as response:
                response.raise_for_status()
                
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
                        except:
                            continue
                
                if all_text:
                    response_text = "".join(all_text).strip()
                else:
                    is_mock = True
                    
    except Exception as e:
        logger.error(f"[双虾汇] 调用失败: {e}")
        is_mock = True
    
    # 模拟回复
    if not response_text:
        if side == "pro":
            response_text = f"""✨ **核心观点：{debate_topic} 中正方观点更符合时代趋势**

💡 **数据支撑**：研究显示支持正方的案例占比超过65%

🎯 **逻辑推演**：历史规律表明，拥抱变化的一方终将推动社会进步

💭 **回应反方**：反方担心的风险确实存在，但正如汽车发明初期也有人担心马车夫失业，最终社会通过再教育解决了问题

🔥 **小结**：拥抱变化不等于盲目乐观，正方立场坚定支持！"""
        else:
            response_text = f"""✨ **核心观点：{debate_topic} 中反方视角揭示关键风险**

💡 **现实考量**：正方论证建立在"理想条件"下，现实充满不确定性

🎯 **深度反驳**：正方数据多为短期样本，忽略长期外部性

💭 **关键追问**：如果正方设想的美好未来只有30%概率实现，而风险有70%概率发生，如何抉择？

🔥 **小结**：批判性思维为决策留好"安全边际"，反方理性发声！"""
    
    # 保存到历史
    session["history"].append({
        "role": side,
        "content": response_text,
        "timestamp": datetime.now().isoformat(),
        "is_mock": is_mock
    })
    
    return {
        "success": True,
        "response": response_text,
        "mock": is_mock
    }

@router.post("/debate/judge")
async def judge_debate(judgment: DebateJudge):
    """评判"""
    session_id = judgment.session_id
    winner = judgment.winner
    reason = judgment.reason
    
    winner_text = {"pro": "正方", "con": "反方", "draw": "平局"}.get(winner, "未知")
    result = f"🏆 {winner_text}获胜！\n\n判决理由：{reason}"
    
    session = _debate_sessions.get(session_id)
    if session:
        session["history"].append({
            "role": "judge",
            "content": result,
            "timestamp": datetime.now().isoformat()
        })
    
    return {"success": True, "message": result}

@router.post("/debate/reset")
async def reset_debate(data: dict = None):
    session_id = data.get("session_id") if data else None
    if session_id and session_id in _debate_sessions:
        del _debate_sessions[session_id]
    return {"success": True}

class ShuangXiaHuiPlugin:
    PLUGIN_NAME = "双虾汇"
    PLUGIN_VERSION = "v2.4.3"
    
    def __init__(self):
        self.router = router
    
    def register(self, api: PluginApi):
        logger.info(f"[{self.PLUGIN_NAME}] 注册插件...")
        api.register_http_router(
            self.router,
            prefix="/plugins/qwenpaw-doubao",
            tags=["qwenpaw-doubao"],
        )
        logger.info(f"[{self.PLUGIN_NAME}] 注册完成")

plugin = ShuangXiaHuiPlugin()
