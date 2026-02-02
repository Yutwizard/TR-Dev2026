"""
Treasury Management System - Calendar Service Tests
=====================================================

Unit tests for Thai business day calendar calculations.
"""

import pytest
from datetime import date
from app.services.calendar_service import (
    is_thai_business_day,
    add_business_days,
    subtract_business_days,
    calculate_settlement_date,
    count_business_days,
    get_business_days_in_range,
    get_thai_calendar_service,
)


class TestIsThaiBusinessDay:
    """Tests for is_thai_business_day function"""
    
    def test_weekday_not_holiday(self):
        """Monday to Friday, not a holiday should be business day"""
        # A random Wednesday that is not a holiday
        assert is_thai_business_day(date(2025, 9, 3)) is True
    
    def test_saturday_not_business_day(self):
        """Saturday should not be a business day"""
        assert is_thai_business_day(date(2025, 9, 6)) is False
    
    def test_sunday_not_business_day(self):
        """Sunday should not be a business day"""
        assert is_thai_business_day(date(2025, 9, 7)) is False
    
    def test_new_year_not_business_day(self):
        """New Year's Day should not be a business day"""
        assert is_thai_business_day(date(2025, 1, 1)) is False
    
    def test_songkran_not_business_day(self):
        """Songkran (Apr 13-15) should not be a business day"""
        assert is_thai_business_day(date(2025, 4, 13)) is False
        assert is_thai_business_day(date(2025, 4, 14)) is False
        assert is_thai_business_day(date(2025, 4, 15)) is False
    
    def test_makha_bucha_not_business_day(self):
        """Makha Bucha 2025 (Feb 12) should not be a business day"""
        assert is_thai_business_day(date(2025, 2, 12)) is False
    
    def test_chakri_day_not_business_day(self):
        """Chakri Day (Apr 6) should not be a business day"""
        assert is_thai_business_day(date(2025, 4, 6)) is False


class TestAddBusinessDays:
    """Tests for add_business_days function"""
    
    def test_add_zero_days(self):
        """Adding 0 days should return the same date if it's a business day"""
        start = date(2025, 9, 3)  # Wednesday
        result = add_business_days(start, 0)
        assert result == start
    
    def test_add_one_day_simple(self):
        """Adding 1 day from Monday should give Tuesday"""
        start = date(2025, 9, 1)  # Monday
        result = add_business_days(start, 1)
        assert result == date(2025, 9, 2)  # Tuesday
    
    def test_add_days_skip_weekend(self):
        """Adding days should skip weekends"""
        start = date(2025, 9, 5)  # Friday
        result = add_business_days(start, 1)
        assert result == date(2025, 9, 8)  # Monday
    
    def test_add_days_skip_holiday_and_weekend(self):
        """Adding days should skip both holidays and weekends"""
        # Week containing Songkran (Apr 13-15, 2025)
        start = date(2025, 4, 11)  # Friday
        result = add_business_days(start, 1)
        # Should skip Sat (12), Sun (13 - also holiday), Mon 14 (holiday), Tue 15 (holiday)
        # Next business day is Wed Apr 16
        assert result == date(2025, 4, 16)
    
    def test_add_five_business_days(self):
        """Adding 5 business days should span a week"""
        start = date(2025, 9, 1)  # Monday
        result = add_business_days(start, 5)
        assert result == date(2025, 9, 8)  # Next Monday


class TestSubtractBusinessDays:
    """Tests for subtract_business_days function"""
    
    def test_subtract_one_day(self):
        """Subtracting 1 day from Tuesday should give Monday"""
        start = date(2025, 9, 2)  # Tuesday
        result = subtract_business_days(start, 1)
        assert result == date(2025, 9, 1)  # Monday
    
    def test_subtract_skip_weekend(self):
        """Subtracting should skip weekends"""
        start = date(2025, 9, 8)  # Monday
        result = subtract_business_days(start, 1)
        assert result == date(2025, 9, 5)  # Friday


class TestCalculateSettlementDate:
    """Tests for calculate_settlement_date function (T+N)"""
    
    def test_t_plus_0(self):
        """T+0 should return the same date"""
        trade_date = date(2025, 9, 3)  # Wednesday
        result = calculate_settlement_date(trade_date, 0)
        assert result == trade_date
    
    def test_t_plus_1(self):
        """T+1 should return next business day"""
        trade_date = date(2025, 9, 3)  # Wednesday
        result = calculate_settlement_date(trade_date, 1)
        assert result == date(2025, 9, 4)  # Thursday
    
    def test_t_plus_2_simple(self):
        """T+2 standard bond settlement"""
        trade_date = date(2025, 9, 1)  # Monday
        result = calculate_settlement_date(trade_date, 2)
        assert result == date(2025, 9, 3)  # Wednesday
    
    def test_t_plus_2_over_weekend(self):
        """T+2 settlement should skip weekends"""
        trade_date = date(2025, 9, 4)  # Thursday
        result = calculate_settlement_date(trade_date, 2)
        assert result == date(2025, 9, 8)  # Monday (skip Sat, Sun)
    
    def test_t_plus_2_with_holiday(self):
        """T+2 settlement should skip holidays"""
        # April 6, 2025 is Chakri Day (Sunday - also a holiday)
        # April 7, 2025 is substitute holiday (Monday)
        trade_date = date(2025, 4, 3)  # Thursday
        result = calculate_settlement_date(trade_date, 2)
        # Skip Fri (4), Sat (5 weekend), Sun (6 weekend+holiday), Mon (7 substitute)
        # Next business day is Tue Apr 8
        assert result == date(2025, 4, 8)


class TestCountBusinessDays:
    """Tests for count_business_days function"""
    
    def test_same_day(self):
        """Counting between same day should be 0"""
        d = date(2025, 9, 3)
        result = count_business_days(d, d)
        assert result == 0
    
    def test_consecutive_business_days(self):
        """Count business days Monday to Wednesday"""
        start = date(2025, 9, 1)  # Monday
        end = date(2025, 9, 3)  # Wednesday
        result = count_business_days(start, end)
        assert result == 2
    
    def test_over_weekend(self):
        """Count should not include weekend days"""
        start = date(2025, 9, 5)  # Friday
        end = date(2025, 9, 8)  # Monday
        result = count_business_days(start, end)
        assert result == 1  # Only Mon counts


class TestGetBusinessDaysInRange:
    """Tests for get_business_days_in_range function"""
    
    def test_week_range(self):
        """Get business days for one week"""
        start = date(2025, 9, 1)  # Monday
        end = date(2025, 9, 7)  # Sunday
        result = get_business_days_in_range(start, end)
        
        # Should have Mon, Tue, Wed, Thu, Fri (5 days)
        assert len(result) == 5
        assert date(2025, 9, 6) not in result  # Saturday
        assert date(2025, 9, 7) not in result  # Sunday
    
    def test_includes_start_and_end(self):
        """Range should include start and end if they are business days"""
        start = date(2025, 9, 1)  # Monday
        end = date(2025, 9, 3)  # Wednesday
        result = get_business_days_in_range(start, end)
        
        assert start in result
        assert end in result


class TestThaiCalendarService:
    """Tests for ThaiCalendarService class"""
    
    def test_get_holiday_info(self):
        """Should return holiday information"""
        calendar = get_thai_calendar_service()
        info = calendar.get_holiday_info(date(2025, 1, 1))
        
        assert info is not None
        assert "New Year" in info.get("name_en", "")
    
    def test_get_holidays_in_year_2025(self):
        """Should return holidays for 2025"""
        calendar = get_thai_calendar_service()
        holidays = calendar.get_holidays_in_year(2025)
        
        assert holidays is not None
        assert len(holidays) > 15  # Thailand has ~18-19 public holidays
    
    def test_get_holidays_in_year_2026(self):
        """Should return holidays for 2026"""
        calendar = get_thai_calendar_service()
        holidays = calendar.get_holidays_in_year(2026)
        
        assert holidays is not None
        assert len(holidays) > 15


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
