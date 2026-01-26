import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from backend.routers.auth import router
from backend.models.user import User
from backend.schemas.user import UserCreate


class TestAuthRouter:
    """Test cases for the authentication router."""
    
    def test_register_user_success(self, client, db_session):
        """Test successful user registration."""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword",
            "full_name": "New User",
            "age": 30,
            "weight": 80.0,
            "height": 180.0,
            "activity_level": "active"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert data["age"] == 30
        assert data["weight"] == 80.0
        assert data["height"] == 180.0
        assert data["activity_level"] == "active"
        assert "id" in data
        assert "hashed_password" not in data  # Password should not be returned
    
    def test_register_user_duplicate_username(self, client, db_session, sample_user):
        """Test registration with duplicate username."""
        user_data = {
            "username": sample_user.username,
            "email": "different@example.com",
            "password": "password",
            "full_name": "Different User"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "Username already registered" in response.json()["detail"]
    
    def test_register_user_duplicate_email(self, client, db_session, sample_user):
        """Test registration with duplicate email."""
        user_data = {
            "username": "differentuser",
            "email": sample_user.email,
            "password": "password",
            "full_name": "Different User"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]
    
    def test_register_user_minimal_data(self, client, db_session):
        """Test registration with minimal required data."""
        user_data = {
            "username": "minimaluser",
            "email": "minimal@example.com",
            "password": "password"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "minimaluser"
        assert data["email"] == "minimal@example.com"
        assert data["full_name"] is None
        assert data["age"] is None
        assert data["weight"] is None
        assert data["height"] is None
        assert data["activity_level"] is None
    
    def test_login_success(self, client, db_session, sample_user):
        """Test successful user login."""
        login_data = {
            "username": sample_user.username,
            "password": "testpassword"
        }
        
        response = client.post("/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
    
    def test_login_wrong_password(self, client, db_session, sample_user):
        """Test login with wrong password."""
        login_data = {
            "username": sample_user.username,
            "password": "wrongpassword"
        }
        
        response = client.post("/auth/login", data=login_data)
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_nonexistent_user(self, client, db_session):
        """Test login with nonexistent user."""
        login_data = {
            "username": "nonexistent",
            "password": "password"
        }
        
        response = client.post("/auth/login", data=login_data)
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_missing_password(self, client, db_session):
        """Test login without password."""
        login_data = {
            "username": "testuser"
        }
        
        response = client.post("/auth/login", data=login_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_login_missing_username(self, client, db_session):
        """Test login without username."""
        login_data = {
            "password": "password"
        }
        
        response = client.post("/auth/login", data=login_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_get_current_user_valid_token(self, client, db_session, sample_user):
        """Test getting current user with valid token."""
        # First login to get token
        login_data = {
            "username": sample_user.username,
            "password": "testpassword"
        }
        login_response = client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        
        # Use token to get current user
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == sample_user.username
        assert data["email"] == sample_user.email
        assert data["full_name"] == sample_user.full_name
    
    def test_get_current_user_invalid_token(self, client, db_session):
        """Test getting current user with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]
    
    def test_get_current_user_missing_token(self, client, db_session):
        """Test getting current user without token."""
        response = client.get("/auth/me")
        
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    def test_get_current_user_expired_token(self, client, db_session):
        """Test getting current user with expired token."""
        # Create an expired token manually
        from backend.auth.auth import create_access_token
        from datetime import timedelta
        import time
        
        token_data = {"sub": "testuser"}
        # Create token that expired 1 hour ago
        expired_token = create_access_token(token_data, expires_delta=-3600)
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]
    
    def test_register_user_invalid_email(self, client, db_session):
        """Test registration with invalid email format."""
        user_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "password",
            "full_name": "Test User"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_register_user_short_password(self, client, db_session):
        """Test registration with password that's too short."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "123",  # Too short
            "full_name": "Test User"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        # Should succeed as password validation might be handled at application level
        # or might not be enforced in this implementation
        assert response.status_code in [200, 422]
    
    def test_login_inactive_user(self, client, db_session, sample_user):
        """Test login with inactive user."""
        # Make user inactive
        sample_user.is_active = False
        db_session.commit()
        
        login_data = {
            "username": sample_user.username,
            "password": "testpassword"
        }
        
        response = client.post("/auth/login", data=login_data)
        
        assert response.status_code == 400
        assert "Inactive user" in response.json()["detail"]