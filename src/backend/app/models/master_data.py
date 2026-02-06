"""
Treasury Management System - Master Data Models
=================================================

SQLAlchemy models for master data tables:
- EntityMaster: Bank entities
- SecurityMaster: Bonds and securities
- CounterpartyMaster: Trading counterparties
- PortfolioMaster: Portfolio definitions
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import (
    Column, String, Integer, Numeric, Boolean, Date, DateTime,
    Text, ForeignKey, Index, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, AuditMixin


class EntityMaster(Base, TimestampMixin):
    """
    Bank/Entity Master Data
    
    Stores information about entities (banks, branches) that participate
    in treasury operations.
    """
    __tablename__ = "entity_master"
    
    entity_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    entity_name: Mapped[str] = mapped_column(String(255), nullable=False)
    entity_name_th: Mapped[Optional[str]] = mapped_column(String(255))
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # BANK, BRANCH, SUBSIDIARY
    parent_entity_id: Mapped[Optional[str]] = mapped_column(String(40), ForeignKey("entity_master.entity_id"))
    bot_code: Mapped[Optional[str]] = mapped_column(String(13))  # BOT 13-digit code
    swift_bic: Mapped[Optional[str]] = mapped_column(String(11))  # SWIFT BIC
    tax_id: Mapped[Optional[str]] = mapped_column(String(20))
    address: Mapped[Optional[str]] = mapped_column(Text)
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    children = relationship("EntityMaster", back_populates="parent")
    parent = relationship("EntityMaster", back_populates="children", remote_side=[entity_id])
    
    # Indexes
    __table_args__ = (
        Index("ix_entity_bot_code", "bot_code"),
        Index("ix_entity_swift", "swift_bic"),
    )
    
    def __repr__(self):
        return f"<EntityMaster(entity_id='{self.entity_id}', name='{self.entity_name}')>"


class SecurityMaster(Base, TimestampMixin, AuditMixin):
    """
    Security Master Data
    
    Stores bond and security information.
    Supports: T-Bill, T-Bond, BOT Bond, SOE Bond, Corporate Bond
    """
    __tablename__ = "security_master"
    
    security_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    isin: Mapped[str] = mapped_column(String(12), unique=True, nullable=False)
    symbol: Mapped[Optional[str]] = mapped_column(String(20))
    security_name: Mapped[str] = mapped_column(String(255), nullable=False)
    security_name_th: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Classification
    security_type: Mapped[str] = mapped_column(String(20), nullable=False)  # TBILL, TBOND, BOT, SOE, CORP
    issuer_type: Mapped[str] = mapped_column(String(20), nullable=False)  # GOV, SOE, CORP
    issuer_id: Mapped[Optional[str]] = mapped_column(String(40), ForeignKey("entity_master.entity_id"))
    
    # Terms
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    maturity_date: Mapped[date] = mapped_column(Date, nullable=False)
    coupon_rate: Mapped[Decimal] = mapped_column(Numeric(10, 6), default=0)  # Annual rate
    coupon_frequency: Mapped[int] = mapped_column(Integer, default=2)  # Times per year (2=semi-annual)
    day_count_convention: Mapped[str] = mapped_column(String(20), default="ACT/365")
    
    # Amounts
    face_value: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=100)  # Per unit
    outstanding_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    minimum_denomination: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=1000)
    
    # Ratings
    credit_rating: Mapped[Optional[str]] = mapped_column(String(10))  # AAA, AA+, etc.
    rating_agency: Mapped[Optional[str]] = mapped_column(String(50))  # TRIS, Fitch, etc.
    
    # Trading Info
    is_tradeable: Mapped[bool] = mapped_column(Boolean, default=True)
    is_repo_eligible: Mapped[bool] = mapped_column(Boolean, default=True)
    haircut_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)  # For repo collateral
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")  # ACTIVE, MATURED, CALLED
    
    # Relationships
    issuer = relationship("EntityMaster", foreign_keys=[issuer_id])
    market_data = relationship("ThaiBMAMarketData", back_populates="security")
    
    # Indexes and Constraints
    __table_args__ = (
        Index("ix_security_isin", "isin"),
        Index("ix_security_type", "security_type"),
        Index("ix_security_maturity", "maturity_date"),
        CheckConstraint("maturity_date > issue_date", name="ck_security_maturity_after_issue"),
        CheckConstraint("coupon_rate >= 0", name="ck_security_coupon_positive"),
    )
    
    @property
    def is_zero_coupon(self) -> bool:
        """Check if security is zero coupon (T-Bill)"""
        return self.coupon_rate == 0
    
    @property
    def tenor_days(self) -> int:
        """Calculate tenor in days"""
        return (self.maturity_date - self.issue_date).days
    
    def __repr__(self):
        return f"<SecurityMaster(isin='{self.isin}', name='{self.security_name}')>"


class CounterpartyMaster(Base, TimestampMixin, AuditMixin):
    """
    Counterparty Master Data
    
    Trading counterparties for bonds, interbank, and repo transactions.
    """
    __tablename__ = "counterparty_master"
    
    counterparty_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    counterparty_name: Mapped[str] = mapped_column(String(255), nullable=False)
    counterparty_name_th: Mapped[Optional[str]] = mapped_column(String(255))
    short_name: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Classification
    counterparty_type: Mapped[str] = mapped_column(String(30), nullable=False)  # BANK, BROKER, ASSET_MGR, INSURANCE, CORPORATE
    entity_id: Mapped[Optional[str]] = mapped_column(String(40), ForeignKey("entity_master.entity_id"))
    
    # Settlement Info
    bot_code: Mapped[Optional[str]] = mapped_column(String(13))
    swift_bic: Mapped[Optional[str]] = mapped_column(String(11))
    tsd_participant_code: Mapped[Optional[str]] = mapped_column(String(20))
    bahtnet_member_code: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Contact
    contact_person: Mapped[Optional[str]] = mapped_column(String(100))
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50))
    contact_email: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Limits
    has_isda: Mapped[bool] = mapped_column(Boolean, default=False)  # ISDA agreement
    has_gmra: Mapped[bool] = mapped_column(Boolean, default=False)  # GMRA for repos
    credit_limit: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")
    
    # Relationships
    entity = relationship("EntityMaster")
    
    # Indexes
    __table_args__ = (
        Index("ix_counterparty_type", "counterparty_type"),
        Index("ix_counterparty_bot_code", "bot_code"),
    )
    
    def __repr__(self):
        return f"<CounterpartyMaster(id='{self.counterparty_id}', name='{self.counterparty_name}')>"


class PortfolioMaster(Base, TimestampMixin):
    """
    Portfolio Master Data
    
    Defines trading portfolios/books for position tracking.
    """
    __tablename__ = "portfolio_master"
    
    portfolio_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    portfolio_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    portfolio_name: Mapped[str] = mapped_column(String(255), nullable=False)
    portfolio_name_th: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Classification
    portfolio_type: Mapped[str] = mapped_column(String(30), nullable=False)  # TRADING, BANKING, HTM, AFS, FVPL, FVOCI
    entity_id: Mapped[str] = mapped_column(String(40), ForeignKey("entity_master.entity_id"), nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(50))
    
    # TFRS 9 Classification
    tfrs9_classification: Mapped[str] = mapped_column(String(20), default="FVPL")  # FVPL, FVOCI, AC
    business_model: Mapped[str] = mapped_column(String(50), default="TRADING")  # TRADING, HOLD_COLLECT, HOLD_SELL
    
    # Accounting
    gl_account: Mapped[Optional[str]] = mapped_column(String(20))
    cost_center: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    entity = relationship("EntityMaster")
    
    def __repr__(self):
        return f"<PortfolioMaster(code='{self.portfolio_code}', name='{self.portfolio_name}')>"


class HaircutMatrix(Base, TimestampMixin):
    """
    Haircut Matrix for Repo Collateral
    
    BOT-standard haircut rates by security type and tenor.
    """
    __tablename__ = "haircut_matrix"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    security_type: Mapped[str] = mapped_column(String(20), nullable=False)  # GOV, SOE, CORP
    credit_rating: Mapped[Optional[str]] = mapped_column(String(10))
    tenor_from_days: Mapped[int] = mapped_column(Integer, default=0)
    tenor_to_days: Mapped[int] = mapped_column(Integer, default=99999)
    haircut_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date)
    
    __table_args__ = (
        Index("ix_haircut_security_type", "security_type", "credit_rating"),
        UniqueConstraint("security_type", "credit_rating", "tenor_from_days", "effective_date", 
                        name="uq_haircut_definition"),
    )
