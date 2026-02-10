import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

from app.services.interbank_service import InterbankService
from app.models.transactions import InterbankDeal
from app.core.enums import TradeStatus, InterbankDealType

from app.models.master_data import CounterpartyMaster
from app.models.limits import LimitDefinition
from app.models.transactions import InterbankDeal
from sqlalchemy import func

@pytest.fixture
def mock_db():
    mock_session = MagicMock()
    
    # Create a query mock that can differentiate based on model
    def query_side_effect(*args):
        mock_query = MagicMock()
        model = args[0] if args else None
        
        # DEBUG
        # print(f"DEBUG: Querying model: {model} (Type: {type(model)})")

        if model is CounterpartyMaster or "CounterpartyMaster" in str(model):
            # Return a valid counterparty
            mock_cp = MagicMock()
            mock_cp.counterparty_id = "CP_KBANK"
            mock_cp.is_active = True
            mock_query.filter.return_value.first.return_value = mock_cp
            return mock_query
            
        elif model is LimitDefinition:
            # Return no limit (None) -> Success
            mock_query.filter.return_value.first.return_value = None
            return mock_query
            
        # Handle func.count and func.sum which are harder to match by equality
        model_str = str(model)
        if "count" in model_str:
             mock_query.filter.return_value.scalar.return_value = 0
             return mock_query
        elif "sum" in model_str:
             mock_query.filter.return_value.scalar.return_value = Decimal("0")
             return mock_query
        
        # Default behavior
        mock_query.filter.return_value.first.return_value = None
        mock_query.filter.return_value.scalar.return_value = 0
        return mock_query

    mock_session.query.side_effect = query_side_effect
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
    # Verify DB add called for deal
    # mock_db.add.assert_called_once() # Called twice (Deal + Audit)
    mock_db.add.assert_any_call(deal)
    # assert mock_db.add.call_args[0][0] == deal

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
    
    # Configure mock query for InterbankDeal
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_deal
    
    # Keep original side effect logic but override for InterbankDeal
    original_side_effect = mock_db.query.side_effect
    
    def side_effect(*args):
        if args and args[0] == InterbankDeal:
            return mock_query
        return original_side_effect(*args)
        
    mock_db.query.side_effect = side_effect

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
    
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_deal
    
    original_side_effect = mock_db.query.side_effect
    
    def side_effect(*args):
        if args and args[0] == InterbankDeal:
            return mock_query
        return original_side_effect(*args)
        
    mock_db.query.side_effect = side_effect

    result, error = service.approve_deal("IB-TEST-001", "TRADER01")  # Same ID

    assert result is None
    assert "Four-Eyes Principle" in error

def test_batch_accrual_update(service, mock_db):
    """Test daily accrual calculation batch"""
    # Mock calculation engine to isolate service logic
    service.calc = MagicMock()
    service.calc.calculate_daily_accrual.return_value = Decimal("100.00")

    # Setup mock active deals
    mock_deal1 = MagicMock(spec=InterbankDeal)
    mock_deal1.status = TradeStatus.ACTIVE
    mock_deal1.principal_amount = Decimal("100000000")
    mock_deal1.interest_rate = Decimal("2.0")
    mock_deal1.day_count_convention = "ACT/365"
    mock_deal1.start_date = date.today() - timedelta(days=5)
    mock_deal1.maturity_date = date.today() + timedelta(days=2)
    mock_deal1.accrued_interest = Decimal("0")

    mock_query = MagicMock()
    mock_query.filter.return_value.all.return_value = [mock_deal1]
    
    original_side_effect = mock_db.query.side_effect
    
    def side_effect(*args):
        if args and args[0] == InterbankDeal:
            return mock_query
        return original_side_effect(*args)
        
    mock_db.query.side_effect = side_effect

    count = service.update_daily_accrual(date.today())

    assert count == 1
    # Check if calculation was called
    service.calc.calculate_daily_accrual.assert_called_once()
    
    # Check if accrued_interest was updated 
    # Daily 100 * 5 days = 500
    assert mock_deal1.accrued_interest == Decimal("500.00")
