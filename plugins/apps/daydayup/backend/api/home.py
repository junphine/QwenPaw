"""
Home API - 主页学习空间
基于 Deep Tutor 的 Home 模块
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger("daydayup")

router = APIRouter()


class DashboardRequest(BaseModel):
    """仪表板请求"""
    user_id: str


class DashboardResponse(BaseModel):
    """仪表板响应"""
    recent_courses: List[Dict[str, Any]]
    recent_memories: List[Dict[str, Any]]
    active_partners: List[Dict[str, Any]]
    progress: Dict[str, Any]
    notifications: List[Dict[str, Any]]


class QuickActionRequest(BaseModel):
    """快速操作请求"""
    action: str
    user_id: str
    params: Optional[Dict[str, Any]] = None


@router.get("/dashboard")
async def get_dashboard(user_id: str = "default"):
    """
    获取仪表板数据
    
    返回：
    - 最近课程
    - 最近记忆
    - 活跃伙伴
    - 学习进度
    - 通知
    """
    logger.debug(f"[Home] Getting dashboard for user: {user_id}")
    
    return {
        "recent_courses": [
            {
                "id": "course_1",
                "title": "Python 基础入门",
                "progress": 75,
                "last_accessed": "2024-01-15T10:30:00Z"
            },
            {
                "id": "course_2",
                "title": "AI 学习助手使用指南",
                "progress": 30,
                "last_accessed": "2024-01-14T15:20:00Z"
            }
        ],
        "recent_memories": [
            {
                "id": "mem_1",
                "content": "学习了 Python 的列表推导式",
                "timestamp": "2024-01-15T10:30:00Z",
                "layer": "l1"
            },
            {
                "id": "mem_2",
                "content": "理解了面向对象编程的概念",
                "timestamp": "2024-01-14T16:00:00Z",
                "layer": "l2"
            }
        ],
        "active_partners": [
            {
                "id": "partner_1",
                "name": "小智",
                "personality": "friendly",
                "last_chat": "2024-01-15T09:00:00Z"
            }
        ],
        "progress": {
            "courses_completed": 5,
            "courses_in_progress": 3,
            "total_study_time": "45小时30分钟",
            "streak_days": 7
        },
        "notifications": [
            {
                "id": "notif_1",
                "type": "reminder",
                "title": "继续学习 Python 基础",
                "message": "您已经3天没有学习了，继续加油！",
                "timestamp": "2024-01-15T08:00:00Z"
            }
        ]
    }


@router.get("/quick-actions")
async def get_quick_actions():
    """获取快速操作列表"""
    return {
        "actions": [
            {
                "id": "continue_learning",
                "name": "继续学习",
                "icon": "📖",
                "description": "继续上次的学习进度"
            },
            {
                "id": "chat_with_partner",
                "name": "和学习伙伴聊天",
                "icon": "💬",
                "description": "与AI学习伙伴交流"
            },
            {
                "id": "add_memory",
                "name": "记录学习",
                "icon": "📝",
                "description": "记录今天的学习内容"
            },
            {
                "id": "search_knowledge",
                "name": "搜索知识",
                "icon": "🔍",
                "description": "在知识库中搜索"
            },
            {
                "id": "create_agent",
                "name": "创建智能体",
                "icon": "🤖",
                "description": "创建自定义AI智能体"
            }
        ]
    }


@router.post("/quick-action")
async def execute_quick_action(request: QuickActionRequest):
    """执行快速操作"""
    logger.info(f"[Home] Quick action: {request.action} for user: {request.user_id}")
    
    action_handlers = {
        "continue_learning": _handle_continue_learning,
        "chat_with_partner": _handle_chat_with_partner,
        "add_memory": _handle_add_memory,
        "search_knowledge": _handle_search_knowledge,
        "create_agent": _handle_create_agent
    }
    
    handler = action_handlers.get(request.action)
    if not handler:
        raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")
    
    return await handler(request.user_id, request.params or {})


async def _handle_continue_learning(user_id: str, params: Dict[str, Any]):
    """处理继续学习"""
    return {
        "success": True,
        "action": "continue_learning",
        "redirect": "/learning/continue",
        "data": {
            "course_id": "course_1",
            "lesson_id": "lesson_5"
        }
    }


async def _handle_chat_with_partner(user_id: str, params: Dict[str, Any]):
    """处理和学习伙伴聊天"""
    return {
        "success": True,
        "action": "chat_with_partner",
        "redirect": "/partners/chat",
        "data": {
            "partner_id": "partner_1"
        }
    }


async def _handle_add_memory(user_id: str, params: Dict[str, Any]):
    """处理记录学习"""
    return {
        "success": True,
        "action": "add_memory",
        "redirect": "/memory/add",
        "data": {}
    }


async def _handle_search_knowledge(user_id: str, params: Dict[str, Any]):
    """处理搜索知识"""
    return {
        "success": True,
        "action": "search_knowledge",
        "redirect": "/knowledge/search",
        "data": {
            "query": params.get("query", "")
        }
    }


async def _handle_create_agent(user_id: str, params: Dict[str, Any]):
    """处理创建智能体"""
    return {
        "success": True,
        "action": "create_agent",
        "redirect": "/agents/create",
        "data": {}
    }


@router.get("/stats")
async def get_home_stats(user_id: str = "default"):
    """获取主页统计"""
    return {
        "total_courses": 12,
        "completed_courses": 5,
        "total_memories": 156,
        "active_partners": 3,
        "total_study_time": "45小时30分钟",
        "streak_days": 7,
        "weekly_progress": [
            {"day": "周一", "minutes": 60},
            {"day": "周二", "minutes": 90},
            {"day": "周三", "minutes": 45},
            {"day": "周四", "minutes": 120},
            {"day": "周五", "minutes": 30},
            {"day": "周六", "minutes": 0},
            {"day": "周日", "minutes": 45}
        ]
    }
