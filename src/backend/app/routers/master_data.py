"""
Treasury Management System - Master Data Router
================================================

CRUD endpoints for master data tables:
- /securities - Security Master
- /counterparties - Counterparty Master
- /portfolios - Portfolio Master
- /entities - Entity Master
"""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.master_data import (
    EntityMaster, SecurityMaster, CounterpartyMaster, 
    PortfolioMaster, HaircutMatrix
)


router = APIRouter()


# ==================== PYDANTIC SCHEMAS ====================

# Entity Schemas
class EntityBase(BaseModel):
    entity_name: str
    entity_name_th: Optional[str] = None
    entity_type: str
    parent_entity_id: Optional[str] = None
    bot_code: Optional[str] = None
    swift_bic: Optional[str] = None
    tax_id: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True


class EntityCreate(EntityBase):
    entity_id: str


class EntityUpdate(BaseModel):
    entity_name: Optional[str] = None
    entity_name_th: Optional[str] = None
    entity_type: Optional[str] = None
    bot_code: Optional[str] = None
    swift_bic: Optional[str] = None
    is_active: Optional[bool] = None


class EntityResponse(EntityBase):
    entity_id: str
    
    class Config:
        from_attributes = True


# Security Schemas
class SecurityBase(BaseModel):
    isin: str
    symbol: Optional[str] = None
    security_name: str
    security_name_th: Optional[str] = None
    security_type: str
    issuer_type: str
    issuer_id: Optional[str] = None
    issue_date: date
    maturity_date: date
    coupon_rate: Decimal = 0
    coupon_frequency: int = 2
    day_count_convention: str = "ACT/365"
    face_value: Decimal = 100
    outstanding_amount: Optional[Decimal] = None
    minimum_denomination: Decimal = 1000
    credit_rating: Optional[str] = None
    rating_agency: Optional[str] = None
    is_tradeable: bool = True
    is_repo_eligible: bool = True
    haircut_pct: Decimal = 0
    status: str = "ACTIVE"


class SecurityCreate(SecurityBase):
    security_id: str


class SecurityUpdate(BaseModel):
    security_name: Optional[str] = None
    credit_rating: Optional[str] = None
    rating_agency: Optional[str] = None
    is_tradeable: Optional[bool] = None
    is_repo_eligible: Optional[bool] = None
    haircut_pct: Optional[Decimal] = None
    outstanding_amount: Optional[Decimal] = None
    status: Optional[str] = None


class SecurityResponse(SecurityBase):
    security_id: str
    is_zero_coupon: bool = False
    tenor_days: int = 0
    
    class Config:
        from_attributes = True


# Counterparty Schemas
class CounterpartyBase(BaseModel):
    counterparty_name: str
    counterparty_name_th: Optional[str] = None
    short_name: Optional[str] = None
    counterparty_type: str
    entity_id: Optional[str] = None
    bot_code: Optional[str] = None
    swift_bic: Optional[str] = None
    tsd_participant_code: Optional[str] = None
    bahtnet_member_code: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    has_isda: bool = False
    has_gmra: bool = False
    credit_limit: Optional[Decimal] = None
    is_active: bool = True
    status: str = "ACTIVE"


class CounterpartyCreate(CounterpartyBase):
    counterparty_id: str


class CounterpartyUpdate(BaseModel):
    counterparty_name: Optional[str] = None
    short_name: Optional[str] = None
    swift_bic: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    has_isda: Optional[bool] = None
    has_gmra: Optional[bool] = None
    credit_limit: Optional[Decimal] = None
    is_active: Optional[bool] = None
    status: Optional[str] = None


class CounterpartyResponse(CounterpartyBase):
    counterparty_id: str
    
    class Config:
        from_attributes = True


# Portfolio Schemas
class PortfolioBase(BaseModel):
    portfolio_code: str
    portfolio_name: str
    portfolio_name_th: Optional[str] = None
    portfolio_type: str
    entity_id: str
    department: Optional[str] = None
    tfrs9_classification: str = "FVPL"
    business_model: str = "TRADING"
    gl_account: Optional[str] = None
    cost_center: Optional[str] = None
    is_active: bool = True


class PortfolioCreate(PortfolioBase):
    portfolio_id: str


class PortfolioUpdate(BaseModel):
    portfolio_name: Optional[str] = None
    portfolio_name_th: Optional[str] = None
    tfrs9_classification: Optional[str] = None
    business_model: Optional[str] = None
    gl_account: Optional[str] = None
    cost_center: Optional[str] = None
    is_active: Optional[bool] = None


class PortfolioResponse(PortfolioBase):
    portfolio_id: str
    
    class Config:
        from_attributes = True


# Haircut Schemas
class HaircutBase(BaseModel):
    security_type: str
    credit_rating: Optional[str] = None
    tenor_from_days: int = 0
    tenor_to_days: int = 99999
    haircut_pct: Decimal
    effective_date: date
    expiry_date: Optional[date] = None


class HaircutCreate(HaircutBase):
    pass


class HaircutResponse(HaircutBase):
    id: int
    
    class Config:
        from_attributes = True


# ==================== ENTITY ENDPOINTS ====================

@router.get("/entities", response_model=List[EntityResponse], tags=["Master Data"])
async def list_entities(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    db: Session = Depends(get_db)
):
    """List all entities with optional filters"""
    query = db.query(EntityMaster)
    
    if is_active is not None:
        query = query.filter(EntityMaster.is_active == is_active)
    if entity_type:
        query = query.filter(EntityMaster.entity_type == entity_type)
    
    return query.all()


@router.get("/entities/{entity_id}", response_model=EntityResponse, tags=["Master Data"])
async def get_entity(entity_id: str, db: Session = Depends(get_db)):
    """Get entity by ID"""
    entity = db.query(EntityMaster).filter(EntityMaster.entity_id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity


@router.post("/entities", response_model=EntityResponse, status_code=status.HTTP_201_CREATED, tags=["Master Data"])
async def create_entity(entity: EntityCreate, db: Session = Depends(get_db)):
    """Create a new entity"""
    existing = db.query(EntityMaster).filter(EntityMaster.entity_id == entity.entity_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Entity ID already exists")
    
    db_entity = EntityMaster(**entity.model_dump())
    db.add(db_entity)
    db.commit()
    db.refresh(db_entity)
    return db_entity


@router.put("/entities/{entity_id}", response_model=EntityResponse, tags=["Master Data"])
async def update_entity(entity_id: str, entity: EntityUpdate, db: Session = Depends(get_db)):
    """Update an entity"""
    db_entity = db.query(EntityMaster).filter(EntityMaster.entity_id == entity_id).first()
    if not db_entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    update_data = entity.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_entity, key, value)
    
    db.commit()
    db.refresh(db_entity)
    return db_entity


# ==================== SECURITY ENDPOINTS ====================

@router.get("/securities", response_model=List[SecurityResponse], tags=["Master Data"])
async def list_securities(
    security_type: Optional[str] = Query(None, description="Filter by security type"),
    status: Optional[str] = Query("ACTIVE", description="Filter by status"),
    is_tradeable: Optional[bool] = Query(None, description="Filter by tradeable"),
    is_repo_eligible: Optional[bool] = Query(None, description="Filter for repo eligibility"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List all securities with optional filters"""
    query = db.query(SecurityMaster)
    
    if security_type:
        query = query.filter(SecurityMaster.security_type == security_type)
    if status:
        query = query.filter(SecurityMaster.status == status)
    if is_tradeable is not None:
        query = query.filter(SecurityMaster.is_tradeable == is_tradeable)
    if is_repo_eligible is not None:
        query = query.filter(SecurityMaster.is_repo_eligible == is_repo_eligible)
    
    return query.offset(skip).limit(limit).all()


@router.get("/securities/{security_id}", response_model=SecurityResponse, tags=["Master Data"])
async def get_security(security_id: str, db: Session = Depends(get_db)):
    """Get security by ID"""
    security = db.query(SecurityMaster).filter(SecurityMaster.security_id == security_id).first()
    if not security:
        raise HTTPException(status_code=404, detail="Security not found")
    return security


@router.get("/securities/isin/{isin}", response_model=SecurityResponse, tags=["Master Data"])
async def get_security_by_isin(isin: str, db: Session = Depends(get_db)):
    """Get security by ISIN"""
    security = db.query(SecurityMaster).filter(SecurityMaster.isin == isin).first()
    if not security:
        raise HTTPException(status_code=404, detail="Security not found")
    return security


@router.post("/securities", response_model=SecurityResponse, status_code=status.HTTP_201_CREATED, tags=["Master Data"])
async def create_security(security: SecurityCreate, db: Session = Depends(get_db)):
    """Create a new security"""
    existing = db.query(SecurityMaster).filter(
        (SecurityMaster.security_id == security.security_id) | 
        (SecurityMaster.isin == security.isin)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Security ID or ISIN already exists")
    
    db_security = SecurityMaster(**security.model_dump())
    db.add(db_security)
    db.commit()
    db.refresh(db_security)
    return db_security


@router.put("/securities/{security_id}", response_model=SecurityResponse, tags=["Master Data"])
async def update_security(security_id: str, security: SecurityUpdate, db: Session = Depends(get_db)):
    """Update a security"""
    db_security = db.query(SecurityMaster).filter(SecurityMaster.security_id == security_id).first()
    if not db_security:
        raise HTTPException(status_code=404, detail="Security not found")
    
    update_data = security.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_security, key, value)
    
    db.commit()
    db.refresh(db_security)
    return db_security


# ==================== COUNTERPARTY ENDPOINTS ====================

@router.get("/counterparties", response_model=List[CounterpartyResponse], tags=["Master Data"])
async def list_counterparties(
    counterparty_type: Optional[str] = Query(None, description="Filter by type (BANK, BROKER, ASSET_MGR, etc.)"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    has_gmra: Optional[bool] = Query(None, description="Filter by GMRA agreement"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List all counterparties with optional filters"""
    query = db.query(CounterpartyMaster)
    
    if counterparty_type:
        query = query.filter(CounterpartyMaster.counterparty_type == counterparty_type)
    if is_active is not None:
        query = query.filter(CounterpartyMaster.is_active == is_active)
    if has_gmra is not None:
        query = query.filter(CounterpartyMaster.has_gmra == has_gmra)
    
    return query.offset(skip).limit(limit).all()


@router.get("/counterparties/{counterparty_id}", response_model=CounterpartyResponse, tags=["Master Data"])
async def get_counterparty(counterparty_id: str, db: Session = Depends(get_db)):
    """Get counterparty by ID"""
    counterparty = db.query(CounterpartyMaster).filter(
        CounterpartyMaster.counterparty_id == counterparty_id
    ).first()
    if not counterparty:
        raise HTTPException(status_code=404, detail="Counterparty not found")
    return counterparty


@router.post("/counterparties", response_model=CounterpartyResponse, status_code=status.HTTP_201_CREATED, tags=["Master Data"])
async def create_counterparty(counterparty: CounterpartyCreate, db: Session = Depends(get_db)):
    """Create a new counterparty"""
    existing = db.query(CounterpartyMaster).filter(
        CounterpartyMaster.counterparty_id == counterparty.counterparty_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Counterparty ID already exists")
    
    db_counterparty = CounterpartyMaster(**counterparty.model_dump())
    db.add(db_counterparty)
    db.commit()
    db.refresh(db_counterparty)
    return db_counterparty


@router.put("/counterparties/{counterparty_id}", response_model=CounterpartyResponse, tags=["Master Data"])
async def update_counterparty(
    counterparty_id: str, 
    counterparty: CounterpartyUpdate, 
    db: Session = Depends(get_db)
):
    """Update a counterparty"""
    db_counterparty = db.query(CounterpartyMaster).filter(
        CounterpartyMaster.counterparty_id == counterparty_id
    ).first()
    if not db_counterparty:
        raise HTTPException(status_code=404, detail="Counterparty not found")
    
    update_data = counterparty.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_counterparty, key, value)
    
    db.commit()
    db.refresh(db_counterparty)
    return db_counterparty


# ==================== PORTFOLIO ENDPOINTS ====================

@router.get("/portfolios", response_model=List[PortfolioResponse], tags=["Master Data"])
async def list_portfolios(
    portfolio_type: Optional[str] = Query(None, description="Filter by type (TRADING, BANKING)"),
    tfrs9_classification: Optional[str] = Query(None, description="Filter by TFRS9 classification"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    entity_id: Optional[str] = Query(None, description="Filter by entity"),
    db: Session = Depends(get_db)
):
    """List all portfolios with optional filters"""
    query = db.query(PortfolioMaster)
    
    if portfolio_type:
        query = query.filter(PortfolioMaster.portfolio_type == portfolio_type)
    if tfrs9_classification:
        query = query.filter(PortfolioMaster.tfrs9_classification == tfrs9_classification)
    if is_active is not None:
        query = query.filter(PortfolioMaster.is_active == is_active)
    if entity_id:
        query = query.filter(PortfolioMaster.entity_id == entity_id)
    
    return query.all()


@router.get("/portfolios/{portfolio_id}", response_model=PortfolioResponse, tags=["Master Data"])
async def get_portfolio(portfolio_id: str, db: Session = Depends(get_db)):
    """Get portfolio by ID"""
    portfolio = db.query(PortfolioMaster).filter(PortfolioMaster.portfolio_id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio


@router.post("/portfolios", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED, tags=["Master Data"])
async def create_portfolio(portfolio: PortfolioCreate, db: Session = Depends(get_db)):
    """Create a new portfolio"""
    existing = db.query(PortfolioMaster).filter(
        (PortfolioMaster.portfolio_id == portfolio.portfolio_id) |
        (PortfolioMaster.portfolio_code == portfolio.portfolio_code)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Portfolio ID or Code already exists")
    
    db_portfolio = PortfolioMaster(**portfolio.model_dump())
    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio


@router.put("/portfolios/{portfolio_id}", response_model=PortfolioResponse, tags=["Master Data"])
async def update_portfolio(portfolio_id: str, portfolio: PortfolioUpdate, db: Session = Depends(get_db)):
    """Update a portfolio"""
    db_portfolio = db.query(PortfolioMaster).filter(PortfolioMaster.portfolio_id == portfolio_id).first()
    if not db_portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    update_data = portfolio.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_portfolio, key, value)
    
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio


# ==================== HAIRCUT MATRIX ENDPOINTS ====================

@router.get("/haircuts", response_model=List[HaircutResponse], tags=["Master Data"])
async def list_haircuts(
    security_type: Optional[str] = Query(None, description="Filter by security type"),
    credit_rating: Optional[str] = Query(None, description="Filter by credit rating"),
    db: Session = Depends(get_db)
):
    """List all haircut configurations"""
    query = db.query(HaircutMatrix)
    
    if security_type:
        query = query.filter(HaircutMatrix.security_type == security_type)
    if credit_rating:
        query = query.filter(HaircutMatrix.credit_rating == credit_rating)
    
    return query.all()


@router.get("/haircuts/lookup", response_model=HaircutResponse, tags=["Master Data"])
async def lookup_haircut(
    security_type: str = Query(..., description="Security type"),
    credit_rating: str = Query(..., description="Credit rating"),
    tenor_days: int = Query(..., description="Tenor in days"),
    as_of_date: Optional[date] = Query(None, description="Effective date (default: today)"),
    db: Session = Depends(get_db)
):
    """
    Look up the applicable haircut for a given security type, rating, and tenor.
    Returns the haircut configuration that matches the criteria.
    """
    if as_of_date is None:
        as_of_date = date.today()
    
    haircut = db.query(HaircutMatrix).filter(
        HaircutMatrix.security_type == security_type,
        HaircutMatrix.credit_rating == credit_rating,
        HaircutMatrix.tenor_from_days <= tenor_days,
        HaircutMatrix.tenor_to_days >= tenor_days,
        HaircutMatrix.effective_date <= as_of_date,
        (HaircutMatrix.expiry_date.is_(None) | (HaircutMatrix.expiry_date > as_of_date))
    ).first()
    
    if not haircut:
        raise HTTPException(
            status_code=404, 
            detail=f"No haircut found for {security_type}/{credit_rating} with tenor {tenor_days} days"
        )
    return haircut


@router.post("/haircuts", response_model=HaircutResponse, status_code=status.HTTP_201_CREATED, tags=["Master Data"])
async def create_haircut(haircut: HaircutCreate, db: Session = Depends(get_db)):
    """Create a new haircut configuration"""
    db_haircut = HaircutMatrix(**haircut.model_dump())
    db.add(db_haircut)
    db.commit()
    db.refresh(db_haircut)
    return db_haircut
