"""
Memory API - 三层记忆系统
基于 Deep Tutor 的 Memory 模块

三层记忆：
- L1: 工作记忆（短期，最近50条）
- L2: 语义记忆（中期，最近200条）
- L3: 情景记忆（长期，最多1000条）
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging
from datetime import datetime

logger = logging.getLogger("daydayup")

router = APIRouter()


class MemoryEntry(BaseModel):
    """记忆条目"""
    id: str
    content: str
    layer: str  # l1, l2, l3
    type: str  # learning, conversation, observation, reflection
    source: str
    user_id: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None
    tags: List[str]
    importance: int  # 1-5


class MemoryQuery(BaseModel):
    """记忆查询"""
    query: str
    layers: List[str] = ["l1", "l2", "l3"]
    limit: int = 10
    tags: Optional[List[str]] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class MemoryCreateRequest(BaseModel):
    """创建记忆请求"""
    content: str
    type: str = "learning"
    layer: str = "l1"
    tags: List[str] = []
    importance: int = 3
    metadata: Optional[Dict[str, Any]] = None


# 示例记忆数据
SAMPLE_MEMORIES = [
    {
        "id": "mem_1",
        "content": "学习了 Python 的列表推导式：[x for x in range(10)]",
        "layer": "l1",
        "type": "learning",
        "source": "course_1",
        "user_id": "default",
        "timestamp": "2024-01-15T10:30:00Z",
        "metadata": {"course_id": "course_1", "lesson_id": "lesson_3"},
        "tags": ["Python", "列表", "语法"],
        "importance": 4
    },
    {
        "id": "mem_2",
        "content": "理解了面向对象编程的核心概念：封装、继承、多态",
        "layer": "l2",
        "type": "learning",
        "source": "course_1",
        "user_id": "default",
        "timestamp": "2024-01-14T16:00:00Z",
        "metadata": {"course_id": "course_1", "lesson_id": "lesson_5"},
        "tags": ["Python", "OOP", "概念"],
        "importance": 5
    },
    {
        "id": "mem_3",
        "content": "和小智讨论了学习 Python 的最佳实践",
        "layer": "l1",
        "type": "conversation",
        "source": "partner_1",
        "user_id": "default",
        "timestamp": "2024-01-13T14:00:00Z",
        "metadata": {"partner_id": "partner_1"},
        "tags": ["讨论", "Python", "学习方法"],
        "importance": 3
    },
    {
        "id": "mem_4",
        "content": "发现自己在理解递归概念时遇到困难，需要更多练习",
        "layer": "l3",
        "type": "reflection",
        "source": "self",
        "user_id": "default",
        "timestamp": "2024-01-12T20:00:00Z",
        "metadata": {"topic": "递归", "difficulty": "high"},
        "tags": ["反思", "困难", "递归"],
        "importance": 4
    }
]


@router.get("/layers")
async def get_memory_layers():
    """获取记忆层信息"""
    return {
        "layers": [
            {
                "id": "l1",
                "name": "工作记忆",
                "description": "短期记忆，保存最近的学习内容和交互",
                "capacity": 50,
                "retention_period": "7天",
                "current_count": len([m for m in SAMPLE_MEMORIES if m["layer"] == "l1"])
            },
            {
                "id": "l2",
                "name": "语义记忆",
                "description": "中期记忆，保存重要的概念和知识",
                "capacity": 200,
                "retention_period": "30天",
                "current_count": len([m for m in SAMPLE_MEMORIES if m["layer"] == "l2"])
            },
            {
                "id": "l3",
                "name": "情景记忆",
                "description": "长期记忆，保存重要的学习经历和反思",
                "capacity": 1000,
                "retention_period": "永久",
                "current_count": len([m for m in SAMPLE_MEMORIES if m["layer"] == "l3"])
            }
        ]
    }


@router.get("/list")
async def get_memories(
    layer: Optional[str] = None,
    type: Optional[str] = None,
    limit: int = 50,
    user_id: str = "default"
):
    """获取记忆列表"""
    logger.debug(f"[Memory] Getting memories for user {user_id}, layer: {layer}")
    
    memories = SAMPLE_MEMORIES
    
    if layer:
        memories = [m for m in memories if m["layer"] == layer]
    
    if type:
        memories = [m for m in memories if m["type"] == type]
    
    memories = memories[:limit]
    
    return {
        "memories": memories,
        "total": len(memories),
        "layer": layer,
        "type": type
    }


@router.post("/search")
async def search_memories(query: MemoryQuery, user_id: str = "default"):
    """搜索记忆"""
    logger.info(f"[Memory] Searching memories: {query.query}")
    
    # 模拟搜索
    results = []
    for memory in SAMPLE_MEMORIES:
        if query.query.lower() in memory["content"].lower():
            if memory["layer"] in query.layers:
                results.append(memory)
    
    results = results[:query.limit]
    
    return {
        "query": query.query,
        "results": results,
        "total": len(results),
        "layers": query.layers
    }


@router.post("/create")
async def create_memory(request: MemoryCreateRequest, user_id: str = "default"):
    """创建记忆"""
    logger.info(f"[Memory] Creating memory: {request.content[:50]}...")
    
    import uuid
    
    memory = {
        "id": f"mem_{uuid.uuid4().hex[:8]}",
        "content": request.content,
        "layer": request.layer,
        "type": request.type,
        "source": "user",
        "user_id": user_id,
        "timestamp": datetime.now().isoformat(),
        "metadata": request.metadata or {},
        "tags": request.tags,
        "importance": request.importance
    }
    
    SAMPLE_MEMORIES.insert(0, memory)
    
    return {
        "success": True,
        "memory": memory,
        "message": "Memory created successfully"
    }


@router.post("/{memory_id}/consolidate")
async def consolidate_memory(memory_id: str, target_layer: str = "l2"):
    """整合记忆（升级到其他层）"""
    logger.info(f"[Memory] Consolidating memory {memory_id} to {target_layer}")
    
    memory = next((m for m in SAMPLE_MEMORIES if m["id"] == memory_id), None)
    if not memory:
        raise HTTPException(status_code=404, detail=f"Memory not found: {memory_id}")
    
    memory["layer"] = target_layer
    memory["timestamp"] = datetime.now().isoformat()
    
    return {
        "success": True,
        "memory": memory,
        "message": f"Memory consolidated to {target_layer}"
    }


@router.post("/consolidate/auto")
async def auto_consolidate(user_id: str = "default"):
    """自动整合记忆"""
    logger.info("[Memory] Running auto-consolidation")
    
    # 模拟自动整合
    consolidated = 0
    for memory in SAMPLE_MEMORIES:
        if memory["layer"] == "l1" and memory["importance"] >= 4:
            memory["layer"] = "l2"
            consolidated += 1
    
    return {
        "success": True,
        "consolidated_count": consolidated,
        "message": f"Auto-consolidated {consolidated} memories"
    }


@router.get("/stats")
async def get_memory_stats(user_id: str = "default"):
    """获取记忆统计"""
    l1_count = len([m for m in SAMPLE_MEMORIES if m["layer"] == "l1"])
    l2_count = len([m for m in SAMPLE_MEMORIES if m["layer"] == "l2"])
    l3_count = len([m for m in SAMPLE_MEMORIES if m["layer"] == "l3"])
    
    return {
        "total_memories": len(SAMPLE_MEMORIES),
        "by_layer": {
            "l1": {"count": l1_count, "capacity": 50, "usage": (l1_count / 50) * 100},
            "l2": {"count": l2_count, "capacity": 200, "usage": (l2_count / 200) * 100},
            "l3": {"count": l3_count, "capacity": 1000, "usage": (l3_count / 1000) * 100}
        },
        "by_type": {
            "learning": len([m for m in SAMPLE_MEMORIES if m["type"] == "learning"]),
            "conversation": len([m for m in SAMPLE_MEMORIES if m["type"] == "conversation"]),
            "observation": len([m for m in SAMPLE_MEMORIES if m["type"] == "observation"]),
            "reflection": len([m for m in SAMPLE_MEMORIES if m["type"] == "reflection"])
        },
        "recent_additions": len([m for m in SAMPLE_MEMORIES if m["timestamp"].startswith("2024-01-15")])
    }


@router.get("/timeline")
async def get_memory_timeline(user_id: str = "default", days: int = 30):
    """获取记忆时间线"""
    # 按日期分组
    timeline = {}
    for memory in SAMPLE_MEMORIES:
        date = memory["timestamp"][:10]  # YYYY-MM-DD
        if date not in timeline:
            timeline[date] = []
        timeline[date].append(memory)
    
    return {
        "timeline": [
            {"date": date, "memories": memories, "count": len(memories)}
            for date, memories in sorted(timeline.items(), reverse=True)
        ]
    }


@router.delete("/{memory_id}")
async def delete_memory(memory_id: str):
    """删除记忆"""
    logger.info(f"[Memory] Deleting memory: {memory_id}")
    
    global SAMPLE_MEMORIES
    SAMPLE_MEMORIES = [m for m in SAMPLE_MEMORIES if m["id"] != memory_id]
    
    return {
        "success": True,
        "message": "Memory deleted successfully"
    }


@router.get("/{memory_id}")
async def get_memory(memory_id: str):
    """获取单个记忆"""
    logger.debug(f"[Memory] Getting memory: {memory_id}")
    
    memory = next((m for m in SAMPLE_MEMORIES if m["id"] == memory_id), None)
    if not memory:
        raise HTTPException(status_code=404, detail=f"Memory not found: {memory_id}")
    
    return memory
