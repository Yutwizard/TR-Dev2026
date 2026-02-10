"""
Treasury Management System - Repo/Reverse Repo Router
======================================================

API endpoints for managing repo and reverse repo transactions.
delegates logic to RepoService.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from enum import Enum
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user, UserInToken
from app.db.session import get_db
from app.services.repo_service import RepoService
from app.models.transactions import RepoTrade
from app.core.enums import RepoTradeType, TradeStatus

router = APIRouter()


# =============================================================================
# Request/Response Models
# =============================================================================

class RepoTradeCreate(BaseModel):
    """Request to create a new repo/reverse repo trade"""
    repo_type: RepoTradeType = Field(..., description="REPO or REVERSE_REPO")
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
    security_id: Optional[str]
    isin: Optional[str]
    security_name: Optional[str]
    face_value: Optional[Decimal]
    market_price: Optional[Decimal]
    market_value: Optional[Decimal]
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
    # Margins
    initial_margin: Optional[Decimal]
    current_margin: Optional[Decimal]
    margin_call_threshold: Decimal
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

    class Config:
        from_attributes = True


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


# =============================================================================
# Helper
# =============================================================================

def map_trade_to_response(trade: RepoTrade) -> RepoTradeResponse:
    # Calculate derived/nested fields for response
    collateral_val = trade.collateral_market_value or Decimal("0")
    face_val = trade.collateral_face_value or Decimal("0")
    
    # Simple price derivation (avoid division by zero)
    market_price = (collateral_val / face_val * 100) if face_val > 0 else Decimal("0")
    
    # Collateral Value (post-haircut)
    post_haircut_val = collateral_val * (1 - (trade.haircut_pct or 0) / 100)
    
    collateral_info = CollateralInfo(
        security_id=trade.collateral_security_id,
        isin=trade.collateral_isin,
        security_name=trade.collateral_security.security_name if trade.collateral_security else None,
        face_value=face_val,
        market_price=round(market_price, 4),
        market_value=collateral_val,
        haircut_pct=trade.haircut_pct or Decimal("0"),
        collateral_value=round(post_haircut_val, 2)
    )

    return RepoTradeResponse(
        trade_id=trade.trade_id,
        trade_ref=trade.trade_ref,
        external_ref=trade.external_ref,
        repo_type=trade.trade_type,  # Map REPO/REVERSE_REPO to response field
        entity_id=trade.entity_id,
        counterparty_id=trade.counterparty_id,
        portfolio_id=trade.portfolio_id,
        currency=trade.currency,
        near_leg_amount=trade.near_leg_amount,
        far_leg_amount=trade.far_leg_amount,
        repo_rate=trade.repo_rate,
        day_count_convention=trade.day_count_convention,
        interest_amount=trade.interest_amount,
        trade_date=trade.trade_date,
        start_date=trade.start_date,
        end_date=trade.end_date,
        tenor_days=(trade.end_date - trade.start_date).days,
        collateral=collateral_info,
        initial_margin=trade.initial_margin,
        current_margin=trade.current_margin,
        margin_call_threshold=trade.margin_call_threshold,
        status=trade.status,
        near_leg_cash_status=trade.near_leg_cash_status,
        near_leg_collateral_status=trade.near_leg_collateral_status,
        far_leg_cash_status=trade.far_leg_cash_status,
        far_leg_collateral_status=trade.far_leg_collateral_status,
        trader_id=trade.trader_id,
        approver_id=trade.approver_id,
        is_early_terminated=trade.is_early_terminated,
        early_termination_date=trade.early_termination_date,
        created_at=trade.created_at,
        updated_at=trade.updated_at
    )


# =============================================================================
# Endpoints
# =============================================================================

@router.get("", response_model=RepoTradeListResponse)
async def list_repo_trades(
    repo_type: Optional[RepoTradeType] = Query(None),
    status: Optional[TradeStatus] = Query(None),
    counterparty_id: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user)
):
    """List repo/reverse repo trades with filtering."""
    service = RepoService(db)
    filters = {}
    if repo_type: filters["repo_type"] = repo_type.value # DB field is 'trade_type'? No, 'repo_type' is BILATERAL. 'trade_type' is REPO/REVERSE_REPO
    # Wait, Model has `trade_type` (REPO/REVERSE_REPO) AND `repo_type` (BILATERAL/BRP).
    # The Query param `repo_type` corresponds to `trade_type` field in Model based on Enum values?
    # Enum RepoType has REPO, REVERSE_REPO.
    # So filters["trade_type"] = repo_type.value
    
    if repo_type: filters["trade_type"] = repo_type.value
    if status: filters["status"] = status.value
    if counterparty_id: filters["counterparty_id"] = counterparty_id
    if from_date: filters["date_from"] = from_date
    if to_date: filters["date_to"] = to_date

    trades, total = service.list_trades(skip=(page - 1) * size, limit=size, filters=filters)
    
    items = [map_trade_to_response(t) for t in trades]
    
    return RepoTradeListResponse(
        items=items,
        total=total,
        page=page,
        size=size
    )


@router.post("", response_model=RepoTradeResponse, status_code=status.HTTP_201_CREATED)
async def create_repo_trade(
    trade_in: RepoTradeCreate,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user)
):
    """Create a new repo/reverse repo trade."""
    service = RepoService(db)
    
    # Convert Pydantic to args
    trade, validation = service.create_trade(
        trade_type=trade_in.repo_type.value, # REPO or REVERSE_REPO
        repo_type="BILATERAL", # Default or enhance input
        counterparty_id=trade_in.counterparty_id,
        portfolio_id=trade_in.portfolio_id,
        start_date=trade_in.start_date,
        end_date=trade_in.end_date,
        near_leg_amount=trade_in.near_leg_amount,
        repo_rate=trade_in.repo_rate,
        trader_id=current_user.user_id,
        collateral_security_id=trade_in.collateral_security_id,
        collateral_isin=trade_in.collateral_isin,
        collateral_face_value=trade_in.collateral_face_value,
        haircut_pct=trade_in.haircut_pct,
        margin_call_threshold=trade_in.margin_call_threshold,
        currency=trade_in.currency,
        external_ref=None, # Or from input
        notes=trade_in.notes
    )

    if not trade:
        # Construct error message from validation details
        error_msg = "; ".join(validation.get("errors", []))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation Failed: {error_msg}"
        )
    
    try:
        db.commit()
        db.refresh(trade)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
        
    return map_trade_to_response(trade)


@router.get("/collateral-summary", response_model=CollateralSummary)
async def get_collateral_summary(
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user)
):
    """Get collateral position summary."""
    service = RepoService(db)
    summary = service.get_collateral_summary()
    # Map dictionary to Pydantic if needed, but Pydantic handles dict nicely
    return summary


@router.get("/{trade_ref}", response_model=RepoTradeResponse)
async def get_repo_trade(
    trade_ref: str,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user)
):
    """Get trade details."""
    service = RepoService(db)
    trade = service.get_trade(trade_ref)
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    return map_trade_to_response(trade)


@router.post("/{trade_ref}/approve", response_model=RepoTradeResponse)
async def approve_repo_trade(
    trade_ref: str,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user)
):
    """Approve trade (Four-Eyes Principle)."""
    service = RepoService(db)
    trade, error = service.approve_trade(trade_ref, current_user.user_id)
    
    if error:
        raise HTTPException(status_code=400, detail=error)
        
    db.commit()
    db.refresh(trade)
    return map_trade_to_response(trade)


@router.post("/{trade_ref}/cancel", response_model=RepoTradeResponse)
async def cancel_repo_trade(
    trade_ref: str,
    reason: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user)
):
    """Cancel trade."""
    service = RepoService(db)
    trade, error = service.cancel_trade(trade_ref, current_user.user_id, reason)
    
    if error:
        raise HTTPException(status_code=400, detail=error)
        
    db.commit()
    db.refresh(trade)
    return map_trade_to_response(trade)


@router.post("/{trade_ref}/start-leg-settle", response_model=RepoTradeResponse)
async def settle_near_leg(
    trade_ref: str,
    bahtnet_ref: Optional[str] = None,
    custodian_ref: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user)
):
    """Settle Near Leg."""
    service = RepoService(db)
    trade, error = service.settle_near_leg(trade_ref, current_user.user_id, bahtnet_ref, custodian_ref)
    
    if error:
        raise HTTPException(status_code=400, detail=error)
        
    db.commit()
    db.refresh(trade)
    return map_trade_to_response(trade)


@router.post("/{trade_ref}/end-leg-settle", response_model=RepoTradeResponse)
async def settle_far_leg(
    trade_ref: str,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user)
):
    """Settle Far Leg."""
    service = RepoService(db)
    trade, error = service.settle_far_leg(trade_ref, current_user.user_id)
    
    if error:
        raise HTTPException(status_code=400, detail=error)
        
    db.commit()
    db.refresh(trade)
    return map_trade_to_response(trade)


@router.post("/{trade_ref}/early-terminate", response_model=RepoTradeResponse)
async def early_terminate_repo(
    trade_ref: str,
    termination_date: date = Query(..., description="Date of early termination"),
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user)
):
    """Early terminate a repo trade."""
    service = RepoService(db)
    trade, error = service.early_terminate_trade(trade_ref, termination_date, current_user.user_id)
    
    if error:
        raise HTTPException(status_code=400, detail=error)
        
    db.commit()
    db.refresh(trade)
    return map_trade_to_response(trade)


class MarginCallResult(BaseModel):
    """Margin call calculation result"""
    trade_ref: str
    current_margin_pct: Decimal
    required_margin_pct: Decimal
    margin_call_triggered: bool
    margin_call_amount: Decimal
    margin_call_direction: str
    calculated_at: datetime


@router.post("/{trade_ref}/margin-call", response_model=MarginCallResult)
async def check_margin_call(
    trade_ref: str,
    current_market_price: Decimal = Query(..., description="Current market price of collateral"),
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user)
):
    """Check margin call status."""
    service = RepoService(db)
    result = service.check_margin_call(trade_ref, current_market_price)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
        
    return result
