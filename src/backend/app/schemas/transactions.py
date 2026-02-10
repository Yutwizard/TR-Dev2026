"""
Treasury Management System - Transaction Schemas
==================================================

Pydantic schemas for trade validation and serialization.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum


# =============================================================================
# Enums
# =============================================================================
class TradeSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class TradeStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PENDING_SETTLEMENT = "PENDING_SETTLEMENT"
    SETTLED = "SETTLED"
    CANCELLED = "CANCELLED"


class InterbankDealType(str, Enum):
    IB_LEND = "IB_LEND"
    IB_BORROW = "IB_BORROW"


class RepoType(str, Enum):
    REPO = "REPO"
    REVERSE_REPO = "REVERSE_REPO"


class RateType(str, Enum):
    FIXED = "FIXED"
    FLOAT = "FLOAT"


# =============================================================================
# Bond Trade Schemas
# =============================================================================
class BondTradeBase(BaseModel):
    """Base schema for bond trade"""
    counterparty_id: str
    portfolio_id: str
    security_id: str
    isin: str = Field(..., min_length=12, max_length=12)
    
    trade_side: TradeSide
    trade_date: date
    settlement_date: date
    
    face_value: Decimal = Field(..., gt=0)
    quantity: Decimal = Field(..., gt=0)
    clean_price: Decimal = Field(..., gt=0, le=200)  # Price per 100 face
    
    @field_validator('settlement_date')
    @classmethod
    def settlement_after_trade(cls, v, info):
        if 'trade_date' in info.data and v < info.data['trade_date']:
            raise ValueError('Settlement date cannot be before trade date')
        return v


class BondTradeCreate(BondTradeBase):
    """Schema for creating a bond trade"""
    entity_id: Optional[str] = None
    external_ref: Optional[str] = None
    yield_rate: Optional[Decimal] = None
    trader_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "counterparty_id": "CP001",
                "portfolio_id": "TRAD001",
                "security_id": "SEC001",
                "isin": "TH0623A3B702",
                "trade_side": "BUY",
                "trade_date": "2025-09-01",
                "settlement_date": "2025-09-03",
                "face_value": 10000000,
                "quantity": 10000,
                "clean_price": 99.5,
                "yield_rate": 3.65
            }
        }


class BondTradeUpdate(BaseModel):
    """Schema for updating a bond trade (limited fields)"""
    external_ref: Optional[str] = None
    trader_id: Optional[str] = None


class BondTradeResponse(BondTradeBase):
    """Schema for bond trade response"""
    trade_id: str
    trade_ref: str
    entity_id: str
    external_ref: Optional[str] = None
    thaibma_ref: Optional[str] = None
    
    # Calculated amounts
    dirty_price: Optional[Decimal] = None
    yield_rate: Optional[Decimal] = None
    principal_amount: Decimal
    accrued_interest: Decimal
    settlement_amount: Decimal
    
    # Fees
    commission: Decimal = 0
    broker_fee: Decimal = 0
    withholding_tax: Decimal = 0
    
    # Status
    status: TradeStatus
    is_thaibma_reported: bool
    settlement_status: str
    
    # Workflow
    trader_id: Optional[str] = None
    approver_id: Optional[str] = None
    approved_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BondTradeList(BaseModel):
    """Schema for listing bond trades"""
    items: List[BondTradeResponse]
    total: int


# =============================================================================
# Interbank Deal Schemas
# =============================================================================
from app.core.enums import InterbankDealType, RateType, TradeStatus, DayCountConvention

class InterbankDealBase(BaseModel):
    """Base schema for interbank deal"""
    counterparty_id: str
    portfolio_id: str
    
    deal_type: InterbankDealType
    
    start_date: date
    maturity_date: date
    
    principal_amount: Decimal = Field(..., gt=0)
    interest_rate: Decimal = Field(..., gt=0, le=100)
    rate_type: RateType = RateType.FIXED
    spread: Decimal = Field(default=0, ge=0)
    reference_rate: Optional[str] = None
    day_count_convention: DayCountConvention = DayCountConvention.ACT_365
    
    @field_validator('maturity_date')
    @classmethod
    def maturity_after_start(cls, v, info):
        if 'start_date' in info.data and v <= info.data['start_date']:
            raise ValueError('Maturity date must be after start date')
        return v


class InterbankDealCreate(InterbankDealBase):
    """Schema for creating an interbank deal"""
    entity_id: Optional[str] = None
    external_ref: Optional[str] = None
    trader_id: Optional[str] = None
    currency: str = "THB"
    
    class Config:
        json_schema_extra = {
            "example": {
                "counterparty_id": "CP_KBANK",
                "portfolio_id": "MM001",
                "deal_type": "PLACEMENT",
                "start_date": "2025-09-01",
                "maturity_date": "2025-09-08",
                "principal_amount": 100000000,
                "interest_rate": 2.25,
                "rate_type": "FIXED",
                "day_count_convention": "ACT/365"
            }
        }


class InterbankDealResponse(InterbankDealBase):
    """Schema for interbank deal response"""
    deal_id: str
    deal_ref: str
    entity_id: str
    external_ref: Optional[str] = None
    currency: str = "THB"
    deal_date: date
    
    # Calculated
    interest_amount: Decimal
    accrued_interest: Decimal
    maturity_amount: Decimal
    tenor_days: int
    
    # Status
    status: TradeStatus
    start_settlement_status: str
    maturity_settlement_status: str
    
    # Early Termination
    is_early_terminated: bool
    early_termination_date: Optional[date] = None
    
    # Workflow
    trader_id: Optional[str] = None
    approver_id: Optional[str] = None
    approved_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class InterbankDealList(BaseModel):
    """Schema for listing interbank deals"""
    items: List[InterbankDealResponse]
    total: int
    page: int
    size: int


# =============================================================================
# Repo Trade Schemas
# =============================================================================
class RepoTradeBase(BaseModel):
    """Base schema for repo trade"""
    counterparty_id: str
    portfolio_id: str
    
    trade_type: RepoType
    repo_type: str = "BILATERAL"
    
    trade_date: date
    start_date: date
    end_date: date
    
    near_leg_amount: Decimal = Field(..., gt=0)
    repo_rate: Decimal = Field(..., ge=0, le=100)
    rate_type: RateType = RateType.FIXED
    
    # Collateral
    collateral_security_id: Optional[str] = None
    collateral_isin: Optional[str] = None
    collateral_face_value: Optional[Decimal] = None
    haircut_pct: Decimal = Field(default=0, ge=0, le=100)
    
    @field_validator('end_date')
    @classmethod
    def end_after_start(cls, v, info):
        if 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError('End date cannot be before start date')
        return v


class RepoTradeCreate(RepoTradeBase):
    """Schema for creating a repo trade"""
    entity_id: Optional[str] = None
    external_ref: Optional[str] = None
    trader_id: Optional[str] = None
    margin_call_threshold: Decimal = Field(default=2, ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "counterparty_id": "CP_SCB",
                "portfolio_id": "REPO001",
                "trade_type": "REPO",
                "repo_type": "BILATERAL",
                "trade_date": "2025-09-01",
                "start_date": "2025-09-01",
                "end_date": "2025-09-08",
                "near_leg_amount": 100000000,
                "repo_rate": 2.15,
                "collateral_isin": "TH0623A3B702",
                "collateral_face_value": 105000000,
                "haircut_pct": 2.5
            }
        }


class RepoTradeResponse(RepoTradeBase):
    """Schema for repo trade response"""
    trade_id: str
    trade_ref: str
    entity_id: str
    external_ref: Optional[str] = None
    currency: str = "THB"
    
    # Calculated
    far_leg_amount: Decimal
    interest_amount: Decimal
    tenor_days: int
    collateral_market_value: Optional[Decimal] = None
    
    # Margin
    initial_margin: Optional[Decimal] = None
    current_margin: Optional[Decimal] = None
    margin_call_threshold: Decimal
    
    # Status
    status: TradeStatus
    near_leg_cash_status: str
    near_leg_collateral_status: str
    far_leg_cash_status: str
    far_leg_collateral_status: str
    
    # Early Termination
    is_early_terminated: bool
    
    # Workflow
    trader_id: Optional[str] = None
    approver_id: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    
    class Config:
        from_attributes = True
