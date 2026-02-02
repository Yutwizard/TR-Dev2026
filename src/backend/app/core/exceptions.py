"""
Treasury Management System - Custom Exceptions
===============================================

Custom exception classes and global exception handlers.

Usage:
    from app.core.exceptions import ValidationError, NotFoundError
    
    raise ValidationError("Invalid trade date")
    raise NotFoundError("Trade", trade_id)
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# Base Exception
# =============================================================================
class TreasuryException(Exception):
    """Base exception for all TMS exceptions"""
    
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: Optional[Any] = None
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


# =============================================================================
# Authentication Exceptions
# =============================================================================
class AuthenticationError(TreasuryException):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            code="AUTH_FAILED",
            message=message,
            status_code=401
        )


class AuthorizationError(TreasuryException):
    """Raised when user lacks permission"""
    
    def __init__(self, message: str = "Access denied", required_permission: str = None):
        super().__init__(
            code="ACCESS_DENIED",
            message=message,
            status_code=403,
            details={"required_permission": required_permission}
        )


# =============================================================================
# Validation Exceptions
# =============================================================================
class ValidationError(TreasuryException):
    """Raised when validation fails"""
    
    def __init__(self, message: str, field: str = None, details: Any = None):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=400,
            details={"field": field, **(details or {})}
        )


class BusinessRuleError(TreasuryException):
    """Raised when a business rule is violated"""
    
    def __init__(self, rule: str, message: str, details: Any = None):
        super().__init__(
            code="BUSINESS_RULE_VIOLATION",
            message=message,
            status_code=400,
            details={"rule": rule, **(details or {})}
        )


# =============================================================================
# Resource Exceptions
# =============================================================================
class NotFoundError(TreasuryException):
    """Raised when a resource is not found"""
    
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource_type} with ID '{resource_id}' not found",
            status_code=404,
            details={"resource_type": resource_type, "resource_id": resource_id}
        )


class DuplicateError(TreasuryException):
    """Raised when a duplicate resource is detected"""
    
    def __init__(self, resource_type: str, identifier: str):
        super().__init__(
            code="DUPLICATE",
            message=f"{resource_type} with identifier '{identifier}' already exists",
            status_code=409,
            details={"resource_type": resource_type, "identifier": identifier}
        )


# =============================================================================
# Trade Exceptions
# =============================================================================
class TradeError(TreasuryException):
    """Base exception for trade-related errors"""
    pass


class LimitExceededError(TradeError):
    """Raised when a limit is exceeded"""
    
    def __init__(
        self,
        limit_type: str,
        limit_amount: float,
        requested_amount: float,
        available_amount: float
    ):
        super().__init__(
            code="LIMIT_EXCEEDED",
            message=f"{limit_type} limit exceeded",
            status_code=400,
            details={
                "limit_type": limit_type,
                "limit_amount": limit_amount,
                "requested_amount": requested_amount,
                "available_amount": available_amount,
                "excess_amount": requested_amount - available_amount
            }
        )


class SettlementDateError(TradeError):
    """Raised when settlement date is invalid"""
    
    def __init__(self, message: str, trade_date: str, settlement_date: str):
        super().__init__(
            code="INVALID_SETTLEMENT_DATE",
            message=message,
            status_code=400,
            details={
                "trade_date": trade_date,
                "settlement_date": settlement_date
            }
        )


class FourEyesViolationError(TradeError):
    """Raised when four-eyes principle is violated"""
    
    def __init__(self, user_id: str):
        super().__init__(
            code="FOUR_EYES_VIOLATION",
            message="You cannot approve your own action (four-eyes principle)",
            status_code=403,
            details={"user_id": user_id}
        )


class TradeStatusError(TradeError):
    """Raised when trade is in wrong status for an action"""
    
    def __init__(self, action: str, current_status: str, required_status: str):
        super().__init__(
            code="INVALID_TRADE_STATUS",
            message=f"Cannot {action}: trade is '{current_status}', must be '{required_status}'",
            status_code=400,
            details={
                "action": action,
                "current_status": current_status,
                "required_status": required_status
            }
        )


# =============================================================================
# Settlement Exceptions
# =============================================================================
class SettlementError(TreasuryException):
    """Base exception for settlement errors"""
    pass


class CollateralError(SettlementError):
    """Raised when collateral is insufficient"""
    
    def __init__(self, required: float, available: float):
        super().__init__(
            code="INSUFFICIENT_COLLATERAL",
            message=f"Insufficient collateral: required {required:,.2f}, available {available:,.2f}",
            status_code=400,
            details={
                "required": required,
                "available": available,
                "shortfall": required - available
            }
        )


class MarginCallError(SettlementError):
    """Raised when margin call fails"""
    
    def __init__(self, message: str, margin_call_id: str = None):
        super().__init__(
            code="MARGIN_CALL_ERROR",
            message=message,
            status_code=400,
            details={"margin_call_id": margin_call_id}
        )


# =============================================================================
# External Integration Exceptions
# =============================================================================
class ExternalServiceError(TreasuryException):
    """Raised when external service fails"""
    
    def __init__(self, service: str, message: str, details: Any = None):
        super().__init__(
            code="EXTERNAL_SERVICE_ERROR",
            message=f"{service}: {message}",
            status_code=502,
            details={"service": service, **(details or {})}
        )


class ThaiBMAError(ExternalServiceError):
    """Raised when ThaiBMA integration fails"""
    
    def __init__(self, message: str, trade_id: str = None):
        super().__init__(
            service="ThaiBMA",
            message=message,
            details={"trade_id": trade_id}
        )


# =============================================================================
# Exception Handlers
# =============================================================================
def setup_exception_handlers(app: FastAPI):
    """Setup global exception handlers for the FastAPI app"""
    
    @app.exception_handler(TreasuryException)
    async def treasury_exception_handler(request: Request, exc: TreasuryException):
        """Handle all TreasuryException subclasses"""
        logger.error(
            f"TreasuryException: {exc.code} - {exc.message}",
            extra={"details": exc.details, "path": request.url.path}
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details
                }
            }
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle standard HTTP exceptions"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": f"HTTP_{exc.status_code}",
                    "message": exc.detail
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions"""
        logger.exception(
            f"Unexpected error: {str(exc)}",
            extra={"path": request.url.path}
        )
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred. Please try again later."
                }
            }
        )
