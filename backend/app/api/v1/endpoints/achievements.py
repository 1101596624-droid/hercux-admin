"""
Achievement Center API Endpoints
勋章中心 - 读取后台配置的勋章和用户解锁记录
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone

from app.db.session import get_db
from app.db.neo4j import get_neo4j, Neo4jClient
from app.schemas.schemas import AchievementResponse, SkillTreeNode
from app.models.models import (
    User, Achievement, LearningProgress, CourseNode, NodeStatus, NodeType,
    BadgeConfig, UserBadge, SkillTreeConfig, UserSkillProgress,
    SkillAchievementConfig, UserSkillAchievement
)
from app.core.security import get_current_user

router = APIRouter()


# ============ Achievement Definitions ============

ACHIEVEMENT_DEFINITIONS = {
    "first_step": {
        "badge_id": "first_step",
        "badge_name": "First Step",
        "badge_description": "Complete your first learning node",
        "rarity": "common",
        "icon_url": "/badges/first_step.png",
        "condition": lambda stats: stats["completed_nodes"] >= 1
    },
    "dedicated_learner": {
        "badge_id": "dedicated_learner",
        "badge_name": "Dedicated Learner",
        "badge_description": "Complete 10 learning nodes",
        "rarity": "common",
        "icon_url": "/badges/dedicated_learner.png",
        "condition": lambda stats: stats["completed_nodes"] >= 10
    },
    "knowledge_seeker": {
        "badge_id": "knowledge_seeker",
        "badge_name": "Knowledge Seeker",
        "badge_description": "Complete 50 learning nodes",
        "rarity": "rare",
        "icon_url": "/badges/knowledge_seeker.png",
        "condition": lambda stats: stats["completed_nodes"] >= 50
    },
    "master_student": {
        "badge_id": "master_student",
        "badge_name": "Master Student",
        "badge_description": "Complete 100 learning nodes",
        "rarity": "epic",
        "icon_url": "/badges/master_student.png",
        "condition": lambda stats: stats["completed_nodes"] >= 100
    },
    "course_completer": {
        "badge_id": "course_completer",
        "badge_name": "Course Completer",
        "badge_description": "Complete your first course",
        "rarity": "common",
        "icon_url": "/badges/course_completer.png",
        "condition": lambda stats: stats["completed_courses"] >= 1
    },
    "multi_course_master": {
        "badge_id": "multi_course_master",
        "badge_name": "Multi-Course Master",
        "badge_description": "Complete 5 courses",
        "rarity": "rare",
        "icon_url": "/badges/multi_course_master.png",
        "condition": lambda stats: stats["completed_courses"] >= 5
    },
    "streak_3": {
        "badge_id": "streak_3",
        "badge_name": "3-Day Streak",
        "badge_description": "Learn for 3 consecutive days",
        "rarity": "common",
        "icon_url": "/badges/streak_3.png",
        "condition": lambda stats: stats["current_streak"] >= 3
    },
    "streak_7": {
        "badge_id": "streak_7",
        "badge_name": "Week Warrior",
        "badge_description": "Learn for 7 consecutive days",
        "rarity": "rare",
        "icon_url": "/badges/streak_7.png",
        "condition": lambda stats: stats["current_streak"] >= 7
    },
    "streak_30": {
        "badge_id": "streak_30",
        "badge_name": "Monthly Master",
        "badge_description": "Learn for 30 consecutive days",
        "rarity": "epic",
        "icon_url": "/badges/streak_30.png",
        "condition": lambda stats: stats["current_streak"] >= 30
    },
    "streak_100": {
        "badge_id": "streak_100",
        "badge_name": "Centurion",
        "badge_description": "Learn for 100 consecutive days",
        "rarity": "legendary",
        "icon_url": "/badges/streak_100.png",
        "condition": lambda stats: stats["current_streak"] >= 100
    },
    "time_10h": {
        "badge_id": "time_10h",
        "badge_name": "10 Hours",
        "badge_description": "Spend 10 hours learning",
        "rarity": "common",
        "icon_url": "/badges/time_10h.png",
        "condition": lambda stats: stats["total_hours"] >= 10
    },
    "time_50h": {
        "badge_id": "time_50h",
        "badge_name": "50 Hours",
        "badge_description": "Spend 50 hours learning",
        "rarity": "rare",
        "icon_url": "/badges/time_50h.png",
        "condition": lambda stats: stats["total_hours"] >= 50
    },
    "time_100h": {
        "badge_id": "time_100h",
        "badge_name": "100 Hours",
        "badge_description": "Spend 100 hours learning",
        "rarity": "epic",
        "icon_url": "/badges/time_100h.png",
        "condition": lambda stats: stats["total_hours"] >= 100
    },
    "perfectionist": {
        "badge_id": "perfectionist",
        "badge_name": "Perfectionist",
        "badge_description": "Achieve 100% completion rate on 3 courses",
        "rarity": "epic",
        "icon_url": "/badges/perfectionist.png",
        "condition": lambda stats: stats["perfect_courses"] >= 3
    }
}


# ============ Helper Functions ============

async def get_user_stats(user_id: int, db: AsyncSession) -> Dict[str, Any]:
    """Get user statistics for achievement checking"""

    # Get completed nodes count
    completed_nodes_query = select(func.count(LearningProgress.id)).where(
        and_(
            LearningProgress.user_id == user_id,
            LearningProgress.status == NodeStatus.COMPLETED
        )
    )
    completed_nodes = await db.scalar(completed_nodes_query) or 0

    # Get total learning time
    time_query = select(func.sum(LearningProgress.time_spent_seconds)).where(
        LearningProgress.user_id == user_id
    )
    total_seconds = await db.scalar(time_query) or 0
    total_hours = total_seconds / 3600

    # Calculate streak (simplified - should be more sophisticated)
    from sqlalchemy import cast, Date, desc
    from datetime import timedelta

    dates_query = select(
        func.distinct(cast(LearningProgress.last_accessed, Date))
    ).where(
        and_(
            LearningProgress.user_id == user_id,
            LearningProgress.last_accessed.isnot(None)
        )
    ).order_by(desc(cast(LearningProgress.last_accessed, Date)))

    result = await db.execute(dates_query)
    activity_dates = [row[0] for row in result.all()]

    current_streak = 0
    if activity_dates:
        today = datetime.now(timezone.utc).date()
        if activity_dates[0] >= today - timedelta(days=1):
            current_streak = 1
            for i in range(1, len(activity_dates)):
                if activity_dates[i] == activity_dates[i-1] - timedelta(days=1):
                    current_streak += 1
                else:
                    break

    # Get completed courses count (courses with 100% completion)
    from app.models.models import Course

    # Get all courses user has progress in
    courses_query = select(
        func.distinct(CourseNode.course_id)
    ).select_from(
        LearningProgress
    ).join(
        CourseNode, LearningProgress.node_id == CourseNode.id
    ).where(
        LearningProgress.user_id == user_id
    )

    result = await db.execute(courses_query)
    course_ids = [row[0] for row in result.all()]

    completed_courses = 0
    perfect_courses = 0

    for course_id in course_ids:
        # Get total nodes in course
        total_nodes_query = select(func.count(CourseNode.id)).where(
            CourseNode.course_id == course_id
        )
        total_nodes = await db.scalar(total_nodes_query) or 0

        # Get completed nodes in course
        completed_query = select(func.count(LearningProgress.id)).where(
            and_(
                LearningProgress.user_id == user_id,
                LearningProgress.node_id.in_(
                    select(CourseNode.id).where(CourseNode.course_id == course_id)
                ),
                LearningProgress.status == NodeStatus.COMPLETED
            )
        )
        completed = await db.scalar(completed_query) or 0

        if total_nodes > 0 and completed == total_nodes:
            completed_courses += 1
            perfect_courses += 1

    return {
        "completed_nodes": completed_nodes,
        "total_hours": total_hours,
        "current_streak": current_streak,
        "completed_courses": completed_courses,
        "perfect_courses": perfect_courses
    }


async def check_and_unlock_achievements(user_id: int, db: AsyncSession) -> List[str]:
    """
    Check user stats and unlock any new achievements

    Returns list of newly unlocked achievement IDs
    """
    # Get user stats
    stats = await get_user_stats(user_id, db)

    # Get already unlocked achievements
    unlocked_query = select(Achievement.badge_id).where(
        Achievement.user_id == user_id
    )
    result = await db.execute(unlocked_query)
    unlocked_badges = set(row[0] for row in result.all())

    # Check each achievement
    newly_unlocked = []

    for badge_id, achievement_def in ACHIEVEMENT_DEFINITIONS.items():
        # Skip if already unlocked
        if badge_id in unlocked_badges:
            continue

        # Check condition
        if achievement_def["condition"](stats):
            # Unlock achievement
            achievement = Achievement(
                user_id=user_id,
                badge_id=achievement_def["badge_id"],
                badge_name=achievement_def["badge_name"],
                badge_description=achievement_def["badge_description"],
                rarity=achievement_def["rarity"],
                icon_url=achievement_def["icon_url"]
            )
            db.add(achievement)
            newly_unlocked.append(badge_id)

    if newly_unlocked:
        await db.commit()

    return newly_unlocked


# ============ Endpoints ============

@router.get("/", response_model=List[AchievementResponse])
async def get_user_achievements(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's unlocked and locked achievements

    Returns all possible achievements with unlock status
    """
    # Check and unlock any new achievements first
    await check_and_unlock_achievements(current_user.id, db)

    # Get unlocked achievements
    unlocked_query = select(Achievement).where(
        Achievement.user_id == current_user.id
    )
    result = await db.execute(unlocked_query)
    unlocked_achievements = result.scalars().all()

    unlocked_badge_ids = {ach.badge_id for ach in unlocked_achievements}

    # Build response with all achievements
    achievements_list = []

    for badge_id, achievement_def in ACHIEVEMENT_DEFINITIONS.items():
        is_unlocked = badge_id in unlocked_badge_ids
        unlocked_at = None

        if is_unlocked:
            # Find the unlocked achievement
            for ach in unlocked_achievements:
                if ach.badge_id == badge_id:
                    unlocked_at = ach.unlocked_at
                    break

        achievements_list.append(AchievementResponse(
            badge_id=achievement_def["badge_id"],
            badge_name=achievement_def["badge_name"],
            badge_description=achievement_def["badge_description"],
            rarity=achievement_def["rarity"],
            icon_url=achievement_def["icon_url"],
            is_unlocked=is_unlocked,
            unlocked_at=unlocked_at
        ))

    # Sort: unlocked first, then by rarity
    rarity_order = {"legendary": 0, "epic": 1, "rare": 2, "common": 3}
    achievements_list.sort(
        key=lambda x: (not x.is_unlocked, rarity_order.get(x.rarity, 4))
    )

    return achievements_list


@router.get("/skill-tree", response_model=List[SkillTreeNode])
async def get_skill_tree(
    current_user: User = Depends(get_current_user),
    neo4j: Neo4jClient = Depends(get_neo4j),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's skill tree from Neo4j

    Returns skill nodes with:
    - Skill name and category
    - Current level (0-3)
    - Progress percentage
    - Dependencies
    """
    from app.services.skill_tree_service import SkillTreeService

    try:
        # Initialize skill tree service
        skill_service = SkillTreeService(neo4j, db)

        # Get user's skill tree
        skill_tree = await skill_service.get_user_skill_tree(current_user.id)

        # Convert to response format
        return [
            SkillTreeNode(
                skill_id=skill["skill_id"],
                skill_name=skill["skill_name"],
                category=skill["category"],
                current_level=skill["current_level"],
                max_level=skill["max_level"],
                progress_percentage=skill["progress_percentage"],
                is_unlocked=skill["is_unlocked"],
                prerequisites=skill["prerequisites"]
            )
            for skill in skill_tree
        ]
    except Exception as e:
        # If Neo4j is not available or there's an error, return empty list
        print(f"Skill tree error: {e}")
        return []


@router.get("/leaderboard")
async def get_leaderboard(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Get learning community leaderboard

    Ranks users by:
    - Total completed nodes
    - Total learning time
    - Achievement count
    """
    # Get top users by completed nodes
    from sqlalchemy import desc

    leaderboard_query = select(
        User.id,
        User.username,
        User.full_name,
        User.avatar_url,
        func.count(LearningProgress.id).label("completed_nodes"),
        func.sum(LearningProgress.time_spent_minutes).label("total_minutes")
    ).join(
        LearningProgress, User.id == LearningProgress.user_id
    ).where(
        LearningProgress.status == NodeStatus.COMPLETED
    ).group_by(
        User.id, User.username, User.full_name, User.avatar_url
    ).order_by(
        desc("completed_nodes")
    ).limit(limit)

    result = await db.execute(leaderboard_query)
    rows = result.all()

    leaderboard = []
    rank = 1

    for row in rows:
        # Get achievement count for this user
        achievement_count_query = select(func.count(Achievement.id)).where(
            Achievement.user_id == row.id
        )
        achievement_count = await db.scalar(achievement_count_query) or 0

        leaderboard.append({
            "rank": rank,
            "user_id": row.id,
            "username": row.username,
            "full_name": row.full_name,
            "avatar_url": row.avatar_url,
            "completed_nodes": row.completed_nodes,
            "total_hours": round((row.total_minutes or 0) / 60, 1),
            "achievement_count": achievement_count
        })
        rank += 1

    return {"leaderboard": leaderboard}


@router.post("/check-unlock")
async def check_unlock_achievements(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger achievement unlock check

    Returns list of newly unlocked achievements
    """
    newly_unlocked = await check_and_unlock_achievements(current_user.id, db)

    return {
        "newly_unlocked": newly_unlocked,
        "count": len(newly_unlocked)
    }
