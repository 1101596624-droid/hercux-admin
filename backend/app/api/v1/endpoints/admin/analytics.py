"""
Admin Analytics API
Provides comprehensive analytics data for the admin dashboard
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case, extract, distinct
from typing import Optional
from datetime import datetime, timedelta, timezone, date

from app.db.session import get_db
from app.models.models import (
    User, UserCourse, LearningProgress, LearningStatistics,
    Course, CourseNode, ChatHistory, NodeStatus, TokenUsage
)
from app.core.security import get_current_admin_user

router = APIRouter()


# ============ Overview Statistics ============

@router.get("/analytics/overview")
async def get_analytics_overview(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get overview statistics for the admin dashboard

    Returns:
    - Total users, active users, new users today
    - Learning hours, AI conversations
    - Completion rates
    """
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timedelta(days=1)
    seven_days_ago = today_start - timedelta(days=7)

    # Total users
    total_users_result = await db.execute(
        select(func.count()).select_from(User).where(User.is_active == 1)
    )
    total_users = total_users_result.scalar() or 0

    # New users today
    new_users_today_result = await db.execute(
        select(func.count()).select_from(User).where(
            User.created_at >= today_start,
            User.is_active == 1
        )
    )
    new_users_today = new_users_today_result.scalar() or 0

    # New users yesterday (for comparison)
    new_users_yesterday_result = await db.execute(
        select(func.count()).select_from(User).where(
            User.created_at >= yesterday_start,
            User.created_at < today_start,
            User.is_active == 1
        )
    )
    new_users_yesterday = new_users_yesterday_result.scalar() or 0

    # Active users (users with learning activity in last 7 days)
    active_users_result = await db.execute(
        select(func.count(distinct(LearningProgress.user_id))).where(
            LearningProgress.last_accessed >= seven_days_ago
        )
    )
    active_users = active_users_result.scalar() or 0

    # Today's learning hours
    today_learning_result = await db.execute(
        select(func.sum(LearningStatistics.total_time_seconds)).where(
            LearningStatistics.date >= today_start
        )
    )
    today_learning_seconds = today_learning_result.scalar() or 0
    today_learning_hours = round(today_learning_seconds / 3600, 1)

    # AI conversations today
    ai_conversations_result = await db.execute(
        select(func.count()).select_from(ChatHistory).where(
            ChatHistory.created_at >= today_start,
            ChatHistory.role == 'user'
        )
    )
    ai_conversations = ai_conversations_result.scalar() or 0

    # Total courses
    total_courses_result = await db.execute(
        select(func.count()).select_from(Course)
    )
    total_courses = total_courses_result.scalar() or 0

    # Published courses
    published_courses_result = await db.execute(
        select(func.count()).select_from(Course).where(Course.is_published == 1)
    )
    published_courses = published_courses_result.scalar() or 0

    # Average completion rate
    completion_result = await db.execute(
        select(func.avg(LearningProgress.completion_percentage)).where(
            LearningProgress.status.in_([NodeStatus.IN_PROGRESS, NodeStatus.COMPLETED])
        )
    )
    avg_completion = completion_result.scalar() or 0

    return {
        "totalUsers": total_users,
        "newUsersToday": new_users_today,
        "newUsersYesterday": new_users_yesterday,
        "activeUsers": active_users,
        "todayLearningHours": today_learning_hours,
        "aiConversations": ai_conversations,
        "totalCourses": total_courses,
        "publishedCourses": published_courses,
        "avgCompletion": round(avg_completion, 1)
    }


# ============ User Growth Data ============

@router.get("/analytics/growth")
async def get_user_growth(
    period: str = Query("30d", description="Period: 7d, 30d, 90d"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user growth data over time
    """
    days = {"7d": 7, "30d": 30, "90d": 90}.get(period, 30)
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=days)

    # Get daily new user counts
    growth_data = []

    for i in range(days):
        day_start = (start_date + timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        # New users on this day
        new_users_result = await db.execute(
            select(func.count()).select_from(User).where(
                User.created_at >= day_start,
                User.created_at < day_end
            )
        )
        new_users = new_users_result.scalar() or 0

        # Total users up to this day
        total_users_result = await db.execute(
            select(func.count()).select_from(User).where(
                User.created_at < day_end
            )
        )
        total_users = total_users_result.scalar() or 0

        # Active users on this day
        active_users_result = await db.execute(
            select(func.count(distinct(LearningProgress.user_id))).where(
                LearningProgress.last_accessed >= day_start,
                LearningProgress.last_accessed < day_end
            )
        )
        active_users = active_users_result.scalar() or 0

        growth_data.append({
            "date": day_start.strftime("%m/%d"),
            "newUsers": new_users,
            "totalUsers": total_users,
            "activeUsers": active_users
        })

    return growth_data


# ============ Retention Data ============

@router.get("/analytics/retention")
async def get_retention_data(
    cohort_days: int = Query(30, description="Days to look back for cohort"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user retention data (D1, D3, D7, D14, D30)
    """
    now = datetime.now(timezone.utc)
    cohort_start = now - timedelta(days=cohort_days + 30)  # Need extra days for D30
    cohort_end = now - timedelta(days=30)  # Users who registered at least 30 days ago

    # Get users in cohort
    cohort_users_result = await db.execute(
        select(User.id, User.created_at).where(
            User.created_at >= cohort_start,
            User.created_at < cohort_end,
            User.is_active == 1
        )
    )
    cohort_users = cohort_users_result.all()

    if not cohort_users:
        return {
            "d1": 0, "d3": 0, "d7": 0, "d14": 0, "d30": 0,
            "cohortSize": 0,
            "curve": []
        }

    cohort_size = len(cohort_users)
    retention_days = [1, 3, 7, 14, 30]
    retention_rates = {}

    for day in retention_days:
        retained_count = 0
        for user_id, created_at in cohort_users:
            day_start = created_at + timedelta(days=day)
            day_end = day_start + timedelta(days=1)

            # Check if user had activity on that day
            activity_result = await db.execute(
                select(func.count()).select_from(LearningProgress).where(
                    LearningProgress.user_id == user_id,
                    LearningProgress.last_accessed >= day_start,
                    LearningProgress.last_accessed < day_end
                )
            )
            if activity_result.scalar() > 0:
                retained_count += 1

        retention_rates[f"d{day}"] = round((retained_count / cohort_size) * 100, 1)

    # Generate retention curve data
    curve_data = []
    for day in range(31):
        if day == 0:
            curve_data.append({"day": f"D{day}", "rate": 100})
        elif day in retention_days:
            curve_data.append({"day": f"D{day}", "rate": retention_rates[f"d{day}"]})

    return {
        **retention_rates,
        "cohortSize": cohort_size,
        "curve": curve_data
    }


# ============ Learning Funnel ============

@router.get("/analytics/funnel")
async def get_learning_funnel(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get learning conversion funnel data
    """
    # Total registered users
    total_users_result = await db.execute(
        select(func.count()).select_from(User).where(User.is_active == 1)
    )
    total_users = total_users_result.scalar() or 0

    # Users who enrolled in at least one course
    enrolled_users_result = await db.execute(
        select(func.count(distinct(UserCourse.user_id)))
    )
    enrolled_users = enrolled_users_result.scalar() or 0

    # Users who started learning (have any progress)
    started_users_result = await db.execute(
        select(func.count(distinct(LearningProgress.user_id)))
    )
    started_users = started_users_result.scalar() or 0

    # Users who completed at least one node
    completed_node_users_result = await db.execute(
        select(func.count(distinct(LearningProgress.user_id))).where(
            LearningProgress.status == NodeStatus.COMPLETED
        )
    )
    completed_node_users = completed_node_users_result.scalar() or 0

    # Users who completed at least one course (all nodes in a course)
    # This is more complex - simplified version
    completed_course_users_result = await db.execute(
        select(func.count(distinct(UserCourse.user_id))).where(
            UserCourse.completed_at.isnot(None)
        )
    )
    completed_course_users = completed_course_users_result.scalar() or 0

    funnel = [
        {"stage": "注册用户", "count": total_users, "rate": 100},
        {"stage": "选课用户", "count": enrolled_users, "rate": round((enrolled_users / total_users * 100) if total_users > 0 else 0, 1)},
        {"stage": "开始学习", "count": started_users, "rate": round((started_users / total_users * 100) if total_users > 0 else 0, 1)},
        {"stage": "完成节点", "count": completed_node_users, "rate": round((completed_node_users / total_users * 100) if total_users > 0 else 0, 1)},
        {"stage": "完成课程", "count": completed_course_users, "rate": round((completed_course_users / total_users * 100) if total_users > 0 else 0, 1)},
    ]

    return funnel


# ============ Activity Heatmap ============

@router.get("/analytics/heatmap")
async def get_activity_heatmap(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get 7x24 activity heatmap data (day of week x hour)
    """
    # Get learning activity from last 30 days
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)

    # Initialize heatmap data
    heatmap = [[0 for _ in range(24)] for _ in range(7)]

    # Get all learning progress updates in last 30 days
    activity_result = await db.execute(
        select(LearningProgress.last_accessed).where(
            LearningProgress.last_accessed >= thirty_days_ago,
            LearningProgress.last_accessed.isnot(None)
        )
    )
    activities = activity_result.scalars().all()

    # Count activities by day and hour
    for activity_time in activities:
        if activity_time:
            day_of_week = activity_time.weekday()  # 0=Monday, 6=Sunday
            hour = activity_time.hour
            heatmap[day_of_week][hour] += 1

    # Normalize to 0-100 scale
    max_value = max(max(row) for row in heatmap) or 1
    normalized_heatmap = [
        [round(value / max_value * 100) for value in row]
        for row in heatmap
    ]

    return {
        "data": normalized_heatmap,
        "days": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
        "hours": list(range(24))
    }


# ============ User Source Distribution ============

@router.get("/analytics/user-sources")
async def get_user_sources(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user registration source distribution
    Note: This is a placeholder - actual implementation would need a source tracking field
    """
    # Since we don't have source tracking, return mock distribution based on user patterns
    total_users_result = await db.execute(
        select(func.count()).select_from(User).where(User.is_active == 1)
    )
    total_users = total_users_result.scalar() or 0

    # Mock distribution (in real implementation, this would come from a registration_source field)
    sources = [
        {"name": "自然搜索", "value": int(total_users * 0.35), "color": "#3B82F6"},
        {"name": "社交媒体", "value": int(total_users * 0.25), "color": "#10B981"},
        {"name": "口碑推荐", "value": int(total_users * 0.20), "color": "#F59E0B"},
        {"name": "付费推广", "value": int(total_users * 0.12), "color": "#EF4444"},
        {"name": "其他渠道", "value": int(total_users * 0.08), "color": "#8B5CF6"},
    ]

    return sources


# ============ Learning Time Distribution ============

@router.get("/analytics/learning-time")
async def get_learning_time_distribution(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get daily learning time distribution
    """
    # Get learning statistics from last 30 days
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)

    stats_result = await db.execute(
        select(LearningStatistics.total_time_seconds).where(
            LearningStatistics.date >= thirty_days_ago
        )
    )
    all_times = stats_result.scalars().all()

    # Categorize by time ranges (in minutes)
    ranges = [
        {"range": "0-15分钟", "min": 0, "max": 15, "count": 0},
        {"range": "15-30分钟", "min": 15, "max": 30, "count": 0},
        {"range": "30-60分钟", "min": 30, "max": 60, "count": 0},
        {"range": "1-2小时", "min": 60, "max": 120, "count": 0},
        {"range": "2小时以上", "min": 120, "max": float('inf'), "count": 0},
    ]

    for time_seconds in all_times:
        time_minutes = time_seconds / 60
        for r in ranges:
            if r["min"] <= time_minutes < r["max"]:
                r["count"] += 1
                break

    return [{"range": r["range"], "count": r["count"]} for r in ranges]


# ============ User Clusters ============

@router.get("/analytics/user-clusters")
async def get_user_clusters(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user behavior clusters
    """
    # Get all active users with their statistics
    users_result = await db.execute(
        select(User.id).where(User.is_active == 1)
    )
    user_ids = [row[0] for row in users_result.all()]

    clusters = {
        "高活跃学习者": {"count": 0, "description": "每周学习>5小时，完成率>80%", "color": "#10B981"},
        "稳定学习者": {"count": 0, "description": "每周学习2-5小时，完成率50-80%", "color": "#3B82F6"},
        "间歇学习者": {"count": 0, "description": "每周学习<2小时，完成率30-50%", "color": "#F59E0B"},
        "流失风险用户": {"count": 0, "description": "7天以上未活跃", "color": "#EF4444"},
    }

    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

    for user_id in user_ids:
        # Get user's weekly learning time
        time_result = await db.execute(
            select(func.sum(LearningStatistics.total_time_seconds)).where(
                LearningStatistics.user_id == user_id,
                LearningStatistics.date >= seven_days_ago
            )
        )
        weekly_seconds = time_result.scalar() or 0
        weekly_hours = weekly_seconds / 3600

        # Get user's completion rate
        progress_result = await db.execute(
            select(func.avg(LearningProgress.completion_percentage)).where(
                LearningProgress.user_id == user_id
            )
        )
        completion_rate = progress_result.scalar() or 0

        # Get last activity
        last_activity_result = await db.execute(
            select(func.max(LearningProgress.last_accessed)).where(
                LearningProgress.user_id == user_id
            )
        )
        last_activity = last_activity_result.scalar()

        # Classify user
        if last_activity and last_activity < seven_days_ago:
            clusters["流失风险用户"]["count"] += 1
        elif weekly_hours > 5 and completion_rate > 80:
            clusters["高活跃学习者"]["count"] += 1
        elif weekly_hours >= 2 and completion_rate >= 50:
            clusters["稳定学习者"]["count"] += 1
        else:
            clusters["间歇学习者"]["count"] += 1

    return [
        {"name": name, **data}
        for name, data in clusters.items()
    ]


# ============ AI Usage Statistics ============

@router.get("/analytics/ai-usage")
async def get_ai_usage_stats(
    period: str = Query("24h", description="Period: 24h, 7d, 30d"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI conversation usage statistics
    """
    hours = {"24h": 24, "7d": 168, "30d": 720}.get(period, 24)
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(hours=hours)

    # Total conversations
    total_result = await db.execute(
        select(func.count()).select_from(ChatHistory).where(
            ChatHistory.created_at >= start_time,
            ChatHistory.role == 'user'
        )
    )
    total_conversations = total_result.scalar() or 0

    # Unique users
    unique_users_result = await db.execute(
        select(func.count(distinct(ChatHistory.user_id))).where(
            ChatHistory.created_at >= start_time
        )
    )
    unique_users = unique_users_result.scalar() or 0

    # Average messages per conversation (simplified)
    avg_messages = round(total_conversations / max(unique_users, 1), 1)

    # Trend data
    trend_data = []
    if period == "24h":
        # Hourly data
        for i in range(24):
            hour_start = start_time + timedelta(hours=i)
            hour_end = hour_start + timedelta(hours=1)

            count_result = await db.execute(
                select(func.count()).select_from(ChatHistory).where(
                    ChatHistory.created_at >= hour_start,
                    ChatHistory.created_at < hour_end,
                    ChatHistory.role == 'user'
                )
            )
            count = count_result.scalar() or 0
            trend_data.append({
                "time": hour_start.strftime("%H:00"),
                "count": count
            })
    else:
        # Daily data
        days = hours // 24
        for i in range(days):
            day_start = (start_time + timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)

            count_result = await db.execute(
                select(func.count()).select_from(ChatHistory).where(
                    ChatHistory.created_at >= day_start,
                    ChatHistory.created_at < day_end,
                    ChatHistory.role == 'user'
                )
            )
            count = count_result.scalar() or 0
            trend_data.append({
                "time": day_start.strftime("%m/%d"),
                "count": count
            })

    return {
        "totalConversations": total_conversations,
        "uniqueUsers": unique_users,
        "avgMessagesPerUser": avg_messages,
        "trend": trend_data
    }


# ============ Course Statistics ============

@router.get("/analytics/courses")
async def get_course_statistics(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get course-level statistics
    """
    courses_result = await db.execute(
        select(Course).where(Course.is_published == 1)
    )
    courses = courses_result.scalars().all()

    course_stats = []
    for course in courses:
        # Enrolled users
        enrolled_result = await db.execute(
            select(func.count()).select_from(UserCourse).where(
                UserCourse.course_id == course.id
            )
        )
        enrolled_count = enrolled_result.scalar() or 0

        # Total nodes
        nodes_result = await db.execute(
            select(func.count()).select_from(CourseNode).where(
                CourseNode.course_id == course.id
            )
        )
        total_nodes = nodes_result.scalar() or 0

        # Average completion
        completion_result = await db.execute(
            select(func.avg(LearningProgress.completion_percentage)).select_from(
                LearningProgress
            ).join(
                CourseNode, LearningProgress.node_id == CourseNode.id
            ).where(
                CourseNode.course_id == course.id
            )
        )
        avg_completion = completion_result.scalar() or 0

        # Total learning time
        time_result = await db.execute(
            select(func.sum(LearningProgress.time_spent_seconds)).select_from(
                LearningProgress
            ).join(
                CourseNode, LearningProgress.node_id == CourseNode.id
            ).where(
                CourseNode.course_id == course.id
            )
        )
        total_time = time_result.scalar() or 0

        course_stats.append({
            "id": course.id,
            "name": course.name,
            "enrolledUsers": enrolled_count,
            "totalNodes": total_nodes,
            "avgCompletion": round(avg_completion, 1),
            "totalLearningHours": round(total_time / 3600, 1)
        })

    return course_stats


# ============ Token Usage Statistics ============

@router.get("/analytics/token-usage")
async def get_token_usage_stats(
    period: str = Query("7d", description="Period: 24h, 7d, 30d"),
    feature: Optional[str] = Query(None, description="Filter by feature"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI token usage statistics for admin dashboard
    """
    hours = {"24h": 24, "7d": 168, "30d": 720}.get(period, 168)
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(hours=hours)

    # Base query
    base_filter = [TokenUsage.created_at >= start_time]
    if feature:
        base_filter.append(TokenUsage.feature == feature)

    # Total tokens
    total_result = await db.execute(
        select(
            func.sum(TokenUsage.total_tokens),
            func.sum(TokenUsage.input_tokens),
            func.sum(TokenUsage.output_tokens),
            func.count()
        ).where(*base_filter)
    )
    row = total_result.one()
    total_tokens = row[0] or 0
    total_input = row[1] or 0
    total_output = row[2] or 0
    total_requests = row[3] or 0

    # Unique users
    unique_users_result = await db.execute(
        select(func.count(distinct(TokenUsage.user_id))).where(
            *base_filter,
            TokenUsage.user_id.isnot(None)
        )
    )
    unique_users = unique_users_result.scalar() or 0

    # By feature breakdown
    feature_result = await db.execute(
        select(
            TokenUsage.feature,
            func.sum(TokenUsage.total_tokens),
            func.count()
        ).where(*base_filter).group_by(TokenUsage.feature)
    )
    by_feature = [
        {"feature": row[0], "tokens": row[1] or 0, "requests": row[2] or 0}
        for row in feature_result.all()
    ]

    # By model breakdown
    model_result = await db.execute(
        select(
            TokenUsage.model,
            func.sum(TokenUsage.total_tokens),
            func.count()
        ).where(*base_filter).group_by(TokenUsage.model)
    )
    by_model = [
        {"model": row[0], "tokens": row[1] or 0, "requests": row[2] or 0}
        for row in model_result.all()
    ]

    # Daily trend
    trend_data = []
    if period == "24h":
        # Hourly data
        for i in range(24):
            hour_start = start_time + timedelta(hours=i)
            hour_end = hour_start + timedelta(hours=1)

            hour_result = await db.execute(
                select(func.sum(TokenUsage.total_tokens)).where(
                    TokenUsage.created_at >= hour_start,
                    TokenUsage.created_at < hour_end,
                    *([TokenUsage.feature == feature] if feature else [])
                )
            )
            tokens = hour_result.scalar() or 0
            trend_data.append({
                "time": hour_start.strftime("%H:00"),
                "tokens": tokens
            })
    else:
        # Daily data
        days = hours // 24
        for i in range(days):
            day_start = (start_time + timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)

            day_result = await db.execute(
                select(func.sum(TokenUsage.total_tokens)).where(
                    TokenUsage.created_at >= day_start,
                    TokenUsage.created_at < day_end,
                    *([TokenUsage.feature == feature] if feature else [])
                )
            )
            tokens = day_result.scalar() or 0
            trend_data.append({
                "time": day_start.strftime("%m/%d"),
                "tokens": tokens
            })

    # Estimate cost (rough estimate: $3/1M input, $15/1M output for Claude Sonnet)
    estimated_cost = (total_input * 3 / 1_000_000) + (total_output * 15 / 1_000_000)

    return {
        "totalTokens": total_tokens,
        "totalInput": total_input,
        "totalOutput": total_output,
        "totalRequests": total_requests,
        "uniqueUsers": unique_users,
        "avgTokensPerRequest": round(total_tokens / max(total_requests, 1), 0),
        "estimatedCost": round(estimated_cost, 2),
        "byFeature": by_feature,
        "byModel": by_model,
        "trend": trend_data
    }
