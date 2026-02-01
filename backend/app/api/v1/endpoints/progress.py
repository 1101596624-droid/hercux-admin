from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from typing import List, Optional
from datetime import datetime, timedelta, timezone

from app.db.session import get_db
from app.models.models import (
    User,
    LearningProgress,
    CourseNode,
    Course,
    NodeStatus
)
from app.core.security import get_current_user
from pydantic import BaseModel

router = APIRouter()


# ============ Schemas ============

class ProgressSummary(BaseModel):
    """User progress summary"""
    total_nodes_started: int
    total_nodes_completed: int
    total_courses_enrolled: int
    total_learning_hours: float
    current_streak_days: int
    completion_rate: float


class NodeProgressDetail(BaseModel):
    """Detailed node progress"""
    id: int
    node_id: str
    node_title: str
    node_type: str
    course_id: int
    course_name: str
    status: str
    completion_percentage: int
    time_spent_seconds: int
    last_accessed: Optional[datetime]
    completed_at: Optional[datetime]


class CourseProgressDetail(BaseModel):
    """Course progress detail"""
    course_id: int
    course_name: str
    total_nodes: int
    completed_nodes: int
    in_progress_nodes: int
    locked_nodes: int
    completion_percentage: float
    total_time_spent_seconds: int
    last_accessed: Optional[datetime]


# ============ Endpoints ============

@router.get("/summary")
async def get_progress_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's overall learning progress summary

    Returns:
    - Total nodes started/completed
    - Total courses enrolled
    - Total learning hours
    - Current streak
    - Completion rate
    """
    # Get total nodes started
    started_query = select(func.count(LearningProgress.id)).where(
        LearningProgress.user_id == current_user.id
    )
    total_started = await db.scalar(started_query) or 0

    # Get total nodes completed
    completed_query = select(func.count(LearningProgress.id)).where(
        and_(
            LearningProgress.user_id == current_user.id,
            LearningProgress.status == NodeStatus.COMPLETED
        )
    )
    total_completed = await db.scalar(completed_query) or 0

    # Get total courses enrolled (courses with at least one progress record)
    courses_query = select(func.count(func.distinct(CourseNode.course_id))).select_from(
        LearningProgress
    ).join(
        CourseNode, LearningProgress.node_id == CourseNode.id
    ).where(
        LearningProgress.user_id == current_user.id
    )
    total_courses = await db.scalar(courses_query) or 0

    # Get total learning hours
    time_query = select(func.sum(LearningProgress.time_spent_seconds)).where(
        LearningProgress.user_id == current_user.id
    )
    total_seconds = await db.scalar(time_query) or 0
    total_hours = round(total_seconds / 3600, 1)

    # Calculate current streak (consecutive days with activity)
    # For now, return 0 streak to avoid date parsing issues
    # TODO: Fix streak calculation for SQLite
    streak = 0

    # Calculate completion rate
    completion_rate = (total_completed / total_started * 100) if total_started > 0 else 0

    return ProgressSummary(
        total_nodes_started=total_started,
        total_nodes_completed=total_completed,
        total_courses_enrolled=total_courses,
        total_learning_hours=total_hours,
        current_streak_days=streak,
        completion_rate=round(completion_rate, 2)
    )


@router.get("/nodes")
async def get_node_progress(
    current_user: User = Depends(get_current_user),
    course_id: Optional[int] = Query(None, description="Filter by course ID"),
    status: Optional[NodeStatus] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's node-level progress with filtering

    Filters:
    - course_id: Filter by specific course
    - status: Filter by node status (locked, in_progress, completed)
    - Pagination: skip, limit
    """
    # Build query
    query = select(
        LearningProgress,
        CourseNode,
        Course
    ).join(
        CourseNode, LearningProgress.node_id == CourseNode.id
    ).join(
        Course, CourseNode.course_id == Course.id
    ).where(
        LearningProgress.user_id == current_user.id
    )

    # Apply filters
    if course_id:
        query = query.where(CourseNode.course_id == course_id)

    if status:
        query = query.where(LearningProgress.status == status)

    # Order by last accessed (most recent first)
    query = query.order_by(desc(LearningProgress.last_accessed))

    # Get total count
    count_query = select(func.count()).select_from(LearningProgress).join(
        CourseNode, LearningProgress.node_id == CourseNode.id
    ).where(LearningProgress.user_id == current_user.id)

    if course_id:
        count_query = count_query.where(CourseNode.course_id == course_id)
    if status:
        count_query = count_query.where(LearningProgress.status == status)

    total = await db.scalar(count_query) or 0

    # Apply pagination
    query = query.offset(skip).limit(limit)

    # Execute query
    result = await db.execute(query)
    rows = result.all()

    # Format response
    progress_list = []
    for progress, node, course in rows:
        progress_list.append(NodeProgressDetail(
            id=progress.id,
            node_id=node.node_id,
            node_title=node.title,
            node_type=node.type.value,
            course_id=course.id,
            course_name=course.name,
            status=progress.status.value,
            completion_percentage=progress.completion_percentage,
            time_spent_seconds=progress.time_spent_seconds,
            last_accessed=progress.last_accessed,
            completed_at=progress.completed_at
        ))

    return {
        "items": progress_list,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/courses")
async def get_course_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's course-level progress summary

    Returns progress for all courses the user has started
    """
    # Get all courses user has progress in
    courses_query = select(
        func.distinct(CourseNode.course_id)
    ).select_from(
        LearningProgress
    ).join(
        CourseNode, LearningProgress.node_id == CourseNode.id
    ).where(
        LearningProgress.user_id == current_user.id
    )

    result = await db.execute(courses_query)
    course_ids = [row[0] for row in result.all()]

    course_progress_list = []

    for course_id in course_ids:
        # Get course info
        course_result = await db.execute(
            select(Course).where(Course.id == course_id)
        )
        course = course_result.scalar_one_or_none()

        if not course:
            continue

        # Get total nodes in course
        total_nodes_query = select(func.count(CourseNode.id)).where(
            CourseNode.course_id == course_id
        )
        total_nodes = await db.scalar(total_nodes_query) or 0

        # Get completed nodes
        completed_query = select(func.count(LearningProgress.id)).where(
            and_(
                LearningProgress.user_id == current_user.id,
                LearningProgress.node_id.in_(
                    select(CourseNode.id).where(CourseNode.course_id == course_id)
                ),
                LearningProgress.status == NodeStatus.COMPLETED
            )
        )
        completed_nodes = await db.scalar(completed_query) or 0

        # Get in-progress nodes
        in_progress_query = select(func.count(LearningProgress.id)).where(
            and_(
                LearningProgress.user_id == current_user.id,
                LearningProgress.node_id.in_(
                    select(CourseNode.id).where(CourseNode.course_id == course_id)
                ),
                LearningProgress.status == NodeStatus.IN_PROGRESS
            )
        )
        in_progress_nodes = await db.scalar(in_progress_query) or 0

        # Get locked nodes
        locked_query = select(func.count(LearningProgress.id)).where(
            and_(
                LearningProgress.user_id == current_user.id,
                LearningProgress.node_id.in_(
                    select(CourseNode.id).where(CourseNode.course_id == course_id)
                ),
                LearningProgress.status == NodeStatus.LOCKED
            )
        )
        locked_nodes = await db.scalar(locked_query) or 0

        # Get total time spent
        time_query = select(func.sum(LearningProgress.time_spent_seconds)).where(
            and_(
                LearningProgress.user_id == current_user.id,
                LearningProgress.node_id.in_(
                    select(CourseNode.id).where(CourseNode.course_id == course_id)
                )
            )
        )
        total_time = await db.scalar(time_query) or 0

        # Get last accessed
        last_accessed_query = select(func.max(LearningProgress.last_accessed)).where(
            and_(
                LearningProgress.user_id == current_user.id,
                LearningProgress.node_id.in_(
                    select(CourseNode.id).where(CourseNode.course_id == course_id)
                )
            )
        )
        last_accessed = await db.scalar(last_accessed_query)

        # Calculate completion percentage
        completion_percentage = (completed_nodes / total_nodes * 100) if total_nodes > 0 else 0

        course_progress_list.append(CourseProgressDetail(
            course_id=course.id,
            course_name=course.name,
            total_nodes=total_nodes,
            completed_nodes=completed_nodes,
            in_progress_nodes=in_progress_nodes,
            locked_nodes=locked_nodes,
            completion_percentage=round(completion_percentage, 2),
            total_time_spent_seconds=total_time,
            last_accessed=last_accessed
        ))

    # Sort by last accessed (most recent first)
    course_progress_list.sort(
        key=lambda x: x.last_accessed if x.last_accessed else datetime.min,
        reverse=True
    )

    return {
        "courses": course_progress_list,
        "total_courses": len(course_progress_list)
    }


@router.get("/recent")
async def get_recent_progress(
    current_user: User = Depends(get_current_user),
    days: int = Query(7, ge=1, le=90, description="Number of days to look back"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's recent learning activity

    Returns nodes accessed in the last N days
    """
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

    query = select(
        LearningProgress,
        CourseNode,
        Course
    ).join(
        CourseNode, LearningProgress.node_id == CourseNode.id
    ).join(
        Course, CourseNode.course_id == Course.id
    ).where(
        and_(
            LearningProgress.user_id == current_user.id,
            LearningProgress.last_accessed >= cutoff_date
        )
    ).order_by(desc(LearningProgress.last_accessed))

    result = await db.execute(query)
    rows = result.all()

    recent_activity = []
    for progress, node, course in rows:
        recent_activity.append({
            "node_id": node.node_id,
            "node_title": node.title,
            "node_type": node.type.value,
            "course_name": course.name,
            "status": progress.status.value,
            "completion_percentage": progress.completion_percentage,
            "time_spent_seconds": progress.time_spent_seconds,
            "last_accessed": progress.last_accessed.isoformat() if progress.last_accessed else None
        })

    return {
        "recent_activity": recent_activity,
        "days": days,
        "total_activities": len(recent_activity)
    }


@router.get("/growth-stats")
async def get_growth_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户成长统计数据
    """
    # 获取总学习时间
    time_query = select(func.sum(LearningProgress.time_spent_seconds)).where(
        LearningProgress.user_id == current_user.id
    )
    total_seconds = await db.scalar(time_query) or 0

    # 获取完成节点数
    completed_query = select(func.count(LearningProgress.id)).where(
        and_(
            LearningProgress.user_id == current_user.id,
            LearningProgress.status == NodeStatus.COMPLETED
        )
    )
    completed_nodes = await db.scalar(completed_query) or 0

    return {
        "total_learning_hours": round(total_seconds / 3600, 1),
        "completed_nodes": completed_nodes,
        "streak_days": 0,
        "weekly_goal_progress": 0
    }
