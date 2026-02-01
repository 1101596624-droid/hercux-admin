"""
Unit tests for StatisticsService
"""
import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.statistics_service import StatisticsService
from app.models.models import (
    User,
    Course,
    CourseNode,
    LearningProgress,
    LearningStatistics,
    NodeStatus
)


@pytest.mark.unit
class TestStatisticsService:
    """Test StatisticsService functionality"""

    async def test_get_user_summary(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_progress
    ):
        """Test getting user summary statistics"""
        service = StatisticsService(db_session)
        summary = await service.get_user_summary(test_user.id)

        assert "totalLearningTimeSeconds" in summary
        assert "totalLearningTimeHours" in summary
        assert "nodesCompleted" in summary
        assert "currentStreak" in summary
        assert "activeCourses" in summary
        assert summary["nodesCompleted"] >= 1  # At least one completed node

    async def test_get_weekly_statistics(
        self,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test getting weekly statistics"""
        # Create statistics for the past week
        today = datetime.now(timezone.utc).date()
        for i in range(7):
            stat = LearningStatistics(
                user_id=test_user.id,
                date=today - timedelta(days=i),
                total_time_seconds=3600 * (i + 1),
                nodes_completed=i + 1,
                streak_days=i + 1
            )
            db_session.add(stat)
        await db_session.commit()

        service = StatisticsService(db_session)
        weekly_stats = await service.get_weekly_statistics(test_user.id)

        assert "weekStart" in weekly_stats
        assert "weekEnd" in weekly_stats
        assert "dailyBreakdown" in weekly_stats
        assert "totalTimeSeconds" in weekly_stats
        assert len(weekly_stats["dailyBreakdown"]) <= 7

    async def test_get_monthly_statistics(
        self,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test getting monthly statistics"""
        # Create statistics for current month
        today = datetime.now(timezone.utc)
        year = today.year
        month = today.month

        for i in range(10):
            stat = LearningStatistics(
                user_id=test_user.id,
                date=datetime(year, month, min(i + 1, 28)).date(),
                total_time_seconds=3600 * (i + 1),
                nodes_completed=i + 1,
                streak_days=i + 1
            )
            db_session.add(stat)
        await db_session.commit()

        service = StatisticsService(db_session)
        monthly_stats = await service.get_monthly_statistics(test_user.id, year, month)

        assert monthly_stats["year"] == year
        assert monthly_stats["month"] == month
        assert "dailyBreakdown" in monthly_stats
        assert "totalTimeSeconds" in monthly_stats
        assert "averageTimePerDay" in monthly_stats

    async def test_get_course_progress_summary(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_course: Course,
        test_nodes,
        test_progress
    ):
        """Test getting course progress summary"""
        service = StatisticsService(db_session)
        course_summaries = await service.get_course_progress_summary(test_user.id)

        assert isinstance(course_summaries, list)
        assert len(course_summaries) >= 1

        # Check first course summary structure
        summary = course_summaries[0]
        assert "courseId" in summary
        assert "courseName" in summary
        assert "totalNodes" in summary
        assert "completedNodes" in summary
        assert "progressPercentage" in summary
        assert "timeSpentSeconds" in summary

    async def test_calculate_streak_consecutive_days(
        self,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test streak calculation with consecutive days"""
        today = datetime.now(timezone.utc).replace(hour=12, minute=0, second=0, microsecond=0)

        # Create 5 consecutive days of activity
        for i in range(5):
            stat = LearningStatistics(
                user_id=test_user.id,
                date=today - timedelta(days=i),
                total_time_seconds=3600,
                nodes_completed=1,
                streak_days=0
            )
            db_session.add(stat)
        await db_session.commit()

        service = StatisticsService(db_session)
        streak = await service._calculate_streak(test_user.id)

        assert streak == 5

    async def test_calculate_streak_with_gap(
        self,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test streak calculation with gap in activity"""
        today = datetime.now(timezone.utc).replace(hour=12, minute=0, second=0, microsecond=0)

        # Create activity today and yesterday
        for i in range(2):
            stat = LearningStatistics(
                user_id=test_user.id,
                date=today - timedelta(days=i),
                total_time_seconds=3600,
                nodes_completed=1,
                streak_days=0
            )
            db_session.add(stat)

        # Gap of 2 days, then more activity
        for i in range(3, 6):
            stat = LearningStatistics(
                user_id=test_user.id,
                date=today - timedelta(days=i),
                total_time_seconds=3600,
                nodes_completed=1,
                streak_days=0
            )
            db_session.add(stat)

        await db_session.commit()

        service = StatisticsService(db_session)
        streak = await service._calculate_streak(test_user.id)

        # Streak should only count consecutive days from today
        assert streak == 2

    async def test_calculate_streak_no_activity(
        self,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test streak calculation with no recent activity"""
        service = StatisticsService(db_session)
        streak = await service._calculate_streak(test_user.id)

        assert streak == 0

    async def test_update_daily_statistics(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_nodes,
        test_progress
    ):
        """Test updating daily statistics"""
        today = datetime.now(timezone.utc).date()

        service = StatisticsService(db_session)
        await service.update_daily_statistics(test_user.id, datetime.now(timezone.utc))

        # Verify statistics were created/updated
        from sqlalchemy import select, and_, func
        stat_query = select(LearningStatistics).where(
            LearningStatistics.user_id == test_user.id
        ).order_by(LearningStatistics.date.desc()).limit(1)
        result = await db_session.execute(stat_query)
        stat = result.scalar_one_or_none()

        assert stat is not None
        assert stat.total_time_seconds >= 0
        assert stat.nodes_completed >= 0

    async def test_empty_statistics(
        self,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test statistics with no learning data"""
        service = StatisticsService(db_session)

        # Get summary with no progress
        summary = await service.get_user_summary(test_user.id)
        assert summary["totalLearningTimeSeconds"] == 0
        assert summary["nodesCompleted"] == 0
        assert summary["currentStreak"] == 0

        # Get weekly stats with no data
        weekly = await service.get_weekly_statistics(test_user.id)
        assert weekly["totalTimeSeconds"] == 0
        assert len(weekly["dailyBreakdown"]) == 0
