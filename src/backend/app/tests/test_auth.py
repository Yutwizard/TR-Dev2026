"""
Treasury Management System - Authentication Tests
===================================================

Unit tests for JWT authentication and security.
"""

import pytest
from datetime import datetime, timedelta
from jose import jwt
from fastapi import HTTPException

from app.core.auth import (
    create_access_token,
    create_refresh_token,
    verify_token,
    Token,
    UserInToken,
)
from app.core.security import (
    get_password_hash,
    verify_password,
    validate_password_strength,
    generate_random_token,
    sanitize_input,
)
from app.core.permissions import (
    Role,
    Permission,
    get_role_permissions,
    has_permission,
    validate_four_eyes,
)
from app.config import settings


class TestPasswordHashing:
    """Tests for password hashing functions"""
    
    def test_hash_password(self):
        """Should create a hash different from original"""
        password = "SecurePassword123!"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert hashed.startswith("$2b$")  # bcrypt prefix
    
    def test_verify_correct_password(self):
        """Should verify correct password"""
        password = "SecurePassword123!"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_incorrect_password(self):
        """Should reject incorrect password"""
        password = "SecurePassword123!"
        hashed = get_password_hash(password)
        
        assert verify_password("WrongPassword", hashed) is False
    
    def test_different_hashes_for_same_password(self):
        """Same password should produce different hashes (salt)"""
        password = "SecurePassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestPasswordValidation:
    """Tests for password strength validation"""
    
    def test_valid_password(self):
        """Should accept valid password"""
        is_valid, errors = validate_password_strength("SecurePassword123!")
        assert is_valid is True
        assert len(errors) == 0
    
    def test_short_password(self):
        """Should reject short password"""
        is_valid, errors = validate_password_strength("Short1!")
        assert is_valid is False
        assert any("8 characters" in e for e in errors)
    
    def test_no_uppercase(self):
        """Should reject password without uppercase"""
        is_valid, errors = validate_password_strength("nouppercase123!")
        assert is_valid is False
        assert any("uppercase" in e for e in errors)
    
    def test_no_lowercase(self):
        """Should reject password without lowercase"""
        is_valid, errors = validate_password_strength("NOLOWERCASE123!")
        assert is_valid is False
        assert any("lowercase" in e for e in errors)
    
    def test_no_digit(self):
        """Should reject password without digit"""
        is_valid, errors = validate_password_strength("NoDigitsHere!")
        assert is_valid is False
        assert any("digit" in e for e in errors)


class TestTokenCreation:
    """Tests for JWT token creation"""
    
    def test_create_access_token(self):
        """Should create valid access token"""
        data = {
            "user_id": "USER001",
            "username": "testuser",
            "email": "test@example.com",
            "role": "TRADER"
        }
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 100  # JWT tokens are long
    
    def test_access_token_contains_data(self):
        """Access token should contain user data"""
        data = {
            "user_id": "USER001",
            "username": "testuser",
            "email": "test@example.com",
            "role": "TRADER"
        }
        token = create_access_token(data)
        
        # Decode and verify
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        assert payload["user_id"] == "USER001"
        assert payload["username"] == "testuser"
        assert payload["role"] == "TRADER"
        assert "exp" in payload
    
    def test_create_refresh_token(self):
        """Should create refresh token with longer expiry"""
        data = {
            "user_id": "USER001",
            "username": "testuser",
            "email": "test@example.com",
            "role": "TRADER"
        }
        
        access_token = create_access_token(data)
        refresh_token = create_refresh_token(data)
        
        # Decode both
        access_payload = jwt.decode(
            access_token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        refresh_payload = jwt.decode(
            refresh_token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # Refresh token should have longer expiry
        assert refresh_payload["exp"] > access_payload["exp"]
        assert refresh_payload["token_type"] == "refresh"


class TestTokenVerification:
    """Tests for JWT token verification"""
    
    def test_verify_valid_token(self):
        """Should verify valid token"""
        data = {
            "user_id": "USER001",
            "username": "testuser",
            "email": "test@example.com",
            "role": "TRADER"
        }
        token = create_access_token(data)
        
        user = verify_token(token)
        
        assert user is not None
        assert user.user_id == "USER001"
        assert user.username == "testuser"
    
    def test_reject_invalid_token(self):
        """Should reject invalid token"""
        with pytest.raises(HTTPException) as exc_info:
            verify_token("invalid.token.here")
        
        assert exc_info.value.status_code == 401
    
    def test_reject_expired_token(self):
        """Should reject expired token"""
        # Create token with negative expiry
        data = {
            "user_id": "USER001",
            "username": "testuser",
            "email": "test@example.com",
            "role": "TRADER",
            "exp": datetime.utcnow() - timedelta(hours=1)
        }
        token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)
        
        assert exc_info.value.status_code == 401


class TestRolePermissions:
    """Tests for role-based access control"""
    
    def test_trader_has_create_trade(self):
        """Trader should have CREATE_TRADE permission"""
        permissions = get_role_permissions(Role.TRADER)
        assert Permission.CREATE_TRADE in permissions
    
    def test_trader_cannot_approve(self):
        """Trader should not have APPROVE_TRADE permission"""
        permissions = get_role_permissions(Role.TRADER)
        assert Permission.APPROVE_TRADE not in permissions
    
    def test_supervisor_can_approve(self):
        """Supervisor should have APPROVE_TRADE permission"""
        permissions = get_role_permissions(Role.SUPERVISOR)
        assert Permission.APPROVE_TRADE in permissions
    
    def test_admin_has_all_permissions(self):
        """Admin should have all permissions"""
        permissions = get_role_permissions(Role.ADMIN)
        
        # Check a few key permissions
        assert Permission.CREATE_TRADE in permissions
        assert Permission.APPROVE_TRADE in permissions
        assert Permission.CREATE_LIMIT in permissions
        assert Permission.MANAGE_USERS in permissions
    
    def test_has_permission_true(self):
        """has_permission should return True for valid permission"""
        assert has_permission(Role.TRADER, Permission.CREATE_TRADE) is True
    
    def test_has_permission_false(self):
        """has_permission should return False for invalid permission"""
        assert has_permission(Role.VIEWER, Permission.CREATE_TRADE) is False


class TestFourEyesPrinciple:
    """Tests for four-eyes principle validation"""
    
    def test_different_users_allowed(self):
        """Different users should be allowed"""
        # Should not raise
        validate_four_eyes("USER001", "USER002")
    
    def test_same_user_rejected(self):
        """Same user should be rejected"""
        with pytest.raises(HTTPException) as exc_info:
            validate_four_eyes("USER001", "USER001")
        
        assert exc_info.value.status_code == 403
        assert "four-eyes" in exc_info.value.detail.lower()


class TestInputSanitization:
    """Tests for input sanitization"""
    
    def test_sanitize_normal_input(self):
        """Normal input should pass through"""
        result = sanitize_input("Hello World")
        assert result == "Hello World"
    
    def test_sanitize_removes_script(self):
        """Should remove script tags"""
        result = sanitize_input("<script>alert('xss')</script>Hello")
        assert "<script>" not in result
        assert "Hello" in result
    
    def test_sanitize_removes_sql_injection(self):
        """Should remove SQL injection attempts"""
        result = sanitize_input("'; DROP TABLE users; --")
        assert "DROP TABLE" not in result


class TestRandomTokenGeneration:
    """Tests for random token generation"""
    
    def test_generate_token_default_length(self):
        """Should generate 32-byte token by default"""
        token = generate_random_token()
        assert len(token) == 64  # 32 bytes = 64 hex chars
    
    def test_generate_token_custom_length(self):
        """Should generate token of specified length"""
        token = generate_random_token(16)
        assert len(token) == 32  # 16 bytes = 32 hex chars
    
    def test_tokens_are_unique(self):
        """Each token should be unique"""
        tokens = [generate_random_token() for _ in range(100)]
        assert len(set(tokens)) == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
