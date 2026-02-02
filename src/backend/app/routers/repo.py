"""
Treasury Management System - Repo/Reverse Repo Router
======================================================

API endpoints for managing repo and reverse repo transactions.

Repo = Sell securities with agreement to repurchase (borrowing cash)
Reverse Repo = Buy securities with agreement to resell (lending cash)

Endpoints:
- GET /: List repo trades
- POST /: Create new repo
- GET /{trade_ref}: Get trade details
- POST /{trade_ref}/approve: Approve trade
- POST /{trade_ref}/start-leg-settle: Settle near leg
- POST /{trade_ref}/end-leg-settle: Settle far leg
- GET /collateral-summary: Collateral position summary
- POST /{trade_ref}/margin-call: Calculate/trigger margin call
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from enum import Enum

from app.core.auth import get_current_active_user, UserInToken


router = APIRouter()


# =============================================================================
# Enums
# =============================================================================
class RepoType(str, Enum):
    REPO = "REPO"           # Sell and repurchase (borrow cash)
    REVERSE_REPO = "REVERSE_REPO"  # Buy and resell (lend cash)


class TradeStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    NEAR_LEG_SETTLED = "NEAR_LEG_SETTLED"
    ACTIVE = "ACTIVE"
    FAR_LEG_SETTLED = "FAR_LEG_SETTLED"
    MATURED = "MATURED"
    EARLY_TERMINATED = "EARLY_TERMINATED"
    CANCELLED = "CANCELLED"


class SettlementStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SETTLED = "SETTLED"
    FAILED = "FAILED"


# =============================================================================
# Request/Response Models
# =============================================================================
class RepoTradeCreate(BaseModel):
    """Request to create a new repo/reverse repo trade"""
    repo_type: RepoType = Field(..., description="REPO or REVERSE_REPO")
    counterparty_id: str = Field(..., max_length=40)
    portfolio_id: str = Field(..., max_length=40)
    currency: str = Field(default="THB", max_length=3)
    # Cash leg
    near_leg_amount: Decimal = Field(..., gt=0, description="Cash amount for near leg")
    repo_rate: Decimal = Field(..., ge=0, le=100, description="Repo rate (annual %)")
    start_date: date
    end_date: date
    # Collateral
    collateral_security_id: str = Field(..., max_length=40)
    collateral_isin: str = Field(..., max_length=12)
    collateral_face_value: Decimal = Field(..., gt=0)
    haircut_pct: Decimal = Field(default=Decimal("2.0"), ge=0, le=50)
    margin_call_threshold: Decimal = Field(default=Decimal("2.0"), ge=0, le=10)
    notes: Optional[str] = None


class CollateralInfo(BaseModel):
    """Collateral details"""
    security_id: str
    isin: str
    security_name: str
    face_value: Decimal
    market_price: Decimal
    market_value: Decimal
    haircut_pct: Decimal
    collateral_value: Decimal


class RepoTradeResponse(BaseModel):
    """Repo trade response"""
    trade_id: str
    trade_ref: str
    external_ref: Optional[str]
    repo_type: str
    entity_id: str
    counterparty_id: str
    counterparty_name: str
    portfolio_id: str
    currency: str
    # Cash
    near_leg_amount: Decimal
    far_leg_amount: Decimal
    repo_rate: Decimal
    day_count_convention: str
    interest_amount: Decimal
    # Dates
    trade_date: date
    start_date: date
    end_date: date
    tenor_days: int
    # Collateral
    collateral: CollateralInfo
    haircut_pct: Decimal
    initial_margin: Decimal
    current_margin: Decimal
    margin_call_threshold: Decimal
    margin_call_amount: Decimal
    # Status
    status: str
    near_leg_cash_status: str
    near_leg_collateral_status: str
    far_leg_cash_status: str
    far_leg_collateral_status: str
    # Workflow
    trader_id: Optional[str]
    approver_id: Optional[str]
    is_early_terminated: bool
    early_termination_date: Optional[date]
    created_at: datetime
    updated_at: Optional[datetime]


class RepoTradeListResponse(BaseModel):
    """List of repo trades"""
    items: List[RepoTradeResponse]
    total: int
    page: int
    size: int


class CollateralSummary(BaseModel):
    """Summary of collateral positions"""
    total_pledged_value: Decimal
    total_received_value: Decimal
    net_collateral: Decimal
    by_security: List[dict]
    margin_calls_pending: int


class MarginCallResult(BaseModel):
    """Margin call calculation result"""
    trade_ref: str
    current_margin_pct: Decimal
    required_margin_pct: Decimal
    margin_call_triggered: bool
    margin_call_amount: Decimal
    margin_call_direction: str  # "DELIVER" or "RETURN"
    calculated_at: datetime


# =============================================================================
# Mock Data
# =============================================================================
def generate_trade_ref() -> str:
    from uuid import uuid4
    return f"RP{datetime.now().strftime('%Y%m%d')}{str(uuid4())[:6].upper()}"


MOCK_REPO_TRADES = [
    RepoTradeResponse(
        trade_id="TRADE001",
        trade_ref="RP202502010001",
        external_ref=None,
        repo_type="REPO",
        entity_id="BANK001",
        counterparty_id="CPTY001",
        counterparty_name="Bangkok Bank PCL",
        portfolio_id="PORT001",
        currency="THB",
        near_leg_amount=Decimal("100000000.00"),
        far_leg_amount=Decimal("100136986.30"),
        repo_rate=Decimal("2.50"),
        day_count_convention="ACT/365",
        interest_amount=Decimal("136986.30"),
        trade_date=date(2025, 2, 1),
        start_date=date(2025, 2, 3),
        end_date=date(2025, 2, 23),
        tenor_days=20,
        collateral=CollateralInfo(
            security_id="SEC001",
            isin="TH0623A3B702",
            security_name="LB236A - Government Bond 2.5% 2036",
            face_value=Decimal("100000000.00"),
            market_price=Decimal("102.50"),
            market_value=Decimal("102500000.00"),
            haircut_pct=Decimal("2.0"),
            collateral_value=Decimal("100450000.00")
        ),
        haircut_pct=Decimal("2.0"),
        initial_margin=Decimal("102.50"),
        current_margin=Decimal("102.45"),
        margin_call_threshold=Decimal("2.0"),
        margin_call_amount=Decimal("0"),
        status="ACTIVE",
        near_leg_cash_status="SETTLED",
        near_leg_collateral_status="SETTLED",
        far_leg_cash_status="PENDING",
        far_leg_collateral_status="PENDING",
        trader_id="TRADER001",
        approver_id="SUP001",
        is_early_terminated=False,
        early_termination_date=None,
        created_at=datetime.now(),
        updated_at=None
    ),
    RepoTradeResponse(
        trade_id="TRADE002",
        trade_ref="RP202502020001",
        external_ref=None,
        repo_type="REVERSE_REPO",
        entity_id="BANK001",
        counterparty_id="CPTY002",
        counterparty_name="Kasikornbank PCL",
        portfolio_id="PORT001",
        currency="THB",
        near_leg_amount=Decimal("50000000.00"),
        far_leg_amount=Decimal("50041095.89"),
        repo_rate=Decimal("2.30"),
        day_count_convention="ACT/365",
        interest_amount=Decimal("41095.89"),
        trade_date=date(2025, 2, 2),
        start_date=date(2025, 2, 3),
        end_date=date(2025, 2, 16),
        tenor_days=13,
        collateral=CollateralInfo(
            security_id="SEC002",
            isin="TH0623031R17",
            security_name="ThaiBMA Bill 1.75% 2025",
            face_value=Decimal("51000000.00"),
            market_price=Decimal("99.85"),
            market_value=Decimal("50923500.00"),
            haircut_pct=Decimal("1.5"),
            collateral_value=Decimal("50159648.00")
        ),
        haircut_pct=Decimal("1.5"),
        initial_margin=Decimal("101.50"),
        current_margin=Decimal("101.82"),
        margin_call_threshold=Decimal("2.0"),
        margin_call_amount=Decimal("0"),
        status="PENDING_APPROVAL",
        near_leg_cash_status="PENDING",
        near_leg_collateral_status="PENDING",
        far_leg_cash_status="PENDING",
        far_leg_collateral_status="PENDING",
        trader_id="TRADER001",
        approver_id=None,
        is_early_terminated=False,
        early_termination_date=None,
        created_at=datetime.now(),
        updated_at=None
    ),
]


# =============================================================================
# Endpoints
# =============================================================================
@router.get("", response_model=RepoTradeListResponse)
async def list_repo_trades(
    repo_type: Optional[RepoType] = Query(None),
    status: Optional[TradeStatus] = Query(None),
    counterparty_id: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: UserInToken = Depends(get_current_active_user)
):
    """
    List repo/reverse repo trades with filtering.
    """
    trades = MOCK_REPO_TRADES.copy()
    
    if repo_type:
        trades = [t for t in trades if t.repo_type == repo_type.value]
    if status:
        trades = [t for t in trades if t.status == status.value]
    if counterparty_id:
        trades = [t for t in trades if t.counterparty_id == counterparty_id]
    
    total = len(trades)
    start = (page - 1) * size
    end = start + size
    
    return RepoTradeListResponse(
        items=trades[start:end],
        total=total,
        page=page,
        size=size
    )


@router.post("", response_model=RepoTradeResponse, status_code=status.HTTP_201_CREATED)
async def create_repo_trade(
    trade: RepoTradeCreate,
    current_user: UserInToken = Depends(get_current_active_user)
):
    """
    Create a new repo or reverse repo trade.
    
    REPO: We sell securities and receive cash (borrow)
    REVERSE_REPO: We buy securities and pay cash (lend)
    """
    if trade.end_date <= trade.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date"
        )
    
    tenor_days = (trade.end_date - trade.start_date).days
    
    # Calculate interest and far leg amount
    interest = trade.near_leg_amount * trade.repo_rate / 100 * tenor_days / 365
    far_leg_amount = trade.near_leg_amount + interest
    
    # Calculate collateral value after haircut
    mock_price = Decimal("100.50")
    market_value = trade.collateral_face_value * mock_price / 100
    collateral_value = market_value * (1 - trade.haircut_pct / 100)
    
    # Check collateral coverage
    if collateral_value < trade.near_leg_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient collateral: value {collateral_value} < loan {trade.near_leg_amount}"
        )
    
    trade_ref = generate_trade_ref()
    
    response = RepoTradeResponse(
        trade_id=f"T{trade_ref}",
        trade_ref=trade_ref,
        external_ref=None,
        repo_type=trade.repo_type.value,
        entity_id="BANK001",
        counterparty_id=trade.counterparty_id,
        counterparty_name="Sample Counterparty",
        portfolio_id=trade.portfolio_id,
        currency=trade.currency,
        near_leg_amount=trade.near_leg_amount,
        far_leg_amount=round(far_leg_amount, 2),
        repo_rate=trade.repo_rate,
        day_count_convention="ACT/365",
        interest_amount=round(interest, 2),
        trade_date=date.today(),
        start_date=trade.start_date,
        end_date=trade.end_date,
        tenor_days=tenor_days,
        collateral=CollateralInfo(
            security_id=trade.collateral_security_id,
            isin=trade.collateral_isin,
            security_name="Security (placeholder)",
            face_value=trade.collateral_face_value,
            market_price=mock_price,
            market_value=market_value,
            haircut_pct=trade.haircut_pct,
            collateral_value=collateral_value
        ),
        haircut_pct=trade.haircut_pct,
        initial_margin=collateral_value / trade.near_leg_amount * 100,
        current_margin=collateral_value / trade.near_leg_amount * 100,
        margin_call_threshold=trade.margin_call_threshold,
        margin_call_amount=Decimal("0"),
        status="PENDING_APPROVAL",
        near_leg_cash_status="PENDING",
        near_leg_collateral_status="PENDING",
        far_leg_cash_status="PENDING",
        far_leg_collateral_status="PENDING",
        trader_id=current_user.user_id,
        approver_id=None,
        is_early_terminated=False,
        early_termination_date=None,
        created_at=datetime.now(),
        updated_at=None
    )
    
    return response


@router.get("/pending-approval", response_model=List[RepoTradeResponse])
async def get_pending_approval_trades(
    current_user: UserInToken = Depends(get_current_active_user)
):
    """Get all repo trades pending approval."""
    return [t for t in MOCK_REPO_TRADES if t.status == "PENDING_APPROVAL"]


@router.get("/collateral-summary", response_model=CollateralSummary)
async def get_collateral_summary(
    current_user: UserInToken = Depends(get_current_active_user)
):
    """
    Get summary of all collateral positions.
    
    Shows:
    - Total pledged (collateral we gave)
    - Total received (collateral we hold)
    - Net position
    - Breakdown by security
    """
    pledged = Decimal("0")
    received = Decimal("0")
    
    for trade in MOCK_REPO_TRADES:
        if trade.status in ["ACTIVE", "NEAR_LEG_SETTLED"]:
            if trade.repo_type == "REPO":
                pledged += trade.collateral.market_value
            else:
                received += trade.collateral.market_value
    
    return CollateralSummary(
        total_pledged_value=pledged,
        total_received_value=received,
        net_collateral=received - pledged,
        by_security=[
            {
                "isin": "TH0623A3B702",
                "security_name": "LB236A",
                "pledged_value": pledged,
                "received_value": Decimal("0")
            },
            {
                "isin": "TH0623031R17",
                "security_name": "ThaiBMA Bill",
                "pledged_value": Decimal("0"),
                "received_value": received
            }
        ],
        margin_calls_pending=0
    )


@router.get("/{trade_ref}", response_model=RepoTradeResponse)
async def get_repo_trade(
    trade_ref: str,
    current_user: UserInToken = Depends(get_current_active_user)
):
    """Get repo trade details by reference."""
    trade = next((t for t in MOCK_REPO_TRADES if t.trade_ref == trade_ref), None)
    
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trade {trade_ref} not found"
        )
    
    return trade


@router.post("/{trade_ref}/approve", response_model=RepoTradeResponse)
async def approve_repo_trade(
    trade_ref: str,
    current_user: UserInToken = Depends(get_current_active_user)
):
    """
    Approve a repo trade.
    
    Requires SUPERVISOR or ADMIN role.
    Implements four-eyes principle.
    """
    trade = next((t for t in MOCK_REPO_TRADES if t.trade_ref == trade_ref), None)
    
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trade {trade_ref} not found"
        )
    
    if trade.status != "PENDING_APPROVAL":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trade is in {trade.status} status, cannot approve"
        )
    
    if trade.trader_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot approve your own trade (four-eyes principle)"
        )
    
    updated = trade.model_copy(update={
        "status": "APPROVED",
        "approver_id": current_user.user_id,
        "updated_at": datetime.now()
    })
    
    return updated


@router.post("/{trade_ref}/margin-call", response_model=MarginCallResult)
async def calculate_margin_call(
    trade_ref: str,
    current_market_price: Decimal = Query(..., description="Current market price of collateral"),
    current_user: UserInToken = Depends(get_current_active_user)
):
    """
    Calculate margin call for a repo trade.
    
    Based on current market price of the collateral security,
    determines if a margin call is needed.
    """
    trade = next((t for t in MOCK_REPO_TRADES if t.trade_ref == trade_ref), None)
    
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trade {trade_ref} not found"
        )
    
    if trade.status not in ["ACTIVE", "NEAR_LEG_SETTLED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Margin call only applicable to active trades"
        )
    
    # Recalculate margin with current price
    new_market_value = trade.collateral.face_value * current_market_price / 100
    new_collateral_value = new_market_value * (1 - trade.haircut_pct / 100)
    current_margin_pct = new_collateral_value / trade.near_leg_amount * 100
    required_margin_pct = Decimal("100.00")
    
    # Check if margin call triggered
    margin_shortfall = required_margin_pct - current_margin_pct
    margin_call_triggered = margin_shortfall > trade.margin_call_threshold
    
    if margin_call_triggered:
        margin_call_amount = (margin_shortfall / 100) * trade.near_leg_amount
        direction = "DELIVER" if trade.repo_type == "REPO" else "RETURN"
    else:
        margin_call_amount = Decimal("0")
        direction = "NONE"
    
    return MarginCallResult(
        trade_ref=trade_ref,
        current_margin_pct=round(current_margin_pct, 2),
        required_margin_pct=required_margin_pct,
        margin_call_triggered=margin_call_triggered,
        margin_call_amount=round(margin_call_amount, 2),
        margin_call_direction=direction,
        calculated_at=datetime.now()
    )


@router.post("/{trade_ref}/early-terminate", response_model=RepoTradeResponse)
async def early_terminate_repo(
    trade_ref: str,
    termination_date: date = Query(...),
    current_user: UserInToken = Depends(get_current_active_user)
):
    """
    Early terminate a repo trade.
    
    Calculates interest up to termination date and adjusts settlement amounts.
    """
    trade = next((t for t in MOCK_REPO_TRADES if t.trade_ref == trade_ref), None)
    
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trade {trade_ref} not found"
        )
    
    if trade.status not in ["ACTIVE", "NEAR_LEG_SETTLED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only early terminate active trades"
        )
    
    if termination_date >= trade.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Termination date must be before original end date"
        )
    
    # Recalculate interest for shorter period
    new_tenor = (termination_date - trade.start_date).days
    new_interest = trade.near_leg_amount * trade.repo_rate / 100 * new_tenor / 365
    new_far_leg = trade.near_leg_amount + new_interest
    
    updated = trade.model_copy(update={
        "status": "EARLY_TERMINATED",
        "is_early_terminated": True,
        "early_termination_date": termination_date,
        "far_leg_amount": round(new_far_leg, 2),
        "interest_amount": round(new_interest, 2),
        "tenor_days": new_tenor,
        "updated_at": datetime.now()
    })
    
    return updated
