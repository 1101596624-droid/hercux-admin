# HERCU Backend Tests

This directory contains unit and integration tests for the HERCU backend API.

## Test Structure

```
tests/
├── conftest.py                    # Test fixtures and configuration
├── test_auth.py                   # Authentication endpoint tests
├── test_courses.py                # Course endpoint tests
├── test_nodes.py                  # Node endpoint tests
├── test_progress.py               # Progress tracking tests
├── test_ai.py                     # AI service endpoint tests
├── test_users.py                  # User endpoint tests
└── test_statistics_service.py     # Statistics service unit tests
```

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_courses.py
```

### Run Tests with Coverage

```bash
pytest --cov=app --cov-report=html
```

This will generate an HTML coverage report in `htmlcov/index.html`.

### Run Tests by Marker

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only slow tests
pytest -m slow
```

### Run Tests in Verbose Mode

```bash
pytest -v
```

### Run Tests and Stop on First Failure

```bash
pytest -x
```

## Test Fixtures

The `conftest.py` file provides several useful fixtures:

- `db_session`: Fresh database session for each test (SQLite in-memory)
- `client`: AsyncClient for making API requests
- `test_user`: Pre-created test user
- `test_user_token`: JWT token for the test user
- `auth_headers`: Authorization headers with test user token
- `test_course`: Pre-created test course
- `test_nodes`: Pre-created course nodes with dependencies
- `test_progress`: Pre-created learning progress records

## Writing New Tests

### Example Test

```python
import pytest
from httpx import AsyncClient

@pytest.mark.unit
async def test_my_endpoint(client: AsyncClient, auth_headers: dict):
    """Test description"""
    response = await client.get(
        "/api/v1/my-endpoint",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "expected_field" in data
```

### Test Markers

Use markers to categorize tests:

- `@pytest.mark.unit` - Fast unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow-running tests

## Mocking External Services

For tests that interact with external services (like Claude API), use mocking:

```python
from unittest.mock import patch

async def test_with_mock(client: AsyncClient, auth_headers: dict):
    with patch("app.services.ai_service.AIService.method") as mock_method:
        mock_method.return_value = "mocked response"

        response = await client.post("/api/v1/endpoint", headers=auth_headers)
        assert response.status_code == 200
```

## Coverage Goals

- **Target**: 80%+ code coverage
- **Critical paths**: 100% coverage for authentication, progress tracking, and unlock logic
- **AI services**: Mock external API calls to ensure consistent test results

## Continuous Integration

These tests are designed to run in CI/CD pipelines. The in-memory SQLite database ensures fast, isolated test execution without external dependencies.

## Troubleshooting

### Import Errors

If you encounter import errors, ensure you're running tests from the backend directory:

```bash
cd backend
pytest
```

### Async Warnings

If you see warnings about async fixtures, ensure `pytest-asyncio` is installed and `asyncio_mode = auto` is set in `pytest.ini`.

### Database Errors

Tests use an in-memory SQLite database that's created fresh for each test. If you encounter database errors, check that:
1. All models are properly imported in `conftest.py`
2. The test database URL is correct
3. Tables are being created/dropped correctly

## Future Improvements

- [ ] Add integration tests with real PostgreSQL database
- [ ] Add performance/load tests
- [ ] Add end-to-end tests for complete learning flows
- [ ] Add tests for Neo4j skill tree integration
- [ ] Add tests for Redis caching behavior
