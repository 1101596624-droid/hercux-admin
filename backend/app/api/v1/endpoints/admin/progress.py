"""
Admin Learning Progress Management API
Provides progress tracking and management operations for administrators
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, desc
from typing import List, Optional
from datetime import datetime, timezone

from app.db.session import get_db
from app.models.models import (
    User, Course, CourseNode, LearningProgress, NodeStatus, NodeType
)
from app.core.security import get_current_admin_user
from app.core.utils import get_enum_value, status_equals

router = APIRouter()


def get_status_value(status_obj) -> str:
    """Get status value, handling both enum and string types"""
    return status_obj.value if hasattr(status_obj, 'value') else status_obj


# ============ Progress List with Filters ============

@router.get("/progress")
async def list_progress(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    course_id: Optional[int] = Query(None, description="Filter by course ID"),
    status: Optional[NodeStatus] = Query(None, description="Filter by status"),
    sort_by: str = Query("last_accessed", description="Sort field: last_accessed, created_at, completion_percentage"),
    sort_order: str = Query("desc", description="Sort order: asc, desc"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated list of learning progress with filters

    Admin endpoint for progress management
    """
    # Build query
    query = select(LearningProgress, User, CourseNode, Course).join(
        User, LearningProgress.user_id == User.id
    ).join(
        CourseNode, LearningProgress.node_id == CourseNode.id
    ).join(
        Course, CourseNode.course_id == Course.id
    )

    # Apply filters
    filters = []

    if user_id is not None:
        filters.append(LearningProgress.user_id == user_id)

    if course_id is not None:
        filters.append(CourseNode.course_id == course_id)

    if status is not None:
        filters.append(status_equals(LearningProgress.status, status))

    if filters:
        query = query.where(and_(*filters))

    # Apply sorting
    sort_column = getattr(LearningProgress, sort_by, LearningProgress.last_accessed)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Get total count
    count_query = select(func.count()).select_from(LearningProgress)
    if user_id is not None:
        count_query = count_query.where(LearningProgress.user_id == user_id)
    if course_id is not None:
        count_query = count_query.join(CourseNode, LearningProgress.node_id == CourseNode.id).where(
            CourseNode.course_id == course_id
        )
    if status is not None:
        count_query = count_query.where(status_equals(LearningProgress.status, status))

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    # Execute query
    result = await db.execute(query)
    progress_data = result.all()

    # Format response
    progress_list = []
    for progress, user, node, course in progress_data:
        progress_list.append({
            "id": progress.id,
            "user_id": user.id,
            "username": user.username,
            "user_email": user.email,
            "course_id": course.id,
            "course_name": course.name,
            "node_id": node.node_id,
            "node_title": node.title,
            "node_type": get_enum_value(node.type),
            "status": get_status_value(progress.status),
            "completion_percentage": progress.completion_percentage,
            "time_spent_seconds": progress.time_spent_seconds,
            "time_spent_hours": round(progress.time_spent_seconds / 3600, 2),
            "last_accessed": progress.last_accessed,
            "completed_at": progress.completed_at,
            "created_at": progress.created_at
        })

    return {
        "items": progress_list,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


# ============ Progress Detail ============

@router.get("/progress/{progress_id}")
async def get_progress_detail(
    progress_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed progress information
    """
    # Get progress with related data
    query = select(LearningProgress, User, CourseNode, Course).join(
        User, LearningProgress.user_id == User.id
    ).join(
        CourseNode, LearningProgress.node_id == CourseNode.id
    ).join(
        Course, CourseNode.course_id == Course.id
    ).where(LearningProgress.id == progress_id)

    result = await db.execute(query)
    data = result.first()

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Progress {progress_id} not found"
        )

    progress, user, node, course = data

    return {
        "id": progress.id,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url
        },
        "course": {
            "id": course.id,
            "name": course.name,
            "description": course.description,
            "difficulty": course.difficulty.value
        },
        "node": {
            "id": node.id,
            "node_id": node.node_id,
            "title": node.title,
            "description": node.description,
            "type": get_enum_value(node.type),
            "sequence": node.sequence
        },
        "status": get_status_value(progress.status),
        "completion_percentage": progress.completion_percentage,
        "time_spent_seconds": progress.time_spent_seconds,
        "time_spent_hours": round(progress.time_spent_seconds / 3600, 2),
        "last_accessed": progress.last_accessed,
        "completed_at": progress.completed_at,
        "created_at": progress.created_at,
        "updated_at": progress.updated_at
    }


# ============ Update Progress ============

@router.put("/progress/{progress_id}")
async def update_progress(
    progress_id: int,
    status: Optional[NodeStatus] = None,
    completion_percentage: Optional[float] = None,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update progress information

    Admin only
    """
    # Get progress
    result = await db.execute(select(LearningProgress).where(LearningProgress.id == progress_id))
    progress = result.scalar_one_or_none()

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Progress {progress_id} not found"
        )

    # Update fields
    if status is not None:
        progress.status = status
        if status == NodeStatus.COMPLETED and not progress.completed_at:
            progress.completed_at = datetime.now(timezone.utc)

    if completion_percentage is not None:
        progress.completion_percentage = max(0, min(100, completion_percentage))

    await db.commit()
    await db.refresh(progress)

    return {
        "id": progress.id,
        "status": get_status_value(progress.status),
        "completion_percentage": progress.completion_percentage,
        "completed_at": progress.completed_at,
        "message": "Progress updated successfully"
    }


# ============ Delete Progress ============

@router.delete("/progress/{progress_id}")
async def delete_progress(
    progress_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a progress record

    Admin only
    """
    # Get progress
    result = await db.execute(select(LearningProgress).where(LearningProgress.id == progress_id))
    progress = result.scalar_one_or_none()

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Progress {progress_id} not found"
        )

    # Delete progress
    await db.delete(progress)
    await db.commit()

    return {
        "message": "Progress deleted successfully",
        "progress_id": progress_id
    }


# ============ Course Progress Overview ============

@router.get("/progress/course/{course_id}/overview")
async def get_course_progress_overview(
    course_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get progress overview for a specific course

    Shows completion statistics for all users
    """
    # Verify course exists
    course_result = await db.execute(select(Course).where(Course.id == course_id))
    course = course_result.scalar_one_or_none()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course {course_id} not found"
        )

    # Get all nodes for this course
    nodes_query = select(CourseNode).where(CourseNode.course_id == course_id).order_by(CourseNode.sequence)
    nodes_result = await db.execute(nodes_query)
    nodes = nodes_result.scalars().all()

    # Get progress statistics for each node
    node_stats = []
    for node in nodes:
        # Count users who started this node
        started_query = select(func.count()).select_from(LearningProgress).where(
            LearningProgress.node_id == node.id
        )
        started_result = await db.execute(started_query)
        started_count = started_result.scalar()

        # Count users who completed this node
        completed_query = select(func.count()).select_from(LearningProgress).where(
            LearningProgress.node_id == node.id,
            status_equals(LearningProgress.status, NodeStatus.COMPLETED)
        )
        completed_result = await db.execute(completed_query)
        completed_count = completed_result.scalar()

        # Calculate average completion percentage
        avg_completion_query = select(func.avg(LearningProgress.completion_percentage)).where(
            LearningProgress.node_id == node.id
        )
        avg_completion_result = await db.execute(avg_completion_query)
        avg_completion = avg_completion_result.scalar() or 0

        # Calculate average time spent
        avg_time_query = select(func.avg(LearningProgress.time_spent_seconds)).where(
            LearningProgress.node_id == node.id
        )
        avg_time_result = await db.execute(avg_time_query)
        avg_time = avg_time_result.scalar() or 0

        completion_rate = (completed_count / started_count * 100) if started_count > 0 else 0

        node_stats.append({
            "node_id": node.node_id,
            "title": node.title,
            "type": get_enum_value(node.type),
            "sequence": node.sequence,
            "started_count": started_count,
            "completed_count": completed_count,
            "completion_rate": round(completion_rate, 2),
            "avg_completion_percentage": round(avg_completion, 2),
            "avg_time_hours": round(avg_time / 3600, 2)
        })

    # Get overall course statistics
    from app.models.models import UserCourse

    enrolled_query = select(func.count()).select_from(UserCourse).where(UserCourse.course_id == course_id)
    enrolled_result = await db.execute(enrolled_query)
    enrolled_count = enrolled_result.scalar()

    return {
        "course_id": course_id,
        "course_name": course.name,
        "enrolled_users": enrolled_count,
        "total_nodes": len(nodes),
        "node_statistics": node_stats
    }


# ============ User Progress Overview ============

@router.get("/progress/user/{user_id}/overview")
async def get_user_progress_overview(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get progress overview for a specific user

    Shows all courses and their completion status
    """
    # Verify user exists
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )

    # Get all enrolled courses
    from app.models.models import UserCourse

    courses_query = select(UserCourse, Course).join(
        Course, UserCourse.course_id == Course.id
    ).where(UserCourse.user_id == user_id)
    courses_result = await db.execute(courses_query)
    courses_data = courses_result.all()

    course_progress = []
    for user_course, course in courses_data:
        # Get all nodes for this course
        total_nodes_query = select(func.count()).select_from(CourseNode).where(
            CourseNode.course_id == course.id
        )
        total_nodes_result = await db.execute(total_nodes_query)
        total_nodes = total_nodes_result.scalar()

        # Get user's progress on this course
        started_nodes_query = select(func.count()).select_from(LearningProgress).join(
            CourseNode, LearningProgress.node_id == CourseNode.id
        ).where(
            CourseNode.course_id == course.id,
            LearningProgress.user_id == user_id
        )
        started_nodes_result = await db.execute(started_nodes_query)
        started_nodes = started_nodes_result.scalar()

        completed_nodes_query = select(func.count()).select_from(LearningProgress).join(
            CourseNode, LearningProgress.node_id == CourseNode.id
        ).where(
            CourseNode.course_id == course.id,
            LearningProgress.user_id == user_id,
            status_equals(LearningProgress.status, NodeStatus.COMPLETED)
        )
        completed_nodes_result = await db.execute(completed_nodes_query)
        completed_nodes = completed_nodes_result.scalar()

        # Get total time spent
        time_query = select(func.sum(LearningProgress.time_spent_seconds)).select_from(
            LearningProgress
        ).join(
            CourseNode, LearningProgress.node_id == CourseNode.id
        ).where(
            CourseNode.course_id == course.id,
            LearningProgress.user_id == user_id
        )
        time_result = await db.execute(time_query)
        time_spent = time_result.scalar() or 0

        completion_rate = (completed_nodes / total_nodes * 100) if total_nodes > 0 else 0

        course_progress.append({
            "course_id": course.id,
            "course_name": course.name,
            "difficulty": course.difficulty.value,
            "enrolled_at": user_course.enrolled_at,
            "last_accessed": user_course.last_accessed,
            "total_nodes": total_nodes,
            "started_nodes": started_nodes,
            "completed_nodes": completed_nodes,
            "completion_rate": round(completion_rate, 2),
            "time_spent_hours": round(time_spent / 3600, 1)
        })

    return {
        "user_id": user_id,
        "username": user.username,
        "email": user.email,
        "course_progress": course_progress,
        "total_courses": len(course_progress)
    }
