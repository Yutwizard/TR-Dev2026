"""
Treasury Management System - Calendar Router
==============================================

API endpoints for Thai business day calendar.
"""

from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Query, HTTPException, status
from pydantic import BaseModel

from app.services.calendar_service import (
    is_thai_business_day,
    add_business_days,
    subtract_business_days,
    calculate_settlement_date,
    count_business_days,
    get_business_days_in_range,
    get_thai_calendar_service,
)


router = APIRouter()


# =============================================================================
# Response Models
# =============================================================================
class BusinessDayCheckResponse(BaseModel):
    """Response for business day check"""
    date: date
    is_business_day: bool
    is_weekend: bool
    is_holiday: bool
    holiday_name: Optional[str] = None


class SettlementDateResponse(BaseModel):
    """Response for settlement date calculation"""
    trade_date: date
    settlement_days: int
    settlement_date: date
    business_days_between: int


class HolidayInfo(BaseModel):
    """Holiday information"""
    date: date
    name_en: str
    name_th: Optional[str] = None
    day_of_week: str


class BusinessDaysRangeResponse(BaseModel):
    """Response for business days in range"""
    start_date: date
    end_date: date
    business_days: List[date]
    total_business_days: int
    total_holidays: int


# =============================================================================
# Endpoints
# =============================================================================
@router.get("/check/{check_date}")
async def check_business_day(
    check_date: date,
) -> BusinessDayCheckResponse:
    """
    Check if a specific date is a Thai business day.
    
    Returns:
    - Whether the date is a business day
    - Whether it's a weekend
    - Whether it's a holiday
    - Holiday name (if applicable)
    """
    calendar = get_thai_calendar_service()
    is_biz_day = is_thai_business_day(check_date)
    is_weekend = check_date.weekday() >= 5
    
    # Check for holiday
    is_holiday = False
    holiday_name = None
    holiday_info = calendar.get_holiday_info(check_date)
    if holiday_info:
        is_holiday = True
        holiday_name = holiday_info.get("name_en")
    
    return BusinessDayCheckResponse(
        date=check_date,
        is_business_day=is_biz_day,
        is_weekend=is_weekend,
        is_holiday=is_holiday,
        holiday_name=holiday_name
    )


@router.get("/settlement-date")
async def get_settlement_date(
    trade_date: date,
    days: int = Query(2, ge=0, le=30, description="Settlement days (T+N)"),
) -> SettlementDateResponse:
    """
    Calculate T+N settlement date.
    
    Parameters:
    - **trade_date**: The trade date
    - **days**: Number of business days after trade (default: 2 for T+2)
    
    Returns the settlement date, accounting for weekends and Thai holidays.
    """
    if not is_thai_business_day(trade_date):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trade date {trade_date} is not a Thai business day"
        )
    
    settlement = calculate_settlement_date(trade_date, days)
    biz_days = count_business_days(trade_date, settlement)
    
    return SettlementDateResponse(
        trade_date=trade_date,
        settlement_days=days,
        settlement_date=settlement,
        business_days_between=biz_days
    )


@router.get("/add-business-days")
async def add_biz_days(
    start_date: date,
    days: int = Query(..., ge=-365, le=365),
) -> dict:
    """
    Add or subtract business days from a date.
    
    Parameters:
    - **start_date**: Starting date
    - **days**: Number of business days to add (negative to subtract)
    """
    if days >= 0:
        result = add_business_days(start_date, days)
    else:
        result = subtract_business_days(start_date, abs(days))
    
    return {
        "start_date": start_date,
        "business_days": days,
        "result_date": result,
        "result_is_business_day": is_thai_business_day(result)
    }


@router.get("/business-days-in-range")
async def business_days_range(
    start_date: date,
    end_date: date,
) -> BusinessDaysRangeResponse:
    """
    Get all business days in a date range.
    
    Parameters:
    - **start_date**: Start of range (inclusive)
    - **end_date**: End of range (inclusive)
    """
    if end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date"
        )
    
    # Limit range to 365 days
    if (end_date - start_date).days > 365:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Date range cannot exceed 365 days"
        )
    
    biz_days = get_business_days_in_range(start_date, end_date)
    total_days = (end_date - start_date).days + 1
    total_holidays = total_days - len(biz_days) - sum(
        1 for d in range(total_days) 
        if (start_date.toordinal() + d) and 
           date.fromordinal(start_date.toordinal() + d).weekday() >= 5
    )
    
    return BusinessDaysRangeResponse(
        start_date=start_date,
        end_date=end_date,
        business_days=biz_days,
        total_business_days=len(biz_days),
        total_holidays=max(0, total_holidays)
    )


@router.get("/count-business-days")
async def count_biz_days(
    start_date: date,
    end_date: date,
) -> dict:
    """
    Count business days between two dates.
    
    Parameters:
    - **start_date**: Start date
    - **end_date**: End date
    """
    if end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date"
        )
    
    count = count_business_days(start_date, end_date)
    
    return {
        "start_date": start_date,
        "end_date": end_date,
        "business_days_count": count,
        "calendar_days_count": (end_date - start_date).days
    }


@router.get("/holidays/{year}")
async def get_holidays(
    year: int,
) -> List[HolidayInfo]:
    """
    Get all Thai public holidays for a given year.
    
    Currently supports years 2025-2026.
    """
    calendar = get_thai_calendar_service()
    holidays = calendar.get_holidays_in_year(year)
    
    if not holidays:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Holiday data for year {year} not available"
        )
    
    result = []
    for h_date, h_info in holidays.items():
        result.append(HolidayInfo(
            date=h_date,
            name_en=h_info.get("name_en", "Unknown"),
            name_th=h_info.get("name_th"),
            day_of_week=h_date.strftime("%A")
        ))
    
    return sorted(result, key=lambda x: x.date)


@router.get("/next-business-day")
async def next_business_day(
    from_date: date,
) -> dict:
    """
    Get the next business day from a given date.
    
    If the given date is a business day, returns that date.
    Otherwise, returns the next business day.
    """
    if is_thai_business_day(from_date):
        return {
            "from_date": from_date,
            "next_business_day": from_date,
            "is_same_day": True
        }
    
    next_biz_day = add_business_days(from_date, 1)
    
    return {
        "from_date": from_date,
        "next_business_day": next_biz_day,
        "is_same_day": False,
        "days_skipped": (next_biz_day - from_date).days
    }


@router.get("/current-info")
async def current_date_info() -> dict:
    """
    Get information about the current business date.
    """
    today = date.today()
    is_biz_day = is_thai_business_day(today)
    
    # Calculate some useful dates
    t_plus_1 = calculate_settlement_date(today, 1) if is_biz_day else None
    t_plus_2 = calculate_settlement_date(today, 2) if is_biz_day else None
    
    # Find next business day if today is not
    if is_biz_day:
        next_biz = today
    else:
        next_biz = add_business_days(today, 1)
    
    return {
        "current_date": today,
        "is_business_day": is_biz_day,
        "day_of_week": today.strftime("%A"),
        "next_business_day": next_biz,
        "t_plus_1": t_plus_1,
        "t_plus_2": t_plus_2,
    }
