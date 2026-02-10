"""
Treasury Management System - Interbank Deals Router
====================================================

API endpoints for managing interbank money market deals
(Placements and Borrowings).

Delegates business logic to InterbankService.
"""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user, UserInToken, require_permission, Permission
from app.core.enums import TradeStatus, InterbankDealType
from app.database import get_db
from app.services.interbank_service import InterbankService
from app.schemas.transactions import (
    InterbankDealCreate, 
    InterbankDealResponse, 
    InterbankDealList
)

router = APIRouter()


@router.get("/", response_model=InterbankDealList)
def list_interbank_deals(
    status: Optional[TradeStatus] = Query(None),
    deal_type: Optional[InterbankDealType] = Query(None),
    counterparty_id: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user)
):
    """
    List interbank deals with filtering and pagination.
    """
    service = InterbankService(db)
    
    filters = {}
    if status: filters["status"] = status
    if deal_type: filters["deal_type"] = deal_type
    if counterparty_id: filters["counterparty_id"] = counterparty_id
    if start_date: filters["date_from"] = start_date
    if end_date: filters["date_to"] = end_date
    
    skip = (page - 1) * size
    items, total = service.list_deals(skip=skip, limit=size, filters=filters)
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size
    }


@router.post("/", response_model=InterbankDealResponse, status_code=status.HTTP_201_CREATED)
def create_interbank_deal(
    deal: InterbankDealCreate,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(require_permission(Permission.TRADE_CREATE))
):
    """
    Create a new interbank deal (Placement or Borrowing).
    """
    service = InterbankService(db)
    
    new_deal, validation = service.create_deal(
        deal_type=deal.deal_type,
        counterparty_id=deal.counterparty_id,
        portfolio_id=deal.portfolio_id,
        principal_amount=deal.principal_amount,
        interest_rate=deal.interest_rate,
        start_date=deal.start_date,
        maturity_date=deal.maturity_date,
        trader_id=current_user.user_id,
        entity_id=deal.entity_id or current_user.entity_id or "BANK001",
        currency=deal.currency,
        rate_type=deal.rate_type,
        day_count_convention=deal.day_count_convention,
        external_ref=deal.external_ref,
        spread=deal.spread,
        reference_rate=deal.reference_rate
    )
    
    if not new_deal:
        # If validation failed (returned None), raising 400 with details
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=validation
        )
        
    db.commit()
    db.refresh(new_deal)
    return new_deal


@router.get("/{deal_ref}", response_model=InterbankDealResponse)
def get_interbank_deal(
    deal_ref: str,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user)
):
    """
    Get interbank deal details by reference.
    """
    service = InterbankService(db)
    deal = service.get_deal(deal_ref)
    if not deal:
        raise HTTPException(status_code=404, detail=f"Deal {deal_ref} not found")
    return deal


@router.post("/{deal_ref}/approve", response_model=InterbankDealResponse)
def approve_interbank_deal(
    deal_ref: str,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(require_permission(Permission.TRADE_APPROVE))
):
    """
    Approve an interbank deal (Four-Eyes Principle).
    """
    service = InterbankService(db)
    deal, error = service.approve_deal(deal_ref, current_user.user_id)
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    db.commit()
    db.refresh(deal)
    return deal


@router.post("/{deal_ref}/reject", response_model=InterbankDealResponse)
def reject_interbank_deal(
    deal_ref: str,
    reason: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(require_permission(Permission.TRADE_APPROVE))
):
    """
    Reject an interbank deal with a reason.
    """
    service = InterbankService(db)
    deal, error = service.reject_deal(deal_ref, current_user.user_id, reason)
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    db.commit()
    db.refresh(deal)
    return deal


@router.post("/{deal_ref}/cancel", response_model=InterbankDealResponse)
def cancel_interbank_deal(
    deal_ref: str,
    reason: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(require_permission(Permission.TRADE_CREATE))
):
    """
    Cancel a DRAFT or PENDING_APPROVAL deal.
    """
    service = InterbankService(db)
    deal, error = service.cancel_deal(deal_ref, current_user.user_id, reason)
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    db.commit()
    db.refresh(deal)
    return deal
