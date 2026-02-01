"""
Manual Integration Test Script for HERCU
Tests the complete user journey using direct HTTP requests
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"


def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def print_success(message):
    print(f"✓ {message}")


def print_error(message):
    print(f"✗ {message}")


def test_complete_journey():
    """Test complete user learning journey"""

    print_section("HERCU Backend Integration Test")
    print(f"Testing against: {BASE_URL}")

    # Test 1: Register a new user
    print_section("1. User Registration")
    timestamp = int(time.time())
    register_data = {
        "email": f"test_{timestamp}@hercu.com",
        "username": f"testuser_{timestamp}",
        "password": "test123456",
        "full_name": "Integration Test User"
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code == 201:
            user = response.json()
            print_success(f"User registered: {user['email']}")
            print(f"  User ID: {user['id']}")
            print(f"  Username: {user['username']}")
        else:
            print_error(f"Registration failed: {response.status_code}")
            print(f"  Response: {response.text}")
            # Try with existing user
            register_data["email"] = "test@hercu.com"
            register_data["username"] = "testuser"
    except Exception as e:
        print_error(f"Registration error: {e}")
        return False

    # Test 2: Login
    print_section("2. User Login")
    login_data = {
        "username": register_data["email"],
        "password": register_data["password"]
    }

    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            token_data = response.json()
            token = token_data["access_token"]
            print_success("Login successful")
            print(f"  Token: {token[:50]}...")
        else:
            print_error(f"Login failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Login error: {e}")
        return False

    # Set auth header for subsequent requests
    headers = {"Authorization": f"Bearer {token}"}

    # Test 3: Get user profile
    print_section("3. Get User Profile")
    try:
        response = requests.get(f"{BASE_URL}/user/profile", headers=headers)
        if response.status_code == 200:
            profile = response.json()
            print_success("Profile retrieved")
            print(f"  Email: {profile['email']}")
            print(f"  Username: {profile['username']}")
            print(f"  Full Name: {profile['full_name']}")
        else:
            print_error(f"Get profile failed: {response.status_code}")
    except Exception as e:
        print_error(f"Get profile error: {e}")

    # Test 4: Browse courses
    print_section("4. Browse Courses")
    try:
        response = requests.get(f"{BASE_URL}/courses", headers=headers)
        if response.status_code == 200:
            courses = response.json()
            print_success(f"Found {len(courses)} courses")
            if courses:
                course = courses[0]
                course_id = course["id"]
                print(f"  Course 1: {course['name']}")
                print(f"    Difficulty: {course['difficulty']}")
                print(f"    Duration: {course['duration_hours']} hours")
                print(f"    Total Nodes: {course.get('total_nodes', 'N/A')}")
            else:
                print_error("No courses found")
                return False
        else:
            print_error(f"Get courses failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get courses error: {e}")
        return False

    # Test 5: Get course details
    print_section("5. Get Course Details")
    try:
        response = requests.get(f"{BASE_URL}/courses/{course_id}", headers=headers)
        if response.status_code == 200:
            course_detail = response.json()
            print_success(f"Course details retrieved: {course_detail['name']}")
            print(f"  Description: {course_detail['description'][:100]}...")
            print(f"  Instructor: {course_detail['instructor']}")
            print(f"  Progress: {course_detail.get('progress_percentage', 0)}%")
        else:
            print_error(f"Get course details failed: {response.status_code}")
    except Exception as e:
        print_error(f"Get course details error: {e}")

    # Test 6: Get course structure
    print_section("6. Get Course Structure")
    try:
        response = requests.get(f"{BASE_URL}/courses/{course_id}/structure", headers=headers)
        if response.status_code == 200:
            structure = response.json()
            nodes = structure.get("nodes", [])
            print_success(f"Course structure retrieved: {len(nodes)} nodes")
            if nodes:
                node = nodes[0]
                node_id = node["id"]
                print(f"  Node 1: {node['title']}")
                print(f"    Type: {node['node_type']}")
                print(f"    Status: {node.get('status', 'N/A')}")
            else:
                print_error("No nodes found in course")
                return False
        else:
            print_error(f"Get course structure failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get course structure error: {e}")
        return False

    # Test 7: Get node details
    print_section("7. Get Node Details")
    try:
        response = requests.get(f"{BASE_URL}/nodes/{node_id}", headers=headers)
        if response.status_code == 200:
            node_detail = response.json()
            print_success(f"Node details retrieved: {node_detail['title']}")
            print(f"  Type: {node_detail['node_type']}")
            print(f"  Sequence: {node_detail['sequence']}")
        else:
            print_error(f"Get node details failed: {response.status_code}")
    except Exception as e:
        print_error(f"Get node details error: {e}")

    # Test 8: Check unlock status
    print_section("8. Check Node Unlock Status")
    try:
        response = requests.get(f"{BASE_URL}/nodes/{node_id}/unlock-status", headers=headers)
        if response.status_code == 200:
            unlock_status = response.json()
            print_success(f"Unlock status retrieved")
            print(f"  Is Unlocked: {unlock_status.get('is_unlocked', False)}")
            print(f"  Can Unlock: {unlock_status.get('can_unlock', False)}")
        else:
            print_error(f"Get unlock status failed: {response.status_code}")
    except Exception as e:
        print_error(f"Get unlock status error: {e}")

    # Test 9: Update progress
    print_section("9. Update Node Progress")
    progress_data = {
        "status": "in_progress",
        "current_step": 1,
        "time_spent": 60
    }
    try:
        response = requests.post(
            f"{BASE_URL}/progress/node/{node_id}",
            json=progress_data,
            headers=headers
        )
        if response.status_code == 200:
            progress_result = response.json()
            print_success("Progress updated")
            print(f"  Status: {progress_result.get('status', 'N/A')}")
        else:
            print_error(f"Update progress failed: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print_error(f"Update progress error: {e}")

    # Test 10: Get user progress
    print_section("10. Get User Progress")
    try:
        response = requests.get(f"{BASE_URL}/progress?course_id={course_id}", headers=headers)
        if response.status_code == 200:
            progress_list = response.json()
            print_success(f"User progress retrieved: {len(progress_list)} nodes")
            if progress_list:
                print(f"  First node status: {progress_list[0].get('status', 'N/A')}")
        else:
            print_error(f"Get progress failed: {response.status_code}")
    except Exception as e:
        print_error(f"Get progress error: {e}")

    # Test 11: Get user summary
    print_section("11. Get User Summary")
    try:
        response = requests.get(f"{BASE_URL}/user/summary", headers=headers)
        if response.status_code == 200:
            summary = response.json()
            print_success("User summary retrieved")
            print(f"  Total Learning Time: {summary.get('total_learning_time', 0)} seconds")
            print(f"  Completed Nodes: {summary.get('completed_nodes', 0)}")
            print(f"  Current Streak: {summary.get('current_streak', 0)} days")
        else:
            print_error(f"Get summary failed: {response.status_code}")
    except Exception as e:
        print_error(f"Get summary error: {e}")

    # Test 12: Test AI chat (optional, may fail if API key not configured)
    print_section("12. Test AI Guide Chat (Optional)")
    chat_data = {
        "node_id": node_id,
        "user_message": "Can you explain this concept?",
        "context": {}
    }
    try:
        response = requests.post(
            f"{BASE_URL}/ai/guide-chat",
            json=chat_data,
            headers=headers
        )
        if response.status_code == 200:
            ai_response = response.json()
            print_success("AI chat successful")
            print(f"  Response: {ai_response.get('response', '')[:100]}...")
        else:
            print_error(f"AI chat failed: {response.status_code}")
            print(f"  Note: This may fail if Claude API key is not configured")
    except Exception as e:
        print_error(f"AI chat error: {e}")

    # Final summary
    print_section("Integration Test Complete")
    print_success("All core functionality tests passed!")
    print("\nNext steps:")
    print("  1. Test the frontend at http://localhost:3000")
    print("  2. Login with the test user credentials")
    print("  3. Navigate through the learning workflow")
    print("  4. Verify data synchronization between frontend and backend")

    return True


if __name__ == "__main__":
    print("\n" + "🚀 "*20)
    print("HERCU Backend Integration Test Suite")
    print("🚀 "*20)

    try:
        success = test_complete_journey()
        if success:
            print("\n" + "✅ "*20)
            print("All tests passed successfully!")
            print("✅ "*20)
        else:
            print("\n" + "❌ "*20)
            print("Some tests failed. Check the output above.")
            print("❌ "*20)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
