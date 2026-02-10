"""
Treasury Management System - Calculation Engine
=================================================

Single source of truth for ALL financial calculations:
- Day count fractions
- Accrued interest (bonds, interbank, repo)
- Settlement amounts
- Margin calculations

IMPORTANT: Never implement financial calculations inline in routers
           or services. Always use this engine.

Supports day count conventions:
- ACT/365: Most THB bonds, interbank
- ACT/360: Some short-term instruments
- 30/360:  Some corporate bonds
- ACT/ACT: Government bonds (actual days in year)

Usage:
    from app.services.calculation_engine import CalculationEngine

    engine = CalculationEngine()
    
    # Accrued interest
    accrued = engine.calculate_accrued_interest(
        nominal=Decimal("10000000"),
        coupon_rate=Decimal("3.5"),
        start_date=date(2026, 1, 15),
        end_date=date(2026, 2, 10),
        convention=DayCountConvention.ACT_365
    )
    
    # Interbank interest
    interest = engine.calculate_simple_interest(
        principal=Decimal("100000000"),
        rate=Decimal("2.25"),
        start_date=date(2026, 2, 1),
        end_date=date(2026, 5, 1),
        convention=DayCountConvention.ACT_365
    )
"""

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, Optional
from calendar import isleap
import logging

from app.core.enums import DayCountConvention

logger = logging.getLogger(__name__)


# =============================================================================
# Day Count Fraction Calculations
# =============================================================================

def _days_in_year(d: date) -> int:
    """Get actual days in the year of the given date."""
    return 366 if isleap(d.year) else 365


def calculate_day_count_fraction(
    start_date: date,
    end_date: date,
    convention: DayCountConvention
) -> Decimal:
    """
    Calculate the day count fraction between two dates.
    
    This is the core calculation used by all interest formulas.
    
    Args:
        start_date: Period start date (inclusive)
        end_date: Period end date (exclusive)
        convention: Day count convention to use
    
    Returns:
        Day count fraction as a Decimal
    
    Raises:
        ValueError: If end_date <= start_date or unknown convention
    """
    if end_date <= start_date:
        raise ValueError(
            f"end_date ({end_date}) must be after start_date ({start_date})"
        )
    
    if convention == DayCountConvention.ACT_365:
        # Actual days / 365 (fixed denominator)
        actual_days = (end_date - start_date).days
        return Decimal(str(actual_days)) / Decimal("365")
    
    elif convention == DayCountConvention.ACT_360:
        # Actual days / 360 (fixed denominator)
        actual_days = (end_date - start_date).days
        return Decimal(str(actual_days)) / Decimal("360")
    
    elif convention == DayCountConvention.THIRTY_360:
        # 30/360 (Bond Basis)
        # Each month has 30 days, year has 360 days
        d1 = min(start_date.day, 30)
        d2 = min(end_date.day, 30) if d1 >= 30 else end_date.day
        
        days = (
            360 * (end_date.year - start_date.year)
            + 30 * (end_date.month - start_date.month)
            + (d2 - d1)
        )
        return Decimal(str(days)) / Decimal("360")
    
    elif convention == DayCountConvention.ACT_ACT:
        # Actual days / Actual days in year
        actual_days = (end_date - start_date).days
        days_in_yr = _days_in_year(start_date)
        return Decimal(str(actual_days)) / Decimal(str(days_in_yr))
    
    else:
        raise ValueError(f"Unknown day count convention: {convention}")


def get_actual_days(start_date: date, end_date: date) -> int:
    """Get actual calendar days between two dates."""
    return (end_date - start_date).days


# =============================================================================
# Interest Calculations
# =============================================================================

def calculate_simple_interest(
    principal: Decimal,
    rate: Decimal,
    start_date: date,
    end_date: date,
    convention: DayCountConvention = DayCountConvention.ACT_365
) -> Decimal:
    """
    Calculate simple interest for a period.
    
    Formula: Principal × Rate(%) × DayCountFraction
    
    Used for:
    - Interbank deal interest
    - Repo interest
    - Money market instruments
    
    Args:
        principal: Principal amount
        rate: Annual interest rate as percentage (e.g., 2.25 for 2.25%)
        start_date: Interest accrual start date
        end_date: Interest accrual end date
        convention: Day count convention
    
    Returns:
        Interest amount (rounded to 2 decimal places)
    """
    dcf = calculate_day_count_fraction(start_date, end_date, convention)
    interest = principal * (rate / Decimal("100")) * dcf
    return interest.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_daily_accrual(
    principal: Decimal,
    rate: Decimal,
    convention: DayCountConvention = DayCountConvention.ACT_365
) -> Decimal:
    """
    Calculate daily interest accrual amount.
    
    Formula: Principal × Rate(%) × (1/DayCountBase)
    
    Used for:
    - Daily batch accrual processing
    - Position costing
    
    Args:
        principal: Principal/nominal amount
        rate: Annual rate as percentage
        convention: Day count convention
    
    Returns:
        Daily accrual amount (rounded to 2 decimal places)
    """
    if convention in (DayCountConvention.ACT_365,):
        base = Decimal("365")
    elif convention in (DayCountConvention.ACT_360, DayCountConvention.THIRTY_360):
        base = Decimal("360")
    elif convention == DayCountConvention.ACT_ACT:
        # Use 365 as approximation for daily; actual used for period calcs
        base = Decimal("365")
    else:
        base = Decimal("365")
    
    daily = principal * (rate / Decimal("100")) / base
    return daily.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_accrued_interest(
    nominal: Decimal,
    coupon_rate: Decimal,
    start_date: date,
    end_date: date,
    convention: DayCountConvention = DayCountConvention.ACT_365,
    coupon_frequency: int = 2,
    issue_date: Optional[date] = None
) -> Decimal:
    """
    Calculate accrued interest for a bond.
    
    For bonds, accrued interest is calculated from the last coupon date
    to the settlement date. If issue_date is provided and no coupon has
    been paid yet, accrual starts from the issue date.
    
    Formula: Nominal × CouponRate(%) × DayCountFraction
    
    Args:
        nominal: Face value / nominal amount
        coupon_rate: Annual coupon rate as percentage (e.g., 3.5 for 3.5%)
        start_date: Last coupon date (or issue date)
        end_date: Settlement date (or calculation date)
        convention: Day count convention
        coupon_frequency: Number of coupon payments per year (default: 2 = semi-annual)
        issue_date: Original issue date (for calculating last coupon date)
    
    Returns:
        Accrued interest amount (rounded to 2 decimal places)
    """
    if coupon_rate == 0:
        # Zero coupon bond (T-Bill, discount bond)
        return Decimal("0")
    
    # If issue_date provided, calculate last coupon date
    actual_start = start_date
    if issue_date and coupon_frequency > 0:
        days_per_period = 365 // coupon_frequency
        days_since_issue = (end_date - issue_date).days
        days_since_last_coupon = days_since_issue % days_per_period
        actual_start = end_date - __import__('datetime').timedelta(days=days_since_last_coupon)
    
    if actual_start >= end_date:
        return Decimal("0")
    
    dcf = calculate_day_count_fraction(actual_start, end_date, convention)
    accrued = nominal * (coupon_rate / Decimal("100")) * dcf
    return accrued.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# =============================================================================
# Bond Trade Calculations
# =============================================================================

def calculate_bond_trade_amounts(
    face_value: Decimal,
    clean_price: Decimal,
    accrued_interest: Decimal,
    trade_side: str
) -> Dict[str, Decimal]:
    """
    Calculate all amounts for a bond trade.
    
    Args:
        face_value: Face value (par value)
        clean_price: Clean price as percentage (e.g., 99.50 means 99.50% of par)
        accrued_interest: Pre-calculated accrued interest
        trade_side: "BUY" or "SELL"
    
    Returns:
        Dictionary with calculated amounts:
        - principal_amount: Face × CleanPrice / 100
        - dirty_price: CleanPrice + (AccruedInterest per 100 face)
        - settlement_amount: Principal + AccruedInterest
        - quantity: Face / 1000 (standard lot)
        - withholding_tax: 0 (WHT applies to coupon, not trade)
    """
    # Principal = Face Value × Clean Price / 100
    principal = (face_value * clean_price / Decimal("100")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    
    # Dirty Price = Clean Price + Accrued per 100 face
    if face_value > 0:
        accrued_per_100 = (accrued_interest / face_value * Decimal("100")).quantize(
            Decimal("0.000001"), rounding=ROUND_HALF_UP
        )
    else:
        accrued_per_100 = Decimal("0")
    
    dirty_price = (clean_price + accrued_per_100).quantize(
        Decimal("0.000001"), rounding=ROUND_HALF_UP
    )
    
    # Settlement Amount = Principal + Accrued Interest
    settlement_amount = (principal + accrued_interest).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    
    # Quantity in standard units (par 1000)
    quantity = (face_value / Decimal("1000")).quantize(
        Decimal("0.000001"), rounding=ROUND_HALF_UP
    )
    
    return {
        "principal_amount": principal,
        "accrued_interest": accrued_interest,
        "dirty_price": dirty_price,
        "settlement_amount": settlement_amount,
        "withholding_tax": Decimal("0"),
        "quantity": quantity,
    }


# =============================================================================
# Repo Calculations
# =============================================================================

def calculate_repo_interest(
    near_leg_amount: Decimal,
    repo_rate: Decimal,
    start_date: date,
    end_date: date,
    convention: DayCountConvention = DayCountConvention.ACT_365
) -> Dict[str, Decimal]:
    """
    Calculate repo interest and far leg amount.
    
    Args:
        near_leg_amount: Near leg cash amount
        repo_rate: Repo rate as percentage
        start_date: Near leg settlement date
        end_date: Far leg settlement date
        convention: Day count convention
    
    Returns:
        Dictionary with:
        - interest_amount: Repo interest
        - far_leg_amount: Near leg + interest
        - tenor_days: Number of days
    """
    interest = calculate_simple_interest(
        near_leg_amount, repo_rate, start_date, end_date, convention
    )
    
    return {
        "interest_amount": interest,
        "far_leg_amount": (near_leg_amount + interest).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        ),
        "tenor_days": get_actual_days(start_date, end_date),
    }


def calculate_collateral_value(
    face_value: Decimal,
    market_price: Decimal,
    haircut_pct: Decimal
) -> Dict[str, Decimal]:
    """
    Calculate collateral value after haircut.
    
    Args:
        face_value: Collateral face value
        market_price: Current market price (per 100 face)
        haircut_pct: Haircut percentage (e.g., 5 for 5%)
    
    Returns:
        Dictionary with:
        - market_value: Face × Price / 100
        - haircut_amount: Market value × Haircut%
        - collateral_value: Market value after haircut
    """
    market_value = (face_value * market_price / Decimal("100")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    
    haircut_amount = (market_value * haircut_pct / Decimal("100")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    
    collateral_value = market_value - haircut_amount
    
    return {
        "market_value": market_value,
        "haircut_amount": haircut_amount,
        "collateral_value": collateral_value.quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        ),
    }


def calculate_margin(
    collateral_value: Decimal,
    exposure_amount: Decimal,
    threshold_pct: Decimal = Decimal("2")
) -> Dict[str, Any]:
    """
    Calculate margin status for a repo trade.
    
    If (collateral - exposure) / exposure < -threshold%, margin call needed.
    
    Args:
        collateral_value: Current collateral value (after haircut)
        exposure_amount: Current exposure (near leg + accrued)
        threshold_pct: Margin call threshold percentage
    
    Returns:
        Dictionary with:
        - margin_amount: Collateral - Exposure (positive = excess, negative = deficit)
        - margin_pct: Margin as percentage of exposure
        - needs_margin_call: Whether margin call is required
        - margin_call_amount: Amount needed to restore margin (0 if no call needed)
    """
    if exposure_amount == 0:
        return {
            "margin_amount": collateral_value,
            "margin_pct": Decimal("100"),
            "needs_margin_call": False,
            "margin_call_amount": Decimal("0"),
        }
    
    margin_amount = collateral_value - exposure_amount
    margin_pct = ((collateral_value / exposure_amount - 1) * Decimal("100")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    
    needs_margin_call = margin_pct < -threshold_pct
    margin_call_amount = Decimal("0")
    
    if needs_margin_call:
        # Amount needed to bring margin back to 0%
        margin_call_amount = abs(margin_amount).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    
    return {
        "margin_amount": margin_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        "margin_pct": margin_pct,
        "needs_margin_call": needs_margin_call,
        "margin_call_amount": margin_call_amount,
    }


# =============================================================================
# Interbank Calculations  
# =============================================================================

def calculate_interbank_amounts(
    principal: Decimal,
    interest_rate: Decimal,
    start_date: date,
    maturity_date: date,
    convention: DayCountConvention = DayCountConvention.ACT_365
) -> Dict[str, Decimal]:
    """
    Calculate interbank deal amounts.
    
    Args:
        principal: Principal amount
        interest_rate: Annual interest rate as percentage
        start_date: Deal start date
        maturity_date: Deal maturity date
        convention: Day count convention
    
    Returns:
        Dictionary with:
        - interest_amount: Total interest for the period
        - maturity_amount: Principal + interest
        - tenor_days: Number of days
        - daily_accrual: Daily accrual amount
    """
    interest = calculate_simple_interest(
        principal, interest_rate, start_date, maturity_date, convention
    )
    
    daily = calculate_daily_accrual(principal, interest_rate, convention)
    
    return {
        "interest_amount": interest,
        "maturity_amount": (principal + interest).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        ),
        "tenor_days": get_actual_days(start_date, maturity_date),
        "daily_accrual": daily,
    }


# =============================================================================
# Convenience Class
# =============================================================================

class CalculationEngine:
    """
    High-level calculation engine.
    
    Wraps all calculation functions into a single interface.
    Useful for dependency injection in services.
    """
    
    # Day Count
    calculate_day_count_fraction = staticmethod(calculate_day_count_fraction)
    get_actual_days = staticmethod(get_actual_days)
    
    # Interest
    calculate_simple_interest = staticmethod(calculate_simple_interest)
    calculate_daily_accrual = staticmethod(calculate_daily_accrual)
    calculate_accrued_interest = staticmethod(calculate_accrued_interest)
    
    # Bond
    calculate_bond_trade_amounts = staticmethod(calculate_bond_trade_amounts)
    
    # Repo
    calculate_repo_interest = staticmethod(calculate_repo_interest)
    calculate_collateral_value = staticmethod(calculate_collateral_value)
    calculate_margin = staticmethod(calculate_margin)
    
    # Interbank
    calculate_interbank_amounts = staticmethod(calculate_interbank_amounts)
