"""
User Statistics Service
Handles aggregation and calculation of user learning statistics
"""
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from datetime import datetime, timedelta, timezone
import logging

from app.models.models import (
    User,
    LearningProgress,
    LearningStatistics,
    CourseNode,
    Course,
    NodeStatus
)
from app.core.utils import status_equals

logger = logging.getLogger(__name__)


class StatisticsService:
    """Service for calculating and aggregating user statistics"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_summary(self, user_id: int) -> Dict:
        """
        Get user learning summary for dashboard

        Returns:
            - Total learning time
            - Nodes completed
            - Current streak
            - Active courses
        """
        # Get total learning time
        total_time_query = select(func.sum(LearningProgress.time_spent_seconds)).where(
            LearningProgress.user_id == user_id
        )
        total_time = await self.db.scalar(total_time_query) or 0

        # Get nodes completed count
        completed_query = select(func.count(LearningProgress.id)).where(
            and_(
                LearningProgress.user_id == user_id,
                status_equals(LearningProgress.status, NodeStatus.COMPLETED)
            )
        )
        nodes_completed = await self.db.scalar(completed_query) or 0

        # Get current streak
        streak = await self._calculate_streak(user_id)

        # Get active courses (courses with progress)
        active_courses_query = select(func.count(func.distinct(CourseNode.course_id))).where(
            CourseNode.id.in_(
                select(LearningProgress.node_id).where(
                    LearningProgress.user_id == user_id
                )
            )
        )
        active_courses = await self.db.scalar(active_courses_query) or 0

        return {
            "totalLearningTimeSeconds": int(total_time),
            "totalLearningTimeHours": round(total_time / 3600, 1),
            "nodesCompleted": nodes_completed,
            "currentStreak": streak,
            "activeCourses": active_courses
        }

    async def get_weekly_statistics(self, user_id: int) -> Dict:
        """
        Get weekly learning statistics

        Returns:
            - Daily breakdown for the past 7 days
            - Total time this week
            - Nodes completed this week
        """
        today = datetime.now(timezone.utc).date()
        week_ago = today - timedelta(days=7)

        # Get daily statistics for the past week
        daily_stats_query = select(LearningStatistics).where(
            and_(
                LearningStatistics.user_id == user_id,
                LearningStatistics.date >= week_ago,
                LearningStatistics.date <= today
            )
        ).order_by(LearningStatistics.date)

        result = await self.db.execute(daily_stats_query)
        daily_stats = result.scalars().all()

        # Build daily breakdown
        daily_breakdown = []
        total_time_week = 0
        total_nodes_week = 0

        for stat in daily_stats:
            daily_breakdown.append({
                "date": stat.date.isoformat(),
                "timeSeconds": stat.total_time_seconds,
                "nodesCompleted": stat.nodes_completed
            })
            total_time_week += stat.total_time_seconds
            total_nodes_week += stat.nodes_completed

        return {
            "weekStart": week_ago.isoformat(),
            "weekEnd": today.isoformat(),
            "dailyBreakdown": daily_breakdown,
            "totalTimeSeconds": total_time_week,
            "totalNodesCompleted": total_nodes_week
        }

    async def get_monthly_statistics(self, user_id: int, year: int, month: int) -> Dict:
        """
        Get monthly learning statistics

        Args:
            user_id: User ID
            year: Year (e.g., 2026)
            month: Month (1-12)

        Returns:
            Monthly statistics with daily breakdown
        """
        from calendar import monthrange

        # Get first and last day of month
        first_day = datetime(year, month, 1).date()
        last_day_num = monthrange(year, month)[1]
        last_day = datetime(year, month, last_day_num).date()

        # Get statistics for the month
        monthly_stats_query = select(LearningStatistics).where(
            and_(
                LearningStatistics.user_id == user_id,
                LearningStatistics.date >= first_day,
                LearningStatistics.date <= last_day
            )
        ).order_by(LearningStatistics.date)

        result = await self.db.execute(monthly_stats_query)
        monthly_stats = result.scalars().all()

        # Build daily breakdown
        daily_breakdown = []
        total_time_month = 0
        total_nodes_month = 0

        for stat in monthly_stats:
            daily_breakdown.append({
                "date": stat.date.isoformat(),
                "timeSeconds": stat.total_time_seconds,
                "nodesCompleted": stat.nodes_completed
            })
            total_time_month += stat.total_time_seconds
            total_nodes_month += stat.nodes_completed

        return {
            "year": year,
            "month": month,
            "monthStart": first_day.isoformat(),
            "monthEnd": last_day.isoformat(),
            "dailyBreakdown": daily_breakdown,
            "totalTimeSeconds": total_time_month,
            "totalNodesCompleted": total_nodes_month,
            "averageTimePerDay": round(total_time_month / last_day_num, 1) if last_day_num > 0 else 0
        }

    async def get_course_progress_summary(self, user_id: int) -> List[Dict]:
        """
        Get progress summary for all user's courses

        Returns:
            List of courses with progress information
        """
        # Get all courses the user has started
        courses_query = select(Course).where(
            Course.id.in_(
                select(func.distinct(CourseNode.course_id)).where(
                    CourseNode.id.in_(
                        select(LearningProgress.node_id).where(
                            LearningProgress.user_id == user_id
                        )
                    )
                )
            )
        )

        result = await self.db.execute(courses_query)
        courses = result.scalars().all()

        course_summaries = []

        for course in courses:
            # Get total nodes in course
            total_nodes_query = select(func.count(CourseNode.id)).where(
                CourseNode.course_id == course.id
            )
            total_nodes = await self.db.scalar(total_nodes_query) or 0

            # Get completed nodes
            completed_query = select(func.count(LearningProgress.id)).where(
                and_(
                    LearningProgress.user_id == user_id,
                    LearningProgress.node_id.in_(
                        select(CourseNode.id).where(CourseNode.course_id == course.id)
                    ),
                    status_equals(LearningProgress.status, NodeStatus.COMPLETED)
                )
            )
            completed_nodes = await self.db.scalar(completed_query) or 0

            # Get total time spent on this course
            time_query = select(func.sum(LearningProgress.time_spent_seconds)).where(
                and_(
                    LearningProgress.user_id == user_id,
                    LearningProgress.node_id.in_(
                        select(CourseNode.id).where(CourseNode.course_id == course.id)
                    )
                )
            )
            time_spent = await self.db.scalar(time_query) or 0

            # Get last accessed time
            last_accessed_query = select(func.max(LearningProgress.last_accessed)).where(
                and_(
                    LearningProgress.user_id == user_id,
                    LearningProgress.node_id.in_(
                        select(CourseNode.id).where(CourseNode.course_id == course.id)
                    )
                )
            )
            last_accessed = await self.db.scalar(last_accessed_query)

            progress_percentage = (completed_nodes / total_nodes * 100) if total_nodes > 0 else 0

            course_summaries.append({
                "courseId": course.id,
                "courseName": course.name,
                "difficulty": course.difficulty.value,
                "totalNodes": total_nodes,
                "completedNodes": completed_nodes,
                "progressPercentage": round(progress_percentage, 2),
                "timeSpentSeconds": int(time_spent),
                "lastAccessed": last_accessed.isoformat() if last_accessed else None
            })

        # Sort by last accessed (most recent first)
        course_summaries.sort(key=lambda x: x["lastAccessed"] or "", reverse=True)

        return course_summaries

    async def _calculate_streak(self, user_id: int) -> int:
        """
        Calculate current learning streak (consecutive days)

        Returns:
            Number of consecutive days with learning activity
        """
        today = datetime.now(timezone.utc).date()
        today_end = datetime.combine(today, datetime.max.time())

        # Get recent statistics ordered by date descending
        recent_stats_query = select(LearningStatistics).where(
            and_(
                LearningStatistics.user_id == user_id,
                LearningStatistics.date <= today_end
            )
        ).order_by(desc(LearningStatistics.date)).limit(365)  # Check up to 1 year

        result = await self.db.execute(recent_stats_query)
        stats = result.scalars().all()

        if not stats:
            return 0

        # Helper to convert datetime to date if needed
        def to_date(d):
            return d.date() if isinstance(d, datetime) else d

        # Check if there's activity today or yesterday (streak can continue if missed today)
        stat_date = to_date(stats[0].date)
        if stat_date < today - timedelta(days=1):
            return 0

        # Count consecutive days
        streak = 0
        expected_date = today

        for stat in stats:
            stat_date = to_date(stat.date)
            if stat_date == expected_date:
                if stat.nodes_completed > 0 or stat.total_time_seconds > 0:
                    streak += 1
                    expected_date -= timedelta(days=1)
                else:
                    break
            elif stat_date < expected_date:
                # Gap in dates, streak broken
                break

        return streak

    async def update_daily_statistics(self, user_id: int, date: Optional[datetime] = None):
        """
        Update or create daily statistics for a user

        This should be called after completing a node or updating progress

        Args:
            user_id: User ID
            date: Date to update (defaults to today)
        """
        if date is None:
            date = datetime.now(timezone.utc).date()
        else:
            date = date.date() if isinstance(date, datetime) else date

        # Calculate statistics for the day
        day_start = datetime.combine(date, datetime.min.time())
        day_end = datetime.combine(date, datetime.max.time())

        # Get total time spent today
        time_query = select(func.sum(LearningProgress.time_spent_seconds)).where(
            and_(
                LearningProgress.user_id == user_id,
                LearningProgress.last_accessed >= day_start,
                LearningProgress.last_accessed <= day_end
            )
        )
        total_time = await self.db.scalar(time_query) or 0

        # Get nodes completed today
        completed_query = select(func.count(LearningProgress.id)).where(
            and_(
                LearningProgress.user_id == user_id,
                status_equals(LearningProgress.status, NodeStatus.COMPLETED),
                LearningProgress.last_accessed >= day_start,
                LearningProgress.last_accessed <= day_end
            )
        )
        nodes_completed = await self.db.scalar(completed_query) or 0

        # Get or create statistics record
        stat_query = select(LearningStatistics).where(
            and_(
                LearningStatistics.user_id == user_id,
                LearningStatistics.date == date
            )
        )
        result = await self.db.execute(stat_query)
        stat = result.scalar_one_or_none()

        if stat:
            # Update existing record
            stat.total_time_seconds = int(total_time)
            stat.nodes_completed = nodes_completed
        else:
            # Create new record
            stat = LearningStatistics(
                user_id=user_id,
                date=date,
                total_time_seconds=int(total_time),
                nodes_completed=nodes_completed,
                streak_days=0  # Will be calculated separately
            )
            self.db.add(stat)

        await self.db.commit()

        logger.info(f"Updated daily statistics for user {user_id} on {date}: {nodes_completed} nodes, {total_time}s")
