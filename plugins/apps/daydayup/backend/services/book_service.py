"""
图书服务
管理交互式书本和学习内容
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib

from ..core.config import Config

logger = logging.getLogger("daydayup")


class BookService:
    """
    图书服务
    管理交互式书本、章节、阅读进度和学习互动
    基于 Deep Tutor Book 系统
    """

    def __init__(self, data_dir: Path, config: Config):
        self.data_dir = data_dir
        self.config = config
        self.service_dir = data_dir / "books"
        self.service_dir.mkdir(exist_ok=True)

        # 图书存储目录
        self.books_dir = self.service_dir / "books"
        self.books_dir.mkdir(exist_ok=True)

        # 阅读进度存储目录
        self.progress_dir = self.service_dir / "progress"
        self.progress_dir.mkdir(exist_ok=True)

        # 交互内容存储目录
        self.interactions_dir = self.service_dir / "interactions"
        self.interactions_dir.mkdir(exist_ok=True)

        # 初始化存储
        self._init_storage()

        logger.info("[BookService] Initialized")

    def _init_storage(self):
        """初始化存储"""
        # 创建一些示例图书（如果不存在）
        sample_books = [
            {
                "id": "book_1",
                "title": "Python 编程入门",
                "author": "AI 导师",
                "description": "从零开始学习 Python 编程，适合初学者的交互式教程",
                "cover_image": "📘",
                "category": "编程",
                "difficulty": "beginner",
                "tags": ["Python", "编程", "入门"],
                "is_interactive": True,
                "total_pages": 85,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "chapters": [
                    {
                        "id": "ch_1",
                        "title": "第一章：Python 简介",
                        "content": "欢迎来到 Python 编程的世界！Python 是一门简单易学、功能强大的编程语言。",
                        "page_count": 10,
                        "exercises": [
                            {
                                "id": "ex_1",
                                "type": "multiple_choice",
                                "question": "Python 的创始人是谁？",
                                "options": ["比尔·盖茨", "史蒂夫·乔布斯", "吉多·范罗苏姆", "埃隆·马斯克"],
                                "correct_answer": 2,
                                "explanation": "Python 是由吉多·范罗苏姆在1989年创造的。"
                            }
                        ]
                    },
                    {
                        "id": "ch_2",
                        "title": "第二章：基础语法",
                        "content": "Python 的语法设计哲学是：优美、明确、简单。这就是著名的 'There should be one-- and preferably only one --obvious way to do it.'",
                        "page_count": 15,
                        "exercises": [
                            {
                                "id": "ex_2",
                                "type": "fill_blank",
                                "question": "在 Python 中，用来定义函数的关键字是______。",
                                "answer": "def",
                                "explanation": "在 Python 中，使用 def 关键字来定义函数。"
                            }
                        ]
                    }
                ]
            },
            {
                "id": "book_2",
                "title": "英语语法精讲",
                "author": "AI 导师",
                "description": "系统学习英语语法，配有大量练习题",
                "cover_image": "📗",
                "category": "语言",
                "difficulty": "intermediate",
                "tags": ["英语", "语法", "学习"],
                "is_interactive": True,
                "total_pages": 82,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "chapters": [
                    {
                        "id": "ch_1",
                        "title": "第一章：名词",
                        "content": "名词是用来表示人、事物、地点或抽象概念的词语。英文名词可以分为可数名词和不可数名词两大类。",
                        "page_count": 12,
                        "exercises": [
                            {
                                "id": "ex_3",
                                "type": "multiple_choice",
                                "question": "以下哪个词是不可数名词？",
                                "options": ["apple", "water", "book", "student"],
                                "correct_answer": 1,
                                "explanation": "water 是不可数名词，不能直接用数字修饰。"
                            }
                        ]
                    }
                ]
            }
        ]

        for book_data in sample_books:
            book_file = self.books_dir / f"{book_data['id']}.json"
            if not book_file.exists():
                self._save_book(book_data)

    async def startup(self):
        """启动服务"""
        logger.info("[BookService] Starting up...")
        # 加载图书到内存缓存（如果需要）

    async def shutdown(self):
        """关闭服务"""
        logger.info("[BookService] Shutting down...")
        # 保存任何未写入的数据

    def _save_book(self, book_data: Dict[str, Any]):
        """保存图书信息"""
        book_id = book_data.get("id")
        if not book_id:
            logger.error("[BookService] Book data missing ID")
            return

        book_file = self.books_dir / f"{book_id}.json"
        try:
            with open(book_file, 'w', encoding='utf-8') as f:
                json.dump(book_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"[BookService] Error saving book {book_id}: {e}")

    def _load_book(self, book_id: str) -> Optional[Dict[str, Any]]:
        """加载图书信息"""
        book_file = self.books_dir / f"{book_id}.json"
        if book_file.exists():
            try:
                with open(book_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"[BookService] Error loading book {book_id}: {e}")
        return None

    def get_book(self, book_id: str) -> Optional[Dict[str, Any]]:
        """获取图书信息"""
        logger.debug(f"[BookService] Getting book: {book_id}")
        return self._load_book(book_id)

    def get_books(self, category: Optional[str] = None,
                  difficulty: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取图书列表"""
        logger.debug("[BookService] Getting books")
        books = []

        if self.books_dir.exists():
            for book_file in self.books_dir.glob("*.json"):
                try:
                    with open(book_file, 'r', encoding='utf-8') as f:
                        book_data = json.load(f)
                        # 应用过滤条件
                        if category and book_data.get("category") != category:
                            continue
                        if difficulty and book_data.get("difficulty") != difficulty:
                            continue
                        books.append(book_data)
                except Exception as e:
                    logger.error(f"[BookService] Error loading book file {book_file}: {e}")

        return books

    def get_chapters(self, book_id: str) -> List[Dict[str, Any]]:
        """获取图书章节"""
        logger.debug(f"[BookService] Getting chapters for book: {book_id}")
        book = self._load_book(book_id)
        if book:
            return book.get("chapters", [])
        return []

    def get_chapter(self, book_id: str, chapter_id: str) -> Optional[Dict[str, Any]]:
        """获取章节详细内容"""
        logger.debug(f"[BookService] Getting chapter {chapter_id} from book {book_id}")
        book = self._load_book(book_id)
        if not book:
            return None

        chapters = book.get("chapters", [])
        for chapter in chapters:
            if chapter.get("id") == chapter_id:
                # 增强章节内容，添加交互元素
                enhanced_chapter = chapter.copy()
                enhanced_chapter["interactive_elements"] = self._generate_interactive_elements(
                    chapter, book_id
                )
                return enhanced_chapter
        return None

    def _generate_interactive_elements(self, chapter: Dict[str, Any],
                                      book_id: str) -> List[Dict[str, Any]]:
        """为章节生成交互元素"""
        elements = []
        chapter_id = chapter.get("id", "")

        # 基于章节内容生成不同类型的交互元素
        title = chapter.get("title", "")
        content = chapter.get("content", "")

        # 添加思考题
        if len(content) > 100:  # 内容足够长时添加思考题
            elements.append({
                "type": "reflection_question",
                "id": f"{chapter_id}_reflect_1",
                "prompt": f"请思考一下：在学习了『{title}』之后，您对这个话题有什么新的理解？",
                "placeholder": "请在这里输入您的思考..."
            })

        # 添加小实践
        if "编程" in chapter.get("book_id", "") or "Python" in title:
            elements.append({
                "type": "code_practice",
                "id": f"{chapter_id}_practice_1",
                "prompt": "请尝试编写一个简单的程序来练习本节内容",
                "placeholder": "# 在这里编写您的代码\nprint('Hello, World!')",
                "language": "python"
            })

        # 添加快速测验
        exercises = chapter.get("exercises", [])
        if exercises:
            elements.append({
                "type": "quick_quiz",
                "id": f"{chapter_id}_quiz_1",
                "question": "快速自测：您刚才学习的内容中，哪一点是最重要的？",
                "options": [
                    "概念理解",
                    "实践操作",
                    "理论知识",
                    "都很重要"
                ],
                "correct_answer": 3
            })

        return elements

    def get_reading_progress(self, book_id: str, user_id: str = "default") -> Dict[str, Any]:
        """获取阅读进度"""
        logger.debug(f"[BookService] Getting reading progress for book {book_id}, user {user_id}")

        progress_file = self.progress_dir / f"{book_id}_{user_id}.json"
        if progress_file.exists():
            try:
                with open(progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"[BookService] Error loading progress for {book_id}_{user_id}: {e}")

        # 返回默认进度
        book = self._load_book(book_id)
        total_chapters = len(book.get("chapters", [])) if book else 0

        return {
            "book_id": book_id,
            "user_id": user_id,
            "current_chapter": 1 if total_chapters > 0 else 0,
            "current_page": 1,
            "total_reading_time": 0,
            "completion_percentage": 0.0,
            "last_read_at": None,
            "bookmarks": [],
            "notes": [],
            "total_chapters": total_chapters
        }

    def update_reading_progress(self, book_id: str, user_id: str = "default",
                               progress_data: Dict[str, Any] = None) -> bool:
        """更新阅读进度"""
        logger.info(f"[BookService] Updating reading progress for book {book_id}, user {user_id}")

        if not progress_data:
            progress_data = {}

        # 确保必填字段存在
        progress_data.update({
            "book_id": book_id,
            "user_id": user_id,
            "last_updated": datetime.now().isoformat()
        })

        # 计算完成百分比
        book = self._load_book(book_id)
        if book:
            total_chapters = len(book.get("chapters", []))
            current_chapter = progress_data.get("current_chapter", 1)
            if total_chapters > 0:
                progress_data["completion_percentage"] = min(100.0,
                    (current_chapter / total_chapters) * 100)

        progress_file = self.progress_dir / f"{book_id}_{user_id}.json"
        try:
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, ensure_ascii=False, indent=2)
            logger.info(f"[BookService] Progress updated for {book_id}_{user_id}")
            return True
        except Exception as e:
            logger.error(f"[BookService] Error saving progress for {book_id}_{user_id}: {e}")
            return False

    def add_note(self, book_id: str, chapter_id: str, page: int,
                content: str, user_id: str = "default") -> str:
        """添加阅读笔记"""
        logger.info(f"[BookService] Adding note to book {book_id}, chapter {chapter_id}, page {page}")

        note_id = self._generate_id(f"{book_id}_{chapter_id}_{page}_{content[:20]}")
        timestamp = datetime.now().isoformat()

        note = {
            "id": note_id,
            "book_id": book_id,
            "chapter_id": chapter_id,
            "page": page,
            "content": content,
            "user_id": user_id,
            "created_at": timestamp,
            "updated_at": timestamp
        }

        # 保存笔记
        notes_dir = self.service_dir / "notes"
        notes_dir.mkdir(exist_ok=True)
        note_file = notes_dir / f"{note_id}.json"

        try:
            with open(note_file, 'w', encoding='utf-8') as f:
                json.dump(note, f, ensure_ascii=False, indent=2)

            # 更新阅读进度中的笔记列表
            progress = self.get_reading_progress(book_id, user_id)
            notes_list = progress.get("notes", [])
            notes_list.append({
                "id": note_id,
                "chapter_id": chapter_id,
                "page": page,
                "content": content[:50] + "..." if len(content) > 50 else content,
                "created_at": timestamp
            })
            progress["notes"] = notes_list
            self.update_reading_progress(book_id, user_id, progress)

            logger.info(f"[BookService] Note added with ID: {note_id}")
            return note_id
        except Exception as e:
            logger.error(f"[BookService] Error adding note: {e}")
            return ""

    def add_bookmark(self, book_id: str, chapter_id: str, page: int,
                    user_id: str = "default") -> str:
        """添加书签"""
        logger.info(f"[BookService] Adding bookmark to book {book_id}, chapter {chapter_id}, page {page}")

        bookmark_id = self._generate_id(f"{book_id}_{chapter_id}_{page}")
        timestamp = datetime.now().isoformat()

        bookmark = {
            "id": bookmark_id,
            "book_id": book_id,
            "chapter_id": chapter_id,
            "page": page,
            "user_id": user_id,
            "created_at": timestamp
        }

        # 保存书签
        bookmarks_dir = self.service_dir / "bookmarks"
        bookmarks_dir.mkdir(exist_ok=True)
        bookmark_file = bookmarks_dir / f"{bookmark_id}.json"

        try:
            with open(bookmark_file, 'w', encoding='utf-8') as f:
                json.dump(bookmark, f, ensure_ascii=False, indent=2)

            # 更新阅读进度中的书签列度
            progress = self.get_reading_progress(book_id, user_id)
            bookmarks_list = progress.get("bookmarks", [])
            bookmarks_list.append({
                "id": bookmark_id,
                "chapter_id": chapter_id,
                "page": page,
                "created_at": timestamp
            })
            progress["bookmarks"] = bookmarks_list
            self.update_reading_progress(book_id, user_id, progress)

            logger.info(f"[BookService] Bookmark added with ID: {bookmark_id}")
            return bookmark_id
        except Exception as e:
            logger.error(f"[BookService] Error adding bookmark: {e}")
            return ""

    def submit_exercise(self, book_id: str, chapter_id: str, exercise_id: str,
                       user_answer: Any, user_id: str = "default") -> Dict[str, Any]:
        """提交练习答案"""
        logger.info(f"[BookService] Submitting exercise {exercise_id} for book {book_id}, chapter {chapter_id}")

        # 获取章节信息
        chapter = self.get_chapter(book_id, chapter_id)
        if not chapter:
            return {
                "success": False,
                "error": f"Chapter not found: {chapter_id}"
            }

        # 查找对应的练习题
        exercises = chapter.get("exercises", [])
        exercise = None
        for ex in exercises:
            if ex.get("id") == exercise_id:
                exercise = ex
                break

        if not exercise:
            return {
                "success": False,
                "error": f"Exercise not found: {exercise_id}"
            }

        # 检查答案
        correct_answer = exercise.get("correct_answer")
        is_correct = self._check_answer(exercise.get("type", ""), correct_answer, user_answer)

        # 生成反馈
        feedback = exercise.get("explanation", "") if is_correct else "再试一次，注意理解概念。"
        if not feedback:
            feedback = "回答正确！" if is_correct else "答案不正确，请重新思考。"

        # 记录练习历史
        self._record_exercise_attempt(book_id, chapter_id, exercise_id, user_answer, is_correct, user_id)

        return {
            "success": True,
            "exercise_id": exercise_id,
            "is_correct": is_correct,
            "feedback": feedback,
            "correct_answer": correct_answer,
            "user_answer": user_answer,
            "timestamp": datetime.now().isoformat()
        }

    def _check_answer(self, exercise_type: str, correct_answer: Any, user_answer: Any) -> bool:
        """检查答案是否正确"""
        if exercise_type == "multiple_choice":
            # 对于选择题，比较索引值
            try:
                return int(user_answer) == int(correct_answer)
            except (ValueError, TypeError):
                return str(user_answer).strip() == str(correct_answer).strip()
        elif exercise_type == "fill_blank":
            # 对于填空题，比较文本内容（忽略大小写和空格）
            if isinstance(user_answer, str) and isinstance(correct_answer, str):
                return user_answer.strip().lower() == correct_answer.strip().lower()
            return str(user_answer).strip() == str(correct_answer).strip()
        else:
            # 其他类型使用精确匹配
            return user_answer == correct_answer

    def _record_exercise_attempt(self, book_id: str, chapter_id: str, exercise_id: str,
                                user_answer: Any, is_correct: bool, user_id: str = "default"):
        """记录练习尝试"""
        try:
            attempts_dir = self.service_dir / "exercise_attempts"
            attempts_dir.mkdir(exist_ok=True)

            attempt_id = self._generate_id(f"{book_id}_{chapter_id}_{exercise_id}_{user_id}_{datetime.now().isoformat()}")
            attempt_file = attempts_dir / f"{attempt_id}.json"

            attempt_data = {
                "attempt_id": attempt_id,
                "book_id": book_id,
                "chapter_id": chapter_id,
                "exercise_id": exercise_id,
                "user_id": user_id,
                "user_answer": user_answer,
                "is_correct": is_correct,
                "timestamp": datetime.now().isoformat()
            }

            with open(attempt_file, 'w', encoding='utf-8') as f:
                json.dump(attempt_data, f, ensure_ascii=False, indent=2)

            # 保持尝试记录在合理范围内（保留最近1000条）
            attempts = list(attempts_dir.glob("*.json"))
            if len(attempts) > 1000:
                attempts.sort(key=lambda x: x.stat().st_mtime)
                for old_attempt in attempts[:-1000]:
                    try:
                        old_attempt.unlink()
                    except:
                        pass

        except Exception as e:
            logger.error(f"[BookService] Error recording exercise attempt: {e}")

    def get_book_interactions(self, book_id: str, user_id: str = "default") -> Dict[str, Any]:
        """获取图书的交互历史"""
        logger.debug(f"[BookService] Getting interactions for book {book_id}, user {user_id}")

        # 获取笔记
        notes = []
        notes_dir = self.service_dir / "notes"
        if notes_dir.exists():
            for note_file in notes_dir.glob("*.json"):
                try:
                    with open(note_file, 'r', encoding='utf-8') as f:
                        note = json.load(f)
                        if note.get("book_id") == book_id and note.get("user_id") == user_id:
                            notes.append(note)
                except Exception as e:
                    logger.error(f"[BookService] Error loading note file {note_file}: {e}")

        # 获取书签
        bookmarks = []
        bookmarks_dir = self.service_dir / "bookmarks"
        if bookmarks_dir.exists():
            for bookmark_file in bookmarks_dir.glob("*.json"):
                try:
                    with open(bookmark_file, 'r', encoding='utf-8') as f:
                        bookmark = json.load(f)
                        if bookmark.get("book_id") == book_id and bookmark.get("user_id") == user_id:
                            bookmarks.append(bookmark)
                except Exception as e:
                    logger.error(f"[BookService] Error loading bookmark file {bookmark_file}: {e}")

        # 获取练习记录
        exercise_attempts = []
        attempts_dir = self.service_dir / "exercise_attempts"
        if attempts_dir.exists():
            for attempt_file in attempts_dir.glob("*.json"):
                try:
                    with open(attempt_file, 'r', encoding='utf-8') as f:
                        attempt = json.load(f)
                        if (attempt.get("book_id") == book_id and
                            attempt.get("user_id") == user_id):
                            exercise_attempts.append(attempt)
                except Exception as e:
                    logger.error(f"[BookService] Error loading attempt file {attempt_file}: {e}")

        return {
            "notes": notes,
            "bookmarks": bookmarks,
            "exercise_attempts": exercise_attempts,
            "total_notes": len(notes),
            "total_bookmarks": len(bookmarks),
            "total_exercise_attempts": len(exercise_attempts)
        }

    def get_stats(self) -> Dict[str, Any]:
        """获取图书服务统计"""
        books = self.get_books()
        total_chapters = sum(len(book.get("chapters", [])) for book in books)
        total_exercises = sum(
            len(chapter.get("exercises", []))
            for book in books
            for chapter in book.get("chapters", [])
        )

        # 获取所有用户的进度数据
        progress_count = 0
        total_reading_time = 0
        if self.progress_dir.exists():
            progress_count = len(list(self.progress_dir.glob("*.json")))
            # 这里可以累加实际的阅读时间，为了简化我们跳过

        return {
            "total_books": len(books),
            "total_chapters": total_chapters,
            "total_exercises": total_exercises,
            "progress_records": progress_count,
            "categories": list(set(book.get("category", "") for book in books if book.get("category"))),
            "difficulty_levels": list(set(book.get("difficulty", "") for book in books if book.get("difficulty")))
        }