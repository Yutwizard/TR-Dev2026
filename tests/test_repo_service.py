
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


def test_settle_far_leg(service):
    """Test far leg settlement (ACTIVE -> MATURED)"""
    mock_trade = MagicMock(spec=RepoTrade)
    mock_trade.status = TradeStatus.ACTIVE
    mock_trade.trade_ref = "RP-20250101-001"
    
    service.get_trade = MagicMock(return_value=mock_trade)
    
    trade, error = service.settle_far_leg("RP-20250101-001", "USER001")
    
    assert trade is not None, f"Expected trade, got error: {error}"
    assert error is None
    assert trade.status == TradeStatus.MATURED
    assert trade.far_leg_cash_status == "SETTLED"
    assert trade.far_leg_collateral_status == "SETTLED"


def test_settle_far_leg_wrong_status(service):
    """Test far leg rejects non-ACTIVE trade"""
    mock_trade = MagicMock(spec=RepoTrade)
    mock_trade.status = TradeStatus.APPROVED  # Wrong status
    
    service.get_trade = MagicMock(return_value=mock_trade)
    
    trade, error = service.settle_far_leg("RP-20250101-001", "USER001")
    
    assert trade is None
    assert "ACTIVE" in error


def test_early_terminate_success(service):
    """Test early termination of active trade - recalculates interest"""
    mock_trade = MagicMock(spec=RepoTrade)
    mock_trade.status = TradeStatus.ACTIVE
    mock_trade.trade_ref = "RP-20250101-001"
    mock_trade.near_leg_amount = Decimal("10000000.00")
    mock_trade.repo_rate = Decimal("2.50")
    mock_trade.start_date = date.today() - timedelta(days=7)
    mock_trade.day_count_convention = "ACT/365"
    
    service.get_trade = MagicMock(return_value=mock_trade)
    
    # Mock recalculated interest for shorter period
    service.calc.calculate_repo_interest.return_value = {
        "interest_amount": Decimal("2397.26"),
        "far_leg_amount": Decimal("10002397.26")
    }
    
    termination_date = date.today() - timedelta(days=2)  # 5 days into 7-day repo
    trade, error = service.early_terminate_trade("RP-20250101-001", termination_date, "USER001")
    
    assert trade is not None, f"Expected trade, got error: {error}"
    assert error is None
    assert trade.status == TradeStatus.EARLY_TERMINATED
    assert trade.is_early_terminated == True
    assert trade.early_termination_date == termination_date
    assert trade.far_leg_amount == Decimal("10002397.26")
    assert trade.interest_amount == Decimal("2397.26")
    
    # Verify calc engine called with correct dates
    service.calc.calculate_repo_interest.assert_called_once()
    
    # Verify audit logged
    service.audit.log_status_change.assert_called_once()


def test_early_terminate_wrong_status(service):
    """Test early termination rejects non-ACTIVE/NEAR_LEG_SETTLED trade"""
    mock_trade = MagicMock(spec=RepoTrade)
    mock_trade.status = TradeStatus.PENDING_APPROVAL  # Cannot terminate pending approval
    
    service.get_trade = MagicMock(return_value=mock_trade)
    
    trade, error = service.early_terminate_trade("RP-20250101-001", date.today(), "USER001")
    
    assert trade is None
    assert "ACTIVE" in error


def test_early_terminate_date_before_start(service):
    """Test early termination rejects termination date before start"""
    mock_trade = MagicMock(spec=RepoTrade)
    mock_trade.status = TradeStatus.ACTIVE
    mock_trade.start_date = date.today()
    
    service.get_trade = MagicMock(return_value=mock_trade)
    
    trade, error = service.early_terminate_trade(
        "RP-20250101-001", 
        date.today() - timedelta(days=1),  # Before start
        "USER001"
    )
    
    assert trade is None
    assert "before start date" in error


def test_check_margin_call_triggered(service):
    """Test margin call when collateral drops below threshold"""
    mock_trade = MagicMock(spec=RepoTrade)
    mock_trade.status = TradeStatus.ACTIVE
    mock_trade.trade_ref = "RP-20250101-001"
    mock_trade.trade_type = "REPO"
    mock_trade.near_leg_amount = Decimal("10000000.00")
    mock_trade.repo_rate = Decimal("2.50")
    mock_trade.start_date = date.today() - timedelta(days=3)
    mock_trade.day_count_convention = "ACT/365"
    mock_trade.collateral_face_value = Decimal("10000000.00")
    mock_trade.haircut_pct = Decimal("2.0")
    mock_trade.margin_call_threshold = Decimal("2.0")
    
    service.get_trade = MagicMock(return_value=mock_trade)
    
    # Mock collateral value (price dropped significantly)
    service.calc.calculate_collateral_value.return_value = {
        "market_value": Decimal("9500000.00"),
        "haircut_amount": Decimal("190000.00"),
        "collateral_value": Decimal("9310000.00")  # Below exposure
    }
    
    # Mock accrued interest
    service.calc.calculate_simple_interest.return_value = Decimal("2054.79")
    
    # Mock margin calculation result - margin call triggered
    service.calc.calculate_margin.return_value = {
        "margin_amount": Decimal("-692054.79"),
        "margin_pct": Decimal("-6.91"),
        "needs_margin_call": True,
        "margin_call_amount": Decimal("692054.79")
    }
    
    result = service.check_margin_call("RP-20250101-001", Decimal("95.00"))
    
    assert "error" not in result, f"Unexpected error: {result.get('error')}"
    assert result["margin_call_triggered"] == True
    assert result["margin_call_amount"] == Decimal("692054.79")
    assert result["margin_call_direction"] == "DELIVER"  # REPO = we deliver more collateral
    assert result["trade_ref"] == "RP-20250101-001"


def test_check_margin_call_not_triggered(service):
    """Test no margin call when collateral is adequate"""
    mock_trade = MagicMock(spec=RepoTrade)
    mock_trade.status = TradeStatus.ACTIVE
    mock_trade.trade_ref = "RP-20250101-001"
    mock_trade.trade_type = "REVERSE_REPO"
    mock_trade.near_leg_amount = Decimal("10000000.00")
    mock_trade.repo_rate = Decimal("2.50")
    mock_trade.start_date = date.today() - timedelta(days=3)
    mock_trade.day_count_convention = "ACT/365"
    mock_trade.collateral_face_value = Decimal("10000000.00")
    mock_trade.haircut_pct = Decimal("2.0")
    mock_trade.margin_call_threshold = Decimal("2.0")
    
    service.get_trade = MagicMock(return_value=mock_trade)
    
    # Mock collateral value (price stable)
    service.calc.calculate_collateral_value.return_value = {
        "market_value": Decimal("10000000.00"),
        "haircut_amount": Decimal("200000.00"),
        "collateral_value": Decimal("9800000.00")
    }
    service.calc.calculate_simple_interest.return_value = Decimal("2054.79")
    
    # Mock margin calculation - no call
    service.calc.calculate_margin.return_value = {
        "margin_amount": Decimal("-202054.79"),
        "margin_pct": Decimal("-2.02"),
        "needs_margin_call": False,
        "margin_call_amount": Decimal("0")
    }
    
    result = service.check_margin_call("RP-20250101-001", Decimal("100.00"))
    
    assert "error" not in result
    assert result["margin_call_triggered"] == False
    assert result["margin_call_amount"] == Decimal("0")
    assert result["margin_call_direction"] == "RETURN"  # REVERSE_REPO


def test_check_margin_call_wrong_status(service):
    """Test margin call rejects non-active trade"""
    mock_trade = MagicMock(spec=RepoTrade)
    mock_trade.status = TradeStatus.MATURED
    
    service.get_trade = MagicMock(return_value=mock_trade)
    
    result = service.check_margin_call("RP-20250101-001", Decimal("100.00"))
    
    assert "error" in result
    assert "active" in result["error"].lower()


def test_collateral_summary(service, mock_db):
    """Test collateral summary aggregation"""
    # Create mock trades
    repo_trade = MagicMock(spec=RepoTrade)
    repo_trade.trade_type = "REPO"
    repo_trade.collateral_market_value = Decimal("5000000.00")
    repo_trade.collateral_isin = "TH0623A3B702"
    
    reverse_trade = MagicMock(spec=RepoTrade)
    reverse_trade.trade_type = "REVERSE_REPO"
    reverse_trade.collateral_market_value = Decimal("8000000.00")
    reverse_trade.collateral_isin = "TH0623A3B702"
    
    # Mock db.query(RepoTrade).filter(...).all() to return trades
    mock_query = MagicMock()
    mock_query.filter.return_value.all.return_value = [repo_trade, reverse_trade]
    mock_db.query.side_effect = None  # Clear previous side effect
    mock_db.query.return_value = mock_query
    
    result = service.get_collateral_summary()
    
    assert result["total_pledged_value"] == Decimal("5000000.00")
    assert result["total_received_value"] == Decimal("8000000.00")
    assert result["net_collateral"] == Decimal("3000000.00")  # received - pledged
    assert len(result["by_security"]) == 1  # Same ISIN
    assert result["by_security"][0]["isin"] == "TH0623A3B702"


def test_cancel_trade(service):
    """Test cancellation of pending trade"""
    mock_trade = MagicMock(spec=RepoTrade)
    mock_trade.status = TradeStatus.PENDING_APPROVAL
    mock_trade.trade_ref = "RP-20250101-001"
    
    service.get_trade = MagicMock(return_value=mock_trade)
    
    trade, error = service.cancel_trade("RP-20250101-001", "USER001", "Duplicate entry")
    
    assert trade is not None, f"Expected trade, got error: {error}"
    assert error is None
    assert trade.status == TradeStatus.CANCELLED
    service.audit.log_cancelled.assert_called_once()


def test_approve_four_eyes_reject(service):
    """Test four-eyes principle: trader cannot approve own trade"""
    mock_trade = MagicMock(spec=RepoTrade)
    mock_trade.status = TradeStatus.PENDING_APPROVAL
    mock_trade.trader_id = "TRADER001"  # Same person
    mock_trade.trade_ref = "RP-20250101-001"
    
    service.get_trade = MagicMock(return_value=mock_trade)
    
    trade, error = service.approve_trade("RP-20250101-001", "TRADER001")  # Same as trader
    
    assert trade is None
    assert "same as the trader" in error.lower()

