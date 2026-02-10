import pytest
import sys
import os
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

# Add src/backend to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/backend')))

from app.services.interbank_service import InterbankService
from app.models.transactions import InterbankDeal
from app.core.enums import TradeStatus, InterbankDealType

@pytest.fixture
def mock_db():
    mock_session = MagicMock()
    # Mock query().filter() pattern
    mock_session.query.return_value.filter.return_value.first.return_value = None
    mock_session.query.return_value.filter.return_value.scalar.return_value = 0
    return mock_session

@pytest.fixture
def service(mock_db):
    return InterbankService(mock_db)

def test_create_deal_success(service, mock_db):
    """Test successful creation of a new deal"""
    deal, validation = service.create_deal(
        deal_type=InterbankDealType.PLACEMENT,
        counterparty_id="CP_KBANK",
        portfolio_id="MM001",
        principal_amount=Decimal("100000000"),
        interest_rate=Decimal("2.25"),
        start_date=date.today(),
        maturity_date=date.today() + timedelta(days=7),
        trader_id="TRADER01"
    )

    assert deal is not None
    assert deal.deal_ref.startswith("IB-")
    assert deal.deal_type == InterbankDealType.PLACEMENT
    assert deal.status == TradeStatus.PENDING_APPROVAL
    
    # Verify DB add called
    mock_db.add.assert_called_once()
    assert mock_db.add.call_args[0][0] == deal

def test_create_deal_validation_fail(service):
    """Test validation failure (maturity before start)"""
    deal, validation = service.create_deal(
        deal_type=InterbankDealType.PLACEMENT,
        counterparty_id="CP_KBANK",
        portfolio_id="MM001",
        principal_amount=Decimal("1000000"),
        interest_rate=Decimal("2.0"),
        start_date=date.today(),
        maturity_date=date.today() - timedelta(days=1),  # Invalid
        trader_id="TRADER01"
    )
    
    assert deal is None
    assert "Maturity date must be after start date" in validation["errors"]

def test_approve_deal_success(service, mock_db):
    """Test successful approval flow"""
    # Setup mock deal
    mock_deal = InterbankDeal(
        deal_ref="IB-TEST-001",
        status=TradeStatus.PENDING_APPROVAL,
        trader_id="TRADER01"
    )
    mock_db.query.return_value.filter.return_value.first.return_value = mock_deal

    result, error = service.approve_deal("IB-TEST-001", "APPROVER01")

    assert error is None
    assert result.status == TradeStatus.APPROVED
    assert result.approver_id == "APPROVER01"
    assert result.approved_at is not None

def test_approve_deal_four_eyes_fail(service, mock_db):
    """Test approval fails if approver is same as trader"""
    mock_deal = InterbankDeal(
        deal_ref="IB-TEST-001",
        status=TradeStatus.PENDING_APPROVAL,
        trader_id="TRADER01"
    )
    mock_db.query.return_value.filter.return_value.first.return_value = mock_deal

    result, error = service.approve_deal("IB-TEST-001", "TRADER01")  # Same ID

    assert result is None
    assert "Four-Eyes Principle" in error

def test_batch_accrual_update(service, mock_db):
    """Test daily accrual calculation batch"""
    # Setup mock active deals
    mock_deal1 = MagicMock(spec=InterbankDeal)
    mock_deal1.status = TradeStatus.ACTIVE
    mock_deal1.principal_amount = Decimal("100000000")
    mock_deal1.interest_rate = Decimal("2.0")
    mock_deal1.day_count_convention = "ACT/365"
    mock_deal1.start_date = date.today() - timedelta(days=5)
    mock_deal1.maturity_date = date.today() + timedelta(days=2)
    mock_deal1.accrued_interest = Decimal("0")

    mock_db.query.return_value.filter.return_value.all.return_value = [mock_deal1]

    count = service.update_daily_accrual(date.today())

    assert count == 1
    # Check if accrued_interest was updated (mock object property set)
    # 100M * 2% * 5/365 = ~27397.26
    assert mock_deal1.accrued_interest > 0
