"""
Treasury Management System - Security Utilities
================================================

Password hashing, validation, and other security utilities.

Usage:
    from app.core.security import verify_password, get_password_hash
    
    # Hash a password
    hashed = get_password_hash("my_password")
    
    # Verify password
    is_valid = verify_password("my_password", hashed)
"""

from passlib.context import CryptContext
import secrets
import string
from typing import Tuple

from app.config import settings


# =============================================================================
# Password Hashing
# =============================================================================
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Good balance of security and performance
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
        
    Example:
        if verify_password(user_input, stored_hash):
            print("Login successful!")
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Hashed password string
        
    Example:
        user.hashed_password = get_password_hash("new_password")
    """
    return pwd_context.hash(password)


# =============================================================================
# Password Validation
# =============================================================================
def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password meets security requirements.
    
    Requirements:
    - Minimum length (from settings)
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Example:
        is_valid, error = validate_password_strength("Test123!")
        if not is_valid:
            raise ValueError(error)
    """
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False, "Password must contain at least one special character"
    
    return True, ""


# =============================================================================
# Token Generation
# =============================================================================
def generate_random_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token.
    
    Args:
        length: Length of the token (default 32)
        
    Returns:
        URL-safe random token string
        
    Example:
        reset_token = generate_random_token(64)
    """
    return secrets.token_urlsafe(length)


def generate_api_key() -> str:
    """
    Generate a new API key.
    
    Format: tms_[32 random chars]
    
    Returns:
        API key string
        
    Example:
        api_key = generate_api_key()
        # Returns: tms_abc123...
    """
    return f"tms_{secrets.token_urlsafe(32)}"


def generate_temp_password(length: int = 12) -> str:
    """
    Generate a temporary password for new users.
    
    Args:
        length: Length of the password (default 12)
        
    Returns:
        Random password meeting security requirements
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    
    # Ensure at least one of each required character type
    password = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%^&*")
    ]
    
    # Fill the rest
    for _ in range(length - 4):
        password.append(secrets.choice(alphabet))
    
    # Shuffle to avoid predictable pattern
    secrets.SystemRandom().shuffle(password)
    
    return "".join(password)


# =============================================================================
# Input Sanitization
# =============================================================================
def sanitize_input(value: str, max_length: int = 255) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        value: Input string to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not value:
        return ""
    
    # Truncate
    value = value[:max_length]
    
    # Remove null bytes
    value = value.replace("\x00", "")
    
    # Strip whitespace
    value = value.strip()
    
    return value


# =============================================================================
# Rate Limiting Helpers
# =============================================================================
def check_login_attempts(attempts: int) -> Tuple[bool, int]:
    """
    Check if login attempts exceed limit.
    
    Args:
        attempts: Number of failed attempts
        
    Returns:
        Tuple of (is_locked, lockout_minutes)
    """
    if attempts >= settings.MAX_LOGIN_ATTEMPTS:
        return True, settings.LOCKOUT_DURATION_MINUTES
    return False, 0
