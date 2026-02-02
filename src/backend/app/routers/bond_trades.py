"""
Treasury Management System - Bond Trades Router (Database-Backed)
==================================================================

API endpoints for bond trade management.
Uses real database operations with full validation and limit checking.
"""

from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import get_current_active_user, UserInToken
from app.core.permissions import require_permission, Permission, validate_four_eyes
from app.models.transactions import BondTrade, TradeStatus
from app.services.bond_trade_service import BondTradeService
from app.services.thaibma_service import ThaiBMAReportingService
from app.services.calendar_service import calculate_settlement_date, is_thai_business_day


router = APIRouter()


# =============================================================================
# Pydantic Schemas
# =============================================================================

class BondTradeCreate(BaseModel):
    """Request model for creating a bond trade"""
    security_id: str = Field(..., description="Security ID")
    counterparty_id: str = Field(..., description="Counterparty ID")
    portfolio_id: str = Field(..., description="Portfolio ID")
    trade_side: str = Field(..., pattern="^(BUY|SELL)$", description="BUY or SELL")
    trade_date: date = Field(..., description="Trade date")
    settlement_date: date = Field(..., description="Settlement date (T+2)")
    face_value: Decimal = Field(..., gt=0, description="Face value")
    clean_price: Decimal = Field(..., gt=0, lt=300, description="Clean price")
    yield_rate: Optional[Decimal] = Field(None, description="Yield rate")
    entity_id: Optional[str] = Field("ENT001", description="Entity ID")


class BondTradeResponse(BaseModel):
    """Response model for bond trade"""
    trade_id: str
    trade_ref: str
    entity_id: str
    counterparty_id: str
    portfolio_id: str
    security_id: str
    isin: Optional[str] = None
    trade_side: str
    trade_type: str
    trade_date: date
    settlement_date: date
    face_value: Decimal
    quantity: Optional[Decimal] = None
    clean_price: Decimal
    dirty_price: Optional[Decimal] = None
    yield_rate: Optional[Decimal] = None
    principal_amount: Optional[Decimal] = None
    accrued_interest: Optional[Decimal] = None
    settlement_amount: Optional[Decimal] = None
    status: str
    is_thaibma_reported: bool = False
    thaibma_ref: Optional[str] = None
    settlement_status: Optional[str] = None
    trader_id: Optional[str] = None
    approver_id: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BondTradeList(BaseModel):
    """Response model for list of trades"""
    items: List[BondTradeResponse]
    total: int
    page: int = 1
    page_size: int = 20


class ApprovalRequest(BaseModel):
    """Request model for trade approval"""
    approved: bool = Field(..., description="True to approve, False to reject")
    reason: Optional[str] = Field(None, description="Reason for rejection")


class CreateTradeResponse(BaseModel):
    """Response for trade creation"""
    trade: BondTradeResponse
    validation: dict


# =============================================================================
# Trade Endpoints
# =============================================================================

@router.get("", response_model=BondTradeList)
async def list_bond_trades(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by status"),
    trade_side: Optional[str] = Query(None, description="Filter by BUY/SELL"),
    counterparty_id: Optional[str] = Query(None, description="Filter by counterparty"),
    portfolio_id: Optional[str] = Query(None, description="Filter by portfolio"),
    security_id: Optional[str] = Query(None, description="Filter by security"),
    trade_date_from: Optional[date] = Query(None, description="Trade date from"),
    trade_date_to: Optional[date] = Query(None, description="Trade date to"),
    settlement_date_from: Optional[date] = Query(None, description="Settlement date from"),
    settlement_date_to: Optional[date] = Query(None, description="Settlement date to"),
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    List bond trades with filtering and pagination.
    """
    query = db.query(BondTrade)
    
    # Apply filters
    if status:
        query = query.filter(BondTrade.status == status)
    if trade_side:
        query = query.filter(BondTrade.trade_side == trade_side)
    if counterparty_id:
        query = query.filter(BondTrade.counterparty_id == counterparty_id)
    if portfolio_id:
        query = query.filter(BondTrade.portfolio_id == portfolio_id)
    if security_id:
        query = query.filter(BondTrade.security_id == security_id)
    if trade_date_from:
        query = query.filter(BondTrade.trade_date >= trade_date_from)
    if trade_date_to:
        query = query.filter(BondTrade.trade_date <= trade_date_to)
    if settlement_date_from:
        query = query.filter(BondTrade.settlement_date >= settlement_date_from)
    if settlement_date_to:
        query = query.filter(BondTrade.settlement_date <= settlement_date_to)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    items = query.order_by(BondTrade.created_at.desc()).offset(offset).limit(page_size).all()
    
    return BondTradeList(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/pending-approval", response_model=BondTradeList)
async def list_pending_approval(
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(
        require_permission(Permission.APPROVE_TRADE)
    ),
):
    """
    List trades pending approval.
    
    Requires APPROVE_TRADE permission.
    """
    service = BondTradeService(db)
    pending = service.get_pending_approvals()
    
    return BondTradeList(
        items=pending,
        total=len(pending),
        page=1,
        page_size=len(pending) or 20
    )


@router.get("/settlement/today", response_model=BondTradeList)
async def get_today_settlements(
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    Get trades settling today.
    """
    service = BondTradeService(db)
    settling = service.get_today_settlements()
    
    return BondTradeList(
        items=settling,
        total=len(settling),
        page=1,
        page_size=len(settling) or 20
    )


@router.get("/{trade_id}", response_model=BondTradeResponse)
async def get_bond_trade(
    trade_id: str,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    Get a specific bond trade by ID.
    """
    trade = db.query(BondTrade).filter(BondTrade.trade_id == trade_id).first()
    
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trade with ID '{trade_id}' not found"
        )
    
    return trade


@router.post("", response_model=CreateTradeResponse, status_code=status.HTTP_201_CREATED)
async def create_bond_trade(
    trade_data: BondTradeCreate,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(
        require_permission(Permission.CREATE_TRADE)
    ),
):
    """
    Create a new bond trade.
    
    Validation includes:
    - Trade date must be a Thai business day
    - Settlement date must be T+2 or later
    - Security must be active and tradeable
    - Counterparty must be active
    - Trade amount must be within counterparty limits
    
    Requires CREATE_TRADE permission.
    """
    service = BondTradeService(db)
    
    trade, validation = service.create_trade(
        security_id=trade_data.security_id,
        counterparty_id=trade_data.counterparty_id,
        portfolio_id=trade_data.portfolio_id,
        trade_side=trade_data.trade_side,
        trade_date=trade_data.trade_date,
        settlement_date=trade_data.settlement_date,
        face_value=trade_data.face_value,
        clean_price=trade_data.clean_price,
        yield_rate=trade_data.yield_rate,
        trader_id=current_user.user_id,
        entity_id=trade_data.entity_id or "ENT001"
    )
    
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Trade validation failed",
                "errors": validation.get("errors", []),
                "limit_check": validation.get("limit_check")
            }
        )
    
    db.commit()
    db.refresh(trade)
    
    return CreateTradeResponse(
        trade=trade,
        validation=validation
    )


@router.post("/{trade_id}/approve", response_model=BondTradeResponse)
async def approve_bond_trade(
    trade_id: str,
    request: ApprovalRequest,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(
        require_permission(Permission.APPROVE_TRADE)
    ),
):
    """
    Approve or reject a bond trade.
    
    Enforces four-eyes principle: approver cannot be the trader.
    
    Requires APPROVE_TRADE permission.
    """
    service = BondTradeService(db)
    
    trade, error = service.approve_trade(
        trade_id=trade_id,
        approver_id=current_user.user_id,
        approved=request.approved,
        reason=request.reason
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    db.commit()
    
    # Auto-report to ThaiBMA if approved
    if request.approved:
        thaibma_service = ThaiBMAReportingService(db)
        thaibma_service.report_trade(trade)
        db.commit()
    
    return trade


@router.post("/{trade_id}/cancel", response_model=BondTradeResponse)
async def cancel_bond_trade(
    trade_id: str,
    reason: Optional[str] = Query(None, description="Cancellation reason"),
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(
        require_permission(Permission.CANCEL_TRADE)
    ),
):
    """
    Cancel a bond trade.
    
    Only DRAFT or PENDING_APPROVAL trades can be cancelled.
    
    Requires CANCEL_TRADE permission.
    """
    service = BondTradeService(db)
    
    trade, error = service.cancel_trade(trade_id, reason)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    db.commit()
    
    return trade


# =============================================================================
# ThaiBMA Reporting Endpoints
# =============================================================================

@router.post("/{trade_id}/thaibma-report")
async def report_to_thaibma(
    trade_id: str,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    Report trade to ThaiBMA.
    
    Trades must be reported within 30 minutes of execution.
    """
    trade = db.query(BondTrade).filter(BondTrade.trade_id == trade_id).first()
    
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trade with ID '{trade_id}' not found"
        )
    
    service = ThaiBMAReportingService(db)
    success, details = service.report_trade(trade)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=details.get("error", "ThaiBMA reporting failed")
        )
    
    db.commit()
    
    return {
        "success": True,
        "message": "Trade reported to ThaiBMA",
        "thaibma_ref": details["thaibma_ref"],
        "report_time": details["report_time"],
        "is_late": details.get("is_late", False)
    }


@router.get("/thaibma/pending")
async def get_pending_thaibma_reports(
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    Get trades pending ThaiBMA reporting.
    """
    service = ThaiBMAReportingService(db)
    pending = service.get_unreported_trades()
    
    return {
        "pending_count": len(pending),
        "trades": [
            {
                "trade_id": t.trade_id,
                "trade_ref": t.trade_ref,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "time_since_created_minutes": (
                    (datetime.now() - t.created_at).total_seconds() / 60
                    if t.created_at else 0
                )
            }
            for t in pending
        ]
    }


@router.post("/thaibma/report-all")
async def report_all_pending_to_thaibma(
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    Report all pending trades to ThaiBMA.
    """
    service = ThaiBMAReportingService(db)
    pending = service.get_unreported_trades()
    
    if not pending:
        return {
            "message": "No trades pending ThaiBMA reporting",
            "reported_count": 0
        }
    
    results = service.report_multiple_trades(pending)
    db.commit()
    
    return results


@router.get("/thaibma/summary")
async def get_thaibma_reporting_summary(
    report_date: Optional[date] = Query(None, description="Report date"),
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    Get ThaiBMA reporting summary for a date.
    """
    service = ThaiBMAReportingService(db)
    return service.get_reporting_summary(report_date)


# =============================================================================
# Settlement Endpoints
# =============================================================================

@router.get("/settlement/upcoming")
async def get_upcoming_settlements(
    days: int = Query(5, ge=1, le=30, description="Number of days to look ahead"),
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    Get trades with upcoming settlements.
    """
    today = date.today()
    end_date = today + date.resolution * days
    
    trades = db.query(BondTrade).filter(
        BondTrade.settlement_date >= today,
        BondTrade.settlement_date <= end_date,
        BondTrade.status == "APPROVED",
        BondTrade.settlement_status.in_(["PENDING", "PARTIAL"])
    ).order_by(BondTrade.settlement_date).all()
    
    # Group by date
    by_date = {}
    for trade in trades:
        date_str = trade.settlement_date.isoformat()
        if date_str not in by_date:
            by_date[date_str] = []
        by_date[date_str].append({
            "trade_id": trade.trade_id,
            "trade_ref": trade.trade_ref,
            "trade_side": trade.trade_side,
            "counterparty_id": trade.counterparty_id,
            "settlement_amount": str(trade.settlement_amount)
        })
    
    return {
        "total_trades": len(trades),
        "by_date": by_date
    }


@router.post("/{trade_id}/settle")
async def mark_trade_settled(
    trade_id: str,
    settlement_ref: Optional[str] = Query(None, description="Settlement reference"),
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    Mark a trade as settled.
    
    This should be called after receiving settlement confirmation.
    """
    trade = db.query(BondTrade).filter(BondTrade.trade_id == trade_id).first()
    
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trade with ID '{trade_id}' not found"
        )
    
    if trade.status != "APPROVED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trade is not approved (status: {trade.status})"
        )
    
    if trade.settlement_status == "SETTLED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trade is already settled"
        )
    
    # Update trade
    trade.settlement_status = "SETTLED"
    trade.status = "SETTLED"
    trade.settlement_ref = settlement_ref
    trade.settled_at = datetime.now()
    trade.updated_at = datetime.now()
    
    # Update position (would call position service here)
    # from app.services.position_service import PositionService
    # position_service = PositionService(db)
    # position_service.update_position_from_trade(trade)
    
    db.commit()
    
    return {
        "success": True,
        "message": "Trade marked as settled",
        "trade_id": trade_id,
        "settlement_ref": settlement_ref
    }
