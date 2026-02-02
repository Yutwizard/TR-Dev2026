"""
Treasury Management System - Position Models
==============================================

SQLAlchemy models for position tracking:
- BondPosition: Bond holdings
- CashPosition: Cash balances
- CollateralPosition: Collateral allocations
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Numeric, Boolean, Date, DateTime,
    Text, ForeignKey, Index, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class BondPosition(Base, TimestampMixin):
    """
    Bond Position
    
    Tracks bond holdings aggregated by portfolio and security.
    Updated after each trade settlement.
    """
    __tablename__ = "bond_positions"
    
    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Position Date
    position_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Keys
    entity_id: Mapped[str] = mapped_column(String(40), ForeignKey("entity_master.entity_id"), nullable=False)
    portfolio_id: Mapped[str] = mapped_column(String(40), ForeignKey("portfolio_master.portfolio_id"), nullable=False)
    security_id: Mapped[str] = mapped_column(String(40), ForeignKey("security_master.security_id"), nullable=False)
    isin: Mapped[str] = mapped_column(String(12), nullable=False)
    
    # Quantities
    face_value: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    
    # Cost
    cost_price: Mapped[Decimal] = mapped_column(Numeric(12, 6), default=0)  # Weighted average
    cost_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    
    # Market Value
    market_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6))
    market_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    
    # Valuation
    accrued_interest: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    unrealized_pnl: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    
    # TFRS 9
    tfrs9_classification: Mapped[str] = mapped_column(String(20), default="FVPL")
    ecl_stage: Mapped[int] = mapped_column(Integer, default=1)  # 1, 2, or 3
    ecl_provision: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    
    # Collateral Status
    pledged_quantity: Mapped[Decimal] = mapped_column(Numeric(20, 6), default=0)
    available_quantity: Mapped[Decimal] = mapped_column(Numeric(20, 6), default=0)
    
    # Relationships
    entity = relationship("EntityMaster")
    portfolio = relationship("PortfolioMaster")
    security = relationship("SecurityMaster")
    
    # Indexes and Constraints
    __table_args__ = (
        UniqueConstraint("position_date", "portfolio_id", "security_id", name="uq_bond_position"),
        Index("ix_bond_pos_date", "position_date"),
        Index("ix_bond_pos_portfolio", "portfolio_id"),
        Index("ix_bond_pos_security", "security_id"),
    )
    
    def __repr__(self):
        return f"<BondPosition(date={self.position_date}, isin='{self.isin}', face_value={self.face_value})>"


class CashPosition(Base, TimestampMixin):
    """
    Cash Position
    
    Tracks cash balances by entity, currency, and account.
    Includes projected flows for liquidity management.
    """
    __tablename__ = "cash_positions"
    
    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Position Date
    position_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Keys
    entity_id: Mapped[str] = mapped_column(String(40), ForeignKey("entity_master.entity_id"), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="THB")
    account_type: Mapped[str] = mapped_column(String(30), default="NOSTRO")  # NOSTRO, BAHTNET, TSD
    account_id: Mapped[Optional[str]] = mapped_column(String(40))
    
    # Balances
    opening_balance: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    closing_balance: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    
    # Daily Movements
    inflows: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    outflows: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    
    # Projected (next 5 days)
    projected_t1_inflow: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    projected_t1_outflow: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    projected_t2_inflow: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    projected_t2_outflow: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    
    # Relationships
    entity = relationship("EntityMaster")
    
    # Indexes and Constraints
    __table_args__ = (
        UniqueConstraint("position_date", "entity_id", "currency", "account_type", name="uq_cash_position"),
        Index("ix_cash_pos_date", "position_date"),
        Index("ix_cash_pos_entity", "entity_id"),
    )
    
    @property
    def net_movement(self) -> Decimal:
        """Calculate net cash movement for the day"""
        return self.inflows - self.outflows
    
    def __repr__(self):
        return f"<CashPosition(date={self.position_date}, currency='{self.currency}', balance={self.closing_balance})>"


class CollateralPosition(Base, TimestampMixin):
    """
    Collateral Position
    
    Tracks securities pledged as collateral for repos.
    """
    __tablename__ = "collateral_positions"
    
    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Position Date
    position_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Keys
    entity_id: Mapped[str] = mapped_column(String(40), ForeignKey("entity_master.entity_id"), nullable=False)
    repo_trade_id: Mapped[str] = mapped_column(String(40), ForeignKey("repo_trades.trade_id"), nullable=False)
    security_id: Mapped[str] = mapped_column(String(40), ForeignKey("security_master.security_id"), nullable=False)
    isin: Mapped[str] = mapped_column(String(12), nullable=False)
    
    # Pledging Direction
    is_pledged: Mapped[bool] = mapped_column(Boolean, default=True)  # True = we pledged, False = we received
    counterparty_id: Mapped[str] = mapped_column(String(40), ForeignKey("counterparty_master.counterparty_id"), nullable=False)
    
    # Quantities
    face_value: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    
    # Valuation
    market_price: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False)
    market_value: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    haircut_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    collateral_value: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)  # After haircut
    
    # Margin
    required_margin: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    excess_margin: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    margin_call_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")  # ACTIVE, RETURNED, SUBSTITUTED
    
    # Relationships
    entity = relationship("EntityMaster")
    repo_trade = relationship("RepoTrade")
    security = relationship("SecurityMaster")
    counterparty = relationship("CounterpartyMaster")
    
    # Indexes
    __table_args__ = (
        Index("ix_collateral_pos_date", "position_date"),
        Index("ix_collateral_repo", "repo_trade_id"),
        Index("ix_collateral_security", "security_id"),
    )
    
    def __repr__(self):
        return f"<CollateralPosition(repo='{self.repo_trade_id}', isin='{self.isin}', value={self.collateral_value})>"


class NetPosition(Base, TimestampMixin):
    """
    Net Position (Aggregated)
    
    Daily aggregate position by security for regulatory reporting.
    """
    __tablename__ = "net_positions"
    
    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Position Date
    position_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Keys
    entity_id: Mapped[str] = mapped_column(String(40), ForeignKey("entity_master.entity_id"), nullable=False)
    security_id: Mapped[str] = mapped_column(String(40), ForeignKey("security_master.security_id"), nullable=False)
    isin: Mapped[str] = mapped_column(String(12), nullable=False)
    
    # Position
    long_position: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    short_position: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    net_position: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    
    # Value
    market_value: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    
    # PnL
    realized_pnl_today: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    unrealized_pnl: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    
    # Relationships
    entity = relationship("EntityMaster")
    security = relationship("SecurityMaster")
    
    __table_args__ = (
        UniqueConstraint("position_date", "entity_id", "security_id", name="uq_net_position"),
        Index("ix_net_pos_date", "position_date"),
    )
