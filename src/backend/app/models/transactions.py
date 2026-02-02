"""
Treasury Management System - Transaction Models
=================================================

SQLAlchemy models for transaction tables:
- BondTrade: Bond buy/sell transactions
- InterbankDeal: Interbank lending/borrowing
- RepoTrade: Repo and Reverse Repo transactions
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from enum import Enum
from sqlalchemy import (
    Column, String, Integer, Numeric, Boolean, Date, DateTime,
    Text, ForeignKey, Index, CheckConstraint, Enum as SQLEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, AuditMixin


# =============================================================================
# Enums
# =============================================================================
class TradeStatus(str, Enum):
    """Trade lifecycle status"""
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PENDING_SETTLEMENT = "PENDING_SETTLEMENT"
    PARTIALLY_SETTLED = "PARTIALLY_SETTLED"
    SETTLED = "SETTLED"
    CANCELLED = "CANCELLED"
    MATURED = "MATURED"


class TradeSide(str, Enum):
    """Trade direction"""
    BUY = "BUY"
    SELL = "SELL"
    LEND = "LEND"
    BORROW = "BORROW"


class DealType(str, Enum):
    """Type of deal"""
    OUTRIGHT = "OUTRIGHT"
    REPO = "REPO"
    REVERSE_REPO = "REVERSE_REPO"
    INTERBANK_LENDING = "IB_LEND"
    INTERBANK_BORROWING = "IB_BORROW"


# =============================================================================
# Bond Trade Model
# =============================================================================
class BondTrade(Base, AuditMixin):
    """
    Bond Trade Transaction
    
    Captures outright bond buy/sell transactions.
    Supports OTC trading with T+2 settlement.
    """
    __tablename__ = "bond_trades"
    
    # Primary Key
    trade_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    
    # Trade Reference
    trade_ref: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    external_ref: Mapped[Optional[str]] = mapped_column(String(50))  # Counterparty reference
    thaibma_ref: Mapped[Optional[str]] = mapped_column(String(50))  # ThaiBMA trade report ref
    
    # Party Info
    entity_id: Mapped[str] = mapped_column(String(40), ForeignKey("entity_master.entity_id"), nullable=False)
    counterparty_id: Mapped[str] = mapped_column(String(40), ForeignKey("counterparty_master.counterparty_id"), nullable=False)
    portfolio_id: Mapped[str] = mapped_column(String(40), ForeignKey("portfolio_master.portfolio_id"), nullable=False)
    
    # Security
    security_id: Mapped[str] = mapped_column(String(40), ForeignKey("security_master.security_id"), nullable=False)
    isin: Mapped[str] = mapped_column(String(12), nullable=False)
    
    # Trade Details
    trade_side: Mapped[str] = mapped_column(String(10), nullable=False)  # BUY, SELL
    trade_type: Mapped[str] = mapped_column(String(20), default="OUTRIGHT")  # OUTRIGHT, WHEN_ISSUED
    
    # Dates
    trade_date: Mapped[date] = mapped_column(Date, nullable=False)
    settlement_date: Mapped[date] = mapped_column(Date, nullable=False)
    value_date: Mapped[Optional[date]] = mapped_column(Date)  # For accrued interest calc
    
    # Quantities
    face_value: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)  # Number of units
    
    # Pricing
    clean_price: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False)  # Price per 100 face
    dirty_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6))
    yield_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 6))  # YTM
    
    # Amounts
    principal_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    accrued_interest: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    settlement_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    
    # Fees
    commission: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    broker_fee: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    withholding_tax: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    
    # Status
    status: Mapped[str] = mapped_column(String(30), default="DRAFT")
    is_thaibma_reported: Mapped[bool] = mapped_column(Boolean, default=False)
    thaibma_report_time: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Workflow
    trader_id: Mapped[Optional[str]] = mapped_column(String(40))
    approver_id: Mapped[Optional[str]] = mapped_column(String(40))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)
    
    # Settlement
    settlement_status: Mapped[str] = mapped_column(String(30), default="PENDING")
    settled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    settlement_ref: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Relationships
    entity = relationship("EntityMaster", foreign_keys=[entity_id])
    counterparty = relationship("CounterpartyMaster")
    portfolio = relationship("PortfolioMaster")
    security = relationship("SecurityMaster")
    
    # Indexes
    __table_args__ = (
        Index("ix_bond_trade_date", "trade_date"),
        Index("ix_bond_settlement_date", "settlement_date"),
        Index("ix_bond_status", "status"),
        Index("ix_bond_counterparty", "counterparty_id"),
        Index("ix_bond_security", "security_id"),
        CheckConstraint("settlement_date >= trade_date", name="ck_bond_settlement_after_trade"),
        CheckConstraint("face_value > 0", name="ck_bond_face_value_positive"),
    )
    
    def __repr__(self):
        return f"<BondTrade(id='{self.trade_id}', ref='{self.trade_ref}', side='{self.trade_side}')>"


# =============================================================================
# Interbank Deal Model
# =============================================================================
class InterbankDeal(Base, AuditMixin):
    """
    Interbank Lending/Borrowing Deal
    
    Tracks interbank placements and takings with interest calculations.
    Supports fixed and floating rate (THOR-based).
    """
    __tablename__ = "interbank_deals"
    
    # Primary Key
    deal_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    
    # Deal Reference
    deal_ref: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    external_ref: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Party Info
    entity_id: Mapped[str] = mapped_column(String(40), ForeignKey("entity_master.entity_id"), nullable=False)
    counterparty_id: Mapped[str] = mapped_column(String(40), ForeignKey("counterparty_master.counterparty_id"), nullable=False)
    portfolio_id: Mapped[str] = mapped_column(String(40), ForeignKey("portfolio_master.portfolio_id"), nullable=False)
    
    # Deal Type
    deal_type: Mapped[str] = mapped_column(String(20), nullable=False)  # IB_LEND, IB_BORROW
    
    # Dates
    deal_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    maturity_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Principal
    currency: Mapped[str] = mapped_column(String(3), default="THB")
    principal_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    
    # Interest Rate
    rate_type: Mapped[str] = mapped_column(String(10), default="FIXED")  # FIXED, FLOAT
    interest_rate: Mapped[Decimal] = mapped_column(Numeric(10, 6), nullable=False)  # Annual rate
    spread: Mapped[Decimal] = mapped_column(Numeric(10, 6), default=0)  # For floating rate
    reference_rate: Mapped[Optional[str]] = mapped_column(String(20))  # THOR, THBFIX
    day_count_convention: Mapped[str] = mapped_column(String(20), default="ACT/365")
    
    # Interest Calculation
    interest_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    accrued_interest: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    
    # Maturity
    maturity_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)  # Principal + Interest
    
    # Status
    status: Mapped[str] = mapped_column(String(30), default="DRAFT")
    
    # Workflow
    trader_id: Mapped[Optional[str]] = mapped_column(String(40))
    approver_id: Mapped[Optional[str]] = mapped_column(String(40))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Settlement - Start Leg
    start_settlement_status: Mapped[str] = mapped_column(String(30), default="PENDING")
    start_settled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    start_bahtnet_ref: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Settlement - Maturity Leg
    maturity_settlement_status: Mapped[str] = mapped_column(String(30), default="PENDING")
    maturity_settled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    maturity_bahtnet_ref: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Early Termination
    is_early_terminated: Mapped[bool] = mapped_column(Boolean, default=False)
    early_termination_date: Mapped[Optional[date]] = mapped_column(Date)
    early_termination_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    
    # Relationships
    entity = relationship("EntityMaster")
    counterparty = relationship("CounterpartyMaster")
    portfolio = relationship("PortfolioMaster")
    
    # Indexes
    __table_args__ = (
        Index("ix_ib_deal_date", "deal_date"),
        Index("ix_ib_maturity_date", "maturity_date"),
        Index("ix_ib_status", "status"),
        Index("ix_ib_counterparty", "counterparty_id"),
        Index("ix_ib_deal_type", "deal_type"),
        CheckConstraint("maturity_date > start_date", name="ck_ib_maturity_after_start"),
        CheckConstraint("principal_amount > 0", name="ck_ib_principal_positive"),
    )
    
    @property
    def tenor_days(self) -> int:
        """Calculate tenor in days"""
        return (self.maturity_date - self.start_date).days
    
    @property
    def is_lending(self) -> bool:
        """Check if this is a lending (placement) deal"""
        return self.deal_type == "IB_LEND"
    
    def __repr__(self):
        return f"<InterbankDeal(id='{self.deal_id}', type='{self.deal_type}', amount={self.principal_amount})>"


# =============================================================================
# Repo Trade Model
# =============================================================================
class RepoTrade(Base, AuditMixin):
    """
    Repo / Reverse Repo Trade
    
    Repo: Bank borrows cash, posts collateral
    Reverse Repo: Bank lends cash, receives collateral
    """
    __tablename__ = "repo_trades"
    
    # Primary Key
    trade_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    
    # Trade Reference
    trade_ref: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    external_ref: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Party Info
    entity_id: Mapped[str] = mapped_column(String(40), ForeignKey("entity_master.entity_id"), nullable=False)
    counterparty_id: Mapped[str] = mapped_column(String(40), ForeignKey("counterparty_master.counterparty_id"), nullable=False)
    portfolio_id: Mapped[str] = mapped_column(String(40), ForeignKey("portfolio_master.portfolio_id"), nullable=False)
    
    # Trade Type
    trade_type: Mapped[str] = mapped_column(String(20), nullable=False)  # REPO, REVERSE_REPO
    repo_type: Mapped[str] = mapped_column(String(20), default="BILATERAL")  # BILATERAL, BOT_BRP
    
    # Dates
    trade_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)  # Near leg
    end_date: Mapped[date] = mapped_column(Date, nullable=False)  # Far leg
    
    # Cash Leg
    currency: Mapped[str] = mapped_column(String(3), default="THB")
    near_leg_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    far_leg_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    
    # Rate
    repo_rate: Mapped[Decimal] = mapped_column(Numeric(10, 6), nullable=False)
    rate_type: Mapped[str] = mapped_column(String(10), default="FIXED")
    day_count_convention: Mapped[str] = mapped_column(String(20), default="ACT/365")
    
    # Interest
    interest_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    
    # Collateral Summary
    collateral_security_id: Mapped[Optional[str]] = mapped_column(String(40), ForeignKey("security_master.security_id"))
    collateral_isin: Mapped[Optional[str]] = mapped_column(String(12))
    collateral_face_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    collateral_market_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    haircut_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    
    # Margin
    initial_margin: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    current_margin: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    margin_call_threshold: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=2)  # 2% threshold
    
    # Status
    status: Mapped[str] = mapped_column(String(30), default="DRAFT")
    
    # Workflow
    trader_id: Mapped[Optional[str]] = mapped_column(String(40))
    approver_id: Mapped[Optional[str]] = mapped_column(String(40))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Settlement - Near Leg
    near_leg_cash_status: Mapped[str] = mapped_column(String(30), default="PENDING")
    near_leg_collateral_status: Mapped[str] = mapped_column(String(30), default="PENDING")
    near_leg_settled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Settlement - Far Leg
    far_leg_cash_status: Mapped[str] = mapped_column(String(30), default="PENDING")
    far_leg_collateral_status: Mapped[str] = mapped_column(String(30), default="PENDING")
    far_leg_settled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Early Termination
    is_early_terminated: Mapped[bool] = mapped_column(Boolean, default=False)
    early_termination_date: Mapped[Optional[date]] = mapped_column(Date)
    
    # Relationships
    entity = relationship("EntityMaster")
    counterparty = relationship("CounterpartyMaster")
    portfolio = relationship("PortfolioMaster")
    collateral_security = relationship("SecurityMaster")
    
    # Indexes
    __table_args__ = (
        Index("ix_repo_trade_date", "trade_date"),
        Index("ix_repo_start_date", "start_date"),
        Index("ix_repo_end_date", "end_date"),
        Index("ix_repo_status", "status"),
        Index("ix_repo_type", "trade_type"),
        CheckConstraint("end_date >= start_date", name="ck_repo_end_after_start"),
        CheckConstraint("near_leg_amount > 0", name="ck_repo_amount_positive"),
    )
    
    @property
    def tenor_days(self) -> int:
        """Calculate tenor in days"""
        return (self.end_date - self.start_date).days
    
    @property
    def is_repo(self) -> bool:
        """Check if this is a repo (we borrow cash)"""
        return self.trade_type == "REPO"
    
    def __repr__(self):
        return f"<RepoTrade(id='{self.trade_id}', type='{self.trade_type}', amount={self.near_leg_amount})>"
