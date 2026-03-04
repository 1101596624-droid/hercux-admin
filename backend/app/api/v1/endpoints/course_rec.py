"""
Phase 11: 课程推荐与学习路径 API 端点
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import get_current_user
from app.services.course_recommendation_service import CourseRecommendationService
from app.schemas.schemas import (
    CourseRelationCreate, RecommendedCoursesRequest,
    CourseLearningPathRequest,
)

router = APIRouter()


@router.post("/recommended-courses")
async def recommend_courses(
    request: RecommendedCoursesRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """BKT驱动的个性化课程推荐"""
    return await CourseRecommendationService.recommend_courses(
        db, current_user.id, request.limit, request.subject_id,
    )


@router.post("/learning-path")
async def generate_learning_path(
    request: CourseLearningPathRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """生成个性化学习路径"""
    return await CourseRecommendationService.generate_learning_path(
        db, current_user.id, request.course_id, request.session_minutes,
    )


@router.get("/course-progress")
async def get_course_progress(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """获取所有课程进度"""
    return await CourseRecommendationService.get_course_progress(
        db, current_user.id,
    )


@router.post("/sync-progress/{course_id}")
async def sync_course_progress(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """同步课程级进度"""
    result = await CourseRecommendationService.sync_course_progress(
        db, current_user.id, course_id,
    )
    await db.commit()
    return result


@router.post("/course-relations")
async def add_course_relation(
    request: CourseRelationCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """添加课程关系"""
    rel = await CourseRecommendationService.add_course_relation(
        db, request.model_dump(),
    )
    await db.commit()
    return {"id": rel.id, "message": "课程关系已添加"}


@router.get("/course-relations/{course_id}")
async def get_course_relations(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """获取课程关系"""
    return await CourseRecommendationService.get_course_relations(
        db, course_id,
    )
