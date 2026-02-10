
import pytest
from unittest.mock import MagicMock, patch
from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

from app.services.repo_service import RepoService
from app.models.transactions import RepoTrade
from app.models.master_data import CounterpartyMaster, SecurityMaster
from app.core.enums import RepoTradeType, TradeStatus

@pytest.fixture
def mock_db():
    mock_session = MagicMock()
    
    # Setup query side effects for Master Data
    def query_side_effect(*args):
        mock_query = MagicMock()
        model = args[0] if args else None
        
        # Use 'is' to avoid triggering SQLAlchemy __eq__ on expressions (like func.count)
        if model is CounterpartyMaster or "CounterpartyMaster" in str(model):
            mock_cp = MagicMock()
            mock_cp.counterparty_id = "CP_SCB"
            mock_cp.is_active = True
            mock_query.filter.return_value.first.return_value = mock_cp
            return mock_query
            
        elif model is SecurityMaster or "SecurityMaster" in str(model):
            mock_sec = MagicMock()
            mock_sec.security_id = "SEC001"
            mock_sec.isin = "TH0623A3B702"
            mock_query.filter.return_value.first.return_value = mock_sec
            return mock_query
            
        elif str(model) == str(RepoTrade) or "RepoTrade" in str(model):
            return mock_query
        
        # Default
        mock_query.filter.return_value.scalar.return_value = 0
        mock_query.filter.return_value.first.return_value = None
        return mock_query

    mock_session.query.side_effect = query_side_effect
    return mock_session

@pytest.fixture
def service(mock_db):
    service = RepoService(mock_db)
    service.calc = MagicMock()
    service.calc.calculate_repo_interest.return_value = {
        "interest_amount": Decimal("5000.00"),
        "far_leg_amount": Decimal("10005000.00")
    }
    # Mock audit to avoid side effects
    service.audit = MagicMock()
    return service

def test_create_repo_trade_success(service, mock_db):
    """Test successful creation of repo trade"""
    trade, validation = service.create_trade(
        trade_type="REPO",
        repo_type="BILATERAL",
        counterparty_id="CP_SCB",
        portfolio_id="PORT001",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=7),
        near_leg_amount=Decimal("10000000.00"),
        repo_rate=Decimal("2.50"),
        trader_id="TRADER001",
        collateral_security_id="SEC001",
        collateral_isin="TH0623A3B702",
        collateral_face_value=Decimal("10000000.00"),
        haircut_pct=Decimal("2.0")
    )
    
    assert trade is not None, f"Trade is None. Validation: {validation}"
    assert trade.trade_type == "REPO", f"Type mismatch: {trade.trade_type}"
    # assert trade.status == TradeStatus.PENDING_APPROVAL # This might fail if Enum mismatch?
    assert trade.status == TradeStatus.PENDING_APPROVAL, f"Status mismatch: {trade.status} vs {TradeStatus.PENDING_APPROVAL}"
    assert trade.near_leg_amount == Decimal("10000000.00"), f"Amount mismatch: {trade.near_leg_amount}"
    
    # Verify DB add called
    mock_db.add.assert_called_once()

def test_create_repo_trade_validation_fail(service):
    """Test validation failure (End < Start)"""
    trade, validation = service.create_trade(
        trade_type="REPO",
        repo_type="BILATERAL",
        counterparty_id="CP_SCB",
        portfolio_id="PORT001",
        start_date=date.today(),
        end_date=date.today() - timedelta(days=1), # Invalid
        near_leg_amount=Decimal("10000000.00"),
        repo_rate=Decimal("2.50"),
        trader_id="TRADER001"
    )
    
    assert trade is None
    assert "End date must be after start date" in validation["errors"]

def test_approve_repo_trade(service, mock_db):
    """Test approval workflow"""
    # Mock get_trade returning a pending trade
    mock_trade = MagicMock(spec=RepoTrade)
    mock_trade.status = TradeStatus.PENDING_APPROVAL
    mock_trade.trader_id = "TRADER001"
    mock_trade.trade_ref = "RP-20250101-001"
    
    # Configure mock_db.query to return this trade
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_trade
    # Reset side effect for query to handle specific RepoTrade query
    # or just let previous side_effect handle it?
    # Previous side_effect returned mock_query for RepoTrade but .first() was None (default)
    # create new side effect wrapper or specific mock configuration
    
    # Simpler: Just override the return value for this specific test scope if possible
    # But side_effect is powerful.
    # Let's patch get_trade method on valid service instance?
    # No, test logic inside approve_trade calls self.get_trade.
    
    # We'll just define a simpler mock_db fixture for this test or rely on get_trade logic.
    # get_trade calls db.query(RepoTrade).filter(...).first()
    
    # Let's adjust mock_db fixture logic in side_effect for "RepoTrade"
    # The fixture is shared.
    pass

    # Actually, simpler to mock service.get_trade directly!
    service.get_trade = MagicMock(return_value=mock_trade)
    
    trade, error = service.approve_trade("RP-20250101-001", "APPROVER001")
    
    assert trade is not None
    assert trade.status == TradeStatus.APPROVED
    assert trade.approver_id == "APPROVER001"

def test_settle_near_leg(service):
    """Test near leg settlement"""
    mock_trade = MagicMock(spec=RepoTrade)
    mock_trade.status = TradeStatus.APPROVED
    mock_trade.trade_ref = "RP-20250101-001"
    
    service.get_trade = MagicMock(return_value=mock_trade)
    
    trade, error = service.settle_near_leg("RP-20250101-001", "USER001")
    
    assert trade is not None
    assert trade.status == TradeStatus.ACTIVE
    assert trade.near_leg_cash_status == "SETTLED"
