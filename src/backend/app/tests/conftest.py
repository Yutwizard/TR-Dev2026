"""
Pytest configuration and fixtures
"""

import pytest
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))


@pytest.fixture(scope="session")
def test_settings():
    """Provide test settings"""
    from app.config import settings
    return settings


@pytest.fixture
def sample_security_data():
    """Sample security data for tests"""
    return {
        "security_id": "TEST001",
        "isin": "TH0000000001",
        "symbol": "TESTSEC",
        "security_name": "Test Security",
        "security_type": "TBOND",
        "issuer_type": "GOV",
        "issue_date": "2025-01-01",
        "maturity_date": "2030-01-01",
        "coupon_rate": 3.5,
        "coupon_frequency": 2,
    }


@pytest.fixture
def sample_trade_data():
    """Sample trade data for tests"""
    return {
        "counterparty_id": "CP001",
        "portfolio_id": "PORT001",
        "security_id": "SEC001",
        "isin": "TH0623A3B702",
        "trade_side": "BUY",
        "trade_date": "2025-09-01",
        "settlement_date": "2025-09-03",
        "face_value": 10000000,
        "quantity": 10000,
        "clean_price": 99.50,
    }


@pytest.fixture
def sample_interbank_data():
    """Sample interbank deal data for tests"""
    return {
        "counterparty_id": "CP001",
        "portfolio_id": "MM001",
        "deal_type": "IB_LEND",
        "deal_date": "2025-09-01",
        "start_date": "2025-09-01",
        "maturity_date": "2025-09-08",
        "principal_amount": 100000000,
        "interest_rate": 2.25,
        "rate_type": "FIXED",
    }


@pytest.fixture
def sample_repo_data():
    """Sample repo trade data for tests"""
    return {
        "counterparty_id": "CP001",
        "portfolio_id": "REPO001",
        "trade_type": "REPO",
        "trade_date": "2025-09-01",
        "start_date": "2025-09-01",
        "end_date": "2025-09-08",
        "near_leg_amount": 100000000,
        "repo_rate": 2.15,
        "collateral_isin": "TH0623A3B702",
        "collateral_face_value": 105000000,
        "haircut_pct": 2.5,
    }
