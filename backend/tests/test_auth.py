"""
Authentication API Tests
Tests for registration, login, token management
"""
import pytest
from httpx import AsyncClient


class TestRegistration:
    """Test user registration endpoint"""
    
    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        """Test successful user registration"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "full_name": "New User",
                "organization": "Example Corp"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert "id" in data
        assert "password" not in data  # Password should not be returned
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        """Test registration with duplicate email"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "password": "SecurePass123!",
            }
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "weak@example.com",
                "password": "weak",  # Too short, no uppercase, no digit
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "password": "SecurePass123!",
            }
        )
        
        assert response.status_code == 422  # Validation error


class TestLogin:
    """Test user login endpoint"""
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user):
        """Test successful login"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "Test123!@#"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        """Test login with wrong password"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "WrongPassword123!"
            }
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with nonexistent user"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "Test123!@#"
            }
        )
        
        assert response.status_code == 401


class TestTokenManagement:
    """Test token refresh and validation"""
    
    @pytest.mark.asyncio
    async def test_token_refresh(self, client: AsyncClient, test_user):
        """Test token refresh"""
        # First, login to get refresh token
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "Test123!@#"
            }
        )
        
        refresh_token = login_response.json()["refresh_token"]
        
        # Now refresh the token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data


class TestUserProfile:
    """Test user profile endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_current_user(self, client: AsyncClient, auth_headers):
        """Test getting current user profile"""
        response = await client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
    
    @pytest.mark.asyncio
    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        """Test accessing profile without authentication"""
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 403  # No auth header
    
    @pytest.mark.asyncio
    async def test_update_profile(self, client: AsyncClient, auth_headers):
        """Test updating user profile"""
        response = await client.put(
            "/api/v1/auth/me",
            headers=auth_headers,
            json={
                "full_name": "Updated Name",
                "organization": "New Corp"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["organization"] == "New Corp"
    
    @pytest.mark.asyncio
    async def test_change_password(self, client: AsyncClient, auth_headers):
        """Test changing password"""
        response = await client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "Test123!@#",
                "new_password": "NewSecure456!@#"
            }
        )
        
        assert response.status_code == 200
        assert "successfully" in response.json()["message"].lower()


class TestHealthCheck:
    """Test health check endpoints"""
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient):
        """Test root endpoint"""
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "running"
    
    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint"""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
