"""
Book API - 交互式书本
基于 Deep Tutor 的 Book 模块
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging

from ..services.book_service import BookService
from ..core.config import Config
from ..core.events import EventManager

logger = logging.getLogger("daydayup")

router = APIRouter()

# 这些将在插件初始化时注入
book_service: Optional[BookService] = None
config: Optional[Config] = None
events: Optional[EventManager] = None


def init_book_service(bs: BookService, cfg: Config, evt_mgr: EventManager):
    """初始化书本服务（由插件主类调用）"""
    global book_service, config, events
    book_service = bs
    config = cfg
    events = evt_mgr


class Book(BaseModel):
    """书本模型"""
    id: str
    title: str
    author: str
    description: str
    cover_image: Optional[str] = None
    chapters: List[Dict[str, Any]]
    total_pages: int
    difficulty: str  # beginner, intermediate, advanced
    category: str
    tags: List[str]
    is_interactive: bool = True
    created_at: str
    updated_at: str


class Chapter(BaseModel):
    """章节模型"""
    id: str
    book_id: str
    title: str
    content: str
    page_number: int
    exercises: List[Dict[str, Any]]
    notes: List[Dict[str, Any]]
    highlights: List[Dict[str, Any]]
    interactive_elements: List[Dict[str, Any]] = []


class ReadingProgress(BaseModel):
    """阅读进度"""
    book_id: str
    user_id: str
    current_chapter: int
    current_page: int
    total_reading_time: int  # minutes
    completion_percentage: float
    last_read_at: str
    bookmarks: List[int]
    notes: List[Dict[str, Any]]


class ProgressUpdateRequest(BaseModel):
    """更新阅读进度请求"""
    current_chapter: int
    current_page: int
    total_reading_time: Optional[int] = None


class NoteRequest(BaseModel):
    """添加笔记请求"""
    chapter_id: str
    page: int
    content: str


class BookmarkRequest(BaseModel):
    """添加书签请求"""
    chapter_id: str
    page: int


class ExerciseSubmitRequest(BaseModel):
    """提交练习请求"""
    chapter_id: str
    exercise_id: str
    answer: Any


@router.get("/list")
async def get_books(category: Optional[str] = None, difficulty: Optional[str] = None):
    """获取书本列表"""
    logger.debug("[Book] Getting book list")

    if not book_service:
        raise HTTPException(status_code=503, detail="Book service not initialized")

    books = book_service.get_books(category=category, difficulty=difficulty)

    return {
        "books": books,
        "total": len(books)
    }


@router.get("/{book_id}/chapters")
async def get_chapters(book_id: str):
    """获取书本章节"""
    logger.debug(f"[Book] Getting chapters for book: {book_id}")

    if not book_service:
        raise HTTPException(status_code=503, detail="Book service not initialized")

    chapters = book_service.get_chapters(book_id)

    if not chapters:
        raise HTTPException(status_code=404, detail=f"Book not found: {book_id}")

    return {
        "book_id": book_id,
        "chapters": chapters
    }


@router.get("/{book_id}/chapters/{chapter_id}")
async def get_chapter(book_id: str, chapter_id: str):
    """获取章节内容"""
    logger.debug(f"[Book] Getting chapter {chapter_id} from book {book_id}")

    if not book_service:
        raise HTTPException(status_code=503, detail="Book service not initialized")

    chapter = book_service.get_chapter(book_id, chapter_id)

    if not chapter:
        raise HTTPException(status_code=404, detail=f"Chapter not found: {chapter_id}")

    return chapter


@router.get("/{book_id}/progress")
async def get_reading_progress(book_id: str, user_id: str = "default"):
    """获取阅读进度"""
    logger.debug(f"[Book] Getting reading progress for book {book_id}, user {user_id}")

    if not book_service:
        raise HTTPException(status_code=503, detail="Book service not initialized")

    progress = book_service.get_reading_progress(book_id, user_id)

    # 添加书本信息
    book = book_service.get_book(book_id)
    if book:
        progress["book_title"] = book["title"]
        progress["book_author"] = book["author"]

    return progress


@router.post("/{book_id}/progress")
async def update_reading_progress(book_id: str,
                                 request: ProgressUpdateRequest = Body(...),
                                 user_id: str = "default"):
    """更新阅读进度"""
    logger.info(f"[Book] Updating reading progress for book {book_id}, user {user_id}")

    if not book_service:
        raise HTTPException(status_code=503, detail="Book service not initialized")

    progress_data = request.dict()
    success = book_service.update_reading_progress(book_id, user_id, progress_data)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to update reading progress")

    # 获取更新后的进度
    updated_progress = book_service.get_reading_progress(book_id, user_id)

    return {
        "success": True,
        "book_id": book_id,
        "progress": updated_progress
    }


@router.post("/{book_id}/notes")
async def add_note(book_id: str, request: NoteRequest = Body(...),
                   user_id: str = "default"):
    """添加笔记"""
    logger.info(f"[Book] Adding note to book {book_id}")

    if not book_service:
        raise HTTPException(status_code=503, detail="Book service not initialized")

    note_id = book_service.add_note(
        book_id=book_id,
        chapter_id=request.chapter_id,
        page=request.page,
        content=request.content,
        user_id=user_id
    )

    if not note_id:
        raise HTTPException(status_code=500, detail="Failed to add note")

    return {
        "success": True,
        "note_id": note_id,
        "message": "Note added successfully"
    }


@router.post("/{book_id}/bookmarks")
async def add_bookmark(book_id: str, request: BookmarkRequest = Body(...),
                      user_id: str = "default"):
    """添加书签"""
    logger.info(f"[Book] Adding bookmark to book {book_id}, page {request.page}")

    if not book_service:
        raise HTTPException(status_code=503, detail="Book service not initialized")

    bookmark_id = book_service.add_bookmark(
        book_id=book_id,
        chapter_id=request.chapter_id,
        page=request.page,
        user_id=user_id
    )

    if not bookmark_id:
        raise HTTPException(status_code=500, detail="Failed to add bookmark")

    return {
        "success": True,
        "bookmark_id": bookmark_id,
        "message": "Bookmark added successfully"
    }


@router.post("/{book_id}/exercises/{exercise_id}/submit")
async def submit_exercise(book_id: str, exercise_id: str,
                         request: ExerciseSubmitRequest = Body(...)):
    """提交练习答案"""
    logger.info(f"[Book] Submitting exercise {exercise_id} for book {book_id}")

    if not book_service:
        raise HTTPException(status_code=503, detail="Book service not initialized")

    result = book_service.submit_exercise(
        book_id=book_id,
        chapter_id=request.chapter_id,
        exercise_id=exercise_id,
        user_answer=request.answer
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to submit exercise"))

    return result


@router.get("/categories")
async def get_categories():
    """获取书本分类"""
    logger.debug("[Book] Getting book categories")

    if not book_service:
        raise HTTPException(status_code=503, detail="Book service not initialized")

    stats = book_service.get_stats()

    return {
        "categories": [
            {"id": cat, "name": cat, "icon": _get_category_icon(cat), "count": 0}
            for cat in stats.get("categories", [])
        ]
    }


@router.get("/recommendations")
async def get_recommendations(user_id: str = "default"):
    """获取推荐书本"""
    logger.debug("[Book] Getting book recommendations")

    if not book_service:
        raise HTTPException(status_code=503, detail="Book service not initialized")

    # 获取所有书本
    books = book_service.get_books()

    # 简单的推荐逻辑：返回最近更新或最受欢迎的书本
    recommendations = []
    for book in books[:3]:  # 取前3本作为示例
        recommendations.append({
            "book_id": book["id"],
            "reason": "基于您的学习历史推荐",
            "confidence": 0.85
        })

    return {
        "recommendations": recommendations
    }


@router.get("/{book_id}")
async def get_book(book_id: str):
    """获取书本详情"""
    logger.debug(f"[Book] Getting book: {book_id}")

    if not book_service:
        raise HTTPException(status_code=503, detail="Book service not initialized")

    book = book_service.get_book(book_id)

    if not book:
        raise HTTPException(status_code=404, detail=f"Book not found: {book_id}")

    return book


def _get_category_icon(category: str) -> str:
    """根据分类获取图标"""
    icons = {
        "编程": "💻",
        "语言": "🌍",
        "数学": "🔢",
        "科学": "🔬",
        "历史": "📜",
        "艺术": "🎨"
    }
    return icons.get(category, "📚")