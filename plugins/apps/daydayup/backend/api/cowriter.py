"""
Co-Writer API - 协同写作
基于 Deep Tutor 的 Co-Writer 模块
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger("daydayup")

router = APIRouter()


class Document(BaseModel):
    """文档模型"""
    id: str
    title: str
    content: str
    type: str  # essay, report, story, code, etc.
    status: str  # draft, reviewing, completed
    created_at: str
    updated_at: str
    owner_id: str
    collaborators: List[str]
    tags: List[str]


class WritingRequest(BaseModel):
    """写作请求"""
    document_id: str
    user_id: str
    action: str  # write, review, suggest, summarize
    content: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class WritingResponse(BaseModel):
    """写作响应"""
    document_id: str
    action: str
    result: str
    suggestions: Optional[List[Dict[str, Any]]] = None
    changes: Optional[List[Dict[str, Any]]] = None


# 示例文档
SAMPLE_DOCUMENTS = [
    {
        "id": "doc_1",
        "title": "Python 学习笔记",
        "content": "# Python 基础\n\nPython 是一门简单易学的编程语言...",
        "type": "notes",
        "status": "draft",
        "created_at": "2024-01-10T10:00:00Z",
        "updated_at": "2024-01-15T15:30:00Z",
        "owner_id": "user_1",
        "collaborators": [],
        "tags": ["Python", "编程", "学习"]
    },
    {
        "id": "doc_2",
        "title": "我的第一篇英文作文",
        "content": "My First Day at School\n\nToday was my first day at school...",
        "type": "essay",
        "status": "reviewing",
        "created_at": "2024-01-12T14:00:00Z",
        "updated_at": "2024-01-14T09:20:00Z",
        "owner_id": "user_1",
        "collaborators": ["agent_2"],
        "tags": ["英语", "写作", "学校"]
    }
]


@router.get("/documents")
async def get_documents(user_id: str = "default"):
    """获取文档列表"""
    logger.debug(f"[CoWriter] Getting documents for user: {user_id}")
    
    return {
        "documents": SAMPLE_DOCUMENTS,
        "total": len(SAMPLE_DOCUMENTS)
    }


@router.get("/documents/{document_id}")
async def get_document(document_id: str):
    """获取单个文档"""
    logger.debug(f"[CoWriter] Getting document: {document_id}")
    
    doc = next((d for d in SAMPLE_DOCUMENTS if d["id"] == document_id), None)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document not found: {document_id}")
    
    return doc


@router.post("/documents")
async def create_document(request: Dict[str, Any], user_id: str = "default"):
    """创建新文档"""
    logger.info(f"[CoWriter] Creating document: {request.get('title')} by user: {user_id}")
    
    import uuid
    from datetime import datetime
    
    doc = {
        "id": f"doc_{uuid.uuid4().hex[:8]}",
        "title": request.get("title", "Untitled"),
        "content": request.get("content", ""),
        "type": request.get("type", "notes"),
        "status": "draft",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "owner_id": user_id,
        "collaborators": request.get("collaborators", []),
        "tags": request.get("tags", [])
    }
    
    return {
        "success": True,
        "document": doc,
        "message": "Document created successfully"
    }


@router.put("/documents/{document_id}")
async def update_document(document_id: str, request: Dict[str, Any]):
    """更新文档"""
    logger.info(f"[CoWriter] Updating document: {document_id}")
    
    doc = next((d for d in SAMPLE_DOCUMENTS if d["id"] == document_id), None)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document not found: {document_id}")
    
    from datetime import datetime
    
    if "title" in request:
        doc["title"] = request["title"]
    if "content" in request:
        doc["content"] = request["content"]
    if "status" in request:
        doc["status"] = request["status"]
    if "tags" in request:
        doc["tags"] = request["tags"]
    
    doc["updated_at"] = datetime.now().isoformat()
    
    return {
        "success": True,
        "document": doc,
        "message": "Document updated successfully"
    }


@router.post("/write")
async def co_write(request: WritingRequest):
    """协同写作"""
    logger.info(f"[CoWriter] Co-writing action: {request.action} on doc: {request.document_id}")
    
    doc = next((d for d in SAMPLE_DOCUMENTS if d["id"] == request.document_id), None)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document not found: {request.document_id}")
    
    if request.action == "write":
        return await _handle_write(doc, request)
    elif request.action == "review":
        return await _handle_review(doc, request)
    elif request.action == "suggest":
        return await _handle_suggest(doc, request)
    elif request.action == "summarize":
        return await _handle_summarize(doc, request)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")


async def _handle_write(doc: Dict, request: WritingRequest) -> Dict[str, Any]:
    """处理写作请求"""
    content = request.content or ""
    
    # AI 协助写作
    suggestions = [
        {
            "type": "improvement",
            "text": "这段内容可以添加更多细节",
            "position": len(content) // 2
        },
        {
            "type": "style",
            "text": "建议使用更正式的表达方式",
            "position": len(content) // 3
        }
    ]
    
    return {
        "document_id": doc["id"],
        "action": "write",
        "result": f"已协助完成写作，当前字数：{len(content)}",
        "suggestions": suggestions,
        "word_count": len(content),
        "estimated_reading_time": f"{len(content) // 200} 分钟"
    }


async def _handle_review(doc: Dict, request: WritingRequest) -> Dict[str, Any]:
    """处理审阅请求"""
    content = doc.get("content", "")
    
    # AI 审阅
    issues = [
        {
            "type": "grammar",
            "severity": "medium",
            "message": "发现一处语法问题",
            "position": 100,
            "suggestion": "建议修改为..."
        },
        {
            "type": "style",
            "severity": "low",
            "message": "表达可以更加简洁",
            "position": 250,
            "suggestion": "可以简化为..."
        }
    ]
    
    return {
        "document_id": doc["id"],
        "action": "review",
        "result": f"审阅完成，发现 {len(issues)} 个问题",
        "issues": issues,
        "score": 85,
        "summary": "整体质量良好，有少量改进空间"
    }


async def _handle_suggest(doc: Dict, request: WritingRequest) -> Dict[str, Any]:
    """处理建议请求"""
    content = doc.get("content", "")
    
    suggestions = [
        {
            "category": "内容",
            "suggestion": "可以添加一个具体的例子来说明这个观点",
            "priority": "high"
        },
        {
            "category": "结构",
            "suggestion": "建议添加一个小标题来分隔这两个段落",
            "priority": "medium"
        },
        {
            "category": "词汇",
            "suggestion": "可以使用更精确的词汇来表达",
            "priority": "low"
        }
    ]
    
    return {
        "document_id": doc["id"],
        "action": "suggest",
        "result": f"提供 {len(suggestions)} 条改进建议",
        "suggestions": suggestions
    }


async def _handle_summarize(doc: Dict, request: WritingRequest) -> Dict[str, Any]:
    """处理总结请求"""
    content = doc.get("content", "")
    
    summary = "本文档主要讨论了...（这里会生成实际的摘要）"
    key_points = [
        "第一点关键内容",
        "第二点关键内容",
        "第三点关键内容"
    ]
    
    return {
        "document_id": doc["id"],
        "action": "summarize",
        "result": "总结完成",
        "summary": summary,
        "key_points": key_points,
        "original_length": len(content),
        "summary_length": len(summary),
        "compression_ratio": f"{len(summary) / len(content) * 100:.1f}%"
    }


@router.get("/templates")
async def get_templates():
    """获取写作模板"""
    return {
        "templates": [
            {
                "id": "template_essay",
                "name": "议论文",
                "description": "标准议论文格式",
                "structure": [
                    {"section": "引言", "description": "引出话题，提出观点"},
                    {"section": "正文", "description": "分论点论证"},
                    {"section": "结论", "description": "总结观点，展望未来"}
                ],
                "icon": "📝"
            },
            {
                "id": "template_report",
                "name": "报告",
                "description": "学术报告格式",
                "structure": [
                    {"section": "摘要", "description": "简要概述"},
                    {"section": "背景", "description": "研究背景"},
                    {"section": "方法", "description": "研究方法"},
                    {"section": "结果", "description": "研究发现"},
                    {"section": "讨论", "description": "讨论分析"},
                    {"section": "结论", "description": "研究结论"}
                ],
                "icon": "📊"
            },
            {
                "id": "template_story",
                "name": "故事",
                "description": "创意故事格式",
                "structure": [
                    {"section": "开头", "description": "引入场景和人物"},
                    {"section": "发展", "description": "情节推进"},
                    {"section": "高潮", "description": "冲突爆发"},
                    {"section": "结局", "description": "问题解决"}
                ],
                "icon": "📖"
            }
        ]
    }


@router.get("/stats")
async def get_writing_stats(user_id: str = "default"):
    """获取写作统计"""
    return {
        "total_documents": len(SAMPLE_DOCUMENTS),
        "total_words": sum(len(d.get("content", "")) for d in SAMPLE_DOCUMENTS),
        "documents_by_type": {
            "notes": 1,
            "essay": 1
        },
        "documents_by_status": {
            "draft": 1,
            "reviewing": 1,
            "completed": 0
        },
        "writing_streak": 5,
        "average_daily_words": 500
    }
