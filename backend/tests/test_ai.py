"""
Unit tests for AI service endpoints
"""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

from app.models.models import User, CourseNode


@pytest.mark.unit
class TestAIEndpoints:
    """Test AI service API endpoints"""

    async def test_ai_guide_chat(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_nodes: list[CourseNode]
    ):
        """Test AI guide chat functionality"""
        node = test_nodes[0]
        request_data = {
            "node_id": node.id,
            "user_message": "Can you explain this concept?",
            "context": {
                "nodeTitle": node.title
            }
        }

        with patch("app.services.ai_service.AIService.guide_chat") as mock_chat:
            mock_chat.return_value = "Let me help you understand this concept..."

            response = await client.post(
                "/api/v1/ai/guide-chat",
                json=request_data,
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert "response" in data

    async def test_ai_guide_chat_with_string_node_id(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_nodes: list[CourseNode]
    ):
        """Test AI guide chat with string node_id"""
        node = test_nodes[0]
        request_data = {
            "node_id": str(node.id),
            "user_message": "What does this mean?",
            "context": {}
        }

        with patch("app.services.ai_service.AIService.guide_chat") as mock_chat:
            mock_chat.return_value = "This concept means..."

            response = await client.post(
                "/api/v1/ai/guide-chat",
                json=request_data,
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert "response" in data

    async def test_ai_generate_plan(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test generating a training plan"""
        request_data = {
            "role": "athlete",
            "goal": "strength",
            "duration_weeks": 12,
            "sessions_per_week": 4,
            "experience_level": "intermediate",
            "available_equipment": ["barbell", "dumbbells"],
            "constraints": None
        }

        with patch("app.services.ai_service.AIService.generate_training_plan") as mock_plan:
            mock_plan.return_value = {
                "title": "Strength Training Plan",
                "duration_weeks": 12,
                "phases": [
                    {
                        "phase_number": 1,
                        "title": "Foundation Phase",
                        "duration_weeks": 4,
                        "sessions": []
                    }
                ]
            }

            response = await client.post(
                "/api/v1/ai/generate-plan",
                json=request_data,
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert "plan_data" in data

    async def test_ai_guide_chat_node_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test AI guide chat with non-existent node"""
        request_data = {
            "node_id": 99999,
            "user_message": "Help me understand",
            "context": {}
        }

        response = await client.post(
            "/api/v1/ai/guide-chat",
            json=request_data,
            headers=auth_headers
        )

        assert response.status_code == 404

    async def test_ai_guide_chat_invalid_node_id(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test AI guide chat with invalid node_id format"""
        request_data = {
            "node_id": "invalid_not_a_number",
            "user_message": "Help me",
            "context": {}
        }

        response = await client.post(
            "/api/v1/ai/guide-chat",
            json=request_data,
            headers=auth_headers
        )

        assert response.status_code == 400

    async def test_ai_unauthorized(self, client: AsyncClient):
        """Test AI endpoints without authentication"""
        request_data = {
            "node_id": 1,
            "user_message": "Help me"
        }

        response = await client.post(
            "/api/v1/ai/guide-chat",
            json=request_data
        )

        assert response.status_code == 401

    async def test_ai_generate_plan_unauthorized(self, client: AsyncClient):
        """Test generate plan without authentication"""
        request_data = {
            "role": "athlete",
            "goal": "strength"
        }

        response = await client.post(
            "/api/v1/ai/generate-plan",
            json=request_data
        )

        assert response.status_code == 401
