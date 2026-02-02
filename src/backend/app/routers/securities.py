"""
Treasury Management System - Securities Router
================================================

API endpoints for security master data management.
"""

from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import uuid4

from app.database import get_async_db
from app.core.auth import get_current_active_user, UserInToken
from app.core.permissions import require_permission, Permission
from app.models.master_data import SecurityMaster
from app.schemas.master_data import (
    SecurityCreate, SecurityUpdate, SecurityResponse, SecurityList, SecurityType
)
from app.schemas.common import APIResponse, PaginatedResponse


router = APIRouter()


# =============================================================================
# Mock Data (for testing without database)
# =============================================================================
MOCK_SECURITIES = [
    {
        "security_id": "SEC001",
        "isin": "TH0623A3B702",
        "symbol": "LB236A",
        "security_name": "Government Bond 3.625% 2036",
        "security_name_th": "พันธบัตรรัฐบาล 3.625% 2579",
        "security_type": "TBOND",
        "issuer_type": "GOV",
        "issue_date": date(2023, 6, 15),
        "maturity_date": date(2036, 6, 15),
        "coupon_rate": 3.625,
        "coupon_frequency": 2,
        "day_count_convention": "ACT/365",
        "face_value": 100,
        "minimum_denomination": 1000,
        "credit_rating": "BBB+",
        "is_tradeable": True,
        "is_repo_eligible": True,
        "haircut_pct": 2.0,
        "outstanding_amount": 50000000000,
        "status": "ACTIVE",
        "created_at": "2023-06-15T00:00:00Z",
        "updated_at": None,
        "tenor_days": 4749,
        "is_zero_coupon": False
    },
    {
        "security_id": "SEC002",
        "isin": "TH0623A3C701",
        "symbol": "LB256A",
        "security_name": "Government Bond 2.875% 2025",
        "security_name_th": "พันธบัตรรัฐบาล 2.875% 2568",
        "security_type": "TBOND",
        "issuer_type": "GOV",
        "issue_date": date(2020, 6, 15),
        "maturity_date": date(2025, 12, 15),
        "coupon_rate": 2.875,
        "coupon_frequency": 2,
        "day_count_convention": "ACT/365",
        "face_value": 100,
        "minimum_denomination": 1000,
        "credit_rating": "BBB+",
        "is_tradeable": True,
        "is_repo_eligible": True,
        "haircut_pct": 1.5,
        "outstanding_amount": 30000000000,
        "status": "ACTIVE",
        "created_at": "2020-06-15T00:00:00Z",
        "updated_at": None,
        "tenor_days": 2009,
        "is_zero_coupon": False
    },
    {
        "security_id": "SEC003",
        "isin": "TH0858A3C501",
        "symbol": "TB25501A",
        "security_name": "T-Bill 91 Days Jan 2025",
        "security_name_th": "ตั๋วเงินคลัง 91 วัน ม.ค. 2568",
        "security_type": "TBILL",
        "issuer_type": "GOV",
        "issue_date": date(2024, 10, 15),
        "maturity_date": date(2025, 1, 15),
        "coupon_rate": 0,
        "coupon_frequency": 0,
        "day_count_convention": "ACT/365",
        "face_value": 100,
        "minimum_denomination": 1000,
        "credit_rating": "BBB+",
        "is_tradeable": True,
        "is_repo_eligible": True,
        "haircut_pct": 0.5,
        "outstanding_amount": 10000000000,
        "status": "ACTIVE",
        "created_at": "2024-10-15T00:00:00Z",
        "updated_at": None,
        "tenor_days": 92,
        "is_zero_coupon": True
    },
]


# =============================================================================
# Endpoints
# =============================================================================
@router.get("", response_model=SecurityList)
async def list_securities(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    security_type: Optional[str] = None,
    issuer_type: Optional[str] = None,
    is_tradeable: Optional[bool] = None,
    is_repo_eligible: Optional[bool] = None,
    search: Optional[str] = None,
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    List all securities with filtering and pagination.
    
    Query Parameters:
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **security_type**: Filter by type (TBILL, TBOND, BOT, SOE, CORP)
    - **issuer_type**: Filter by issuer (GOV, SOE, CORP)
    - **is_tradeable**: Filter by tradeable status
    - **is_repo_eligible**: Filter by repo eligibility
    - **search**: Search in ISIN, symbol, or name
    """
    # Filter mock data
    filtered = MOCK_SECURITIES.copy()
    
    if security_type:
        filtered = [s for s in filtered if s["security_type"] == security_type]
    if issuer_type:
        filtered = [s for s in filtered if s["issuer_type"] == issuer_type]
    if is_tradeable is not None:
        filtered = [s for s in filtered if s["is_tradeable"] == is_tradeable]
    if is_repo_eligible is not None:
        filtered = [s for s in filtered if s["is_repo_eligible"] == is_repo_eligible]
    if search:
        search_lower = search.lower()
        filtered = [s for s in filtered if 
                   search_lower in s["isin"].lower() or
                   search_lower in s.get("symbol", "").lower() or
                   search_lower in s["security_name"].lower()]
    
    # Paginate
    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    items = filtered[start:end]
    
    return SecurityList(items=items, total=total)


@router.get("/{security_id}", response_model=SecurityResponse)
async def get_security(
    security_id: str,
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    Get a specific security by ID.
    """
    for security in MOCK_SECURITIES:
        if security["security_id"] == security_id:
            return security
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Security with ID '{security_id}' not found"
    )


@router.get("/isin/{isin}", response_model=SecurityResponse)
async def get_security_by_isin(
    isin: str,
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    Get a specific security by ISIN.
    """
    for security in MOCK_SECURITIES:
        if security["isin"] == isin:
            return security
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Security with ISIN '{isin}' not found"
    )


@router.post("", response_model=SecurityResponse, status_code=status.HTTP_201_CREATED)
async def create_security(
    security: SecurityCreate,
    current_user: UserInToken = Depends(
        require_permission(Permission.CREATE_MASTER_DATA)
    ),
):
    """
    Create a new security.
    
    Requires CREATE_MASTER_DATA permission.
    """
    # Check for duplicate ISIN
    for existing in MOCK_SECURITIES:
        if existing["isin"] == security.isin:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Security with ISIN '{security.isin}' already exists"
            )
    
    # Create new security
    new_security = {
        "security_id": security.security_id or f"SEC{uuid4().hex[:8].upper()}",
        **security.model_dump(),
        "status": "ACTIVE",
        "created_at": "2025-09-01T00:00:00Z",
        "updated_at": None,
        "tenor_days": (security.maturity_date - security.issue_date).days,
        "is_zero_coupon": security.coupon_rate == 0
    }
    
    MOCK_SECURITIES.append(new_security)
    return new_security


@router.put("/{security_id}", response_model=SecurityResponse)
async def update_security(
    security_id: str,
    updates: SecurityUpdate,
    current_user: UserInToken = Depends(
        require_permission(Permission.MODIFY_MASTER_DATA)
    ),
):
    """
    Update a security.
    
    Requires MODIFY_MASTER_DATA permission.
    Only certain fields can be updated.
    """
    for i, security in enumerate(MOCK_SECURITIES):
        if security["security_id"] == security_id:
            # Apply updates
            update_data = updates.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if value is not None:
                    MOCK_SECURITIES[i][key] = value
            MOCK_SECURITIES[i]["updated_at"] = "2025-09-01T00:00:00Z"
            return MOCK_SECURITIES[i]
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Security with ID '{security_id}' not found"
    )


@router.get("/types/list", response_model=List[dict])
async def get_security_types():
    """
    Get list of available security types.
    """
    return [
        {"code": "TBILL", "name": "Treasury Bill", "issuer": "GOV"},
        {"code": "TBOND", "name": "Treasury Bond", "issuer": "GOV"},
        {"code": "BOT", "name": "BOT Bond", "issuer": "GOV"},
        {"code": "SOE", "name": "State Enterprise Bond", "issuer": "SOE"},
        {"code": "CORP", "name": "Corporate Bond", "issuer": "CORP"},
    ]


@router.get("/repo-eligible/list", response_model=SecurityList)
async def get_repo_eligible_securities(
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    Get list of repo-eligible securities for collateral selection.
    """
    eligible = [s for s in MOCK_SECURITIES if s["is_repo_eligible"]]
    return SecurityList(items=eligible, total=len(eligible))
