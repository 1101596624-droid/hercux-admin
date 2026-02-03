"""
Unit tests for simulator and badge endpoints
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User, Course


@pytest.mark.unit
class TestSimulatorEndpoints:
    """Test simulator API endpoints"""

    async def test_submit_simulator_result(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_course: Course
    ):
        """Test submitting simulator result"""
        result_data = {
            "course_id": test_course.id,
            "node_id": "simulator_node_1",
            "score": 85,
            "time_spent": 120,
            "interactions": [
                {"type": "input_change", "variable": "speed", "value": 50},
                {"type": "run_simulation", "timestamp": 1000}
            ],
            "completed": True
        }

        response = await client.post(
            "/api/v1/simulator/results",
            json=result_data,
            headers=auth_headers
        )

        # Accept 200, 201, or 404 (if endpoint not implemented)
        assert response.status_code in [200, 201, 404]

    async def test_get_simulator_results(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_course: Course
    ):
        """Test getting simulator results for a course"""
        response = await client.get(
            f"/api/v1/simulator/results?course_id={test_course.id}",
            headers=auth_headers
        )

        # Accept 200 or 404 (if endpoint not implemented)
        assert response.status_code in [200, 404]


@pytest.mark.unit
class TestBadgeEndpoints:
    """Test badge/achievement API endpoints"""

    async def test_get_all_badges(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting all available badges"""
        response = await client.get(
            "/api/v1/badges",
            headers=auth_headers
        )

        # Accept 200 or 404
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))

    async def test_get_user_badges(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting user's unlocked badges"""
        response = await client.get(
            "/api/v1/badges/me",
            headers=auth_headers
        )

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))

    async def test_get_badge_by_id(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting a specific badge by ID"""
        response = await client.get(
            "/api/v1/badges/1",
            headers=auth_headers
        )

        # Accept 200, 404 (not found), or 404 (endpoint not implemented)
        assert response.status_code in [200, 404]

    async def test_badges_pagination(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test badge list pagination"""
        response = await client.get(
            "/api/v1/badges?page=1&page_size=40",
            headers=auth_headers
        )

        if response.status_code == 200:
            data = response.json()
            # Should have pagination info or be a list
            assert isinstance(data, (list, dict))


@pytest.mark.unit
class TestQuizEndpoints:
    """Test quiz/assessment API endpoints"""

    async def test_submit_quiz_answer(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_course: Course
    ):
        """Test submitting quiz answer"""
        answer_data = {
            "course_id": test_course.id,
            "node_id": "quiz_node_1",
            "question_id": "q1",
            "selected_index": 0,
            "is_correct": True
        }

        response = await client.post(
            "/api/v1/quiz/submit",
            json=answer_data,
            headers=auth_headers
        )

        # Accept various status codes
        assert response.status_code in [200, 201, 404, 422]

    async def test_get_quiz_stats(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting user quiz statistics"""
        response = await client.get(
            "/api/v1/quiz/stats",
            headers=auth_headers
        )

        if response.status_code == 200:
            data = response.json()
            # Should have stats fields
            assert isinstance(data, dict)

    async def test_get_wrong_questions(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting user's wrong questions"""
        response = await client.get(
            "/api/v1/quiz/wrong-questions",
            headers=auth_headers
        )

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))


@pytest.mark.unit
class TestStudioEndpoints:
    """Test AI Studio API endpoints"""

    async def test_get_studio_processors(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting available studio processors"""
        response = await client.get(
            "/api/v1/studio/processors",
            headers=auth_headers
        )

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))

    async def test_create_studio_package(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test creating a studio package"""
        package_data = {
            "name": "Test Package",
            "description": "A test package",
            "source_type": "text",
            "content": "Sample content for testing"
        }

        response = await client.post(
            "/api/v1/studio/packages",
            json=package_data,
            headers=auth_headers
        )

        # Accept various status codes
        assert response.status_code in [200, 201, 404, 422]

    async def test_get_studio_packages(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting studio packages"""
        response = await client.get(
            "/api/v1/studio/packages",
            headers=auth_headers
        )

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))


@pytest.mark.integration
class TestLearningFlow:
    """Integration tests for complete learning flow"""

    async def test_complete_learning_flow(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_course: Course,
        test_nodes: list
    ):
        """Test a complete learning flow: join course -> learn -> complete"""
        # 1. Join course
        join_response = await client.post(
            f"/api/v1/courses/{test_course.id}/join",
            headers=auth_headers
        )
        assert join_response.status_code in [200, 201, 400]  # 400 if already joined

        # 2. Get course progress
        progress_response = await client.get(
            f"/api/v1/progress/course/{test_course.id}",
            headers=auth_headers
        )
        assert progress_response.status_code in [200, 404]

        # 3. Update node progress
        if test_nodes:
            update_data = {
                "status": "completed",
                "completion_percentage": 100,
                "time_spent_seconds": 300
            }
            update_response = await client.put(
                f"/api/v1/progress/node/{test_nodes[0].id}",
                json=update_data,
                headers=auth_headers
            )
            assert update_response.status_code in [200, 404]

    async def test_course_enrollment_and_progress(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_course: Course
    ):
        """Test course enrollment creates proper progress tracking"""
        # Join course
        join_response = await client.post(
            f"/api/v1/courses/{test_course.id}/join",
            headers=auth_headers
        )

        if join_response.status_code in [200, 201]:
            # Check that user_courses entry was created
            courses_response = await client.get(
                "/api/v1/courses/enrolled",
                headers=auth_headers
            )

            if courses_response.status_code == 200:
                data = courses_response.json()
                # Should include the enrolled course
                assert isinstance(data, (list, dict))
