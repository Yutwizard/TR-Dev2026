"""
Treasury Management System - Bond Trades Router
=================================================

API endpoints for bond trade management.
"""

from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import uuid4

from app.core.auth import get_current_active_user, UserInToken, require_roles
from app.core.permissions import require_permission, Permission, validate_four_eyes
from app.schemas.transactions import (
    BondTradeCreate, BondTradeUpdate, BondTradeResponse, BondTradeList,
    TradeSide, TradeStatus
)
from app.schemas.common import APIResponse, ApprovalRequest
from app.services.calendar_service import calculate_settlement_date, is_thai_business_day


router = APIRouter()


# =============================================================================
# Mock Trade Data
# =============================================================================
MOCK_TRADES = [
    {
        "trade_id": "TRD001",
        "trade_ref": "BND20250901001",
        "entity_id": "ENTITY001",
        "counterparty_id": "CP_KBANK",
        "portfolio_id": "TRAD001",
        "security_id": "SEC001",
        "isin": "TH0623A3B702",
        "trade_side": "BUY",
        "trade_type": "OUTRIGHT",
        "trade_date": date(2025, 9, 1),
        "settlement_date": date(2025, 9, 3),
        "face_value": Decimal("10000000"),
        "quantity": Decimal("10000"),
        "clean_price": Decimal("99.50"),
        "dirty_price": Decimal("100.25"),
        "yield_rate": Decimal("3.65"),
        "principal_amount": Decimal("9950000"),
        "accrued_interest": Decimal("75000"),
        "settlement_amount": Decimal("10025000"),
        "commission": Decimal("0"),
        "broker_fee": Decimal("0"),
        "withholding_tax": Decimal("0"),
        "status": "APPROVED",
        "is_thaibma_reported": True,
        "thaibma_ref": "TBMA20250901001",
        "settlement_status": "PENDING",
        "trader_id": "TRADER001",
        "approver_id": "SUP001",
        "approved_at": datetime(2025, 9, 1, 10, 30),
        "created_at": datetime(2025, 9, 1, 10, 0),
        "updated_at": datetime(2025, 9, 1, 10, 30),
    },
    {
        "trade_id": "TRD002",
        "trade_ref": "BND20250901002",
        "entity_id": "ENTITY001",
        "counterparty_id": "CP_SCB",
        "portfolio_id": "TRAD001",
        "security_id": "SEC002",
        "isin": "TH0623A3C701",
        "trade_side": "SELL",
        "trade_type": "OUTRIGHT",
        "trade_date": date(2025, 9, 1),
        "settlement_date": date(2025, 9, 3),
        "face_value": Decimal("5000000"),
        "quantity": Decimal("5000"),
        "clean_price": Decimal("101.25"),
        "dirty_price": Decimal("101.85"),
        "yield_rate": Decimal("2.45"),
        "principal_amount": Decimal("5062500"),
        "accrued_interest": Decimal("30000"),
        "settlement_amount": Decimal("5092500"),
        "commission": Decimal("0"),
        "broker_fee": Decimal("0"),
        "withholding_tax": Decimal("0"),
        "status": "PENDING_APPROVAL",
        "is_thaibma_reported": False,
        "thaibma_ref": None,
        "settlement_status": "PENDING",
        "trader_id": "TRADER001",
        "approver_id": None,
        "approved_at": None,
        "created_at": datetime(2025, 9, 1, 11, 0),
        "updated_at": None,
    },
]


def generate_trade_ref() -> str:
    """Generate a unique trade reference"""
    today = datetime.now().strftime("%Y%m%d")
    seq = len(MOCK_TRADES) + 1
    return f"BND{today}{seq:03d}"


def calculate_amounts(trade_data: dict) -> dict:
    """Calculate trade amounts"""
    face_value = Decimal(str(trade_data["face_value"]))
    clean_price = Decimal(str(trade_data["clean_price"]))
    
    # Principal = Face Value * Clean Price / 100
    principal = face_value * clean_price / Decimal("100")
    
    # Mock accrued interest calculation (should use actual calendar)
    accrued = face_value * Decimal("0.03625") * Decimal("75") / Decimal("365")
    
    # Dirty price = Clean + Accrued
    dirty = clean_price + (accrued / face_value * Decimal("100"))
    
    # Settlement = Principal + Accrued
    settlement = principal + accrued
    
    return {
        "principal_amount": round(principal, 2),
        "accrued_interest": round(accrued, 2),
        "dirty_price": round(dirty, 6),
        "settlement_amount": round(settlement, 2),
    }


# =============================================================================
# Endpoints
# =============================================================================
@router.get("", response_model=BondTradeList)
async def list_bond_trades(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    trade_side: Optional[str] = None,
    counterparty_id: Optional[str] = None,
    portfolio_id: Optional[str] = None,
    trade_date_from: Optional[date] = None,
    trade_date_to: Optional[date] = None,
    settlement_date_from: Optional[date] = None,
    settlement_date_to: Optional[date] = None,
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    List bond trades with filtering and pagination.
    """
    filtered = MOCK_TRADES.copy()
    
    if status:
        filtered = [t for t in filtered if t["status"] == status]
    if trade_side:
        filtered = [t for t in filtered if t["trade_side"] == trade_side]
    if counterparty_id:
        filtered = [t for t in filtered if t["counterparty_id"] == counterparty_id]
    if portfolio_id:
        filtered = [t for t in filtered if t["portfolio_id"] == portfolio_id]
    if trade_date_from:
        filtered = [t for t in filtered if t["trade_date"] >= trade_date_from]
    if trade_date_to:
        filtered = [t for t in filtered if t["trade_date"] <= trade_date_to]
    if settlement_date_from:
        filtered = [t for t in filtered if t["settlement_date"] >= settlement_date_from]
    if settlement_date_to:
        filtered = [t for t in filtered if t["settlement_date"] <= settlement_date_to]
    
    total = len(filtered)
    start = (page - 1) * page_size
    items = filtered[start:start + page_size]
    
    return BondTradeList(items=items, total=total)


@router.get("/pending-approval", response_model=BondTradeList)
async def list_pending_approval(
    current_user: UserInToken = Depends(
        require_permission(Permission.APPROVE_TRADE)
    ),
):
    """
    List trades pending approval.
    
    Requires APPROVE_TRADE permission.
    """
    pending = [t for t in MOCK_TRADES if t["status"] == "PENDING_APPROVAL"]
    return BondTradeList(items=pending, total=len(pending))


@router.get("/{trade_id}", response_model=BondTradeResponse)
async def get_bond_trade(
    trade_id: str,
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    Get a specific bond trade by ID.
    """
    for trade in MOCK_TRADES:
        if trade["trade_id"] == trade_id:
            return trade
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Trade with ID '{trade_id}' not found"
    )


@router.post("", response_model=BondTradeResponse, status_code=status.HTTP_201_CREATED)
async def create_bond_trade(
    trade: BondTradeCreate,
    current_user: UserInToken = Depends(
        require_permission(Permission.CREATE_TRADE)
    ),
):
    """
    Create a new bond trade.
    
    - Validates trade date is a business day
    - Validates settlement date is T+2 or later
    - Calculates amounts automatically
    - Sets status to PENDING_APPROVAL
    
    Requires CREATE_TRADE permission.
    """
    # Validate trade date is a business day
    if not is_thai_business_day(trade.trade_date):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trade date {trade.trade_date} is not a Thai business day"
        )
    
    # Validate settlement date
    min_settlement = calculate_settlement_date(trade.trade_date, days=2)
    if trade.settlement_date < min_settlement:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Settlement date must be at least T+2 ({min_settlement})"
        )
    
    # Calculate amounts
    trade_data = trade.model_dump()
    amounts = calculate_amounts(trade_data)
    
    # Create trade
    new_trade = {
        "trade_id": f"TRD{uuid4().hex[:8].upper()}",
        "trade_ref": generate_trade_ref(),
        "entity_id": trade.entity_id or "ENTITY001",
        **trade_data,
        **amounts,
        "trade_type": "OUTRIGHT",
        "commission": Decimal("0"),
        "broker_fee": Decimal("0"),
        "withholding_tax": Decimal("0"),
        "status": "PENDING_APPROVAL",
        "is_thaibma_reported": False,
        "thaibma_ref": None,
        "settlement_status": "PENDING",
        "trader_id": current_user.user_id,
        "approver_id": None,
        "approved_at": None,
        "created_at": datetime.now(),
        "updated_at": None,
    }
    
    MOCK_TRADES.append(new_trade)
    return new_trade


@router.post("/{trade_id}/approve", response_model=BondTradeResponse)
async def approve_bond_trade(
    trade_id: str,
    request: ApprovalRequest,
    current_user: UserInToken = Depends(
        require_permission(Permission.APPROVE_TRADE)
    ),
):
    """
    Approve or reject a bond trade.
    
    - Enforces four-eyes principle (approver cannot be trader)
    - Updates status to APPROVED or REJECTED
    
    Requires APPROVE_TRADE permission.
    """
    for i, trade in enumerate(MOCK_TRADES):
        if trade["trade_id"] == trade_id:
            # Check status
            if trade["status"] != "PENDING_APPROVAL":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Trade is not pending approval (current status: {trade['status']})"
                )
            
            # Four-eyes principle
            validate_four_eyes(trade["trader_id"], current_user.user_id)
            
            # Update trade
            if request.approved:
                MOCK_TRADES[i]["status"] = "APPROVED"
                MOCK_TRADES[i]["approver_id"] = current_user.user_id
                MOCK_TRADES[i]["approved_at"] = datetime.now()
            else:
                MOCK_TRADES[i]["status"] = "REJECTED"
                MOCK_TRADES[i]["rejection_reason"] = request.reason
            
            MOCK_TRADES[i]["updated_at"] = datetime.now()
            return MOCK_TRADES[i]
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Trade with ID '{trade_id}' not found"
    )


@router.post("/{trade_id}/cancel", response_model=BondTradeResponse)
async def cancel_bond_trade(
    trade_id: str,
    reason: Optional[str] = None,
    current_user: UserInToken = Depends(
        require_permission(Permission.CANCEL_TRADE)
    ),
):
    """
    Cancel a bond trade.
    
    Only DRAFT or PENDING_APPROVAL trades can be cancelled.
    
    Requires CANCEL_TRADE permission.
    """
    for i, trade in enumerate(MOCK_TRADES):
        if trade["trade_id"] == trade_id:
            if trade["status"] not in ["DRAFT", "PENDING_APPROVAL"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot cancel trade with status '{trade['status']}'"
                )
            
            MOCK_TRADES[i]["status"] = "CANCELLED"
            MOCK_TRADES[i]["updated_at"] = datetime.now()
            return MOCK_TRADES[i]
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Trade with ID '{trade_id}' not found"
    )


@router.get("/settlement/today", response_model=BondTradeList)
async def get_today_settlements(
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    Get trades settling today.
    """
    today = date.today()
    settling_today = [
        t for t in MOCK_TRADES 
        if t["settlement_date"] == today and t["status"] == "APPROVED"
    ]
    return BondTradeList(items=settling_today, total=len(settling_today))


@router.post("/{trade_id}/thaibma-report")
async def report_to_thaibma(
    trade_id: str,
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    Report trade to ThaiBMA (mock endpoint).
    
    In production, this would call ThaiBMA API.
    """
    for i, trade in enumerate(MOCK_TRADES):
        if trade["trade_id"] == trade_id:
            if trade["is_thaibma_reported"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Trade already reported to ThaiBMA"
                )
            
            # Mock ThaiBMA reporting
            MOCK_TRADES[i]["is_thaibma_reported"] = True
            MOCK_TRADES[i]["thaibma_ref"] = f"TBMA{datetime.now().strftime('%Y%m%d%H%M%S')}"
            MOCK_TRADES[i]["thaibma_report_time"] = datetime.now()
            
            return {
                "success": True,
                "message": "Trade reported to ThaiBMA",
                "thaibma_ref": MOCK_TRADES[i]["thaibma_ref"]
            }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Trade with ID '{trade_id}' not found"
    )
