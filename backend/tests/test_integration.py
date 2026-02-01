"""
Integration tests for HERCU backend
Tests the complete user journey from registration to learning
"""

import pytest
import asyncio
from httpx import AsyncClient
from app.main import app

BASE_URL = "http://localhost:8000/api/v1"


class TestUserJourney:
    """Test complete user learning journey"""

    @pytest.mark.skip(reason="Integration test requires running server with specific endpoints")
    @pytest.mark.asyncio
    async def test_complete_user_journey(self):
        """
        Test the complete user journey:
        1. Register a new user
        2. Login
        3. Browse courses
        4. Get course details
        5. Get course nodes
        6. Start learning (update progress)
        7. Complete a node
        8. Check progress
        """
        async with AsyncClient(app=app, base_url=BASE_URL) as client:
            # 1. Register a new user
            print("\n1. Testing user registration...")
            register_data = {
                "email": f"integration_test_{asyncio.get_event_loop().time()}@test.com",
                "username": f"testuser_{int(asyncio.get_event_loop().time())}",
                "password": "testpass123",
                "full_name": "Integration Test User"
            }

            response = await client.post("/auth/register", json=register_data)
            assert response.status_code == 201, f"Registration failed: {response.text}"
            user_data = response.json()
            assert user_data["email"] == register_data["email"]
            print(f"✓ User registered: {user_data['email']}")

            # 2. Login
            print("\n2. Testing login...")
            login_data = {
                "username": register_data["email"],
                "password": register_data["password"]
            }
            response = await client.post(
                "/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            assert response.status_code == 200, f"Login failed: {response.text}"
            token_data = response.json()
            assert "access_token" in token_data
            token = token_data["access_token"]
            print(f"✓ Login successful, token received")

            # Set auth header for subsequent requests
            headers = {"Authorization": f"Bearer {token}"}

            # 3. Browse courses
            print("\n3. Testing course browsing...")
            response = await client.get("/courses", headers=headers)
            assert response.status_code == 200, f"Get courses failed: {response.text}"
            courses = response.json()
            assert len(courses) > 0, "No courses found"
            course_id = courses[0]["id"]
            print(f"✓ Found {len(courses)} courses, selected course ID: {course_id}")

            # 4. Get course details
            print("\n4. Testing course details...")
            response = await client.get(f"/courses/{course_id}", headers=headers)
            assert response.status_code == 200, f"Get course details failed: {response.text}"
            course = response.json()
            assert course["id"] == course_id
            print(f"✓ Course details: {course['name']}")

            # 5. Get course structure (nodes)
            print("\n5. Testing course structure...")
            response = await client.get(f"/courses/{course_id}/structure", headers=headers)
            assert response.status_code == 200, f"Get course structure failed: {response.text}"
            structure = response.json()
            assert "nodes" in structure
            assert len(structure["nodes"]) > 0, "No nodes found in course"
            node_id = structure["nodes"][0]["id"]
            print(f"✓ Course has {len(structure['nodes'])} nodes, selected node ID: {node_id}")

            # 6. Get node details
            print("\n6. Testing node details...")
            response = await client.get(f"/nodes/{node_id}", headers=headers)
            assert response.status_code == 200, f"Get node failed: {response.text}"
            node = response.json()
            assert node["id"] == node_id
            print(f"✓ Node details: {node['title']}")

            # 7. Check node unlock status
            print("\n7. Testing node unlock status...")
            response = await client.get(f"/nodes/{node_id}/unlock-status", headers=headers)
            assert response.status_code == 200, f"Get unlock status failed: {response.text}"
            unlock_status = response.json()
            print(f"✓ Node unlock status: {unlock_status}")

            # 8. Update node progress
            print("\n8. Testing progress update...")
            progress_data = {
                "status": "in_progress",
                "current_step": 1,
                "time_spent": 60
            }
            response = await client.post(
                f"/progress/node/{node_id}",
                json=progress_data,
                headers=headers
            )
            assert response.status_code == 200, f"Update progress failed: {response.text}"
            print(f"✓ Progress updated")

            # 9. Get user progress
            print("\n9. Testing get user progress...")
            response = await client.get(f"/progress?course_id={course_id}", headers=headers)
            assert response.status_code == 200, f"Get progress failed: {response.text}"
            progress = response.json()
            assert len(progress) > 0, "No progress found"
            print(f"✓ User has progress on {len(progress)} nodes")

            # 10. Complete the node
            print("\n10. Testing node completion...")
            response = await client.post(
                f"/progress/node/{node_id}/complete",
                headers=headers
            )
            assert response.status_code == 200, f"Complete node failed: {response.text}"
            completion_result = response.json()
            print(f"✓ Node completed: {completion_result}")

            # 11. Get user summary
            print("\n11. Testing user summary...")
            response = await client.get("/user/summary", headers=headers)
            assert response.status_code == 200, f"Get summary failed: {response.text}"
            summary = response.json()
            assert "total_learning_time" in summary
            print(f"✓ User summary: {summary}")

            print("\n" + "="*50)
            print("✅ All integration tests passed!")
            print("="*50)


class TestAIServices:
    """Test AI-related services"""

    @pytest.mark.asyncio
    async def test_ai_chat(self):
        """Test AI guide chat"""
        async with AsyncClient(app=app, base_url=BASE_URL) as client:
            # Login first
            login_data = {
                "username": "test@hercu.com",
                "password": "test123456"
            }
            response = await client.post(
                "/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            assert response.status_code == 200
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            # Test AI chat
            print("\nTesting AI guide chat...")
            chat_data = {
                "node_id": 1,
                "user_message": "Can you explain this concept?",
                "context": {}
            }
            response = await client.post("/ai/guide-chat", json=chat_data, headers=headers)
            assert response.status_code == 200, f"AI chat failed: {response.text}"
            result = response.json()
            assert "response" in result
            print(f"✓ AI response received: {result['response'][:100]}...")


class TestCourseManagement:
    """Test course management endpoints"""

    @pytest.mark.asyncio
    async def test_course_filtering(self):
        """Test course filtering and search"""
        async with AsyncClient(app=app, base_url=BASE_URL) as client:
            # Login
            login_data = {
                "username": "test@hercu.com",
                "password": "test123456"
            }
            response = await client.post(
                "/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            # Test filtering by difficulty
            print("\nTesting course filtering by difficulty...")
            response = await client.get("/courses?difficulty=intermediate", headers=headers)
            assert response.status_code == 200
            courses = response.json()
            print(f"✓ Found {len(courses)} intermediate courses")

            # Test filtering by tags
            print("\nTesting course filtering by tags...")
            response = await client.get("/courses?tags=biomechanics", headers=headers)
            assert response.status_code == 200
            courses = response.json()
            print(f"✓ Found {len(courses)} courses with 'biomechanics' tag")

            # Test search
            print("\nTesting course search...")
            response = await client.get("/courses?search=力量", headers=headers)
            assert response.status_code == 200
            courses = response.json()
            print(f"✓ Found {len(courses)} courses matching '力量'")


if __name__ == "__main__":
    print("Running integration tests...")
    print("Make sure the backend server is running on http://localhost:8000")
    print("="*50)

    # Run tests
    pytest.main([__file__, "-v", "-s"])
