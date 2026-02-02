"""
Treasury Management System - Positions Router
===============================================

API endpoints for position queries.
"""

from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.core.auth import get_current_active_user, UserInToken
from app.core.permissions import require_permission, Permission
from app.schemas.positions import (
    BondPositionResponse, CashPositionResponse, PositionSummary,
    LimitUtilizationResponse
)


router = APIRouter()


# =============================================================================
# Mock Position Data
# =============================================================================
MOCK_BOND_POSITIONS = [
    {
        "id": 1,
        "position_date": date(2025, 9, 1),
        "entity_id": "ENTITY001",
        "portfolio_id": "TRAD001",
        "security_id": "SEC001",
        "isin": "TH0623A3B702",
        "face_value": Decimal("50000000"),
        "quantity": Decimal("50000"),
        "cost_price": Decimal("99.25"),
        "cost_amount": Decimal("49625000"),
        "market_price": Decimal("99.75"),
        "market_value": Decimal("49875000"),
        "accrued_interest": Decimal("375000"),
        "unrealized_pnl": Decimal("250000"),
        "tfrs9_classification": "FVPL",
        "ecl_stage": 1,
        "ecl_provision": Decimal("0"),
        "pledged_quantity": Decimal("10000"),
        "available_quantity": Decimal("40000"),
    },
    {
        "id": 2,
        "position_date": date(2025, 9, 1),
        "entity_id": "ENTITY001",
        "portfolio_id": "TRAD001",
        "security_id": "SEC002",
        "isin": "TH0623A3C701",
        "face_value": Decimal("30000000"),
        "quantity": Decimal("30000"),
        "cost_price": Decimal("100.50"),
        "cost_amount": Decimal("30150000"),
        "market_price": Decimal("101.25"),
        "market_value": Decimal("30375000"),
        "accrued_interest": Decimal("180000"),
        "unrealized_pnl": Decimal("225000"),
        "tfrs9_classification": "FVPL",
        "ecl_stage": 1,
        "ecl_provision": Decimal("0"),
        "pledged_quantity": Decimal("0"),
        "available_quantity": Decimal("30000"),
    },
]

MOCK_CASH_POSITIONS = [
    {
        "id": 1,
        "position_date": date(2025, 9, 1),
        "entity_id": "ENTITY001",
        "currency": "THB",
        "account_type": "BAHTNET",
        "account_id": "BAHTNET001",
        "opening_balance": Decimal("150000000"),
        "closing_balance": Decimal("145000000"),
        "inflows": Decimal("20000000"),
        "outflows": Decimal("25000000"),
        "net_movement": Decimal("-5000000"),
        "projected_t1_inflow": Decimal("10000000"),
        "projected_t1_outflow": Decimal("5000000"),
        "projected_t2_inflow": Decimal("50000000"),
        "projected_t2_outflow": Decimal("45000000"),
    },
    {
        "id": 2,
        "position_date": date(2025, 9, 1),
        "entity_id": "ENTITY001",
        "currency": "THB",
        "account_type": "TSD",
        "account_id": "TSD001",
        "opening_balance": Decimal("5000000"),
        "closing_balance": Decimal("5000000"),
        "inflows": Decimal("0"),
        "outflows": Decimal("0"),
        "net_movement": Decimal("0"),
        "projected_t1_inflow": Decimal("0"),
        "projected_t1_outflow": Decimal("0"),
        "projected_t2_inflow": Decimal("0"),
        "projected_t2_outflow": Decimal("0"),
    },
]

MOCK_LIMIT_UTILIZATIONS = [
    {
        "utilization_date": date(2025, 9, 1),
        "limit_id": "LIM001",
        "limit_name": "Kasikorn Bank Counterparty Limit",
        "limit_type": "COUNTERPARTY",
        "limit_amount": Decimal("500000000"),
        "utilized_amount": Decimal("350000000"),
        "available_amount": Decimal("150000000"),
        "utilization_pct": Decimal("70.00"),
        "is_warning": False,
        "is_breached": False,
        "warning_threshold_pct": Decimal("80"),
        "counterparty_name": "Kasikorn Bank",
        "security_name": None,
        "portfolio_name": None,
    },
    {
        "utilization_date": date(2025, 9, 1),
        "limit_id": "LIM002",
        "limit_name": "Corporate Bond Portfolio Limit",
        "limit_type": "PORTFOLIO",
        "limit_amount": Decimal("200000000"),
        "utilized_amount": Decimal("175000000"),
        "available_amount": Decimal("25000000"),
        "utilization_pct": Decimal("87.50"),
        "is_warning": True,
        "is_breached": False,
        "warning_threshold_pct": Decimal("80"),
        "counterparty_name": None,
        "security_name": None,
        "portfolio_name": "Corporate Bond Trading",
    },
]


# =============================================================================
# Bond Position Endpoints
# =============================================================================
@router.get("/bonds", response_model=List[BondPositionResponse])
async def list_bond_positions(
    position_date: Optional[date] = None,
    portfolio_id: Optional[str] = None,
    security_id: Optional[str] = None,
    isin: Optional[str] = None,
    tfrs9_classification: Optional[str] = None,
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    List bond positions with filtering.
    
    Query Parameters:
    - **position_date**: Position as-of date (default: today)
    - **portfolio_id**: Filter by portfolio
    - **security_id**: Filter by security
    - **isin**: Filter by ISIN
    - **tfrs9_classification**: Filter by TFRS 9 classification (FVPL, FVOCI, AC)
    """
    filtered = MOCK_BOND_POSITIONS.copy()
    
    if position_date:
        filtered = [p for p in filtered if p["position_date"] == position_date]
    if portfolio_id:
        filtered = [p for p in filtered if p["portfolio_id"] == portfolio_id]
    if security_id:
        filtered = [p for p in filtered if p["security_id"] == security_id]
    if isin:
        filtered = [p for p in filtered if p["isin"] == isin]
    if tfrs9_classification:
        filtered = [p for p in filtered if p["tfrs9_classification"] == tfrs9_classification]
    
    return filtered


@router.get("/bonds/{security_id}", response_model=BondPositionResponse)
async def get_bond_position(
    security_id: str,
    position_date: Optional[date] = None,
    portfolio_id: Optional[str] = None,
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    Get bond position for a specific security.
    """
    for pos in MOCK_BOND_POSITIONS:
        if pos["security_id"] == security_id:
            if portfolio_id and pos["portfolio_id"] != portfolio_id:
                continue
            return pos
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Position for security '{security_id}' not found"
    )


# =============================================================================
# Cash Position Endpoints
# =============================================================================
@router.get("/cash", response_model=List[CashPositionResponse])
async def list_cash_positions(
    position_date: Optional[date] = None,
    currency: Optional[str] = "THB",
    account_type: Optional[str] = None,
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    List cash positions.
    
    Query Parameters:
    - **position_date**: Position as-of date
    - **currency**: Currency code (default: THB)
    - **account_type**: Account type (BAHTNET, TSD, NOSTRO)
    """
    filtered = MOCK_CASH_POSITIONS.copy()
    
    if position_date:
        filtered = [p for p in filtered if p["position_date"] == position_date]
    if currency:
        filtered = [p for p in filtered if p["currency"] == currency]
    if account_type:
        filtered = [p for p in filtered if p["account_type"] == account_type]
    
    return filtered


@router.get("/cash/projection")
async def get_cash_projection(
    days_ahead: int = Query(5, ge=1, le=30),
    currency: str = "THB",
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    Get cash flow projection for the next N days.
    """
    # Mock projection data
    projections = []
    base_balance = Decimal("145000000")
    
    for i in range(days_ahead):
        proj_date = date(2025, 9, 2 + i)
        inflow = Decimal("10000000") + Decimal(str(i * 5000000))
        outflow = Decimal("8000000") + Decimal(str(i * 3000000))
        
        projections.append({
            "date": proj_date,
            "currency": currency,
            "opening_balance": base_balance,
            "projected_inflow": inflow,
            "projected_outflow": outflow,
            "net_change": inflow - outflow,
            "closing_balance": base_balance + (inflow - outflow),
        })
        base_balance = base_balance + (inflow - outflow)
    
    return projections


# =============================================================================
# Summary Endpoints
# =============================================================================
@router.get("/summary", response_model=PositionSummary)
async def get_position_summary(
    position_date: Optional[date] = None,
    entity_id: Optional[str] = None,
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    Get aggregated position summary.
    """
    pos_date = position_date or date(2025, 9, 1)
    
    # Aggregate bond positions
    total_bond_face = sum(p["face_value"] for p in MOCK_BOND_POSITIONS)
    total_bond_market = sum(p["market_value"] or 0 for p in MOCK_BOND_POSITIONS)
    total_bond_pnl = sum(p["unrealized_pnl"] for p in MOCK_BOND_POSITIONS)
    
    # Aggregate cash positions
    total_cash = sum(p["closing_balance"] for p in MOCK_CASH_POSITIONS)
    total_inflows = sum(p["inflows"] for p in MOCK_CASH_POSITIONS)
    total_outflows = sum(p["outflows"] for p in MOCK_CASH_POSITIONS)
    
    return PositionSummary(
        position_date=pos_date,
        entity_id=entity_id or "ENTITY001",
        total_bond_face_value=total_bond_face,
        total_bond_market_value=total_bond_market,
        total_bond_unrealized_pnl=total_bond_pnl,
        total_cash_balance=total_cash,
        total_cash_inflows=total_inflows,
        total_cash_outflows=total_outflows,
        total_pledged_value=Decimal("10000000"),
        total_received_value=Decimal("0"),
        total_margin_calls=Decimal("0"),
        total_ib_lending=Decimal("100000000"),
        total_ib_borrowing=Decimal("50000000"),
        net_ib_position=Decimal("50000000"),
        total_repo_borrowing=Decimal("200000000"),
        total_rrp_lending=Decimal("150000000"),
        net_repo_position=Decimal("-50000000"),
    )


# =============================================================================
# Limit Utilization Endpoints
# =============================================================================
@router.get("/limits", response_model=List[LimitUtilizationResponse])
async def list_limit_utilizations(
    limit_type: Optional[str] = None,
    is_warning: Optional[bool] = None,
    is_breached: Optional[bool] = None,
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    List limit utilizations.
    
    Query Parameters:
    - **limit_type**: Filter by type (COUNTERPARTY, PORTFOLIO, SECURITY)
    - **is_warning**: Filter for limits above warning threshold
    - **is_breached**: Filter for breached limits
    """
    filtered = MOCK_LIMIT_UTILIZATIONS.copy()
    
    if limit_type:
        filtered = [l for l in filtered if l["limit_type"] == limit_type]
    if is_warning is not None:
        filtered = [l for l in filtered if l["is_warning"] == is_warning]
    if is_breached is not None:
        filtered = [l for l in filtered if l["is_breached"] == is_breached]
    
    return filtered


@router.get("/limits/warnings", response_model=List[LimitUtilizationResponse])
async def get_limit_warnings(
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    Get limits that are at or above warning threshold.
    """
    warnings = [l for l in MOCK_LIMIT_UTILIZATIONS if l["is_warning"] or l["is_breached"]]
    return warnings


@router.get("/limits/breaches", response_model=List[LimitUtilizationResponse])
async def get_limit_breaches(
    current_user: UserInToken = Depends(
        require_permission(Permission.VIEW_LIMIT)
    ),
):
    """
    Get breached limits.
    
    Requires VIEW_LIMIT permission.
    """
    breaches = [l for l in MOCK_LIMIT_UTILIZATIONS if l["is_breached"]]
    return breaches
