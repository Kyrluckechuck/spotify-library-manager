"""Unit tests for auth service."""

from datetime import timedelta

import pytest

from api.src.services.auth import AuthService


@pytest.fixture
def auth_service():
    return AuthService()


class TestAuthService:
    """Test AuthService functionality."""

    def test_auth_service_initialization(self, auth_service):
        """Test AuthService can be initialized."""
        assert auth_service is not None
        assert hasattr(auth_service, "verify_password")
        assert hasattr(auth_service, "get_user")
        assert hasattr(auth_service, "authenticate_user")
        assert hasattr(auth_service, "create_access_token")
        assert hasattr(auth_service, "verify_token")

    def test_verify_password_success(self, auth_service):
        """Test successful password verification."""
        result = auth_service.verify_password(
            "admin", auth_service.users["admin"].hashed_password
        )
        assert result is True

    def test_verify_password_failure(self, auth_service):
        """Test failed password verification."""
        result = auth_service.verify_password(
            "wrong_password", auth_service.users["admin"].hashed_password
        )
        assert result is False

    def test_get_user_success(self, auth_service):
        """Test getting existing user."""
        user = auth_service.get_user("admin")
        assert user is not None
        assert user.username == "admin"

    def test_get_user_not_found(self, auth_service):
        """Test getting non-existent user."""
        user = auth_service.get_user("nonexistent")
        assert user is None

    def test_authenticate_user_success(self, auth_service):
        """Test successful user authentication."""
        user = auth_service.authenticate_user("admin", "admin")
        assert user is not None
        assert user.username == "admin"

    def test_authenticate_user_wrong_password(self, auth_service):
        """Test authentication with wrong password."""
        user = auth_service.authenticate_user("admin", "wrong_password")
        assert user is None

    def test_authenticate_user_nonexistent_user(self, auth_service):
        """Test authentication with non-existent user."""
        user = auth_service.authenticate_user("nonexistent", "password")
        assert user is None

    def test_create_access_token_success(self, auth_service):
        """Test creating access token."""
        data = {"sub": "admin"}
        token = auth_service.create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_expires_delta(self, auth_service):
        """Test creating access token with custom expiration."""
        data = {"sub": "admin"}
        expires_delta = timedelta(minutes=30)
        token = auth_service.create_access_token(data, expires_delta)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_success(self, auth_service):
        """Test successful token verification."""
        data = {"sub": "admin"}
        token = auth_service.create_access_token(data)

        username = auth_service.verify_token(token)
        assert username == "admin"

    def test_verify_token_invalid_token(self, auth_service):
        """Test verification of invalid token."""
        username = auth_service.verify_token("invalid_token")
        assert username is None

    def test_verify_token_expired_token(self, auth_service):
        """Test verification of expired token."""
        data = {"sub": "admin"}
        expires_delta = timedelta(seconds=-1)  # Expired token
        token = auth_service.create_access_token(data, expires_delta)

        username = auth_service.verify_token(token)
        assert username is None

    def test_verify_token_missing_subject(self, auth_service):
        """Test verification of token without subject."""
        data = {}  # No 'sub' field
        token = auth_service.create_access_token(data)

        username = auth_service.verify_token(token)
        assert username is None

    def test_auth_service_default_user(self, auth_service):
        """Test that default admin user exists."""
        assert "admin" in auth_service.users
        admin_user = auth_service.users["admin"]
        assert admin_user.username == "admin"
        assert admin_user.disabled is False

    def test_password_hashing(self, auth_service):
        """Test that passwords are properly hashed."""
        admin_user = auth_service.users["admin"]
        assert admin_user.hashed_password != "admin"  # Should be hashed
        assert auth_service.verify_password("admin", admin_user.hashed_password) is True
