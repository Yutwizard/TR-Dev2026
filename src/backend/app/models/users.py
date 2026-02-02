"""
Treasury Management System - User Model
=========================================

SQLAlchemy model for user management and authentication.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Boolean, DateTime, Text, Integer,
    ForeignKey, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """
    User Account
    
    Stores user credentials and profile information.
    Supports role-based access control.
    """
    __tablename__ = "users"
    
    # Primary Key
    user_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    
    # Credentials
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Profile
    full_name: Mapped[Optional[str]] = mapped_column(String(100))
    full_name_th: Mapped[Optional[str]] = mapped_column(String(100))
    employee_id: Mapped[Optional[str]] = mapped_column(String(20))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Organization
    entity_id: Mapped[Optional[str]] = mapped_column(String(40), ForeignKey("entity_master.entity_id"))
    department: Mapped[Optional[str]] = mapped_column(String(50))
    position: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Role & Permissions
    role: Mapped[str] = mapped_column(String(30), nullable=False, default="VIEWER")
    # TRADER, SUPERVISOR, RISK_OFFICER, BACK_OFFICE, ADMIN, VIEWER
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Login Tracking
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    password_changed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # API Key (for system integrations)
    api_key: Mapped[Optional[str]] = mapped_column(String(100))
    api_key_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Relationships
    entity = relationship("EntityMaster")
    
    # Indexes
    __table_args__ = (
        Index("ix_user_username", "username"),
        Index("ix_user_email", "email"),
        Index("ix_user_role", "role"),
    )
    
    def __repr__(self):
        return f"<User(id='{self.user_id}', username='{self.username}', role='{self.role}')>"


class UserSession(Base, TimestampMixin):
    """
    User Session Tracking
    
    Tracks active user sessions for security monitoring.
    """
    __tablename__ = "user_sessions"
    
    # Primary Key
    session_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    
    # User
    user_id: Mapped[str] = mapped_column(String(40), ForeignKey("users.user_id"), nullable=False)
    
    # Session Info
    ip_address: Mapped[Optional[str]] = mapped_column(String(50))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_activity_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    terminated_reason: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Relationships
    user = relationship("User")
    
    __table_args__ = (
        Index("ix_session_user", "user_id"),
        Index("ix_session_expires", "expires_at"),
    )


class AuditLog(Base):
    """
    Audit Log
    
    Tracks all significant actions for compliance.
    """
    __tablename__ = "audit_logs"
    
    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # User
    user_id: Mapped[Optional[str]] = mapped_column(String(40))
    username: Mapped[Optional[str]] = mapped_column(String(50))
    ip_address: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Action
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # CREATE, UPDATE, DELETE, APPROVE, LOGIN, etc.
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)  # BOND_TRADE, USER, etc.
    resource_id: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Details
    description: Mapped[Optional[str]] = mapped_column(Text)
    old_value: Mapped[Optional[str]] = mapped_column(Text)  # JSON of previous state
    new_value: Mapped[Optional[str]] = mapped_column(Text)  # JSON of new state
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="SUCCESS")  # SUCCESS, FAILED
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    
    __table_args__ = (
        Index("ix_audit_timestamp", "timestamp"),
        Index("ix_audit_user", "user_id"),
        Index("ix_audit_action", "action"),
        Index("ix_audit_resource", "resource_type", "resource_id"),
    )
    
    def __repr__(self):
        return f"<AuditLog(action='{self.action}', resource='{self.resource_type}', user='{self.username}')>"
