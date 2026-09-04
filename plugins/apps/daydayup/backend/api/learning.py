"""
Learning API - 学习空间
基于 Deep Tutor 的 Learning Space 模块
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger("daydayup")

router = APIRouter()


class Course(BaseModel):
    """课程模型"""
    id: str
    title: str
    description: str
    cover_image: Optional[str] = None
    difficulty: str  # beginner, intermediate, advanced
    category: str
    lessons: List[Dict[str, Any]]
    total_duration: int  # minutes
    enrolled_count: int
    rating: float
    tags: List[str]
    created_at: str


class Lesson(BaseModel):
    """课时模型"""
    id: str
    course_id: str
    title: str
    content: str
    duration: int  # minutes
    type: str  # video, text, interactive, quiz
    resources: List[Dict[str, Any]]
    is_completed: bool = False


class LearningProgress(BaseModel):
    """学习进度"""
    course_id: str
    user_id: str
    completed_lessons: List[str]
    current_lesson: str
    progress_percentage: float
    total_study_time: int  # minutes
    last_studied_at: str
    quiz_scores: List[Dict[str, Any]]


# 示例课程
SAMPLE_COURSES = [
    {
        "id": "course_1",
        "title": "Python 编程入门",
        "description": "从零开始学习 Python 编程",
        "cover_image": "🐍",
        "difficulty": "beginner",
        "category": "编程",
        "lessons": [
            {"id": "lesson_1", "title": "Python 简介", "duration": 15, "type": "video"},
            {"id": "lesson_2", "title": "安装和环境配置", "duration": 20, "type": "text"},
            {"id": "lesson_3", "title": "基础语法", "duration": 30, "type": "interactive"},
            {"id": "lesson_4", "title": "变量和数据类型", "duration": 25, "type": "video"},
            {"id": "lesson_5", "title": "练习测验", "duration": 15, "type": "quiz"}
        ],
        "total_duration": 105,
        "enrolled_count": 1250,
        "rating": 4.8,
        "tags": ["Python", "编程", "入门"],
        "created_at": "2024-01-01T00:00:00Z"
    },
    {
        "id": "course_2",
        "title": "英语语法精讲",
        "description": "系统学习英语语法",
        "cover_image": "📚",
        "difficulty": "intermediate",
        "category": "语言",
        "lessons": [
            {"id": "lesson_1", "title": "名词基础", "duration": 20, "type": "video"},
            {"id": "lesson_2", "title": "动词时态", "duration": 35, "type": "video"},
            {"id": "lesson_3", "title": "形容词和副词", "duration": 25, "type": "interactive"},
            {"id": "lesson_4", "title": "从句结构", "duration": 40, "type": "video"},
            {"id": "lesson_5", "title": "综合练习", "duration": 30, "type": "quiz"}
        ],
        "total_duration": 150,
        "enrolled_count": 890,
        "rating": 4.6,
        "tags": ["英语", "语法", "学习"],
        "created_at": "2024-01-01T00:00:00Z"
    }
]


@router.get("/courses")
async def get_courses(category: Optional[str] = None, difficulty: Optional[str] = None):
    """获取课程列表"""
    logger.debug("[Learning] Getting course list")
    
    courses = SAMPLE_COURSES
    
    if category:
        courses = [c for c in courses if c["category"] == category]
    
    if difficulty:
        courses = [c for c in courses if c["difficulty"] == difficulty]
    
    return {
        "courses": courses,
        "total": len(courses)
    }


@router.get("/courses/{course_id}")
async def get_course(course_id: str):
    """获取课程详情"""
    logger.debug(f"[Learning] Getting course: {course_id}")
    
    course = next((c for c in SAMPLE_COURSES if c["id"] == course_id), None)
    if not course:
        raise HTTPException(status_code=404, detail=f"Course not found: {course_id}")
    
    return course


@router.get("/courses/{course_id}/lessons")
async def get_lessons(course_id: str):
    """获取课程课时"""
    logger.debug(f"[Learning] Getting lessons for course: {course_id}")
    
    course = next((c for c in SAMPLE_COURSES if c["id"] == course_id), None)
    if not course:
        raise HTTPException(status_code=404, detail=f"Course not found: {course_id}")
    
    return {
        "course_id": course_id,
        "lessons": course.get("lessons", [])
    }


@router.get("/courses/{course_id}/lessons/{lesson_id}")
async def get_lesson(course_id: str, lesson_id: str):
    """获取课时内容"""
    logger.debug(f"[Learning] Getting lesson {lesson_id} from course {course_id}")
    
    course = next((c for c in SAMPLE_COURSES if c["id"] == course_id), None)
    if not course:
        raise HTTPException(status_code=404, detail=f"Course not found: {course_id}")
    
    lesson = next((l for l in course.get("lessons", []) if l["id"] == lesson_id), None)
    if not lesson:
        raise HTTPException(status_code=404, detail=f"Lesson not found: {lesson_id}")
    
    # 模拟课时内容
    lesson_content = {
        "id": lesson_id,
        "course_id": course_id,
        "title": lesson["title"],
        "type": lesson["type"],
        "duration": lesson["duration"],
        "content": f"这是 {lesson['title']} 的内容...\n\n（实际内容会从这里加载）",
        "resources": [
            {"type": "video", "url": "#", "title": "教学视频"},
            {"type": "pdf", "url": "#", "title": "课程讲义"},
            {"type": "code", "url": "#", "title": "示例代码"}
        ]
    }
    
    return lesson_content


@router.get("/courses/{course_id}/progress")
async def get_course_progress(course_id: str, user_id: str = "default"):
    """获取课程进度"""
    logger.debug(f"[Learning] Getting progress for course {course_id}, user {user_id}")
    
    course = next((c for c in SAMPLE_COURSES if c["id"] == course_id), None)
    if not course:
        raise HTTPException(status_code=404, detail=f"Course not found: {course_id}")
    
    lessons = course.get("lessons", [])
    completed_lessons = ["lesson_1", "lesson_2", "lesson_3"]
    current_lesson = "lesson_4"
    
    return {
        "course_id": course_id,
        "user_id": user_id,
        "completed_lessons": completed_lessons,
        "current_lesson": current_lesson,
        "progress_percentage": (len(completed_lessons) / len(lessons)) * 100 if lessons else 0,
        "total_study_time": 180,  # minutes
        "last_studied_at": "2024-01-15T10:30:00Z",
        "quiz_scores": [
            {"lesson_id": "lesson_5", "score": 85, "max_score": 100}
        ]
    }


@router.post("/courses/{course_id}/enroll")
async def enroll_course(course_id: str, user_id: str = "default"):
    """报名课程"""
    logger.info(f"[Learning] User {user_id} enrolling in course {course_id}")
    
    course = next((c for c in SAMPLE_COURSES if c["id"] == course_id), None)
    if not course:
        raise HTTPException(status_code=404, detail=f"Course not found: {course_id}")
    
    return {
        "success": True,
        "course_id": course_id,
        "enrolled_at": "2024-01-15T10:30:00Z",
        "message": "Successfully enrolled in course"
    }


@router.post("/courses/{course_id}/lessons/{lesson_id}/complete")
async def complete_lesson(course_id: str, lesson_id: str, user_id: str = "default"):
    """完成课时"""
    logger.info(f"[Learning] User {user_id} completing lesson {lesson_id} in course {course_id}")
    
    return {
        "success": True,
        "course_id": course_id,
        "lesson_id": lesson_id,
        "completed_at": "2024-01-15T10:30:00Z",
        "message": "Lesson completed successfully"
    }


@router.post("/courses/{course_id}/lessons/{lesson_id}/quiz/submit")
async def submit_quiz(course_id: str, lesson_id: str, request: Dict[str, Any]):
    """提交测验"""
    logger.info(f"[Learning] Submitting quiz for lesson {lesson_id} in course {course_id}")
    
    answers = request.get("answers", {})
    
    # 模拟评分
    score = 85
    max_score = 100
    
    return {
        "success": True,
        "course_id": course_id,
        "lesson_id": lesson_id,
        "score": score,
        "max_score": max_score,
        "percentage": (score / max_score) * 100,
        "feedback": "表现不错！继续保持。",
        "correct_answers": ["A", "B", "C", "D", "A"],
        "user_answers": list(answers.values())
    }


@router.get("/categories")
async def get_categories():
    """获取课程分类"""
    return {
        "categories": [
            {"id": "programming", "name": "编程", "icon": "💻", "course_count": 25},
            {"id": "language", "name": "语言", "icon": "🌍", "course_count": 18},
            {"id": "math", "name": "数学", "icon": "🔢", "course_count": 12},
            {"id": "science", "name": "科学", "icon": "🔬", "course_count": 15},
            {"id": "art", "name": "艺术", "icon": "🎨", "course_count": 8},
            {"id": "music", "name": "音乐", "icon": "🎵", "course_count": 6}
        ]
    }


@router.get("/recommendations")
async def get_recommendations(user_id: str = "default"):
    """获取推荐课程"""
    return {
        "recommendations": [
            {
                "course_id": "course_1",
                "reason": "基于你的编程兴趣推荐",
                "confidence": 0.92
            },
            {
                "course_id": "course_2",
                "reason": "适合你的英语水平",
                "confidence": 0.85
            }
        ]
    }


@router.get("/stats")
async def get_learning_stats(user_id: str = "default"):
    """获取学习统计"""
    return {
        "total_courses": 2,
        "completed_courses": 0,
        "in_progress_courses": 2,
        "total_study_time": 180,  # minutes
        "total_lessons_completed": 6,
        "average_score": 85,
        "learning_streak": 7,
        "weekly_progress": [
            {"day": "周一", "minutes": 30},
            {"day": "周二", "minutes": 45},
            {"day": "周三", "minutes": 60},
            {"day": "周四", "minutes": 30},
            {"day": "周五", "minutes": 45},
            {"day": "周六", "minutes": 0},
            {"day": "周日", "minutes": 30}
        ]
    }
