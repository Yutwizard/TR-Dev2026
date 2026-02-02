"""
Treasury Management System - Bond Trade Service
================================================

Core business logic for bond trading:
- Trade validation (business day, T+2, limits)
- Amount calculations (principal, accrued interest)
- ThaiBMA reporting
- Position updates
"""

from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, List, Dict, Any, Tuple
from uuid import uuid4
import logging

from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, or_

from app.models.transactions import BondTrade, TradeStatus, TradeSide
from app.models.master_data import SecurityMaster, CounterpartyMaster, PortfolioMaster
from app.models.limits import LimitDefinition, LimitUtilization, LimitBreach
from app.services.calendar_service import (
    calculate_settlement_date, is_thai_business_day, get_calendar_service
)

logger = logging.getLogger(__name__)


# =============================================================================
# Trade Reference Generation
# =============================================================================

def generate_trade_ref(db: Session, prefix: str = "BND") -> str:
    """
    Generate a unique trade reference.
    Format: BND + YYYYMMDD + 3-digit sequence
    Example: BND20260202001
    """
    today = date.today()
    date_str = today.strftime("%Y%m%d")
    
    # Count today's trades
    count = db.query(func.count(BondTrade.trade_id)).filter(
        func.date(BondTrade.created_at) == today
    ).scalar() or 0
    
    seq = count + 1
    return f"{prefix}{date_str}{seq:03d}"


# =============================================================================
# Trade Amount Calculations
# =============================================================================

def calculate_accrued_interest(
    security: SecurityMaster,
    face_value: Decimal,
    settlement_date: date
) -> Decimal:
    """
    Calculate accrued interest for a bond.
    
    Uses ACT/365 day count convention (Thai market standard).
    
    Formula: Face Value × Coupon Rate × Days / 365
    
    Args:
        security: Security master record
        face_value: Face value of the trade
        settlement_date: Settlement date for the trade
        
    Returns:
        Accrued interest amount
    """
    if security.coupon_rate == 0:
        # Zero coupon bond (T-Bill)
        return Decimal("0")
    
    # Get last coupon date
    coupon_freq = security.coupon_frequency or 2  # Semi-annual default
    days_per_period = 365 // coupon_freq
    
    # Calculate days since last coupon
    # Simplified: assume coupon dates align with issue date
    issue_date = security.issue_date
    days_since_issue = (settlement_date - issue_date).days
    days_since_last_coupon = days_since_issue % days_per_period
    
    # Calculate accrued interest
    annual_coupon = face_value * (security.coupon_rate / Decimal("100"))
    daily_accrual = annual_coupon / Decimal("365")
    accrued = daily_accrual * Decimal(str(days_since_last_coupon))
    
    return accrued.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_trade_amounts(
    face_value: Decimal,
    clean_price: Decimal,
    accrued_interest: Decimal,
    trade_side: str,
    withholding_tax_rate: Decimal = Decimal("15")  # 15% WHT on interest for non-resident
) -> Dict[str, Decimal]:
    """
    Calculate all trade amounts.
    
    Args:
        face_value: Face value (par value)
        clean_price: Clean price as percentage (e.g., 99.50)
        accrued_interest: Pre-calculated accrued interest
        trade_side: BUY or SELL
        withholding_tax_rate: WHT rate for interest (default 15%)
        
    Returns:
        Dictionary with all calculated amounts
    """
    # Principal = Face Value × Clean Price / 100
    principal = (face_value * clean_price / Decimal("100")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    
    # Dirty Price = Clean Price + Accrued Interest per 100
    accrued_per_100 = (accrued_interest / face_value * Decimal("100")).quantize(
        Decimal("0.000001"), rounding=ROUND_HALF_UP
    )
    dirty_price = clean_price + accrued_per_100
    
    # Settlement Amount
    if trade_side == "BUY":
        # Buyer pays principal + accrued
        settlement_amount = principal + accrued_interest
        withholding_tax = Decimal("0")  # No WHT on buy
    else:
        # Seller receives principal + accrued
        settlement_amount = principal + accrued_interest
        # WHT on interest for sell (if applicable)
        withholding_tax = Decimal("0")  # WHT typically on coupon, not accrued
    
    return {
        "principal_amount": principal,
        "accrued_interest": accrued_interest,
        "dirty_price": dirty_price.quantize(Decimal("0.000001")),
        "settlement_amount": settlement_amount.quantize(Decimal("0.01")),
        "withholding_tax": withholding_tax,
        "quantity": face_value / Decimal("1000"),  # Units (par 1000)
    }


# =============================================================================
# Trade Validation
# =============================================================================

def validate_trade_date(trade_date: date) -> Tuple[bool, Optional[str]]:
    """
    Validate that trade date is a valid Thai business day.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if trade_date > date.today():
        return False, f"Trade date {trade_date} cannot be in the future"
    
    if not is_thai_business_day(trade_date):
        return False, f"Trade date {trade_date} is not a Thai business day"
    
    return True, None


def validate_settlement_date(
    trade_date: date, 
    settlement_date: date,
    min_days: int = 2
) -> Tuple[bool, Optional[str]]:
    """
    Validate settlement date is at least T+N business days.
    
    Thai bond market standard is T+2.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    min_settlement = calculate_settlement_date(trade_date, days=min_days)
    
    if settlement_date < min_settlement:
        return False, f"Settlement date must be at least T+{min_days} ({min_settlement})"
    
    if not is_thai_business_day(settlement_date):
        return False, f"Settlement date {settlement_date} is not a Thai business day"
    
    return True, None


def validate_price_reasonableness(
    clean_price: Decimal,
    min_price: Decimal = Decimal("50"),
    max_price: Decimal = Decimal("200")
) -> Tuple[bool, Optional[str]]:
    """
    Validate price is within reasonable bounds.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if clean_price < min_price or clean_price > max_price:
        return False, f"Clean price {clean_price} is outside reasonable range ({min_price}-{max_price})"
    
    return True, None


def validate_security_tradeable(
    db: Session,
    security_id: str
) -> Tuple[SecurityMaster, Optional[str]]:
    """
    Validate security exists and is tradeable.
    
    Returns:
        Tuple of (security, error_message)
    """
    security = db.query(SecurityMaster).filter(
        SecurityMaster.security_id == security_id
    ).first()
    
    if not security:
        return None, f"Security {security_id} not found"
    
    if security.status != "ACTIVE":
        return None, f"Security {security.isin} is not active (status: {security.status})"
    
    if not security.is_tradeable:
        return None, f"Security {security.isin} is not tradeable"
    
    if security.maturity_date <= date.today():
        return None, f"Security {security.isin} has already matured ({security.maturity_date})"
    
    return security, None


def validate_counterparty_active(
    db: Session,
    counterparty_id: str
) -> Tuple[CounterpartyMaster, Optional[str]]:
    """
    Validate counterparty exists and is active.
    
    Returns:
        Tuple of (counterparty, error_message)
    """
    counterparty = db.query(CounterpartyMaster).filter(
        CounterpartyMaster.counterparty_id == counterparty_id
    ).first()
    
    if not counterparty:
        return None, f"Counterparty {counterparty_id} not found"
    
    if not counterparty.is_active:
        return None, f"Counterparty {counterparty.short_name} is not active"
    
    return counterparty, None


# =============================================================================
# Limit Checking
# =============================================================================

def check_counterparty_limit(
    db: Session,
    counterparty_id: str,
    trade_amount: Decimal,
    entity_id: str = "ENT001"
) -> Tuple[bool, Dict[str, Any]]:
    """
    Check if trade amount is within counterparty limits.
    
    Returns:
        Tuple of (is_within_limit, limit_details)
    """
    today = date.today()
    
    # Find applicable limit
    limit = db.query(LimitDefinition).filter(
        LimitDefinition.counterparty_id == counterparty_id,
        LimitDefinition.entity_id == entity_id,
        LimitDefinition.limit_type == "COUNTERPARTY",
        LimitDefinition.status == "APPROVED",
        LimitDefinition.effective_date <= today,
        or_(LimitDefinition.expiry_date.is_(None), LimitDefinition.expiry_date > today)
    ).first()
    
    if not limit:
        # No limit defined - allow trade with warning
        logger.warning(f"No counterparty limit defined for {counterparty_id}")
        return True, {
            "has_limit": False,
            "message": "No counterparty limit defined"
        }
    
    # Get current utilization
    utilization = db.query(LimitUtilization).filter(
        LimitUtilization.limit_id == limit.limit_id,
        LimitUtilization.utilization_date == today
    ).first()
    
    current_utilized = utilization.utilized_amount if utilization else Decimal("0")
    new_utilized = current_utilized + trade_amount
    utilization_pct = (new_utilized / limit.limit_amount * 100).quantize(Decimal("0.01"))
    
    limit_details = {
        "has_limit": True,
        "limit_id": limit.limit_id,
        "limit_amount": limit.limit_amount,
        "current_utilized": current_utilized,
        "trade_amount": trade_amount,
        "new_utilized": new_utilized,
        "utilization_pct": utilization_pct,
        "available": limit.limit_amount - current_utilized,
        "warning_threshold": limit.warning_threshold_pct,
        "is_warning": utilization_pct >= limit.warning_threshold_pct,
        "is_breached": utilization_pct > Decimal("100")
    }
    
    if limit_details["is_breached"]:
        return False, limit_details
    
    return True, limit_details


def update_limit_utilization(
    db: Session,
    limit_id: str,
    trade_amount: Decimal,
    trade_ref: str
) -> LimitUtilization:
    """
    Update limit utilization after trade booking.
    """
    today = date.today()
    
    # Get limit definition
    limit = db.query(LimitDefinition).filter(
        LimitDefinition.limit_id == limit_id
    ).first()
    
    if not limit:
        raise ValueError(f"Limit {limit_id} not found")
    
    # Get or create utilization record
    utilization = db.query(LimitUtilization).filter(
        LimitUtilization.limit_id == limit_id,
        LimitUtilization.utilization_date == today
    ).first()
    
    if not utilization:
        utilization = LimitUtilization(
            utilization_date=today,
            limit_id=limit_id,
            utilized_amount=Decimal("0"),
            available_amount=limit.limit_amount,
            utilization_pct=Decimal("0")
        )
        db.add(utilization)
    
    # Update amounts
    utilization.utilized_amount += trade_amount
    utilization.available_amount = limit.limit_amount - utilization.utilized_amount
    utilization.utilization_pct = (
        utilization.utilized_amount / limit.limit_amount * 100
    ).quantize(Decimal("0.01"))
    utilization.is_warning = utilization.utilization_pct >= limit.warning_threshold_pct
    utilization.is_breached = utilization.utilization_pct > Decimal("100")
    utilization.last_trade_ref = trade_ref
    
    # Log breach if occurred
    if utilization.is_breached:
        breach = LimitBreach(
            breach_date=datetime.now(),
            limit_id=limit_id,
            limit_amount=limit.limit_amount,
            utilized_amount=utilization.utilized_amount,
            breach_amount=utilization.utilized_amount - limit.limit_amount,
            breach_pct=utilization.utilization_pct,
            trade_ref=trade_ref,
            trade_type="BOND",
            status="OPEN"
        )
        db.add(breach)
        logger.warning(f"Limit breach recorded for {limit_id}: {utilization.utilization_pct}%")
    
    return utilization


# =============================================================================
# Bond Trade Service
# =============================================================================

class BondTradeService:
    """
    Service for managing bond trades.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_trade(
        self,
        security_id: str,
        counterparty_id: str,
        portfolio_id: str,
        trade_side: str,
        trade_date: date,
        settlement_date: date,
        face_value: Decimal,
        clean_price: Decimal,
        yield_rate: Optional[Decimal] = None,
        trader_id: str = None,
        entity_id: str = "ENT001",
        **kwargs
    ) -> Tuple[BondTrade, Dict[str, Any]]:
        """
        Create a new bond trade with full validation.
        
        Returns:
            Tuple of (trade, validation_details)
        """
        validation_details = {"errors": [], "warnings": []}
        
        # Validate trade date
        valid, error = validate_trade_date(trade_date)
        if not valid:
            validation_details["errors"].append(error)
        
        # Validate settlement date
        valid, error = validate_settlement_date(trade_date, settlement_date)
        if not valid:
            validation_details["errors"].append(error)
        
        # Validate price
        valid, error = validate_price_reasonableness(clean_price)
        if not valid:
            validation_details["errors"].append(error)
        
        # Validate security
        security, error = validate_security_tradeable(self.db, security_id)
        if error:
            validation_details["errors"].append(error)
        
        # Validate counterparty
        counterparty, error = validate_counterparty_active(self.db, counterparty_id)
        if error:
            validation_details["errors"].append(error)
        
        if validation_details["errors"]:
            return None, validation_details
        
        # Calculate amounts
        accrued_interest = calculate_accrued_interest(security, face_value, settlement_date)
        amounts = calculate_trade_amounts(face_value, clean_price, accrued_interest, trade_side)
        
        # Check limits
        within_limit, limit_details = check_counterparty_limit(
            self.db, counterparty_id, amounts["settlement_amount"], entity_id
        )
        validation_details["limit_check"] = limit_details
        
        if not within_limit:
            validation_details["errors"].append(
                f"Trade exceeds counterparty limit: {limit_details['utilization_pct']}% utilized"
            )
            return None, validation_details
        
        if limit_details.get("is_warning"):
            validation_details["warnings"].append(
                f"Trade will exceed warning threshold: {limit_details['utilization_pct']}%"
            )
        
        # Generate trade reference
        trade_ref = generate_trade_ref(self.db)
        
        # Create trade record
        trade = BondTrade(
            trade_id=f"TRD{uuid4().hex[:8].upper()}",
            trade_ref=trade_ref,
            entity_id=entity_id,
            counterparty_id=counterparty_id,
            portfolio_id=portfolio_id,
            security_id=security_id,
            isin=security.isin,
            trade_side=trade_side,
            trade_type="OUTRIGHT",
            trade_date=trade_date,
            settlement_date=settlement_date,
            face_value=face_value,
            quantity=amounts["quantity"],
            clean_price=clean_price,
            dirty_price=amounts["dirty_price"],
            yield_rate=yield_rate or Decimal("0"),
            principal_amount=amounts["principal_amount"],
            accrued_interest=amounts["accrued_interest"],
            settlement_amount=amounts["settlement_amount"],
            withholding_tax=amounts["withholding_tax"],
            commission=Decimal("0"),
            broker_fee=Decimal("0"),
            status="PENDING_APPROVAL",
            is_thaibma_reported=False,
            settlement_status="PENDING",
            trader_id=trader_id,
        )
        
        self.db.add(trade)
        
        # Update limit utilization if limit exists
        if limit_details.get("has_limit"):
            update_limit_utilization(
                self.db,
                limit_details["limit_id"],
                amounts["settlement_amount"],
                trade_ref
            )
        
        validation_details["trade_ref"] = trade_ref
        validation_details["amounts"] = amounts
        
        return trade, validation_details
    
    def approve_trade(
        self,
        trade_id: str,
        approver_id: str,
        approved: bool,
        reason: Optional[str] = None
    ) -> Tuple[BondTrade, Optional[str]]:
        """
        Approve or reject a bond trade.
        
        Enforces four-eyes principle: approver cannot be trader.
        
        Returns:
            Tuple of (trade, error_message)
        """
        trade = self.db.query(BondTrade).filter(
            BondTrade.trade_id == trade_id
        ).first()
        
        if not trade:
            return None, f"Trade {trade_id} not found"
        
        if trade.status != "PENDING_APPROVAL":
            return None, f"Trade is not pending approval (status: {trade.status})"
        
        # Four-eyes principle
        if trade.trader_id == approver_id:
            return None, "Approver cannot be the same as trader (four-eyes principle)"
        
        if approved:
            trade.status = "APPROVED"
            trade.approver_id = approver_id
            trade.approved_at = datetime.now()
        else:
            trade.status = "REJECTED"
            trade.rejection_reason = reason
        
        trade.updated_at = datetime.now()
        
        return trade, None
    
    def cancel_trade(
        self,
        trade_id: str,
        reason: Optional[str] = None
    ) -> Tuple[BondTrade, Optional[str]]:
        """
        Cancel a bond trade.
        
        Only DRAFT or PENDING_APPROVAL trades can be cancelled.
        
        Returns:
            Tuple of (trade, error_message)
        """
        trade = self.db.query(BondTrade).filter(
            BondTrade.trade_id == trade_id
        ).first()
        
        if not trade:
            return None, f"Trade {trade_id} not found"
        
        if trade.status not in ["DRAFT", "PENDING_APPROVAL"]:
            return None, f"Cannot cancel trade with status '{trade.status}'"
        
        trade.status = "CANCELLED"
        trade.cancellation_reason = reason
        trade.updated_at = datetime.now()
        
        return trade, None
    
    def get_pending_approvals(self, entity_id: str = None) -> List[BondTrade]:
        """Get all trades pending approval."""
        query = self.db.query(BondTrade).filter(
            BondTrade.status == "PENDING_APPROVAL"
        )
        
        if entity_id:
            query = query.filter(BondTrade.entity_id == entity_id)
        
        return query.order_by(BondTrade.created_at.desc()).all()
    
    def get_today_settlements(self) -> List[BondTrade]:
        """Get all trades settling today."""
        today = date.today()
        return self.db.query(BondTrade).filter(
            BondTrade.settlement_date == today,
            BondTrade.status == "APPROVED",
            BondTrade.settlement_status.in_(["PENDING", "PARTIAL"])
        ).all()
    
    def calculate_position_impact(
        self,
        trade: BondTrade
    ) -> Dict[str, Any]:
        """
        Calculate the impact of a trade on position.
        
        Returns position changes that should be applied after settlement.
        """
        if trade.trade_side == "BUY":
            quantity_change = trade.quantity
            cost_change = trade.settlement_amount
        else:
            quantity_change = -trade.quantity
            cost_change = -trade.settlement_amount
        
        return {
            "security_id": trade.security_id,
            "portfolio_id": trade.portfolio_id,
            "quantity_change": quantity_change,
            "cost_change": cost_change,
            "face_value_change": trade.face_value if trade.trade_side == "BUY" else -trade.face_value
        }
