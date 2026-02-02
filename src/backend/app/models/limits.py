"""
Treasury Management System - Limit Models
==========================================

SQLAlchemy models for limit management:
- LimitDefinition: Limit rules and thresholds
- LimitUtilization: Real-time limit usage tracking
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Numeric, Boolean, Date, DateTime,
    Text, ForeignKey, Index, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, AuditMixin


class LimitDefinition(Base, TimestampMixin, AuditMixin):
    """
    Limit Definition
    
    Defines various types of limits for risk management:
    - Counterparty limits
    - Security limits
    - Portfolio limits
    - Tenor limits
    """
    __tablename__ = "limit_definitions"
    
    # Primary Key
    limit_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    
    # Limit Type
    limit_type: Mapped[str] = mapped_column(String(30), nullable=False)
    # COUNTERPARTY, SECURITY, PORTFOLIO, SECTOR, TENOR, CONCENTRATION
    
    limit_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Entity
    entity_id: Mapped[str] = mapped_column(String(40), ForeignKey("entity_master.entity_id"), nullable=False)
    
    # Target (what the limit applies to)
    counterparty_id: Mapped[Optional[str]] = mapped_column(String(40), ForeignKey("counterparty_master.counterparty_id"))
    security_id: Mapped[Optional[str]] = mapped_column(String(40), ForeignKey("security_master.security_id"))
    portfolio_id: Mapped[Optional[str]] = mapped_column(String(40), ForeignKey("portfolio_master.portfolio_id"))
    sector: Mapped[Optional[str]] = mapped_column(String(50))  # For sector limits
    
    # Limit Values
    currency: Mapped[str] = mapped_column(String(3), default="THB")
    limit_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    warning_threshold_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=80)  # 80%
    
    # Tenor Limits (optional)
    min_tenor_days: Mapped[Optional[int]] = mapped_column(Integer)
    max_tenor_days: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Validity
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date)
    
    # Approval
    status: Mapped[str] = mapped_column(String(20), default="PENDING")  # PENDING, APPROVED, EXPIRED
    approved_by: Mapped[Optional[str]] = mapped_column(String(40))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Relationships
    entity = relationship("EntityMaster")
    counterparty = relationship("CounterpartyMaster")
    security = relationship("SecurityMaster")
    portfolio = relationship("PortfolioMaster")
    
    # Indexes
    __table_args__ = (
        Index("ix_limit_type", "limit_type"),
        Index("ix_limit_counterparty", "counterparty_id"),
        Index("ix_limit_entity", "entity_id"),
        CheckConstraint("limit_amount > 0", name="ck_limit_amount_positive"),
        CheckConstraint("warning_threshold_pct > 0 AND warning_threshold_pct <= 100", 
                       name="ck_limit_warning_valid"),
    )
    
    def __repr__(self):
        return f"<LimitDefinition(id='{self.limit_id}', type='{self.limit_type}', amount={self.limit_amount})>"


class LimitUtilization(Base, TimestampMixin):
    """
    Limit Utilization
    
    Real-time tracking of limit usage.
    Updated on each trade booking.
    """
    __tablename__ = "limit_utilizations"
    
    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Date
    utilization_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Link to Limit
    limit_id: Mapped[str] = mapped_column(String(40), ForeignKey("limit_definitions.limit_id"), nullable=False)
    
    # Utilization
    utilized_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    available_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    utilization_pct: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=0)
    
    # Status
    is_warning: Mapped[bool] = mapped_column(Boolean, default=False)  # Above warning threshold
    is_breached: Mapped[bool] = mapped_column(Boolean, default=False)  # Above 100%
    
    # Last Update
    last_trade_ref: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Relationships
    limit = relationship("LimitDefinition")
    
    # Indexes and Constraints
    __table_args__ = (
        UniqueConstraint("utilization_date", "limit_id", name="uq_limit_utilization"),
        Index("ix_util_date", "utilization_date"),
        Index("ix_util_limit", "limit_id"),
        Index("ix_util_breach", "is_breached"),
    )
    
    def __repr__(self):
        return f"<LimitUtilization(date={self.utilization_date}, utilized={self.utilization_pct}%)>"


class LimitBreach(Base, TimestampMixin):
    """
    Limit Breach History
    
    Records all limit breach events for audit and reporting.
    """
    __tablename__ = "limit_breaches"
    
    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Breach Details
    breach_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    limit_id: Mapped[str] = mapped_column(String(40), ForeignKey("limit_definitions.limit_id"), nullable=False)
    
    # Amounts
    limit_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    utilized_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    breach_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    breach_pct: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    
    # Triggering Trade
    trade_ref: Mapped[Optional[str]] = mapped_column(String(50))
    trade_type: Mapped[Optional[str]] = mapped_column(String(30))
    trader_id: Mapped[Optional[str]] = mapped_column(String(40))
    
    # Resolution
    status: Mapped[str] = mapped_column(String(20), default="OPEN")  # OPEN, RESOLVED, ESCALATED
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text)
    resolved_by: Mapped[Optional[str]] = mapped_column(String(40))
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Relationships
    limit = relationship("LimitDefinition")
    
    __table_args__ = (
        Index("ix_breach_date", "breach_date"),
        Index("ix_breach_limit", "limit_id"),
        Index("ix_breach_status", "status"),
    )
    
    def __repr__(self):
        return f"<LimitBreach(limit='{self.limit_id}', breach_pct={self.breach_pct}%)>"
