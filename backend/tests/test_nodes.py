"""
Unit tests for node endpoints
"""
import pytest
from httpx import AsyncClient

from app.models.models import User, Course, CourseNode, LearningProgress


@pytest.mark.unit
class TestNodeEndpoints:
    """Test node API endpoints"""

    async def test_get_node_by_node_id(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_nodes: list[CourseNode]
    ):
        """Test getting a specific node by node_id"""
        node = test_nodes[0]
        response = await client.get(
            f"/api/v1/nodes/{node.node_id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["node_id"] == node.node_id
        assert data["title"] == node.title

    async def test_get_node_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting a non-existent node"""
        response = await client.get(
            "/api/v1/nodes/nonexistent_node_id",
            headers=auth_headers
        )

        assert response.status_code == 404

    async def test_get_course_map(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_course: Course,
        test_nodes: list[CourseNode]
    ):
        """Test getting course node map"""
        response = await client.get(
            f"/api/v1/nodes/course/{test_course.id}/map",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "course_id" in data
        assert "nodes" in data
        assert data["course_id"] == test_course.id

    async def test_node_unauthorized(
        self,
        client: AsyncClient,
        test_nodes: list[CourseNode]
    ):
        """Test accessing node without authentication"""
        node = test_nodes[0]
        response = await client.get(f"/api/v1/nodes/{node.node_id}")

        assert response.status_code == 401
