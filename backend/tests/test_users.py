"""
Unit tests for user endpoints
"""
import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta, timezone

from app.models.models import User, LearningStatistics


@pytest.mark.unit
class TestUserEndpoints:
    """Test user API endpoints"""

    async def test_get_user_profile(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """Test getting user profile"""
        response = await client.get(
            "/api/v1/user/profile",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username

    async def test_update_user_profile(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test updating user profile"""
        update_data = {
            "full_name": "Updated Name",
            "avatar_url": "https://example.com/avatar.jpg"
        }

        response = await client.put(
            "/api/v1/user/profile",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"

    async def test_get_user_summary(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_progress
    ):
        """Test getting user learning summary"""
        response = await client.get(
            "/api/v1/user/summary",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        # Check for expected fields in summary
        assert isinstance(data, dict)

    async def test_get_weekly_statistics(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session,
        test_user: User
    ):
        """Test getting weekly learning statistics"""
        # Create some statistics data
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

        response = await client.get(
            "/api/v1/user/statistics/weekly",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    async def test_get_monthly_statistics(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session,
        test_user: User
    ):
        """Test getting monthly learning statistics"""
        # Create statistics for current month
        today = datetime.now(timezone.utc)
        year = today.year
        month = today.month

        for i in range(5):
            stat = LearningStatistics(
                user_id=test_user.id,
                date=datetime(year, month, i + 1).date(),
                total_time_seconds=3600 * (i + 1),
                nodes_completed=i + 1,
                streak_days=i + 1
            )
            db_session.add(stat)
        await db_session.commit()

        response = await client.get(
            f"/api/v1/user/statistics/monthly?year={year}&month={month}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    async def test_get_course_progress_summary(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_progress
    ):
        """Test getting progress summary for all courses"""
        response = await client.get(
            "/api/v1/user/statistics/courses",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "courses" in data
        assert "totalCourses" in data
        assert isinstance(data["courses"], list)

    async def test_get_active_course(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_progress
    ):
        """Test getting user's most recently accessed course"""
        response = await client.get(
            "/api/v1/user/active-course",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        # Should have course info or message
        assert "courseId" in data or "message" in data

    async def test_user_endpoints_unauthorized(self, client: AsyncClient):
        """Test user endpoints without authentication"""
        endpoints = [
            "/api/v1/user/profile",
            "/api/v1/user/summary",
            "/api/v1/user/statistics/weekly",
            "/api/v1/user/active-course"
        ]

        for endpoint in endpoints:
            response = await client.get(endpoint)
            assert response.status_code == 401

    async def test_monthly_statistics_validation(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test monthly statistics with invalid parameters"""
        # Invalid month
        response = await client.get(
            "/api/v1/user/statistics/monthly?year=2026&month=13",
            headers=auth_headers
        )
        assert response.status_code == 422

        # Missing parameters
        response = await client.get(
            "/api/v1/user/statistics/monthly",
            headers=auth_headers
        )
        assert response.status_code == 422

    async def test_get_user_settings(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting user settings"""
        response = await client.get(
            "/api/v1/user/settings",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "language" in data
        assert "theme" in data

    async def test_update_user_settings(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test updating user settings"""
        settings_data = {
            "language": "en-US",
            "theme": "dark"
        }

        response = await client.put(
            "/api/v1/user/settings",
            json=settings_data,
            headers=auth_headers
        )

        assert response.status_code == 200
