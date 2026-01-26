import pytest
from fastapi import HTTPException
from jose import JWTError
from backend.auth.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    authenticate_user,
    get_current_user,
    get_current_active_user
)
from backend.models.user import User
from backend.schemas.user import TokenData


class TestPasswordHashing:
    """Test cases for password hashing functions."""
    
    def test_get_password_hash(self):
        """Test password hashing."""
        password = "testpassword"
        hashed_password = get_password_hash(password)
        
        assert hashed_password is not None
        assert hashed_password != password
        assert len(hashed_password) > 0
    
    def test_verify_password_correct(self):
        """Test verifying correct password."""
        password = "testpassword"
        hashed_password = get_password_hash(password)
        
        assert verify_password(password, hashed_password) is True
    
    def test_verify_password_incorrect(self):
        """Test verifying incorrect password."""
        password = "testpassword"
        wrong_password = "wrongpassword"
        hashed_password = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed_password) is False


class TestJWTToken:
    """Test cases for JWT token functions."""
    
    def test_create_access_token(self):
        """Test creating access token."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_with_expiration(self):
        """Test creating access token with custom expiration."""
        data = {"sub": "testuser"}
        expires_delta = 3600  # 1 hour
        token = create_access_token(data, expires_delta)
        
        assert token is not None
        assert isinstance(token, str)
    
    def test_create_access_token_with_empty_data(self):
        """Test creating access token with empty data."""
        data = {}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)


class TestAuthentication:
    """Test cases for authentication functions."""
    
    async def test_authenticate_user_success(self, db_session, sample_user):
        """Test successful user authentication."""
        user = await authenticate_user(
            db_session, 
            sample_user.username, 
            "testpassword"
        )
        
        assert user is not None
        assert user.username == sample_user.username
        assert user.email == sample_user.email
    
    async def test_authenticate_user_wrong_password(self, db_session, sample_user):
        """Test authentication with wrong password."""
        user = await authenticate_user(
            db_session, 
            sample_user.username, 
            "wrongpassword"
        )
        
        assert user is None
    
    async def test_authenticate_user_nonexistent(self, db_session):
        """Test authentication with nonexistent user."""
        user = await authenticate_user(
            db_session, 
            "nonexistent", 
            "password"
        )
        
        assert user is None
    
    async def test_get_current_user_valid_token(self, db_session, sample_user):
        """Test getting current user with valid token."""
        token_data = TokenData(username=sample_user.username)
        token = create_access_token(token_data.dict())
        
        user = await get_current_user(db_session, token)
        
        assert user is not None
        assert user.username == sample_user.username
    
    async def test_get_current_user_invalid_token(self, db_session):
        """Test getting current user with invalid token."""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(db_session, "invalid_token")
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in str(exc_info.value.detail)
    
    async def test_get_current_user_nonexistent_user(self, db_session):
        """Test getting current user for nonexistent user."""
        token_data = TokenData(username="nonexistent")
        token = create_access_token(token_data.dict())
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(db_session, token)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in str(exc_info.value.detail)
    
    async def test_get_current_active_user_active(self, db_session, sample_user):
        """Test getting current active user when user is active."""
        token_data = TokenData(username=sample_user.username)
        token = create_access_token(token_data.dict())
        
        user = await get_current_active_user(db_session, token)
        
        assert user is not None
        assert user.username == sample_user.username
        assert user.is_active is True
    
    async def test_get_current_active_user_inactive(self, db_session, sample_user):
        """Test getting current active user when user is inactive."""
        # Make user inactive
        sample_user.is_active = False
        db_session.commit()
        
        token_data = TokenData(username=sample_user.username)
        token = create_access_token(token_data.dict())
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_active_user(db_session, token)
        
        assert exc_info.value.status_code == 400
        assert "Inactive user" in str(exc_info.value.detail)
    
    async def test_get_current_user_missing_username(self, db_session):
        """Test getting current user when token doesn't contain username."""
        # Create token without username
        token = create_access_token({})
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(db_session, token)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in str(exc_info.value.detail)
    
    async def test_get_current_user_expired_token(self, db_session):
        """Test getting current user with expired token."""
        # Create token with very short expiration
        token_data = TokenData(username="testuser")
        token = create_access_token(token_data.dict(), expires_delta=-3600)  # Expired 1 hour ago
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(db_session, token)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in str(exc_info.value.detail)