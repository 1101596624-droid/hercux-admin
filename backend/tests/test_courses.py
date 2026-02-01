"""
Unit tests for course endpoints
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Course, CourseNode, DifficultyLevel


@pytest.mark.unit
class TestCourseEndpoints:
    """Test course API endpoints"""

    async def test_get_courses_list(self, client: AsyncClient, test_course: Course):
        """Test getting list of courses"""
        response = await client.get("/api/v1/courses")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["name"] == "Test Course"
        assert data[0]["difficulty"] == "beginner"

    async def test_get_courses_with_difficulty_filter(
        self,
        client: AsyncClient,
        test_course: Course
    ):
        """Test filtering courses by difficulty"""
        response = await client.get("/api/v1/courses?difficulty=beginner")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all(course["difficulty"] == "beginner" for course in data)

    async def test_get_courses_with_tag_filter(
        self,
        client: AsyncClient,
        test_course: Course
    ):
        """Test filtering courses by tags"""
        response = await client.get("/api/v1/courses?tags=python")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        # Verify the course has the tag
        assert any("python" in course.get("tags", []) for course in data)

    async def test_get_courses_with_search(
        self,
        client: AsyncClient,
        test_course: Course
    ):
        """Test searching courses by name"""
        response = await client.get("/api/v1/courses?search=Test")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert "Test" in data[0]["name"]

    async def test_get_courses_count(
        self,
        client: AsyncClient,
        test_course: Course
    ):
        """Test getting total course count"""
        response = await client.get("/api/v1/courses/count/total")

        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert data["total"] >= 1

    async def test_get_course_by_id(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_course: Course
    ):
        """Test getting a specific course by ID (requires auth)"""
        response = await client.get(
            f"/api/v1/courses/{test_course.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_course.id
        assert data["name"] == test_course.name
        assert data["difficulty"] == "beginner"

    async def test_get_course_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting a non-existent course"""
        response = await client.get(
            "/api/v1/courses/99999",
            headers=auth_headers
        )

        assert response.status_code == 404

    async def test_pagination(
        self,
        client: AsyncClient,
        db_session: AsyncSession
    ):
        """Test course list pagination"""
        # Create multiple courses
        for i in range(5):
            course = Course(
                name=f"Course {i}",
                description=f"Description {i}",
                difficulty=DifficultyLevel.BEGINNER,
                duration_hours=10,
                is_published=1,
                tags=[]
            )
            db_session.add(course)
        await db_session.commit()

        # Test with limit
        response = await client.get("/api/v1/courses?limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3

        # Test with skip
        response = await client.get("/api/v1/courses?skip=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2
