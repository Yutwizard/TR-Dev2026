"""
Treasury Management System - Authentication Router
===================================================

Endpoints for user authentication:
- POST /token - Login and get access token
- POST /refresh - Refresh access token
- GET /me - Get current user info
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.config import settings
from app.core.auth import (
    create_access_token,
    create_refresh_token,
    get_current_active_user,
    refresh_access_token,
    Token,
    UserInToken,
)
from app.core.security import verify_password, get_password_hash


router = APIRouter()


# =============================================================================
# Request/Response Models
# =============================================================================
class LoginRequest(BaseModel):
    """Login request body"""
    username: str
    password: str


class RefreshRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class UserResponse(BaseModel):
    """User info response"""
    user_id: str
    username: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool


class ChangePasswordRequest(BaseModel):
    """Change password request"""
    current_password: str
    new_password: str


# =============================================================================
# Mock User Database (Replace with real database in production)
# =============================================================================
# This is for testing only - replace with actual database queries
MOCK_USERS = {
    "admin": {
        "user_id": "ADMIN001",
        "username": "admin",
        "email": "admin@bank.com",
        "full_name": "System Administrator",
        "role": "ADMIN",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X.rF7fCKtJ1.JGf/O",  # admin123
        "is_active": True
    },
    "trader1": {
        "user_id": "TRADER001",
        "username": "trader1",
        "email": "trader1@bank.com",
        "full_name": "John Trader",
        "role": "TRADER",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X.rF7fCKtJ1.JGf/O",  # admin123
        "is_active": True
    },
    "supervisor1": {
        "user_id": "SUP001",
        "username": "supervisor1",
        "email": "supervisor1@bank.com",
        "full_name": "Jane Supervisor",
        "role": "SUPERVISOR",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X.rF7fCKtJ1.JGf/O",
        "is_active": True
    },
    "risk1": {
        "user_id": "RISK001",
        "username": "risk1",
        "email": "risk1@bank.com",
        "full_name": "Bob Risk Officer",
        "role": "RISK_OFFICER",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X.rF7fCKtJ1.JGf/O",
        "is_active": True
    },
    "backoffice1": {
        "user_id": "BO001",
        "username": "backoffice1",
        "email": "backoffice1@bank.com",
        "full_name": "Alice Settlement",
        "role": "BACK_OFFICE",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X.rF7fCKtJ1.JGf/O",
        "is_active": True
    },
}


def get_user_by_username(username: str) -> Optional[dict]:
    """Get user from mock database"""
    return MOCK_USERS.get(username)


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate user with username and password"""
    user = get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


# =============================================================================
# Endpoints
# =============================================================================
@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login.
    
    Get an access token for future requests.
    
    **Test credentials:**
    - admin / admin123 (ADMIN role)
    - trader1 / admin123 (TRADER role)
    - supervisor1 / admin123 (SUPERVISOR role)
    - risk1 / admin123 (RISK_OFFICER role)
    - backoffice1 / admin123 (BACK_OFFICE role)
    """
    user = authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
        )
    
    # Create tokens
    token_data = {
        "user_id": user["user_id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "full_name": user.get("full_name")
    }
    
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/login", response_model=Token)
async def login_json(request: LoginRequest):
    """
    JSON-based login (alternative to OAuth2 form).
    
    Send username and password in JSON body.
    """
    user = authenticate_user(request.username, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    if not user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
        )
    
    token_data = {
        "user_id": user["user_id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "full_name": user.get("full_name")
    }
    
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(request: RefreshRequest):
    """
    Refresh access token using refresh token.
    
    Use this when access token expires to get a new one
    without re-entering credentials.
    """
    return await refresh_access_token(request.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserInToken = Depends(get_current_active_user)
):
    """
    Get current authenticated user information.
    
    Requires valid access token in Authorization header.
    """
    return UserResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active
    )


@router.get("/verify")
async def verify_token(
    current_user: UserInToken = Depends(get_current_active_user)
):
    """
    Verify if the current token is valid.
    
    Returns user info if valid, 401 if not.
    """
    return {
        "valid": True,
        "user_id": current_user.user_id,
        "username": current_user.username,
        "role": current_user.role
    }
