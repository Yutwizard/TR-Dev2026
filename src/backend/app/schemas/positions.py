"""
Treasury Management System - Position Schemas
===============================================

Pydantic schemas for position data.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field


class BondPositionResponse(BaseModel):
    """Schema for bond position response"""
    id: int
    position_date: date
    
    entity_id: str
    portfolio_id: str
    security_id: str
    isin: str
    
    # Quantities
    face_value: Decimal
    quantity: Decimal
    
    # Cost
    cost_price: Decimal
    cost_amount: Decimal
    
    # Market Value
    market_price: Optional[Decimal] = None
    market_value: Optional[Decimal] = None
    
    # Valuation
    accrued_interest: Decimal
    unrealized_pnl: Decimal
    
    # TFRS 9
    tfrs9_classification: str
    ecl_stage: int
    ecl_provision: Decimal
    
    # Collateral
    pledged_quantity: Decimal
    available_quantity: Decimal
    
    class Config:
        from_attributes = True


class CashPositionResponse(BaseModel):
    """Schema for cash position response"""
    id: int
    position_date: date
    
    entity_id: str
    currency: str
    account_type: str
    account_id: Optional[str] = None
    
    # Balances
    opening_balance: Decimal
    closing_balance: Decimal
    
    # Movements
    inflows: Decimal
    outflows: Decimal
    net_movement: Decimal
    
    # Projections
    projected_t1_inflow: Decimal
    projected_t1_outflow: Decimal
    projected_t2_inflow: Decimal
    projected_t2_outflow: Decimal
    
    class Config:
        from_attributes = True


class CollateralPositionResponse(BaseModel):
    """Schema for collateral position response"""
    id: int
    position_date: date
    
    entity_id: str
    repo_trade_id: str
    security_id: str
    isin: str
    
    is_pledged: bool
    counterparty_id: str
    
    # Quantities
    face_value: Decimal
    quantity: Decimal
    
    # Valuation
    market_price: Decimal
    market_value: Decimal
    haircut_pct: Decimal
    collateral_value: Decimal
    
    # Margin
    required_margin: Decimal
    excess_margin: Decimal
    margin_call_amount: Decimal
    
    status: str
    
    class Config:
        from_attributes = True


class PositionSummary(BaseModel):
    """Aggregated position summary"""
    position_date: date
    entity_id: str
    
    # Bond Summary
    total_bond_face_value: Decimal = Field(default=0)
    total_bond_market_value: Decimal = Field(default=0)
    total_bond_unrealized_pnl: Decimal = Field(default=0)
    
    # Cash Summary
    total_cash_balance: Decimal = Field(default=0)
    total_cash_inflows: Decimal = Field(default=0)
    total_cash_outflows: Decimal = Field(default=0)
    
    # Collateral Summary
    total_pledged_value: Decimal = Field(default=0)
    total_received_value: Decimal = Field(default=0)
    total_margin_calls: Decimal = Field(default=0)
    
    # Interbank Summary
    total_ib_lending: Decimal = Field(default=0)
    total_ib_borrowing: Decimal = Field(default=0)
    net_ib_position: Decimal = Field(default=0)
    
    # Repo Summary
    total_repo_borrowing: Decimal = Field(default=0)
    total_rrp_lending: Decimal = Field(default=0)
    net_repo_position: Decimal = Field(default=0)


class PositionFilter(BaseModel):
    """Filter parameters for positions"""
    position_date: Optional[date] = None
    entity_id: Optional[str] = None
    portfolio_id: Optional[str] = None
    security_id: Optional[str] = None
    isin: Optional[str] = None
    security_type: Optional[str] = None
    tfrs9_classification: Optional[str] = None


class LimitUtilizationResponse(BaseModel):
    """Schema for limit utilization response"""
    utilization_date: date
    limit_id: str
    limit_name: str
    limit_type: str
    
    limit_amount: Decimal
    utilized_amount: Decimal
    available_amount: Decimal
    utilization_pct: Decimal
    
    is_warning: bool
    is_breached: bool
    warning_threshold_pct: Decimal
    
    # Target info
    counterparty_name: Optional[str] = None
    security_name: Optional[str] = None
    portfolio_name: Optional[str] = None


class DailyPnLResponse(BaseModel):
    """Daily P&L response"""
    report_date: date
    entity_id: str
    
    # Trading P&L
    realized_pnl_bond: Decimal = 0
    unrealized_pnl_bond: Decimal = 0
    
    # Interest Income
    interest_income_ib: Decimal = 0
    interest_expense_ib: Decimal = 0
    net_interest_ib: Decimal = 0
    
    interest_income_repo: Decimal = 0
    interest_expense_repo: Decimal = 0
    net_interest_repo: Decimal = 0
    
    # Total
    total_pnl: Decimal = 0
    
    # Month-to-Date
    mtd_pnl: Decimal = 0
    
    # Year-to-Date
    ytd_pnl: Decimal = 0
