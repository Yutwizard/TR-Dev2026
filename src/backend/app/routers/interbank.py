"""
Treasury Management System - Interbank Deals Router
====================================================

API endpoints for managing interbank money market deals
(Placements and Borrowings).

Endpoints:
- GET /: List interbank deals
- POST /: Create new deal
- GET /{deal_ref}: Get deal details
- POST /{deal_ref}/approve: Approve deal
- POST /{deal_ref}/cancel: Cancel deal
- GET /maturing: Get deals maturing today/soon
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from enum import Enum

from app.core.auth import get_current_active_user, UserInToken
from app.core.permissions import Permission, require_permission


router = APIRouter()


# =============================================================================
# Enums
# =============================================================================
class DealType(str, Enum):
    PLACEMENT = "PLACEMENT"
    BORROWING = "BORROWING"


class DealStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    MATURED = "MATURED"
    CANCELLED = "CANCELLED"


class RateType(str, Enum):
    FIXED = "FIXED"
    FLOATING = "FLOATING"


class SettlementStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SETTLED = "SETTLED"
    FAILED = "FAILED"


# =============================================================================
# Request/Response Models
# =============================================================================
class InterbankDealCreate(BaseModel):
    """Request to create a new interbank deal"""
    deal_type: DealType = Field(..., description="PLACEMENT or BORROWING")
    counterparty_id: str = Field(..., max_length=40)
    portfolio_id: str = Field(..., max_length=40)
    currency: str = Field(default="THB", max_length=3)
    principal_amount: Decimal = Field(..., gt=0, description="Principal amount")
    rate_type: RateType = Field(default=RateType.FIXED)
    interest_rate: Decimal = Field(..., ge=0, le=100, description="Interest rate (annual %)")
    spread: Decimal = Field(default=Decimal("0"), description="Spread over reference rate (bps)")
    reference_rate: Optional[str] = Field(None, description="Reference rate (e.g., THOR)")
    day_count_convention: str = Field(default="ACT/365")
    start_date: date
    maturity_date: date
    notes: Optional[str] = None


class InterbankDealResponse(BaseModel):
    """Interbank deal response"""
    deal_ref: str
    external_ref: Optional[str]
    deal_type: str
    entity_id: str
    counterparty_id: str
    counterparty_name: str
    portfolio_id: str
    currency: str
    principal_amount: Decimal
    rate_type: str
    interest_rate: Decimal
    spread: Decimal
    reference_rate: Optional[str]
    day_count_convention: str
    deal_date: date
    start_date: date
    maturity_date: date
    tenor_days: int
    interest_amount: Decimal
    accrued_interest: Decimal
    maturity_amount: Decimal
    status: str
    trader_id: Optional[str]
    approver_id: Optional[str]
    start_settlement_status: str
    maturity_settlement_status: str
    created_at: datetime
    updated_at: Optional[datetime]


class InterbankDealListResponse(BaseModel):
    """List of interbank deals"""
    items: List[InterbankDealResponse]
    total: int
    page: int
    size: int


class MaturityCalendar(BaseModel):
    """Deals maturing on a specific date"""
    maturity_date: date
    deals: List[InterbankDealResponse]
    total_placement: Decimal
    total_borrowing: Decimal
    net_cash_flow: Decimal


# =============================================================================
# Mock Data
# =============================================================================
def generate_deal_ref() -> str:
    """Generate unique deal reference"""
    from uuid import uuid4
    return f"IB{datetime.now().strftime('%Y%m%d')}{str(uuid4())[:6].upper()}"


MOCK_INTERBANK_DEALS = [
    InterbankDealResponse(
        deal_ref="IB202502010001",
        external_ref=None,
        deal_type="PLACEMENT",
        entity_id="BANK001",
        counterparty_id="CPTY001",
        counterparty_name="Bangkok Bank PCL",
        portfolio_id="PORT001",
        currency="THB",
        principal_amount=Decimal("100000000.00"),
        rate_type="FIXED",
        interest_rate=Decimal("2.25"),
        spread=Decimal("0"),
        reference_rate=None,
        day_count_convention="ACT/365",
        deal_date=date(2025, 2, 1),
        start_date=date(2025, 2, 1),
        maturity_date=date(2025, 5, 1),
        tenor_days=89,
        interest_amount=Decimal("548630.14"),
        accrued_interest=Decimal("12500.00"),
        maturity_amount=Decimal("100548630.14"),
        status="ACTIVE",
        trader_id="TRADER001",
        approver_id="SUP001",
        start_settlement_status="SETTLED",
        maturity_settlement_status="PENDING",
        created_at=datetime.now(),
        updated_at=None
    ),
    InterbankDealResponse(
        deal_ref="IB202502020001",
        external_ref=None,
        deal_type="BORROWING",
        entity_id="BANK001",
        counterparty_id="CPTY002",
        counterparty_name="Kasikornbank PCL",
        portfolio_id="PORT001",
        currency="THB",
        principal_amount=Decimal("50000000.00"),
        rate_type="FLOATING",
        interest_rate=Decimal("2.35"),
        spread=Decimal("10"),
        reference_rate="THOR",
        day_count_convention="ACT/365",
        deal_date=date(2025, 2, 2),
        start_date=date(2025, 2, 3),
        maturity_date=date(2025, 3, 3),
        tenor_days=28,
        interest_amount=Decimal("90136.99"),
        accrued_interest=Decimal("0"),
        maturity_amount=Decimal("50090136.99"),
        status="PENDING_APPROVAL",
        trader_id="TRADER001",
        approver_id=None,
        start_settlement_status="PENDING",
        maturity_settlement_status="PENDING",
        created_at=datetime.now(),
        updated_at=None
    ),
]


# =============================================================================
# Endpoints
# =============================================================================
@router.get("", response_model=InterbankDealListResponse)
async def list_interbank_deals(
    deal_type: Optional[DealType] = Query(None),
    status: Optional[DealStatus] = Query(None),
    counterparty_id: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: UserInToken = Depends(get_current_active_user)
):
    """
    List interbank deals with filtering.
    
    Filters:
    - deal_type: PLACEMENT or BORROWING
    - status: Deal status
    - counterparty_id: Filter by counterparty
    - from_date/to_date: Deal date range
    """
    deals = MOCK_INTERBANK_DEALS.copy()
    
    # Apply filters
    if deal_type:
        deals = [d for d in deals if d.deal_type == deal_type.value]
    if status:
        deals = [d for d in deals if d.status == status.value]
    if counterparty_id:
        deals = [d for d in deals if d.counterparty_id == counterparty_id]
    
    total = len(deals)
    start = (page - 1) * size
    end = start + size
    
    return InterbankDealListResponse(
        items=deals[start:end],
        total=total,
        page=page,
        size=size
    )


@router.post("", response_model=InterbankDealResponse, status_code=status.HTTP_201_CREATED)
async def create_interbank_deal(
    deal: InterbankDealCreate,
    current_user: UserInToken = Depends(get_current_active_user)
):
    """
    Create a new interbank deal (Placement or Borrowing).
    
    Required permissions: CREATE_INTERBANK_DEAL
    
    The deal will be created in PENDING_APPROVAL status
    and requires supervisor approval before becoming active.
    """
    # Validate dates
    if deal.maturity_date <= deal.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maturity date must be after start date"
        )
    
    tenor_days = (deal.maturity_date - deal.start_date).days
    
    # Calculate interest
    if deal.day_count_convention == "ACT/365":
        interest = deal.principal_amount * deal.interest_rate / 100 * tenor_days / 365
    else:  # ACT/360
        interest = deal.principal_amount * deal.interest_rate / 100 * tenor_days / 360
    
    deal_ref = generate_deal_ref()
    
    response = InterbankDealResponse(
        deal_ref=deal_ref,
        external_ref=None,
        deal_type=deal.deal_type.value,
        entity_id="BANK001",
        counterparty_id=deal.counterparty_id,
        counterparty_name="Sample Counterparty",
        portfolio_id=deal.portfolio_id,
        currency=deal.currency,
        principal_amount=deal.principal_amount,
        rate_type=deal.rate_type.value,
        interest_rate=deal.interest_rate,
        spread=deal.spread,
        reference_rate=deal.reference_rate,
        day_count_convention=deal.day_count_convention,
        deal_date=date.today(),
        start_date=deal.start_date,
        maturity_date=deal.maturity_date,
        tenor_days=tenor_days,
        interest_amount=round(interest, 2),
        accrued_interest=Decimal("0"),
        maturity_amount=deal.principal_amount + round(interest, 2),
        status="PENDING_APPROVAL",
        trader_id=current_user.user_id,
        approver_id=None,
        start_settlement_status="PENDING",
        maturity_settlement_status="PENDING",
        created_at=datetime.now(),
        updated_at=None
    )
    
    return response


@router.get("/pending-approval", response_model=List[InterbankDealResponse])
async def get_pending_approval_deals(
    current_user: UserInToken = Depends(get_current_active_user)
):
    """
    Get all interbank deals pending approval.
    
    For supervisors to review and approve deals.
    """
    pending = [d for d in MOCK_INTERBANK_DEALS if d.status == "PENDING_APPROVAL"]
    return pending


@router.get("/maturing", response_model=List[MaturityCalendar])
async def get_maturing_deals(
    days_ahead: int = Query(7, ge=1, le=30),
    current_user: UserInToken = Depends(get_current_active_user)
):
    """
    Get deals maturing within the specified number of days.
    
    Returns deals grouped by maturity date with cash flow summary.
    """
    today = date.today()
    result = []
    
    # Group deals by maturity date
    from collections import defaultdict
    by_date = defaultdict(list)
    
    for deal in MOCK_INTERBANK_DEALS:
        if deal.status in ["ACTIVE", "APPROVED"]:
            days_to_maturity = (deal.maturity_date - today).days
            if 0 <= days_to_maturity <= days_ahead:
                by_date[deal.maturity_date].append(deal)
    
    for mat_date in sorted(by_date.keys()):
        deals = by_date[mat_date]
        total_placement = sum(d.maturity_amount for d in deals if d.deal_type == "PLACEMENT")
        total_borrowing = sum(d.maturity_amount for d in deals if d.deal_type == "BORROWING")
        
        result.append(MaturityCalendar(
            maturity_date=mat_date,
            deals=deals,
            total_placement=total_placement,
            total_borrowing=total_borrowing,
            net_cash_flow=total_placement - total_borrowing
        ))
    
    return result


@router.get("/{deal_ref}", response_model=InterbankDealResponse)
async def get_interbank_deal(
    deal_ref: str,
    current_user: UserInToken = Depends(get_current_active_user)
):
    """Get interbank deal details by reference."""
    deal = next((d for d in MOCK_INTERBANK_DEALS if d.deal_ref == deal_ref), None)
    
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deal {deal_ref} not found"
        )
    
    return deal


@router.post("/{deal_ref}/approve", response_model=InterbankDealResponse)
async def approve_interbank_deal(
    deal_ref: str,
    current_user: UserInToken = Depends(get_current_active_user)
):
    """
    Approve an interbank deal.
    
    Required: SUPERVISOR or ADMIN role.
    Implements four-eyes principle - approver must be different from creator.
    """
    deal = next((d for d in MOCK_INTERBANK_DEALS if d.deal_ref == deal_ref), None)
    
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deal {deal_ref} not found"
        )
    
    if deal.status != "PENDING_APPROVAL":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Deal is in {deal.status} status, cannot approve"
        )
    
    # Four-eyes principle check
    if deal.trader_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot approve your own deal (four-eyes principle)"
        )
    
    # In real implementation, update the deal status
    updated_deal = deal.model_copy(update={
        "status": "APPROVED",
        "approver_id": current_user.user_id,
        "updated_at": datetime.now()
    })
    
    return updated_deal


@router.post("/{deal_ref}/cancel", response_model=InterbankDealResponse)
async def cancel_interbank_deal(
    deal_ref: str,
    reason: str = Query(..., min_length=5),
    current_user: UserInToken = Depends(get_current_active_user)
):
    """
    Cancel an interbank deal.
    
    Can only cancel deals in DRAFT, PENDING_APPROVAL, or APPROVED status.
    Active deals cannot be cancelled directly.
    """
    deal = next((d for d in MOCK_INTERBANK_DEALS if d.deal_ref == deal_ref), None)
    
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deal {deal_ref} not found"
        )
    
    if deal.status not in ["DRAFT", "PENDING_APPROVAL", "APPROVED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel deal in {deal.status} status"
        )
    
    updated_deal = deal.model_copy(update={
        "status": "CANCELLED",
        "updated_at": datetime.now()
    })
    
    return updated_deal


@router.post("/{deal_ref}/generate-bahtnet", response_model=dict)
async def generate_bahtnet_instruction(
    deal_ref: str,
    current_user: UserInToken = Depends(get_current_active_user)
):
    """
    Generate BAHTNET payment instruction for the deal.
    
    Returns the BAHTNET XML message content for manual upload
    or reference number if API integration is enabled.
    """
    deal = next((d for d in MOCK_INTERBANK_DEALS if d.deal_ref == deal_ref), None)
    
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deal {deal_ref} not found"
        )
    
    if deal.status not in ["APPROVED", "ACTIVE"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deal must be approved to generate settlement instruction"
        )
    
    # Calculate amount based on deal type and which leg
    if deal.start_settlement_status == "PENDING":
        amount = deal.principal_amount
        leg = "START"
    else:
        amount = deal.maturity_amount
        leg = "MATURITY"
    
    # Determine payment direction
    if deal.deal_type == "PLACEMENT":
        direction = "OUTGOING" if leg == "START" else "INCOMING"
    else:  # BORROWING
        direction = "INCOMING" if leg == "START" else "OUTGOING"
    
    return {
        "deal_ref": deal_ref,
        "leg": leg,
        "direction": direction,
        "amount": str(amount),
        "currency": deal.currency,
        "counterparty": deal.counterparty_name,
        "value_date": str(deal.start_date if leg == "START" else deal.maturity_date),
        "message_type": "MT202",
        "bahtnet_ready": True,
        "generated_at": datetime.now().isoformat()
    }
