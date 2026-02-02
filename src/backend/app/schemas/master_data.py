"""
Treasury Management System - Master Data Schemas
==================================================

Pydantic schemas for master data validation and serialization.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from enum import Enum


# =============================================================================
# Enums
# =============================================================================
class SecurityType(str, Enum):
    TBILL = "TBILL"
    TBOND = "TBOND"
    BOT = "BOT"
    SOE = "SOE"
    CORP = "CORP"


class IssuerType(str, Enum):
    GOV = "GOV"
    SOE = "SOE"
    CORP = "CORP"


class TFRS9Classification(str, Enum):
    FVPL = "FVPL"
    FVOCI = "FVOCI"
    AC = "AC"


# =============================================================================
# Security Schemas
# =============================================================================
class SecurityBase(BaseModel):
    """Base schema for security data"""
    isin: str = Field(..., min_length=12, max_length=12, description="12-character ISIN")
    symbol: Optional[str] = Field(None, max_length=20)
    security_name: str = Field(..., min_length=1, max_length=255)
    security_name_th: Optional[str] = None
    
    security_type: SecurityType
    issuer_type: IssuerType
    issuer_id: Optional[str] = None
    
    issue_date: date
    maturity_date: date
    coupon_rate: Decimal = Field(default=0, ge=0, le=100)
    coupon_frequency: int = Field(default=2, ge=0, le=12)
    day_count_convention: str = Field(default="ACT/365")
    
    face_value: Decimal = Field(default=100, gt=0)
    minimum_denomination: Decimal = Field(default=1000, gt=0)
    
    credit_rating: Optional[str] = None
    is_tradeable: bool = True
    is_repo_eligible: bool = True
    haircut_pct: Decimal = Field(default=0, ge=0, le=100)
    
    @field_validator('maturity_date')
    @classmethod
    def maturity_after_issue(cls, v, info):
        if 'issue_date' in info.data and v <= info.data['issue_date']:
            raise ValueError('Maturity date must be after issue date')
        return v


class SecurityCreate(SecurityBase):
    """Schema for creating a new security"""
    security_id: Optional[str] = None  # Auto-generated if not provided
    
    class Config:
        json_schema_extra = {
            "example": {
                "isin": "TH0623A3B702",
                "symbol": "LB236A",
                "security_name": "Government Bond 3.625% 2036",
                "security_type": "TBOND",
                "issuer_type": "GOV",
                "issue_date": "2023-06-15",
                "maturity_date": "2036-06-15",
                "coupon_rate": 3.625,
                "coupon_frequency": 2,
                "credit_rating": "BBB+",
                "haircut_pct": 2.0
            }
        }


class SecurityUpdate(BaseModel):
    """Schema for updating a security"""
    security_name: Optional[str] = None
    security_name_th: Optional[str] = None
    credit_rating: Optional[str] = None
    is_tradeable: Optional[bool] = None
    is_repo_eligible: Optional[bool] = None
    haircut_pct: Optional[Decimal] = None
    status: Optional[str] = None


class SecurityResponse(SecurityBase):
    """Schema for security response"""
    security_id: str
    status: str
    outstanding_amount: Optional[Decimal] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Computed fields
    tenor_days: Optional[int] = None
    is_zero_coupon: bool = False
    
    class Config:
        from_attributes = True


class SecurityList(BaseModel):
    """Schema for listing securities"""
    items: List[SecurityResponse]
    total: int


# =============================================================================
# Counterparty Schemas
# =============================================================================
class CounterpartyType(str, Enum):
    BANK = "BANK"
    BROKER = "BROKER"
    ASSET_MGR = "ASSET_MGR"
    INSURANCE = "INSURANCE"
    CORPORATE = "CORPORATE"
    BOT = "BOT"


class CounterpartyBase(BaseModel):
    """Base schema for counterparty"""
    counterparty_name: str = Field(..., min_length=1, max_length=255)
    counterparty_name_th: Optional[str] = None
    short_name: Optional[str] = Field(None, max_length=50)
    
    counterparty_type: CounterpartyType
    
    bot_code: Optional[str] = Field(None, max_length=13)
    swift_bic: Optional[str] = Field(None, max_length=11)
    tsd_participant_code: Optional[str] = None
    bahtnet_member_code: Optional[str] = None
    
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    
    has_isda: bool = False
    has_gmra: bool = False
    credit_limit: Optional[Decimal] = None


class CounterpartyCreate(CounterpartyBase):
    """Schema for creating a counterparty"""
    counterparty_id: Optional[str] = None
    entity_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "counterparty_name": "Kasikorn Bank PCL",
                "short_name": "KBANK",
                "counterparty_type": "BANK",
                "bot_code": "0040000000000",
                "swift_bic": "KASITHBK",
                "has_isda": True,
                "has_gmra": True,
                "credit_limit": 1000000000
            }
        }


class CounterpartyResponse(CounterpartyBase):
    """Schema for counterparty response"""
    counterparty_id: str
    entity_id: Optional[str] = None
    is_active: bool
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# =============================================================================
# Portfolio Schemas
# =============================================================================
class PortfolioType(str, Enum):
    TRADING = "TRADING"
    BANKING = "BANKING"
    HTM = "HTM"
    AFS = "AFS"
    FVPL = "FVPL"
    FVOCI = "FVOCI"


class PortfolioBase(BaseModel):
    """Base schema for portfolio"""
    portfolio_code: str = Field(..., min_length=1, max_length=20)
    portfolio_name: str = Field(..., min_length=1, max_length=255)
    portfolio_name_th: Optional[str] = None
    
    portfolio_type: PortfolioType
    entity_id: str
    department: Optional[str] = None
    
    tfrs9_classification: TFRS9Classification = TFRS9Classification.FVPL
    business_model: str = "TRADING"
    
    gl_account: Optional[str] = None
    cost_center: Optional[str] = None


class PortfolioCreate(PortfolioBase):
    """Schema for creating a portfolio"""
    portfolio_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "portfolio_code": "TRAD001",
                "portfolio_name": "Trading Book - Fixed Income",
                "portfolio_type": "TRADING",
                "entity_id": "ENTITY001",
                "tfrs9_classification": "FVPL",
                "business_model": "TRADING"
            }
        }


class PortfolioResponse(PortfolioBase):
    """Schema for portfolio response"""
    portfolio_id: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
