"""
Knowledge API - 知识中心
基于 Deep Tutor 的 Knowledge Center 模块
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging
from datetime import datetime

logger = logging.getLogger("daydayup")

router = APIRouter()


class KnowledgeBase(BaseModel):
    """知识库模型"""
    id: str
    name: str
    description: str
    owner_id: str
    documents: List[Dict[str, Any]]
    document_count: int
    total_size: int  # bytes
    created_at: str
    updated_at: str
    is_public: bool
    tags: List[str]


class Document(BaseModel):
    """文档模型"""
    id: str
    base_id: str
    title: str
    content: str
    file_type: str
    file_size: int
    chunks: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    created_at: str
    updated_at: str


class SearchQuery(BaseModel):
    """搜索查询"""
    query: str
    base_ids: Optional[List[str]] = None
    limit: int = 10
    filters: Optional[Dict[str, Any]] = None


class SearchResult(BaseModel):
    """搜索结果"""
    document_id: str
    chunk_id: str
    content: str
    score: float
    metadata: Dict[str, Any]


# 示例知识库
SAMPLE_BASES = [
    {
        "id": "kb_1",
        "name": "Python 学习资料",
        "description": "Python 编程相关的学习资料和笔记",
        "owner_id": "default",
        "documents": [
            {"id": "doc_1", "title": "Python 基础教程.pdf", "size": 2048000},
            {"id": "doc_2", "title": "Python 进阶指南.md", "size": 512000}
        ],
        "document_count": 2,
        "total_size": 2560000,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-15T10:00:00Z",
        "is_public": False,
        "tags": ["Python", "编程", "教程"]
    },
    {
        "id": "kb_2",
        "name": "英语学习资源",
        "description": "英语学习的各种资源和材料",
        "owner_id": "default",
        "documents": [
            {"id": "doc_3", "title": "英语语法大全.pdf", "size": 4096000},
            {"id": "doc_4", "title": "常用词汇表.txt", "size": 102400}
        ],
        "document_count": 2,
        "total_size": 4198400,
        "created_at": "2024-01-05T00:00:00Z",
        "updated_at": "2024-01-14T15:00:00Z",
        "is_public": False,
        "tags": ["英语", "语言", "词汇"]
    }
]


@router.get("/bases")
async def get_knowledge_bases(user_id: str = "default"):
    """获取知识库列表"""
    logger.debug(f"[Knowledge] Getting knowledge bases for user: {user_id}")
    
    return {
        "bases": SAMPLE_BASES,
        "total": len(SAMPLE_BASES)
    }


@router.get("/bases/{base_id}")
async def get_knowledge_base(base_id: str):
    """获取知识库详情"""
    logger.debug(f"[Knowledge] Getting knowledge base: {base_id}")
    
    base = next((b for b in SAMPLE_BASES if b["id"] == base_id), None)
    if not base:
        raise HTTPException(status_code=404, detail=f"Knowledge base not found: {base_id}")
    
    return base


@router.post("/bases")
async def create_knowledge_base(request: Dict[str, Any], user_id: str = "default"):
    """创建知识库"""
    logger.info(f"[Knowledge] Creating knowledge base: {request.get('name')}")
    
    import uuid
    
    base = {
        "id": f"kb_{uuid.uuid4().hex[:8]}",
        "name": request.get("name", "Untitled"),
        "description": request.get("description", ""),
        "owner_id": user_id,
        "documents": [],
        "document_count": 0,
        "total_size": 0,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "is_public": request.get("is_public", False),
        "tags": request.get("tags", [])
    }
    
    SAMPLE_BASES.append(base)
    
    return {
        "success": True,
        "base": base,
        "message": "Knowledge base created successfully"
    }


@router.post("/search")
async def search_knowledge(query: SearchQuery):
    """搜索知识库"""
    logger.info(f"[Knowledge] Searching: {query.query}")
    
    # 模拟搜索结果
    results = [
        {
            "document_id": "doc_1",
            "chunk_id": "chunk_1",
            "content": f"这是关于 '{query.query}' 的相关内容...",
            "score": 0.95,
            "metadata": {
                "document_title": "Python 基础教程.pdf",
                "page": 10,
                "base_id": "kb_1"
            }
        },
        {
            "document_id": "doc_2",
            "chunk_id": "chunk_3",
            "content": f"另一个关于 '{query.query}' 的参考...",
            "score": 0.87,
            "metadata": {
                "document_title": "Python 进阶指南.md",
                "section": "第二章",
                "base_id": "kb_1"
            }
        }
    ]
    
    return {
        "query": query.query,
        "results": results[:query.limit],
        "total": len(results),
        "search_time_ms": 150
    }


@router.post("/bases/{base_id}/documents")
async def upload_document(base_id: str, file: UploadFile = File(...), user_id: str = "default"):
    """上传文档到知识库"""
    logger.info(f"[Knowledge] Uploading document to base {base_id}: {file.filename}")
    
    base = next((b for b in SAMPLE_BASES if b["id"] == base_id), None)
    if not base:
        raise HTTPException(status_code=404, detail=f"Knowledge base not found: {base_id}")
    
    import uuid
    
    doc = {
        "id": f"doc_{uuid.uuid4().hex[:8]}",
        "title": file.filename,
        "size": 0  # 实际应该从文件获取
    }
    
    base["documents"].append(doc)
    base["document_count"] = len(base["documents"])
    base["updated_at"] = datetime.now().isoformat()
    
    return {
        "success": True,
        "document": doc,
        "message": "Document uploaded successfully"
    }


@router.get("/bases/{base_id}/documents/{document_id}")
async def get_document(base_id: str, document_id: str):
    """获取文档详情"""
    logger.debug(f"[Knowledge] Getting document {document_id} from base {base_id}")
    
    base = next((b for b in SAMPLE_BASES if b["id"] == base_id), None)
    if not base:
        raise HTTPException(status_code=404, detail=f"Knowledge base not found: {base_id}")
    
    doc = next((d for d in base.get("documents", []) if d["id"] == document_id), None)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document not found: {document_id}")
    
    return {
        "id": document_id,
        "base_id": base_id,
        "title": doc["title"],
        "content": "文档内容会在这里显示...",
        "chunks": [
            {"id": "chunk_1", "content": "第一部分内容...", "index": 0},
            {"id": "chunk_2", "content": "第二部分内容...", "index": 1}
        ],
        "metadata": {
            "file_type": "pdf",
            "file_size": doc["size"],
            "uploaded_at": base["created_at"]
        }
    }


@router.delete("/bases/{base_id}/documents/{document_id}")
async def delete_document(base_id: str, document_id: str):
    """删除文档"""
    logger.info(f"[Knowledge] Deleting document {document_id} from base {base_id}")
    
    base = next((b for b in SAMPLE_BASES if b["id"] == base_id), None)
    if not base:
        raise HTTPException(status_code=404, detail=f"Knowledge base not found: {base_id}")
    
    base["documents"] = [d for d in base["documents"] if d["id"] != document_id]
    base["document_count"] = len(base["documents"])
    base["updated_at"] = datetime.now().isoformat()
    
    return {
        "success": True,
        "message": "Document deleted successfully"
    }


@router.post("/ask")
async def ask_knowledge(request: Dict[str, Any]):
    """基于知识库问答"""
    question = request.get("question", "")
    base_ids = request.get("base_ids", [])
    
    logger.info(f"[Knowledge] Asking: {question}")
    
    # 模拟问答
    return {
        "question": question,
        "answer": f"基于知识库，关于「{question}」的回答是...\n\n（这里会根据实际检索到的内容生成回答）",
        "sources": [
            {
                "document_id": "doc_1",
                "document_title": "Python 基础教程.pdf",
                "relevance": 0.92,
                "excerpt": "相关内容摘录..."
            }
        ],
        "confidence": 0.88
    }


@router.get("/stats")
async def get_knowledge_stats(user_id: str = "default"):
    """获取知识库统计"""
    total_documents = sum(b["document_count"] for b in SAMPLE_BASES)
    total_size = sum(b["total_size"] for b in SAMPLE_BASES)
    
    return {
        "total_bases": len(SAMPLE_BASES),
        "total_documents": total_documents,
        "total_size": total_size,
        "total_size_formatted": f"{total_size / 1024 / 1024:.2f} MB",
        "by_type": {
            "pdf": 2,
            "md": 1,
            "txt": 1
        },
        "recent_additions": [
            {
                "document_id": "doc_1",
                "title": "Python 基础教程.pdf",
                "added_at": "2024-01-15T10:00:00Z"
            }
        ]
    }


@router.get("/tags")
async def get_all_tags():
    """获取所有标签"""
    all_tags = set()
    for base in SAMPLE_BASES:
        all_tags.update(base.get("tags", []))
    
    return {
        "tags": sorted(list(all_tags))
    }
