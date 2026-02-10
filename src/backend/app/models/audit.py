"""
Treasury Management System - Audit Log Model
==============================================

Immutable audit trail for all significant system actions.

This is a regulatory requirement for treasury systems:
- Every deal creation, approval, rejection, cancellation
- Status changes
- Limit checks
- Settlement events
- ThaiBMA reporting

The audit log is append-only. Records are NEVER updated or deleted.

Usage:
    from app.models.audit import AuditLog
    from app.core.enums import AuditAction, EntityType
    
    audit = AuditLog.create(
        entity_type=EntityType.BOND_TRADE,
        entity_id="BND20260210001",
        action=AuditAction.APPROVED,
        user_id="USER001",
        old_values={"status": "PENDING_APPROVAL"},
        new_values={"status": "APPROVED", "approver_id": "USER002"},
        notes="Four-eyes approval completed"
    )
    db.add(audit)
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import uuid4
from sqlalchemy import (
    Column, String, Integer, DateTime, Text, Index, JSON
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TransactionAuditLog(Base):
    """
    Immutable audit trail for financial transactions.
    
    Separate from the general AuditLog in users.py (which handles login,
    system events). This table is specifically for:
    - Trade lifecycle events (create, approve, reject, cancel, settle)
    - Limit checks
    - ThaiBMA reporting
    - Margin calls
    
    One row per action. Records are NEVER updated or deleted.
    """
    __tablename__ = "transaction_audit_log"
    
    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # What was affected
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)   # e.g., "BondTrade"
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False)    # e.g., trade ref
    
    # What happened
    action: Mapped[str] = mapped_column(String(50), nullable=False)        # e.g., "APPROVED"
    
    # State before and after (JSON)
    old_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    new_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Who did it
    user_id: Mapped[str] = mapped_column(String(40), nullable=False)
    user_role: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    
    # Context
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # When (immutable)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        nullable=False
    )
    
    # Correlation ID (for grouping related actions)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Indexes for efficient querying
    __table_args__ = (
        Index("ix_txn_audit_entity", "entity_type", "entity_id"),
        Index("ix_txn_audit_user", "user_id"),
        Index("ix_txn_audit_action", "action"),
        Index("ix_txn_audit_timestamp", "timestamp"),
        Index("ix_txn_audit_correlation", "correlation_id"),
    )
    
    @classmethod
    def create(
        cls,
        entity_type: str,
        entity_id: str,
        action: str,
        user_id: str,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        user_role: Optional[str] = None,
        ip_address: Optional[str] = None,
        notes: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> "TransactionAuditLog":
        """
        Factory method to create an audit log entry.
        
        Returns:
            TransactionAuditLog instance (not yet added to session)
        """
        return cls(
            entity_type=entity_type if isinstance(entity_type, str) else entity_type.value,
            entity_id=entity_id,
            action=action if isinstance(action, str) else action.value,
            user_id=user_id,
            old_values=old_values,
            new_values=new_values,
            user_role=user_role,
            ip_address=ip_address,
            notes=notes,
            correlation_id=correlation_id or uuid4().hex[:12],
            timestamp=datetime.utcnow(),
        )
    
    def __repr__(self):
        return (
            f"<TransactionAuditLog(id={self.id}, entity={self.entity_type}:{self.entity_id}, "
            f"action={self.action}, user={self.user_id}, time={self.timestamp})>"
        )
