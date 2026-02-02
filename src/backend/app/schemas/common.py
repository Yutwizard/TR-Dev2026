"""
Treasury Management System - Common Schemas
=============================================

Common Pydantic schemas used across the application.
"""

from datetime import datetime
from typing import Optional, List, Generic, TypeVar, Any
from pydantic import BaseModel, Field


T = TypeVar('T')


# =============================================================================
# Pagination
# =============================================================================
class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints"""
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(default=None, description="Field to sort by")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper"""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
    
    @classmethod
    def create(cls, items: List[T], total: int, page: int, page_size: int):
        total_pages = (total + page_size - 1) // page_size
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )


# =============================================================================
# API Response Wrappers
# =============================================================================
class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper"""
    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Error response format"""
    success: bool = False
    error: dict = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid input",
                    "details": {"field": "amount", "error": "must be positive"}
                }
            }
        }


# =============================================================================
# Filter Schemas
# =============================================================================
class DateRangeFilter(BaseModel):
    """Date range filter"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class AmountRangeFilter(BaseModel):
    """Amount range filter"""
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None


# =============================================================================
# Status Schemas
# =============================================================================
class StatusUpdate(BaseModel):
    """Generic status update request"""
    status: str
    reason: Optional[str] = None


class ApprovalRequest(BaseModel):
    """Approval/Rejection request"""
    approved: bool
    reason: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "approved": True,
                "reason": "Verified and approved"
            }
        }


# =============================================================================
# Audit Schemas
# =============================================================================
class AuditInfo(BaseModel):
    """Audit information for responses"""
    created_at: datetime
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None


# =============================================================================
# Common Field Validators
# =============================================================================
class ISINField(BaseModel):
    """ISIN validation"""
    isin: str = Field(
        ..., 
        min_length=12, 
        max_length=12,
        pattern="^[A-Z]{2}[A-Z0-9]{9}[0-9]$",
        description="12-character ISIN code"
    )


class CurrencyField(BaseModel):
    """Currency code validation"""
    currency: str = Field(
        default="THB",
        min_length=3,
        max_length=3,
        pattern="^[A-Z]{3}$",
        description="3-letter currency code"
    )
