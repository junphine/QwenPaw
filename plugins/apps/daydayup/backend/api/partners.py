"""
Partners API - AI 学习伙伴
基于 Deep Tutor 的 Partners 模块
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger("daydayup")

router = APIRouter()


class Partner(BaseModel):
    """伙伴模型"""
    id: str
    name: str
    personality: str
    avatar: Optional[str] = None
    description: str
    capabilities: List[str]
    is_active: bool = True
    created_at: str


class ChatRequest(BaseModel):
    """聊天请求"""
    partner_id: str
    user_id: str
    message: str
    context: Optional[List[Dict[str, Any]]] = None


class ChatResponse(BaseModel):
    """聊天响应"""
    message: str
    partner_id: str
    timestamp: str
    suggestions: Optional[List[str]] = None


# 预定义伙伴
DEFAULT_PARTNERS = [
    {
        "id": "partner_1",
        "name": "小智",
        "personality": "friendly",
        "avatar": "🤖",
        "description": "友善的学习伙伴，善于鼓励和引导",
        "capabilities": ["问答", "解释概念", "提供建议", "鼓励"],
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z"
    },
    {
        "id": "partner_2",
        "name": "小思",
        "personality": "analytical",
        "avatar": "🧠",
        "description": "严谨的思考者，擅长逻辑分析和深度探讨",
        "capabilities": ["逻辑分析", "深度思考", "批判性思维", "知识梳理"],
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z"
    },
    {
        "id": "partner_3",
        "name": "小创",
        "personality": "creative",
        "avatar": "✨",
        "description": "富有创造力的伙伴，擅长联想和创新思维",
        "capabilities": ["创意激发", "联想记忆", "故事讲述", "头脑风暴"],
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z"
    },
    {
        "id": "partner_4",
        "name": "小师",
        "personality": "mentor",
        "avatar": "👨‍🏫",
        "description": "经验丰富的导师，善于规划和指导",
        "capabilities": ["学习规划", "进度跟踪", "方法指导", "答疑解惑"],
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z"
    }
]


@router.get("/list")
async def get_partners():
    """获取所有伙伴列表"""
    logger.debug("[Partners] Getting partner list")
    return {
        "partners": DEFAULT_PARTNERS
    }


@router.get("/{partner_id}")
async def get_partner(partner_id: str):
    """获取单个伙伴详情"""
    logger.debug(f"[Partners] Getting partner: {partner_id}")
    
    partner = next((p for p in DEFAULT_PARTNERS if p["id"] == partner_id), None)
    if not partner:
        raise HTTPException(status_code=404, detail=f"Partner not found: {partner_id}")
    
    return partner


@router.post("/chat")
async def chat_with_partner(request: ChatRequest):
    """与伙伴聊天"""
    logger.info(f"[Partners] Chat from user {request.user_id} to {request.partner_id}")
    
    partner = next((p for p in DEFAULT_PARTNERS if p["id"] == request.partner_id), None)
    if not partner:
        raise HTTPException(status_code=404, detail=f"Partner not found: {request.partner_id}")
    
    # 根据伙伴性格生成不同的回复风格
    response = _generate_partner_response(partner["personality"], request.message)
    
    return {
        "message": response,
        "partner_id": request.partner_id,
        "timestamp": "2024-01-15T10:30:00Z",
        "suggestions": _generate_suggestions(partner["personality"], request.message)
    }


def _generate_partner_response(personality: str, message: str) -> str:
    """根据性格生成回复"""
    responses = {
        "friendly": f"你好！很高兴能和你聊天。关于「{message}」，我觉得这是个很有趣的话题！让我来帮你分析一下...",
        "analytical": f"让我从逻辑的角度来分析「{message}」。首先，我们需要明确几个关键点...",
        "creative": f"哇，「{message}」让我想到了很多有趣的可能性！我们可以这样思考...",
        "mentor": f"这是个很好的问题。让我从学习的角度给你一些建议。关于「{message}」，我建议..."
    }
    return responses.get(personality, responses["friendly"])


def _generate_suggestions(personality: str, message: str) -> List[str]:
    """生成建议"""
    suggestions = {
        "friendly": ["能再详细说说吗？", "这听起来很有趣！", "我们一起探讨一下吧"],
        "analytical": ["有哪些数据支持这个观点？", "还有其他角度吗？", "让我验证一下"],
        "creative": ["这让我想到了...", "我们可以尝试另一种方法", "你觉得这个创意怎么样？"],
        "mentor": ["建议你先复习一下基础", "制定一个学习计划吧", "需要我推荐一些资料吗？"]
    }
    return suggestions.get(personality, suggestions["friendly"])


@router.get("/{partner_id}/history")
async def get_chat_history(partner_id: str, user_id: str = "default", limit: int = 20):
    """获取聊天历史"""
    logger.debug(f"[Partners] Getting chat history for {partner_id}, user: {user_id}")
    
    # 模拟聊天历史
    return {
        "history": [
            {
                "id": "msg_1",
                "role": "user",
                "content": "你好！",
                "timestamp": "2024-01-15T10:00:00Z"
            },
            {
                "id": "msg_2",
                "role": "assistant",
                "content": "你好！很高兴见到你！今天想聊些什么呢？",
                "timestamp": "2024-01-15T10:00:05Z"
            },
            {
                "id": "msg_3",
                "role": "user",
                "content": "我想学习 Python",
                "timestamp": "2024-01-15T10:00:30Z"
            },
            {
                "id": "msg_4",
                "role": "assistant",
                "content": "太棒了！Python 是一门非常优秀的编程语言。你想从哪个方面开始呢？",
                "timestamp": "2024-01-15T10:00:35Z"
            }
        ],
        "total": 4,
        "has_more": False
    }


@router.post("/{partner_id}/clear")
async def clear_chat_history(partner_id: str, user_id: str = "default"):
    """清除聊天历史"""
    logger.info(f"[Partners] Clearing chat history for {partner_id}, user: {user_id}")
    return {"success": True, "message": "Chat history cleared"}


@router.get("/personalities")
async def get_personalities():
    """获取可用性格类型"""
    return {
        "personalities": [
            {
                "id": "friendly",
                "name": "友善型",
                "description": "热情友好，善于鼓励和引导",
                "icon": "😊"
            },
            {
                "id": "analytical",
                "name": "分析型",
                "description": "严谨理性，擅长逻辑分析",
                "icon": "🧠"
            },
            {
                "id": "creative",
                "name": "创意型",
                "description": "富有想象力，擅长创新思维",
                "icon": "✨"
            },
            {
                "id": "mentor",
                "name": "导师型",
                "description": "经验丰富，善于规划和指导",
                "icon": "👨‍🏫"
            }
        ]
    }


@router.post("/create")
async def create_partner(partner: Partner):
    """创建自定义伙伴"""
    logger.info(f"[Partners] Creating custom partner: {partner.name}")
    
    # 这里应该保存到数据库
    return {
        "success": True,
        "partner": partner.dict(),
        "message": "Partner created successfully"
    }
