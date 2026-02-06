"""
Treasury Management System - Market Data Models
=================================================

SQLAlchemy models for market data tables:
- ThaiBMA Market Data: Daily mark-to-market data from ThaiBMA
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Numeric, Date, DateTime,
    Index, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, AuditMixin


class ThaiBMAMarketData(Base, AuditMixin):
    """
    ThaiBMA Daily Mark-to-Market Data
    
    Stores daily EOD prices and yield data from ThaiBMA.
    Source: Mark2Market_YYYYMMDD.csv files from ThaiBMA portal.
    
    Key Fields:
    - clean_price: Primary field for MTM valuation
    - market_yield: Yield used for risk calculations
    - accrued_interest: AI percentage for dirty price calculation
    """
    __tablename__ = "thaibma_market_data"
    
    # Primary Key (Composite: security_id + data_date)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Data Date (the date this price data represents)
    data_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    
    # Security Reference
    security_id: Mapped[str] = mapped_column(
        String(40), 
        ForeignKey("security_master.security_id"),
        nullable=False,
        index=True
    )
    thaibma_symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    isin: Mapped[Optional[str]] = mapped_column(String(12))
    
    # Bond Characteristics (from ThaiBMA file)
    coupon_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 6))
    maturity_date: Mapped[Optional[date]] = mapped_column(Date)
    time_to_maturity_years: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 6))
    bond_type: Mapped[Optional[str]] = mapped_column(String(50))  # Government Bonds, SOE, etc.
    coupon_type: Mapped[Optional[str]] = mapped_column(String(20))  # Fixed, Floating
    
    # Ratings
    rating_tris: Mapped[Optional[str]] = mapped_column(String(10))
    rating_fitch: Mapped[Optional[str]] = mapped_column(String(10))
    
    # Trade Data
    last_trade_date: Mapped[Optional[date]] = mapped_column(Date)
    last_executed_yield: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6))
    
    # Quoted Data (Primary source for pricing)
    quoted_date: Mapped[Optional[date]] = mapped_column(Date)
    quoted_yield: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6))
    
    # Yield Range
    max_yield: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6))
    min_yield: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6))
    
    # Model/Market Yields
    model_yield: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6))
    static_spread_bp: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6))  # In basis points
    market_yield: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6))
    duration_metric: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6))
    
    # Price Data (CRITICAL for valuation)
    clean_price: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False)
    accrued_interest: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6))  # As percentage
    dirty_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6))  # Calculated: clean + AI
    
    # Risk Metrics
    modified_duration: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6))
    convexity: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 6))
    
    # Bond Details
    par_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), default=1000)
    currency: Mapped[str] = mapped_column(String(3), default="THB")
    registration_status: Mapped[Optional[str]] = mapped_column(String(20))
    index_ratio: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6))  # For inflation-linked bonds
    
    # Import Metadata
    import_batch_id: Mapped[Optional[str]] = mapped_column(String(50))
    import_file_name: Mapped[str] = mapped_column(String(100), nullable=False)
    import_timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    is_valid: Mapped[bool] = mapped_column(default=True)
    validation_errors: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Relationships
    security = relationship("SecurityMaster", back_populates="market_data")
    
    # Indexes and Constraints
    __table_args__ = (
        UniqueConstraint('security_id', 'data_date', name='uq_thaibma_security_date'),
        Index('ix_thaibma_data_date', 'data_date'),
        Index('ix_thaibma_symbol_date', 'thaibma_symbol', 'data_date'),
        Index('ix_thaibma_price_lookup', 'security_id', 'data_date', 'clean_price'),
    )
    
    def calculate_dirty_price(self) -> Decimal:
        """Calculate dirty price from clean price and accrued interest"""
        if self.accrued_interest:
            return self.clean_price + self.accrued_interest
        return self.clean_price
    
    def get_valuation_price(self) -> Decimal:
        """Return the price to use for position valuation"""
        return self.clean_price
    
    def __repr__(self):
        return f"<ThaiBMAMarketData(symbol='{self.thaibma_symbol}', date='{self.data_date}', price={self.clean_price})>"


class MarketDataImportLog(Base, AuditMixin):
    """
    Log of ThaiBMA Market Data Imports
    
    Tracks each import batch for audit and troubleshooting.
    """
    __tablename__ = "market_data_import_log"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Import Details
    batch_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    import_date: Mapped[date] = mapped_column(Date, nullable=False)
    file_name: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Statistics
    total_records: Mapped[int] = mapped_column(Integer, default=0)
    successful_records: Mapped[int] = mapped_column(Integer, default=0)
    failed_records: Mapped[int] = mapped_column(Integer, default=0)
    skipped_records: Mapped[int] = mapped_column(Integer, default=0)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="PENDING")  # PENDING, PROCESSING, COMPLETED, FAILED
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Error Details
    error_message: Mapped[Optional[str]] = mapped_column(String(1000))
    error_details: Mapped[Optional[str]] = mapped_column(String(2000))
    
    # Validation Summary
    price_movement_alerts: Mapped[int] = mapped_column(Integer, default=0)
    missing_securities: Mapped[int] = mapped_column(Integer, default=0)
    
    __table_args__ = (
        Index('ix_import_log_date', 'import_date'),
        Index('ix_import_log_status', 'status'),
    )
    
    def __repr__(self):
        return f"<MarketDataImportLog(batch='{self.batch_id}', date='{self.import_date}', status='{self.status}')>"
