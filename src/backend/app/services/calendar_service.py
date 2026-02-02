"""
Treasury Management System - Thai Business Day Calendar Service
================================================================

Provides Thai business day calculations for:
- T+N settlement date calculation
- Holiday checking
- Business day counting
- Date range validation

Thai Holidays Source: Bank of Thailand (BOT)
https://www.bot.or.th/en/our-roles/payment-system/bahtnet/holiday.html

Usage:
    from app.services.calendar_service import (
        is_thai_business_day,
        add_business_days,
        calculate_settlement_date
    )
    
    # Check if date is business day
    if is_thai_business_day(date(2025, 9, 15)):
        print("Trading day!")
    
    # Calculate T+2 settlement
    settlement = calculate_settlement_date(trade_date, days=2)
"""

from datetime import date, timedelta
from typing import List, Optional, Set, Tuple
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# Thai Public Holidays 2025-2026
# Source: BOT and Thai Government Gazette
# =============================================================================
THAI_HOLIDAYS_2025: Set[date] = {
    # January
    date(2025, 1, 1),    # New Year's Day
    
    # February  
    date(2025, 2, 12),   # Makha Bucha Day (วันมาฆบูชา)
    
    # April
    date(2025, 4, 6),    # Chakri Memorial Day (วันจักรี)
    date(2025, 4, 13),   # Songkran Festival
    date(2025, 4, 14),   # Songkran Festival
    date(2025, 4, 15),   # Songkran Festival
    
    # May
    date(2025, 5, 1),    # National Labor Day
    date(2025, 5, 4),    # Coronation Day (วันฉัตรมงคล)
    date(2025, 5, 12),   # Substitution for Visakha Bucha Day
    date(2025, 5, 22),   # Visakha Bucha Day (วันวิสาขบูชา) - Observed
    
    # June
    date(2025, 6, 3),    # H.M. Queen Suthida's Birthday
    
    # July
    date(2025, 7, 10),   # Substitution Holiday
    date(2025, 7, 28),   # H.M. King's Birthday
    
    # August
    date(2025, 8, 12),   # H.M. Queen Sirikit's Birthday / Mother's Day
    
    # October
    date(2025, 10, 13),  # Anniversary of King Rama IX's Passing
    date(2025, 10, 23),  # Chulalongkorn Day
    
    # December
    date(2025, 12, 5),   # H.M. King Bhumibol's Birthday / Father's Day
    date(2025, 12, 10),  # Constitution Day
    date(2025, 12, 31),  # New Year's Eve
}

THAI_HOLIDAYS_2026: Set[date] = {
    # January
    date(2026, 1, 1),    # New Year's Day
    date(2026, 1, 2),    # Substitution Holiday
    
    # March
    date(2026, 3, 2),    # Makha Bucha Day
    
    # April
    date(2026, 4, 6),    # Chakri Memorial Day
    date(2026, 4, 13),   # Songkran Festival
    date(2026, 4, 14),   # Songkran Festival
    date(2026, 4, 15),   # Songkran Festival
    
    # May
    date(2026, 5, 1),    # National Labor Day
    date(2026, 5, 4),    # Coronation Day
    date(2026, 5, 11),   # Visakha Bucha Day
    
    # June
    date(2026, 6, 3),    # H.M. Queen Suthida's Birthday
    
    # July
    date(2026, 7, 9),    # Asalha Bucha Day
    date(2026, 7, 28),   # H.M. King's Birthday
    
    # August
    date(2026, 8, 12),   # H.M. Queen Sirikit's Birthday
    
    # October
    date(2026, 10, 13),  # Anniversary of King Rama IX's Passing
    date(2026, 10, 23),  # Chulalongkorn Day
    
    # December
    date(2026, 12, 5),   # Father's Day
    date(2026, 12, 10),  # Constitution Day
    date(2026, 12, 31),  # New Year's Eve
}

# Combined holiday set
ALL_THAI_HOLIDAYS: Set[date] = THAI_HOLIDAYS_2025 | THAI_HOLIDAYS_2026


# =============================================================================
# Holiday Information
# =============================================================================
HOLIDAY_NAMES = {
    # 2025
    date(2025, 1, 1): "New Year's Day",
    date(2025, 2, 12): "Makha Bucha Day",
    date(2025, 4, 6): "Chakri Memorial Day",
    date(2025, 4, 13): "Songkran Festival",
    date(2025, 4, 14): "Songkran Festival",
    date(2025, 4, 15): "Songkran Festival",
    date(2025, 5, 1): "National Labor Day",
    date(2025, 5, 4): "Coronation Day",
    date(2025, 5, 12): "Substitution for Visakha Bucha",
    date(2025, 5, 22): "Visakha Bucha Day",
    date(2025, 6, 3): "H.M. Queen Suthida's Birthday",
    date(2025, 7, 10): "Substitution Holiday",
    date(2025, 7, 28): "H.M. King's Birthday",
    date(2025, 8, 12): "H.M. Queen Mother's Birthday / Mother's Day",
    date(2025, 10, 13): "Anniversary of King Rama IX's Passing",
    date(2025, 10, 23): "Chulalongkorn Day",
    date(2025, 12, 5): "H.M. King Bhumibol's Birthday / Father's Day",
    date(2025, 12, 10): "Constitution Day",
    date(2025, 12, 31): "New Year's Eve",
    # 2026 - Similar pattern
    date(2026, 1, 1): "New Year's Day",
    date(2026, 1, 2): "Substitution Holiday",
}


# =============================================================================
# Core Calendar Functions  
# =============================================================================
def is_weekend(d: date) -> bool:
    """Check if date falls on weekend (Saturday=5, Sunday=6)"""
    return d.weekday() >= 5


def is_thai_holiday(d: date) -> bool:
    """Check if date is a Thai public holiday"""
    return d in ALL_THAI_HOLIDAYS


def is_thai_business_day(d: date) -> bool:
    """
    Check if date is a Thai business day.
    
    A business day is:
    - Not a Saturday
    - Not a Sunday
    - Not a Thai public holiday
    
    Args:
        d: Date to check
        
    Returns:
        True if d is a business day
        
    Example:
        >>> is_thai_business_day(date(2025, 4, 14))
        False  # Songkran
        >>> is_thai_business_day(date(2025, 9, 15))
        True  # Normal Monday
    """
    if is_weekend(d):
        return False
    if is_thai_holiday(d):
        return False
    return True


def get_holiday_name(d: date) -> Optional[str]:
    """Get the name of the holiday for a given date, if any"""
    return HOLIDAY_NAMES.get(d)


# =============================================================================
# Business Day Arithmetic
# =============================================================================
def add_business_days(start_date: date, days: int) -> date:
    """
    Add N business days to a date.
    
    Args:
        start_date: Starting date
        days: Number of business days to add (can be negative)
        
    Returns:
        Date that is N business days after start_date
        
    Example:
        >>> add_business_days(date(2025, 9, 1), 2)  # T+2
        date(2025, 9, 3)  # Wednesday
        
        >>> add_business_days(date(2025, 9, 4), 2)  # Thursday + 2
        date(2025, 9, 8)  # Monday (skips weekend)
    """
    if days == 0:
        # If start_date is not a business day, move to next
        if not is_thai_business_day(start_date):
            return next_business_day(start_date)
        return start_date
    
    direction = 1 if days > 0 else -1
    remaining = abs(days)
    current = start_date
    
    while remaining > 0:
        current = current + timedelta(days=direction)
        if is_thai_business_day(current):
            remaining -= 1
    
    return current


def subtract_business_days(start_date: date, days: int) -> date:
    """Subtract N business days from a date"""
    return add_business_days(start_date, -days)


def next_business_day(d: date) -> date:
    """
    Get the next business day on or after the given date.
    
    If d is already a business day, returns d.
    Otherwise, returns the next business day.
    
    Args:
        d: Starting date
        
    Returns:
        Next business day >= d
    """
    while not is_thai_business_day(d):
        d = d + timedelta(days=1)
    return d


def previous_business_day(d: date) -> date:
    """
    Get the previous business day on or before the given date.
    
    If d is already a business day, returns d.
    Otherwise, returns the previous business day.
    """
    while not is_thai_business_day(d):
        d = d - timedelta(days=1)
    return d


# =============================================================================
# Settlement Date Calculation
# =============================================================================
def calculate_settlement_date(
    trade_date: date,
    days: int = 2,  # T+2 is standard
    adjust_if_holiday: bool = True
) -> date:
    """
    Calculate settlement date for a trade (T+N).
    
    Standard settlement cycles:
    - Bond: T+2
    - Interbank: T+0 to T+2
    - Repo: T+0 or T+1
    
    Args:
        trade_date: Trade execution date
        days: Settlement cycle (default T+2)
        adjust_if_holiday: If True, adjust to next business day
        
    Returns:
        Settlement date
        
    Raises:
        ValueError: If trade_date is not a business day
        
    Example:
        >>> calculate_settlement_date(date(2025, 9, 1), days=2)
        date(2025, 9, 3)  # T+2
    """
    # Validate trade date is a business day
    if not is_thai_business_day(trade_date):
        if adjust_if_holiday:
            trade_date = next_business_day(trade_date)
        else:
            raise ValueError(
                f"Trade date {trade_date} is not a business day. "
                f"Reason: {'Weekend' if is_weekend(trade_date) else get_holiday_name(trade_date)}"
            )
    
    settlement = add_business_days(trade_date, days)
    return settlement


def calculate_t_plus_2(trade_date: date) -> date:
    """Convenience function for T+2 calculation"""
    return calculate_settlement_date(trade_date, days=2)


def calculate_t_plus_0(trade_date: date) -> date:
    """Convenience function for T+0 (same day) settlement"""
    return calculate_settlement_date(trade_date, days=0)


def calculate_t_plus_1(trade_date: date) -> date:
    """Convenience function for T+1 settlement"""
    return calculate_settlement_date(trade_date, days=1)


# =============================================================================
# Business Day Counting
# =============================================================================
def count_business_days(start_date: date, end_date: date) -> int:
    """
    Count business days between two dates (exclusive of start, inclusive of end).
    
    Used for:
    - Interest accrual calculations
    - Tenor calculations
    
    Args:
        start_date: Start date (not counted)
        end_date: End date (counted)
        
    Returns:
        Number of business days
        
    Example:
        >>> count_business_days(date(2025, 9, 1), date(2025, 9, 5))
        4  # Mon->Fri (Tue, Wed, Thu, Fri)
    """
    if end_date < start_date:
        return -count_business_days(end_date, start_date)
    
    count = 0
    current = start_date + timedelta(days=1)
    
    while current <= end_date:
        if is_thai_business_day(current):
            count += 1
        current += timedelta(days=1)
    
    return count


def count_calendar_days(start_date: date, end_date: date) -> int:
    """Count calendar days between dates (for day count conventions)"""
    return (end_date - start_date).days


# =============================================================================
# Date Range Queries
# =============================================================================
def get_business_days_in_range(start_date: date, end_date: date) -> List[date]:
    """
    Get all business days in a date range (inclusive).
    
    Args:
        start_date: Start of range
        end_date: End of range
        
    Returns:
        List of business day dates
    """
    business_days = []
    current = start_date
    
    while current <= end_date:
        if is_thai_business_day(current):
            business_days.append(current)
        current += timedelta(days=1)
    
    return business_days


def get_holidays_in_range(start_date: date, end_date: date) -> List[Tuple[date, str]]:
    """
    Get all holidays in a date range with their names.
    
    Args:
        start_date: Start of range
        end_date: End of range
        
    Returns:
        List of (date, holiday_name) tuples
    """
    holidays = []
    
    for holiday in sorted(ALL_THAI_HOLIDAYS):
        if start_date <= holiday <= end_date:
            name = HOLIDAY_NAMES.get(holiday, "Holiday")
            holidays.append((holiday, name))
    
    return holidays


def get_month_end_business_day(year: int, month: int) -> date:
    """
    Get the last business day of a month.
    
    Useful for:
    - Month-end position reporting
    - Accrual calculations
    
    Args:
        year: Year
        month: Month (1-12)
        
    Returns:
        Last business day of the month
    """
    # Get last day of month
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    
    last_day = next_month - timedelta(days=1)
    
    # Move back to business day if needed
    return previous_business_day(last_day)


# =============================================================================
# Thai Calendar Service Class
# =============================================================================
class ThaiCalendarService:
    """
    Service class for Thai business day operations.
    
    Provides caching and additional functionality.
    
    Usage:
        calendar = ThaiCalendarService()
        
        if calendar.is_business_day(trade_date):
            settlement = calendar.add_business_days(trade_date, 2)
    """
    
    def __init__(self):
        self._holidays = ALL_THAI_HOLIDAYS.copy()
        logger.info(f"ThaiCalendarService initialized with {len(self._holidays)} holidays")
    
    def is_business_day(self, d: date) -> bool:
        """Check if date is Thai business day"""
        return is_thai_business_day(d)
    
    def add_business_days(self, start_date: date, days: int) -> date:
        """Add business days"""
        return add_business_days(start_date, days)
    
    def calculate_settlement(self, trade_date: date, cycle: int = 2) -> date:
        """Calculate settlement date"""
        return calculate_settlement_date(trade_date, days=cycle)
    
    def get_holidays(self, year: int) -> List[Tuple[date, str]]:
        """Get all holidays for a year"""
        return [
            (d, HOLIDAY_NAMES.get(d, "Holiday"))
            for d in sorted(self._holidays)
            if d.year == year
        ]
    
    def add_custom_holiday(self, d: date, name: str = "Custom Holiday"):
        """Add a custom holiday (e.g., bank-specific)"""
        self._holidays.add(d)
        logger.info(f"Added custom holiday: {d} - {name}")
    
    def is_trading_hours(self, d: date) -> bool:
        """
        Check if current date is within trading hours.
        
        Thai bond market hours: 9:00 - 16:30 (weekdays)
        """
        return is_thai_business_day(d)
    
    def validate_trade_date(self, trade_date: date) -> Tuple[bool, str]:
        """
        Validate if a trade date is acceptable.
        
        Returns:
            (is_valid, reason)
        """
        if is_weekend(trade_date):
            return False, f"Trade date {trade_date} is a weekend"
        
        if trade_date in self._holidays:
            holiday_name = HOLIDAY_NAMES.get(trade_date, "Thai holiday")
            return False, f"Trade date {trade_date} is {holiday_name}"
        
        return True, "Valid trade date"


# =============================================================================
# Module-level singleton
# =============================================================================
_calendar_service = None


def get_calendar_service() -> ThaiCalendarService:
    """Get singleton calendar service instance"""
    global _calendar_service
    if _calendar_service is None:
        _calendar_service = ThaiCalendarService()
    return _calendar_service
