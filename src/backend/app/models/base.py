"""
Treasury Management System - SQLAlchemy Base Classes
======================================================

Base classes and mixins for all database models.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    
    All models should inherit from this class.
    """
    pass


class TimestampMixin:
    """
    Mixin that adds created_at and updated_at timestamps.
    
    Usage:
        class MyModel(Base, TimestampMixin):
            __tablename__ = "my_table"
            ...
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=True
    )


class AuditMixin:
    """
    Mixin that adds audit trail fields.
    
    Tracks who created and modified records.
    """
    created_by: Mapped[Optional[str]] = mapped_column(
        String(40),
        nullable=True
    )
    updated_by: Mapped[Optional[str]] = mapped_column(
        String(40),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=True
    )


class SoftDeleteMixin:
    """
    Mixin for soft delete functionality.
    
    Instead of deleting records, mark them as deleted.
    """
    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        nullable=False
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )
    deleted_by: Mapped[Optional[str]] = mapped_column(
        String(40),
        nullable=True
    )
