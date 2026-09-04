"""
API 模块
"""
from .router import create_api_router
from .home import router as home_router
from .partners import router as partners_router
from .agents import router as agents_router
from .cowriter import router as cowriter_router
from .book import router as book_router
from .learning import router as learning_router
from .memory import router as memory_router
from .knowledge import router as knowledge_router

__all__ = [
    "create_api_router",
    "home_router",
    "partners_router",
    "agents_router",
    "cowriter_router",
    "book_router",
    "learning_router",
    "memory_router",
    "knowledge_router"
]
