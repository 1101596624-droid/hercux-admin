"""
Admin User Management API
Provides user management operations for administrators
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, desc
from typing import List, Optional
from datetime import datetime, timedelta, timezone

from app.db.session import get_db
from app.models.models import User, UserCourse, LearningProgress, LearningStatistics, Achievement, NodeStatus, UserProfile
from app.core.security import get_current_admin_user
from app.core.utils import status_equals
from app.services.user_profile_service import UserProfileService
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()


# ============ Create User Schema ============

class CreateUserRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_premium: bool = False


# ============ Create User ============

@router.post("/users")
async def create_user(
    request: CreateUserRequest,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user

    Admin only
    """
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username already exists
    result = await db.execute(select(User).where(User.username == request.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create user
    user = User(
        email=request.email,
        username=request.username,
        hashed_password=pwd_context.hash(request.password),
        full_name=request.full_name,
        is_active=1 if request.is_active else 0,
        is_premium=1 if request.is_premium else 0
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "is_active": bool(user.is_active),
        "is_premium": bool(user.is_premium),
        "created_at": user.created_at,
        "message": "User created successfully"
    }


# ============ User List with Filters ============

@router.get("/users")
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search in username, email, full_name"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_premium: Optional[bool] = Query(None, description="Filter by premium status"),
    sort_by: str = Query("created_at", description="Sort field: created_at, username, email"),
    sort_order: str = Query("desc", description="Sort order: asc, desc"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated list of users with filters

    Admin endpoint for user management
    """
    # Build query
    query = select(User)

    # Apply filters
    filters = []

    if search:
        search_pattern = f"%{search}%"
        filters.append(
            or_(
                User.username.ilike(search_pattern),
                User.email.ilike(search_pattern),
                User.full_name.ilike(search_pattern)
            )
        )

    if is_active is not None:
        filters.append(User.is_active == (1 if is_active else 0))

    if is_premium is not None:
        filters.append(User.is_premium == (1 if is_premium else 0))

    if filters:
        query = query.where(and_(*filters))

    # Apply sorting
    sort_column = getattr(User, sort_by, User.created_at)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Get total count
    count_query = select(func.count()).select_from(User)
    if filters:
        count_query = count_query.where(and_(*filters))
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    # Execute query
    result = await db.execute(query)
    users = result.scalars().all()

    # Get user IDs for batch query
    user_ids = [user.id for user in users]

    # Batch query: enrolled courses count per user
    courses_stats = {}
    if user_ids:
        courses_query = select(
            UserCourse.user_id,
            func.count(UserCourse.id).label('count')
        ).where(UserCourse.user_id.in_(user_ids)).group_by(UserCourse.user_id)
        courses_result = await db.execute(courses_query)
        for row in courses_result.all():
            courses_stats[row.user_id] = row.count

    # Batch query: completed nodes, total time, last activity per user
    progress_stats = {}
    if user_ids:
        progress_query = select(
            LearningProgress.user_id,
            func.count(LearningProgress.id).filter(status_equals(LearningProgress.status, NodeStatus.COMPLETED)).label('completed'),
            func.sum(LearningProgress.time_spent_seconds).label('total_time'),
            func.max(LearningProgress.last_accessed).label('last_activity')
        ).where(LearningProgress.user_id.in_(user_ids)).group_by(LearningProgress.user_id)
        progress_result = await db.execute(progress_query)
        for row in progress_result.all():
            progress_stats[row.user_id] = {
                'completed': row.completed or 0,
                'total_time': row.total_time or 0,
                'last_activity': row.last_activity
            }

    # Build user list with pre-fetched stats
    user_list = []
    for user in users:
        enrolled_courses = courses_stats.get(user.id, 0)
        stats = progress_stats.get(user.id, {'completed': 0, 'total_time': 0, 'last_activity': None})

        user_list.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
            "is_active": bool(user.is_active),
            "is_premium": bool(user.is_premium),
            "created_at": user.created_at,
            "enrolled_courses": enrolled_courses,
            "completed_nodes": stats['completed'],
            "total_time_hours": round(stats['total_time'] / 3600, 1),
            "last_activity": stats['last_activity']
        })

    return {
        "items": user_list,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


# ============ User Detail ============

@router.get("/users/{user_id}")
async def get_user_detail(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed user information including statistics
    """
    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )

    # Get enrolled courses with progress
    from app.models.models import Course, CourseNode

    courses_query = select(UserCourse, Course).join(
        Course, UserCourse.course_id == Course.id
    ).where(UserCourse.user_id == user_id)
    courses_result = await db.execute(courses_query)
    courses_data = courses_result.all()

    enrolled_courses = []
    for user_course, course in courses_data:
        # Get course progress
        total_nodes_query = select(func.count()).select_from(CourseNode).where(
            CourseNode.course_id == course.id
        )
        total_nodes_result = await db.execute(total_nodes_query)
        total_nodes = total_nodes_result.scalar()

        completed_nodes_query = select(func.count()).select_from(LearningProgress).join(
            CourseNode, LearningProgress.node_id == CourseNode.id
        ).where(
            CourseNode.course_id == course.id,
            LearningProgress.user_id == user_id,
            status_equals(LearningProgress.status, NodeStatus.COMPLETED)
        )
        completed_nodes_result = await db.execute(completed_nodes_query)
        completed_nodes = completed_nodes_result.scalar()

        completion_rate = (completed_nodes / total_nodes * 100) if total_nodes > 0 else 0

        enrolled_courses.append({
            "course_id": course.id,
            "course_name": course.name,
            "enrolled_at": user_course.enrolled_at,
            "last_accessed": user_course.last_accessed,
            "is_favorite": bool(user_course.is_favorite),
            "total_nodes": total_nodes,
            "completed_nodes": completed_nodes,
            "completion_rate": round(completion_rate, 2)
        })

    # Get achievements
    achievements_query = select(Achievement).where(Achievement.user_id == user_id)
    achievements_result = await db.execute(achievements_query)
    achievements = achievements_result.scalars().all()

    # Get learning statistics (last 30 days)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    stats_query = select(LearningStatistics).where(
        LearningStatistics.user_id == user_id,
        LearningStatistics.date >= thirty_days_ago
    ).order_by(LearningStatistics.date)
    stats_result = await db.execute(stats_query)
    daily_stats = stats_result.scalars().all()

    # Calculate overall statistics
    total_time_query = select(func.sum(LearningProgress.time_spent_seconds)).where(
        LearningProgress.user_id == user_id
    )
    total_time_result = await db.execute(total_time_query)
    total_time = total_time_result.scalar() or 0

    completed_nodes_query = select(func.count()).select_from(LearningProgress).where(
        LearningProgress.user_id == user_id,
        status_equals(LearningProgress.status, NodeStatus.COMPLETED)
    )
    completed_nodes_result = await db.execute(completed_nodes_query)
    total_completed_nodes = completed_nodes_result.scalar()

    # Get current streak
    current_streak = 0
    if daily_stats:
        current_streak = daily_stats[-1].streak_days

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "avatar_url": user.avatar_url,
        "is_active": bool(user.is_active),
        "is_premium": bool(user.is_premium),
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "statistics": {
            "enrolled_courses": len(enrolled_courses),
            "completed_nodes": total_completed_nodes,
            "total_time_hours": round(total_time / 3600, 1),
            "current_streak": current_streak,
            "achievements_count": len(achievements)
        },
        "enrolled_courses": enrolled_courses,
        "achievements": [
            {
                "badge_id": a.badge_id,
                "badge_name": a.badge_name,
                "badge_description": a.badge_description,
                "rarity": a.rarity,
                "icon_url": a.icon_url,
                "unlocked_at": a.unlocked_at
            }
            for a in achievements
        ],
        "daily_statistics": [
            {
                "date": stat.date.date().isoformat(),
                "total_time_seconds": stat.total_time_seconds,
                "nodes_completed": stat.nodes_completed,
                "streak_days": stat.streak_days
            }
            for stat in daily_stats
        ]
    }


# ============ Update User ============

@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    full_name: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_premium: Optional[bool] = None,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user information

    Admin only
    """
    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )

    # Update fields
    if full_name is not None:
        user.full_name = full_name
    if is_active is not None:
        user.is_active = 1 if is_active else 0
    if is_premium is not None:
        user.is_premium = 1 if is_premium else 0

    await db.commit()
    await db.refresh(user)

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": bool(user.is_active),
        "is_premium": bool(user.is_premium),
        "message": "User updated successfully"
    }


# ============ Delete User ============

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a user

    Admin only - This will also delete all associated data
    """
    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )

    # Delete user (cascade will handle related records)
    await db.delete(user)
    await db.commit()

    return {
        "message": f"User '{user.username}' deleted successfully",
        "user_id": user_id
    }


# ============ User Statistics ============

@router.get("/users/{user_id}/statistics")
async def get_user_statistics(
    user_id: int,
    days: int = Query(30, ge=1, le=365, description="Number of days to retrieve"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed learning statistics for a user

    Admin only
    """
    # Verify user exists
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )

    # Get daily statistics
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    stats_query = select(LearningStatistics).where(
        LearningStatistics.user_id == user_id,
        LearningStatistics.date >= start_date
    ).order_by(LearningStatistics.date)
    stats_result = await db.execute(stats_query)
    daily_stats = stats_result.scalars().all()

    # Get course progress breakdown
    from app.models.models import Course, CourseNode

    courses_query = select(UserCourse, Course).join(
        Course, UserCourse.course_id == Course.id
    ).where(UserCourse.user_id == user_id)
    courses_result = await db.execute(courses_query)
    courses_data = courses_result.all()

    course_progress = []
    for user_course, course in courses_data:
        total_nodes_query = select(func.count()).select_from(CourseNode).where(
            CourseNode.course_id == course.id
        )
        total_nodes_result = await db.execute(total_nodes_query)
        total_nodes = total_nodes_result.scalar()

        completed_nodes_query = select(func.count()).select_from(LearningProgress).join(
            CourseNode, LearningProgress.node_id == CourseNode.id
        ).where(
            CourseNode.course_id == course.id,
            LearningProgress.user_id == user_id,
            status_equals(LearningProgress.status, NodeStatus.COMPLETED)
        )
        completed_nodes_result = await db.execute(completed_nodes_query)
        completed_nodes = completed_nodes_result.scalar()

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

        course_progress.append({
            "course_id": course.id,
            "course_name": course.name,
            "total_nodes": total_nodes,
            "completed_nodes": completed_nodes,
            "completion_rate": round((completed_nodes / total_nodes * 100) if total_nodes > 0 else 0, 2),
            "time_spent_hours": round(time_spent / 3600, 1)
        })

    return {
        "user_id": user_id,
        "username": user.username,
        "daily_statistics": [
            {
                "date": stat.date.date().isoformat(),
                "total_time_seconds": stat.total_time_seconds,
                "nodes_completed": stat.nodes_completed,
                "streak_days": stat.streak_days
            }
            for stat in daily_stats
        ],
        "course_progress": course_progress
    }


# ============ User Profile Analysis ============

@router.get("/users/{user_id}/profile")
async def get_user_profile(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户特征画像

    返回基于AI对话分析的用户学习特征
    """
    # 验证用户存在
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )

    # 获取用户画像
    profile_result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user_id)
    )
    profile = profile_result.scalar_one_or_none()

    if not profile:
        return {
            "user_id": user_id,
            "username": user.username,
            "profile": None,
            "message": "用户画像尚未生成，请先触发分析"
        }

    return {
        "user_id": user_id,
        "username": user.username,
        "profile": {
            "learning_style": profile.learning_style,
            "knowledge_levels": profile.knowledge_levels,
            "interests": profile.interests,
            "strengths": profile.strengths,
            "weaknesses": profile.weaknesses,
            "communication_style": profile.communication_style,
            "engagement_level": profile.engagement_level,
            "question_patterns": profile.question_patterns,
            "learning_pace": profile.learning_pace,
            "personality_traits": profile.personality_traits,
            "recommended_approach": profile.recommended_approach,
            "analysis_summary": profile.analysis_summary,
            "messages_analyzed": profile.messages_analyzed,
            "last_analyzed_at": profile.last_analyzed_at,
            "analysis_version": profile.analysis_version
        }
    }


@router.post("/users/{user_id}/profile/analyze")
async def analyze_user_profile(
    user_id: int,
    force: bool = Query(False, description="强制重新分析"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    触发用户特征分析

    基于用户的AI对话历史分析其学习特征
    """
    # 验证用户存在
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )

    # 执行分析
    profile_service = UserProfileService(db)
    profile_data = await profile_service.analyze_user_profile(user_id, force_update=force)

    if not profile_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无法分析用户画像，可能是对话历史不足"
        )

    return {
        "user_id": user_id,
        "username": user.username,
        "message": "用户画像分析完成",
        "profile": profile_data
    }


@router.get("/profiles")
async def list_user_profiles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    engagement_level: Optional[str] = Query(None, description="筛选参与度: high, medium, low"),
    learning_pace: Optional[str] = Query(None, description="筛选学习节奏: fast, moderate, slow"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有用户画像列表

    支持按参与度和学习节奏筛选
    """
    # 构建查询
    query = select(UserProfile, User).join(User, UserProfile.user_id == User.id)

    # 应用筛选
    filters = []
    if engagement_level:
        filters.append(UserProfile.engagement_level == engagement_level)
    if learning_pace:
        filters.append(UserProfile.learning_pace == learning_pace)

    if filters:
        query = query.where(and_(*filters))

    # 获取总数
    count_query = select(func.count()).select_from(UserProfile)
    if filters:
        count_query = count_query.where(and_(*filters))
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 分页
    offset = (page - 1) * page_size
    query = query.order_by(desc(UserProfile.last_analyzed_at)).offset(offset).limit(page_size)

    # 执行查询
    result = await db.execute(query)
    profiles_data = result.all()

    profiles_list = []
    for profile, user in profiles_data:
        profiles_list.append({
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "engagement_level": profile.engagement_level,
            "learning_pace": profile.learning_pace,
            "communication_style": profile.communication_style,
            "interests": profile.interests,
            "personality_traits": profile.personality_traits,
            "messages_analyzed": profile.messages_analyzed,
            "last_analyzed_at": profile.last_analyzed_at,
            "analysis_summary": profile.analysis_summary
        })

    return {
        "items": profiles_list,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.post("/profiles/batch-analyze")
async def batch_analyze_profiles(
    user_ids: Optional[List[int]] = Query(None, description="指定用户ID列表，为空则分析所有用户"),
    force: bool = Query(False, description="强制重新分析"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    批量分析用户画像

    可指定用户列表或分析所有用户
    """
    # 获取要分析的用户
    if user_ids:
        users_query = select(User).where(User.id.in_(user_ids))
    else:
        users_query = select(User).where(User.is_active == 1)

    users_result = await db.execute(users_query)
    users = users_result.scalars().all()

    profile_service = UserProfileService(db)
    results = {
        "success": [],
        "failed": [],
        "skipped": []
    }

    for user in users:
        try:
            profile_data = await profile_service.analyze_user_profile(user.id, force_update=force)
            if profile_data:
                results["success"].append({
                    "user_id": user.id,
                    "username": user.username
                })
            else:
                results["skipped"].append({
                    "user_id": user.id,
                    "username": user.username,
                    "reason": "对话历史不足"
                })
        except Exception as e:
            results["failed"].append({
                "user_id": user.id,
                "username": user.username,
                "error": str(e)
            })

    return {
        "message": "批量分析完成",
        "total_users": len(users),
        "success_count": len(results["success"]),
        "failed_count": len(results["failed"]),
        "skipped_count": len(results["skipped"]),
        "results": results
    }
