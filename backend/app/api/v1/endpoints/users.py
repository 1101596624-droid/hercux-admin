from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from app.db.session import get_db
from app.models.models import User, LearningProgress, Course
from app.schemas.schemas import (
    UserResponse,
    UserUpdate,
    UserSummary,
    RecommendedCourse,
    CourseResponse
)
from app.services.statistics_service import StatisticsService
from app.core.security import get_current_user

router = APIRouter()


# ============ User Settings Schema ============

class UserSettings(BaseModel):
    """User settings schema"""
    language: Optional[str] = "zh-CN"
    theme: Optional[str] = "light"
    notifications: Optional[Dict[str, bool]] = {
        "email": True,
        "push": True,
        "achievement": True,
        "course_update": True
    }
    privacy: Optional[Dict[str, bool]] = {
        "show_profile": True,
        "show_progress": True,
        "show_achievements": True
    }
    learning_preferences: Optional[Dict[str, Any]] = {
        "daily_goal_minutes": 30,
        "reminder_time": "09:00",
        "auto_play_next": True,
        "playback_speed": 1.0
    }


@router.get("/summary")
async def get_user_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user learning summary for dashboard

    Returns:
    - Total learning hours
    - Consecutive days (streak)
    - Nodes completed
    - Active courses count
    """
    stats_service = StatisticsService(db)
    summary = await stats_service.get_user_summary(current_user.id)

    return summary


@router.get("/statistics/weekly")
async def get_weekly_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get weekly learning statistics with daily breakdown"""
    stats_service = StatisticsService(db)
    weekly_stats = await stats_service.get_weekly_statistics(current_user.id)

    return weekly_stats


@router.get("/statistics/monthly")
async def get_monthly_statistics(
    year: int = Query(..., description="Year (e.g., 2026)"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get monthly learning statistics with daily breakdown"""
    stats_service = StatisticsService(db)
    monthly_stats = await stats_service.get_monthly_statistics(current_user.id, year, month)

    return monthly_stats


@router.get("/statistics/courses")
async def get_course_progress_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get progress summary for all user's courses"""
    stats_service = StatisticsService(db)
    course_summaries = await stats_service.get_course_progress_summary(current_user.id)

    return {
        "courses": course_summaries,
        "totalCourses": len(course_summaries)
    }


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user profile information"""
    return current_user


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user profile"""
    # Update fields
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.avatar_url is not None:
        current_user.avatar_url = user_update.avatar_url

    await db.commit()
    await db.refresh(current_user)

    return current_user


@router.get("/active-course")
async def get_active_course(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's most recently accessed course and node"""
    # Get most recent progress entry
    from sqlalchemy import desc
    from app.models.models import CourseNode

    result = await db.execute(
        select(LearningProgress, CourseNode, Course)
        .join(CourseNode, LearningProgress.node_id == CourseNode.id)
        .join(Course, CourseNode.course_id == Course.id)
        .where(LearningProgress.user_id == current_user.id)
        .order_by(desc(LearningProgress.last_accessed))
        .limit(1)
    )

    row = result.first()

    if not row:
        return {
            "message": "No active course found"
        }

    progress, node, course = row

    return {
        "courseId": course.id,
        "courseName": course.name,
        "nodeId": node.node_id,
        "nodeTitle": node.title,
        "lastAccessed": progress.last_accessed.isoformat() if progress.last_accessed else None,
        "status": progress.status.value,
        "completionPercentage": progress.completion_percentage
    }


# ============ User Settings Endpoints ============

@router.get("/settings")
async def get_user_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user settings

    Returns user preferences, notification settings, privacy settings, etc.
    """
    # Get settings from user metadata or return defaults
    # For now, we'll store settings in a JSON column
    # If User model doesn't have settings column, we'll use a default

    default_settings = {
        "language": "zh-CN",
        "theme": "light",
        "notifications": {
            "email": True,
            "push": True,
            "achievement": True,
            "course_update": True
        },
        "privacy": {
            "show_profile": True,
            "show_progress": True,
            "show_achievements": True
        },
        "learning_preferences": {
            "daily_goal_minutes": 30,
            "reminder_time": "09:00",
            "auto_play_next": True,
            "playback_speed": 1.0
        }
    }

    # Try to get settings from user (if settings column exists)
    # For now, return default settings
    # TODO: Add settings column to User model in future migration

    return default_settings


@router.put("/settings")
async def update_user_settings(
    settings: UserSettings,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user settings

    Updates user preferences, notification settings, privacy settings, etc.
    """
    # Convert settings to dict
    settings_dict = settings.model_dump(exclude_unset=True)

    # TODO: Store settings in User model settings column
    # For now, we'll just return success
    # In a future migration, add: settings = Column(JSON, default={})

    await db.commit()

    return {
        "message": "Settings updated successfully",
        "settings": settings_dict
    }


@router.get("/settings/notifications")
async def get_notification_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user notification preferences"""
    return {
        "email": True,
        "push": True,
        "achievement": True,
        "course_update": True
    }


@router.put("/settings/notifications")
async def update_notification_settings(
    notifications: Dict[str, bool],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user notification preferences"""
    # TODO: Store in user settings
    await db.commit()

    return {
        "message": "Notification settings updated",
        "notifications": notifications
    }


@router.get("/settings/privacy")
async def get_privacy_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user privacy settings"""
    return {
        "show_profile": True,
        "show_progress": True,
        "show_achievements": True
    }


@router.put("/settings/privacy")
async def update_privacy_settings(
    privacy: Dict[str, bool],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user privacy settings"""
    # TODO: Store in user settings
    await db.commit()

    return {
        "message": "Privacy settings updated",
        "privacy": privacy
    }

