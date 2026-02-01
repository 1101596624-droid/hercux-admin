"""
Unit tests for progress endpoints
"""
import pytest
from httpx import AsyncClient
from datetime import datetime

from app.models.models import User, CourseNode, LearningProgress, NodeStatus


@pytest.mark.unit
class TestProgressEndpoints:
    """Test learning progress API endpoints"""

    async def test_get_user_progress_summary(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_progress: list[LearningProgress]
    ):
        """Test getting user's learning progress summary"""
        response = await client.get(
            "/api/v1/progress/summary",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_nodes_started" in data
        assert "total_nodes_completed" in data

    async def test_get_node_progress_list(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_nodes: list[CourseNode],
        test_progress: list[LearningProgress]
    ):
        """Test getting progress for nodes"""
        response = await client.get(
            "/api/v1/progress/nodes",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    async def test_get_course_progress_list(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_course,
        test_progress: list[LearningProgress]
    ):
        """Test getting progress summary for courses"""
        response = await client.get(
            "/api/v1/progress/courses",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "courses" in data
        assert "total_courses" in data

    async def test_progress_unauthorized(
        self,
        client: AsyncClient,
        test_nodes: list[CourseNode]
    ):
        """Test accessing progress without authentication"""
        response = await client.get("/api/v1/progress/summary")

        assert response.status_code == 401

    async def test_get_recent_progress(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_progress: list[LearningProgress]
    ):
        """Test getting recent learning activity"""
        response = await client.get(
            "/api/v1/progress/recent?days=7",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "recent_activity" in data
        assert "days" in data
