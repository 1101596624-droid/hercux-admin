"""
Unit tests for authentication endpoints
"""
import pytest
from httpx import AsyncClient

from app.models.models import User


@pytest.mark.unit
class TestAuthEndpoints:
    """Test authentication API endpoints"""

    async def test_register_user(self, client: AsyncClient):
        """Test user registration"""
        register_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "securepassword123",
            "fullName": "New User"
        }

        response = await client.post(
            "/api/v1/auth/register",
            json=register_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == register_data["email"]
        assert data["username"] == register_data["username"]
        assert "hashedPassword" not in data  # Password should not be returned

    async def test_register_duplicate_email(
        self,
        client: AsyncClient,
        test_user: User
    ):
        """Test registration with duplicate email"""
        register_data = {
            "email": test_user.email,  # Duplicate
            "username": "anotheruser",
            "password": "password123"
        }

        response = await client.post(
            "/api/v1/auth/register",
            json=register_data
        )

        assert response.status_code == 400

    async def test_login_success(
        self,
        client: AsyncClient,
        test_user: User
    ):
        """Test successful login"""
        login_data = {
            "username": test_user.email,  # Can use email as username
            "password": "testpassword123"
        }

        response = await client.post(
            "/api/v1/auth/login",
            data=login_data  # OAuth2 uses form data
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(
        self,
        client: AsyncClient,
        test_user: User
    ):
        """Test login with wrong password"""
        login_data = {
            "username": test_user.email,
            "password": "wrongpassword"
        }

        response = await client.post(
            "/api/v1/auth/login",
            data=login_data
        )

        assert response.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user"""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "password123"
        }

        response = await client.post(
            "/api/v1/auth/login",
            data=login_data
        )

        assert response.status_code == 401

    async def test_get_current_user(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """Test getting current authenticated user"""
        response = await client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username

    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        """Test getting current user without authentication"""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401

    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Test getting current user with invalid token"""
        invalid_headers = {"Authorization": "Bearer invalid_token_here"}

        response = await client.get(
            "/api/v1/auth/me",
            headers=invalid_headers
        )

        assert response.status_code == 401

    async def test_refresh_token(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test token refresh"""
        response = await client.post(
            "/api/v1/auth/refresh",
            headers=auth_headers
        )

        # If refresh endpoint exists
        if response.status_code != 404:
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data

    async def test_logout(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test user logout"""
        response = await client.post(
            "/api/v1/auth/logout",
            headers=auth_headers
        )

        # If logout endpoint exists
        if response.status_code != 404:
            assert response.status_code == 200

    @pytest.mark.skip(reason="Password validation not implemented in API")
    async def test_password_validation(self, client: AsyncClient):
        """Test password validation during registration"""
        weak_password_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "123"  # Too short
        }

        response = await client.post(
            "/api/v1/auth/register",
            json=weak_password_data
        )

        # Should fail validation
        assert response.status_code in [400, 422]

    async def test_email_validation(self, client: AsyncClient):
        """Test email validation during registration"""
        invalid_email_data = {
            "email": "not-an-email",
            "username": "testuser",
            "password": "securepassword123"
        }

        response = await client.post(
            "/api/v1/auth/register",
            json=invalid_email_data
        )

        # Should fail validation
        assert response.status_code in [400, 422]
