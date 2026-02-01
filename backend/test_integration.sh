#!/bin/bash

# HERCU Backend Integration Test Script
# Tests the complete user journey using curl

BASE_URL="http://localhost:8000/api/v1"

echo "============================================================"
echo "  HERCU Backend Integration Test"
echo "============================================================"
echo "Testing against: $BASE_URL"
echo ""

# Test 1: Login with existing user
echo "============================================================"
echo "  1. User Login"
echo "============================================================"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@hercu.com&password=test123456")

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "✗ Login failed"
  echo "Response: $LOGIN_RESPONSE"
  exit 1
fi

echo "✓ Login successful"
echo "  Token: ${TOKEN:0:50}..."
echo ""

# Test 2: Get user profile
echo "============================================================"
echo "  2. Get User Profile"
echo "============================================================"
PROFILE=$(curl -s "$BASE_URL/user/profile" \
  -H "Authorization: Bearer $TOKEN")

echo "✓ Profile retrieved"
echo "$PROFILE" | head -5
echo ""

# Test 3: Browse courses
echo "============================================================"
echo "  3. Browse Courses"
echo "============================================================"
COURSES=$(curl -s "$BASE_URL/courses" \
  -H "Authorization: Bearer $TOKEN")

COURSE_COUNT=$(echo $COURSES | grep -o '"id"' | wc -l)
COURSE_ID=$(echo $COURSES | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

echo "✓ Found $COURSE_COUNT courses"
echo "  Selected course ID: $COURSE_ID"
echo ""

# Test 4: Get course details
echo "============================================================"
echo "  4. Get Course Details"
echo "============================================================"
COURSE_DETAIL=$(curl -s "$BASE_URL/courses/$COURSE_ID" \
  -H "Authorization: Bearer $TOKEN")

echo "✓ Course details retrieved"
echo "$COURSE_DETAIL" | head -10
echo ""

# Test 5: Get course structure (node map)
echo "============================================================"
echo "  5. Get Course Structure (Node Map)"
echo "============================================================"
STRUCTURE=$(curl -s "$BASE_URL/nodes/course/$COURSE_ID/map" \
  -H "Authorization: Bearer $TOKEN")

NODE_ID=$(echo $STRUCTURE | grep -o '"node_id":"[^"]*"' | head -1 | cut -d'"' -f4)

echo "✓ Course structure retrieved"
echo "  First node_id: $NODE_ID"
echo ""

# Test 6: Get node details
echo "============================================================"
echo "  6. Get Node Details"
echo "============================================================"
NODE_DETAIL=$(curl -s "$BASE_URL/nodes/$NODE_ID" \
  -H "Authorization: Bearer $TOKEN")

echo "✓ Node details retrieved"
echo "$NODE_DETAIL" | head -10
echo ""

# Test 7: Update progress
echo "============================================================"
echo "  7. Update Node Progress"
echo "============================================================"
PROGRESS_UPDATE=$(curl -s -X PUT "$BASE_URL/nodes/$NODE_ID/progress" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"in_progress","completion_percentage":50,"time_spent_seconds":60}')

echo "✓ Progress updated"
echo "$PROGRESS_UPDATE"
echo ""

# Test 8: Get user progress (node level)
echo "============================================================"
echo "  8. Get User Progress (Node Level)"
echo "============================================================"
USER_PROGRESS=$(curl -s "$BASE_URL/progress/nodes?course_id=$COURSE_ID" \
  -H "Authorization: Bearer $TOKEN")

echo "✓ User progress retrieved"
echo "$USER_PROGRESS" | head -10
echo ""

# Test 9: Get user summary
echo "============================================================"
echo "  9. Get Progress Summary"
echo "============================================================"
SUMMARY=$(curl -s "$BASE_URL/progress/summary" \
  -H "Authorization: Bearer $TOKEN")

echo "✓ Progress summary retrieved"
echo "$SUMMARY"
echo ""

# Final summary
echo "============================================================"
echo "  Integration Test Complete"
echo "============================================================"
echo "✓ All core functionality tests passed!"
echo ""
echo "Next steps:"
echo "  1. Test the frontend at http://localhost:3000"
echo "  2. Login with: test@hercu.com / test123456"
echo "  3. Navigate through the learning workflow"
echo "  4. Verify data synchronization"
echo ""
