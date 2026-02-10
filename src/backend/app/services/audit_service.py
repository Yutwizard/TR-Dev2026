"""
Treasury Management System - Audit Service
============================================

High-level service for recording audit trail events.

Provides simple methods to log common actions without
needing to construct AuditLog manually.

Usage:
    from app.services.audit_service import AuditService
    
    audit = AuditService(db)
    
    # Log a trade creation
    audit.log_created(
        entity_type=EntityType.BOND_TRADE,
        entity_id="BND20260210001",
        user_id="TRADER01",
        new_values={"status": "PENDING_APPROVAL", "amount": 10000000}
    )
    
    # Log an approval
    audit.log_status_change(
        entity_type=EntityType.BOND_TRADE,
        entity_id="BND20260210001",
        user_id="SUP001",
        old_status="PENDING_APPROVAL",
        new_status="APPROVED",
        notes="Four-eyes approval"
    )
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import uuid4
import logging

from sqlalchemy.orm import Session

from app.models.audit import TransactionAuditLog
from app.core.enums import AuditAction, EntityType

logger = logging.getLogger(__name__)


class AuditService:
    """
    Service for creating audit trail entries.
    
    All methods add TransactionAuditLog entries to the session but do NOT commit.
    The caller is responsible for committing the transaction.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def _log(
        self,
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
    ) -> TransactionAuditLog:
        """Internal method to create and add an audit entry."""
        entry = TransactionAuditLog.create(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            user_id=user_id,
            old_values=old_values,
            new_values=new_values,
            user_role=user_role,
            ip_address=ip_address,
            notes=notes,
            correlation_id=correlation_id,
        )
        self.db.add(entry)
        
        logger.info(
            f"AUDIT: {action} | {entity_type}:{entity_id} | user={user_id}"
        )
        
        return entry
    
    # =========================================================================
    # Common Action Shortcuts
    # =========================================================================
    
    def log_created(
        self,
        entity_type: str,
        entity_id: str,
        user_id: str,
        new_values: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AuditLog:
        """Log entity creation."""
        return self._log(
            entity_type=entity_type,
            entity_id=entity_id,
            action=AuditAction.CREATED,
            user_id=user_id,
            new_values=new_values,
            **kwargs,
        )
    
    def log_status_change(
        self,
        entity_type: str,
        entity_id: str,
        user_id: str,
        old_status: str,
        new_status: str,
        notes: Optional[str] = None,
        **kwargs
    ) -> AuditLog:
        """Log a status transition."""
        return self._log(
            entity_type=entity_type,
            entity_id=entity_id,
            action=AuditAction.STATUS_CHANGE,
            user_id=user_id,
            old_values={"status": old_status},
            new_values={"status": new_status},
            notes=notes,
            **kwargs,
        )
    
    def log_approved(
        self,
        entity_type: str,
        entity_id: str,
        approver_id: str,
        notes: Optional[str] = None,
        **kwargs
    ) -> AuditLog:
        """Log an approval action."""
        return self._log(
            entity_type=entity_type,
            entity_id=entity_id,
            action=AuditAction.APPROVED,
            user_id=approver_id,
            new_values={"approver_id": approver_id, "approved_at": datetime.utcnow().isoformat()},
            notes=notes,
            **kwargs,
        )
    
    def log_rejected(
        self,
        entity_type: str,
        entity_id: str,
        rejector_id: str,
        reason: Optional[str] = None,
        **kwargs
    ) -> AuditLog:
        """Log a rejection action."""
        return self._log(
            entity_type=entity_type,
            entity_id=entity_id,
            action=AuditAction.REJECTED,
            user_id=rejector_id,
            notes=reason,
            **kwargs,
        )
    
    def log_cancelled(
        self,
        entity_type: str,
        entity_id: str,
        user_id: str,
        reason: Optional[str] = None,
        **kwargs
    ) -> AuditLog:
        """Log a cancellation action."""
        return self._log(
            entity_type=entity_type,
            entity_id=entity_id,
            action=AuditAction.CANCELLED,
            user_id=user_id,
            notes=reason,
            **kwargs,
        )
    
    def log_settled(
        self,
        entity_type: str,
        entity_id: str,
        user_id: str,
        settlement_ref: Optional[str] = None,
        **kwargs
    ) -> AuditLog:
        """Log a settlement action."""
        return self._log(
            entity_type=entity_type,
            entity_id=entity_id,
            action=AuditAction.SETTLED,
            user_id=user_id,
            new_values={"settlement_ref": settlement_ref},
            **kwargs,
        )
    
    def log_limit_check(
        self,
        entity_type: str,
        entity_id: str,
        user_id: str,
        limit_details: Dict[str, Any],
        **kwargs
    ) -> AuditLog:
        """Log a limit check result."""
        return self._log(
            entity_type=entity_type,
            entity_id=entity_id,
            action=AuditAction.LIMIT_CHECK,
            user_id=user_id,
            new_values=limit_details,
            **kwargs,
        )
    
    def log_thaibma_reported(
        self,
        entity_id: str,
        user_id: str,
        thaibma_ref: Optional[str] = None,
        **kwargs
    ) -> AuditLog:
        """Log ThaiBMA trade reporting."""
        return self._log(
            entity_type=EntityType.BOND_TRADE,
            entity_id=entity_id,
            action=AuditAction.THAIBMA_REPORTED,
            user_id=user_id,
            new_values={"thaibma_ref": thaibma_ref, "reported_at": datetime.utcnow().isoformat()},
            **kwargs,
        )
    
    def log_margin_call(
        self,
        entity_id: str,
        user_id: str,
        margin_details: Dict[str, Any],
        **kwargs
    ) -> AuditLog:
        """Log a margin call event."""
        return self._log(
            entity_type=EntityType.REPO_TRADE,
            entity_id=entity_id,
            action=AuditAction.MARGIN_CALL,
            user_id=user_id,
            new_values=margin_details,
            **kwargs,
        )
