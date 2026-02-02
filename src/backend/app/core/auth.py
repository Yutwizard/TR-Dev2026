"""
Treasury Management System - JWT Authentication
=================================================

Provides JWT-based authentication for the API.

Usage:
    from app.core.auth import get_current_user, create_access_token
    
    # In route:
    @router.get("/protected")
    async def protected_route(current_user: User = Depends(get_current_user)):
        return {"user": current_user.username}
"""

from datetime import datetime, timedelta
from typing import Optional, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from app.config import settings


# =============================================================================
# OAuth2 Scheme
# =============================================================================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


# =============================================================================
# Token Models
# =============================================================================
class TokenData(BaseModel):
    """Data embedded in JWT token"""
    user_id: str
    username: str
    role: str
    exp: datetime


class Token(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int


class UserInToken(BaseModel):
    """User data in token payload"""
    user_id: str
    username: str
    email: str
    role: str
    full_name: Optional[str] = None
    is_active: bool = True


# =============================================================================
# Token Creation
# =============================================================================
def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a new access token.
    
    Args:
        data: Dictionary containing user information to encode
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
        
    Example:
        token = create_access_token(
            data={"user_id": "123", "username": "trader1", "role": "TRADER"}
        )
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a new refresh token.
    
    Refresh tokens have longer expiration and can be used to get new access tokens.
    
    Args:
        data: Dictionary containing user information to encode
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


# =============================================================================
# Token Verification
# =============================================================================
def verify_token(token: str) -> TokenData:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        TokenData with decoded information
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        user_id: str = payload.get("user_id")
        username: str = payload.get("username")
        role: str = payload.get("role")
        exp: datetime = datetime.fromtimestamp(payload.get("exp"))
        
        if user_id is None or username is None:
            raise credentials_exception
            
        return TokenData(
            user_id=user_id,
            username=username,
            role=role or "USER",
            exp=exp
        )
        
    except JWTError:
        raise credentials_exception


# =============================================================================
# User Dependencies
# =============================================================================
async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInToken:
    """
    Get current authenticated user from JWT token.
    
    This is a FastAPI dependency that extracts and validates the user
    from the Authorization header.
    
    Usage:
        @router.get("/me")
        async def get_me(current_user: UserInToken = Depends(get_current_user)):
            return current_user
    
    Args:
        token: JWT token from Authorization header (injected by Depends)
        
    Returns:
        UserInToken with user information
        
    Raises:
        HTTPException 401: If token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        user_id: str = payload.get("user_id")
        username: str = payload.get("username")
        email: str = payload.get("email", "")
        role: str = payload.get("role", "USER")
        full_name: str = payload.get("full_name")
        
        if user_id is None:
            raise credentials_exception
            
        return UserInToken(
            user_id=user_id,
            username=username,
            email=email,
            role=role,
            full_name=full_name,
            is_active=True
        )
        
    except JWTError:
        raise credentials_exception


async def get_current_active_user(
    current_user: UserInToken = Depends(get_current_user)
) -> UserInToken:
    """
    Get current user and verify they are active.
    
    Usage:
        @router.get("/dashboard")
        async def dashboard(user: UserInToken = Depends(get_current_active_user)):
            return {"welcome": user.full_name}
    
    Raises:
        HTTPException 400: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


# =============================================================================
# Role-based Access Helpers
# =============================================================================
def require_roles(*allowed_roles: str):
    """
    Dependency factory for role-based access.
    
    Usage:
        @router.post("/trades")
        async def create_trade(
            user: UserInToken = Depends(require_roles("TRADER", "SUPERVISOR"))
        ):
            return {"message": "Trade created"}
    
    Args:
        allowed_roles: List of roles that can access the endpoint
        
    Returns:
        Dependency function that validates user role
    """
    async def role_checker(
        current_user: UserInToken = Depends(get_current_active_user)
    ) -> UserInToken:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role}' not authorized. Required: {allowed_roles}"
            )
        return current_user
    
    return role_checker


# Convenience role dependencies
require_trader = require_roles("TRADER", "SUPERVISOR", "ADMIN")
require_supervisor = require_roles("SUPERVISOR", "RISK_OFFICER", "ADMIN")
require_risk_officer = require_roles("RISK_OFFICER", "ADMIN")
require_admin = require_roles("ADMIN")


# =============================================================================
# Token Refresh
# =============================================================================
async def refresh_access_token(refresh_token: str) -> Token:
    """
    Create new access token from refresh token.
    
    Args:
        refresh_token: Valid refresh token
        
    Returns:
        New Token with access_token and expires_in
        
    Raises:
        HTTPException 401: If refresh token is invalid
    """
    try:
        payload = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        # Create new access token
        new_access_token = create_access_token(
            data={
                "user_id": payload.get("user_id"),
                "username": payload.get("username"),
                "email": payload.get("email"),
                "role": payload.get("role"),
                "full_name": payload.get("full_name")
            }
        )
        
        return Token(
            access_token=new_access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
