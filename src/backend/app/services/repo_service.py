"""
Treasury Management System - Repo Service
=========================================

Core business logic for Repo and Reverse Repo transactions:
- Trade creation and validation
- Interest and far leg calculations (via CalculationEngine)
- Collateral valuation
- Workflow management (Approval, Settlement)
- Audit logging
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from uuid import uuid4
import logging

from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, or_

from app.models.transactions import RepoTrade
from app.models.master_data import CounterpartyMaster, SecurityMaster, PortfolioMaster
from app.core.enums import (
    TradeStatus, RepoTradeType, DayCountConvention, EntityType, AuditAction
)
from app.core.state_machine import (
    assert_transition, REPO_TRADE_TRANSITIONS
)
from app.services.calculation_engine import CalculationEngine
from app.services.audit_service import AuditService
from app.services.calendar_service import is_thai_business_day

logger = logging.getLogger(__name__)


class RepoService:
    """
    Service for managing the lifecycle of Repo/Reverse Repo trades.
    """

    def __init__(self, db: Session):
        self.db = db
        self.calc = CalculationEngine()
        self.audit = AuditService(db)

    def _generate_trade_ref(self, prefix: str = "RP-") -> str:
        """
        Generate a unique trade reference.
        Format: RP-YYYYMMDD-XXX
        """
        today = date.today()
        date_str = today.strftime("%Y%m%d")
        
        # Count today's repo trades
        count = self.db.query(func.count(RepoTrade.trade_id)).filter(
            func.date(RepoTrade.created_at) == today
        ).scalar() or 0
        
        seq = count + 1
        return f"{prefix}{date_str}-{seq:03d}"

    def create_trade(
        self,
        trade_type: str,
        repo_type: str,
        counterparty_id: str,
        portfolio_id: str,
        start_date: date,
        end_date: date,
        near_leg_amount: Decimal,
        repo_rate: Decimal,
        trader_id: str,
        collateral_security_id: Optional[str] = None,
        collateral_isin: Optional[str] = None,
        collateral_face_value: Optional[Decimal] = None,
        haircut_pct: Decimal = Decimal("0"),
        entity_id: str = "BANK001",
        currency: str = "THB",
        external_ref: Optional[str] = None,
        rate_type: str = "FIXED",
        day_count_convention: str = "ACT/365",
        margin_call_threshold: Decimal = Decimal("2"),
        **kwargs
    ) -> Tuple[Optional[RepoTrade], Dict[str, Any]]:
        """
        Create a new Repo/Reverse Repo trade with validation.
        """
        validation_details = {"errors": [], "warnings": []}

        # 1. Validation
        if end_date <= start_date:
            validation_details["errors"].append("End date must be after start date")

        if not is_thai_business_day(start_date):
             validation_details["warnings"].append(f"Start date {start_date} is not a Thai business day")
        
        # Counterparty check
        cp = self.db.query(CounterpartyMaster).filter(
            CounterpartyMaster.counterparty_id == counterparty_id,
            CounterpartyMaster.is_active == True
        ).first()
        if not cp:
            validation_details["errors"].append(f"Counterparty {counterparty_id} not found or inactive")

        # Security check (if provided)
        if collateral_security_id:
            sec = self.db.query(SecurityMaster).filter(
                SecurityMaster.security_id == collateral_security_id
            ).first()
            if not sec:
                validation_details["errors"].append(f"Security {collateral_security_id} not found")
            elif collateral_isin and sec.isin != collateral_isin:
                 validation_details["warnings"].append(f"Security ID {collateral_security_id} ISIN mismatch: provided {collateral_isin}, found {sec.isin}")

        if validation_details["errors"]:
            return None, validation_details

        # 2. Calculations
        try:
            dcc_enum = DayCountConvention(day_count_convention)
        except ValueError:
             # Fallback or strict error? 
             # Strict is better but let's default to ACT/365 if unknown to be safe or map common aliases
             dcc_enum = DayCountConvention.ACT_365

        # Calculate Interest and Far Leg Amount
        repo_calc = self.calc.calculate_repo_interest(
            near_leg_amount,
            repo_rate,
            start_date,
            end_date,
            convention=dcc_enum
        )

        # Calculate Collateral Market Value (if price available - simplified here as we don't have price feed yet)
        # In a real system, we'd fetch latest price. Here we might assume Par or need input.
        # For now, we'll set initial market value based on face value if price not provided?
        # Let's assume price is 100 (Par) if not fetched.
        # TODO: Integrate with MarketDataService for price.
        collateral_market_value = Decimal("0")
        if collateral_face_value:
             # Assume Par for initial booking if no price logic yet
             collateral_market_value = collateral_face_value 

        # 3. Persistence
        trade_ref = self._generate_trade_ref()
        trade = RepoTrade(
            trade_id=f"RPD-{uuid4().hex[:8].upper()}",
            trade_ref=trade_ref,
            external_ref=external_ref,
            entity_id=entity_id,
            counterparty_id=counterparty_id,
            portfolio_id=portfolio_id,
            trade_type=trade_type,
            repo_type=repo_type,
            trade_date=date.today(),
            start_date=start_date,
            end_date=end_date,
            currency=currency,
            near_leg_amount=near_leg_amount,
            far_leg_amount=repo_calc["far_leg_amount"],
            interest_amount=repo_calc["interest_amount"],
            repo_rate=repo_rate,
            rate_type=rate_type,
            day_count_convention=day_count_convention,
            collateral_security_id=collateral_security_id,
            collateral_isin=collateral_isin,
            collateral_face_value=collateral_face_value,
            collateral_market_value=collateral_market_value,
            haircut_pct=haircut_pct,
            margin_call_threshold=margin_call_threshold,
            status=TradeStatus.PENDING_APPROVAL,
            trader_id=trader_id,
            near_leg_cash_status="PENDING",
            near_leg_collateral_status="PENDING",
            far_leg_cash_status="PENDING",
            far_leg_collateral_status="PENDING"
        )

        self.db.add(trade)
        
        # 4. Audit Trail
        self.audit.log_created(
            entity_type=EntityType.REPO_TRADE,
            entity_id=trade_ref,
            user_id=trader_id,
            new_values={
                "near_leg": str(near_leg_amount),
                "far_leg": str(repo_calc["far_leg_amount"]),
                "rate": str(repo_rate),
                "type": trade_type,
                "collateral": collateral_isin
            }
        )

        return trade, validation_details

    def get_trade(self, trade_ref: str) -> Optional[RepoTrade]:
        """Get a trade by reference."""
        return self.db.query(RepoTrade).filter(RepoTrade.trade_ref == trade_ref).first()

    def list_trades(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Dict[str, Any] = None
    ) -> Tuple[List[RepoTrade], int]:
        """List trades with filtering."""
        query = self.db.query(RepoTrade)
        
        if filters:
            if filters.get("status"):
                query = query.filter(RepoTrade.status == filters["status"])
            if filters.get("trade_type"):
                query = query.filter(RepoTrade.trade_type == filters["trade_type"])
            if filters.get("counterparty_id"):
                query = query.filter(RepoTrade.counterparty_id == filters["counterparty_id"])
            if filters.get("date_from"):
                query = query.filter(RepoTrade.trade_date >= filters["date_from"])
            if filters.get("date_to"):
                query = query.filter(RepoTrade.trade_date <= filters["date_to"])

        total = query.count()
        items = query.order_by(RepoTrade.created_at.desc()).offset(skip).limit(limit).all()
        
        return items, total

    def approve_trade(self, trade_ref: str, approver_id: str) -> Tuple[Optional[RepoTrade], Optional[str]]:
        """Approve a repo trade (Four-Eyes Principle)."""
        trade = self.get_trade(trade_ref)
        if not trade:
            return None, f"Trade {trade_ref} not found"

        if trade.trader_id == approver_id:
            return None, "Approver cannot be the same as the trader"

        try:
            assert_transition(
                trade.status, 
                TradeStatus.APPROVED, 
                REPO_TRADE_TRANSITIONS,
                entity_type="RepoTrade",
                entity_ref=trade_ref
            )
        except ValueError as e:
            return None, str(e)

        old_status = trade.status
        trade.status = TradeStatus.APPROVED
        trade.approver_id = approver_id
        trade.approved_at = datetime.utcnow()

        self.audit.log_approved(
            entity_type=EntityType.REPO_TRADE,
            entity_id=trade_ref,
            approver_id=approver_id
        )
        
        return trade, None

    def reject_trade(self, trade_ref: str, rejector_id: str, reason: str) -> Tuple[Optional[RepoTrade], Optional[str]]:
        """Reject a repo trade."""
        trade = self.get_trade(trade_ref)
        if not trade:
            return None, f"Trade {trade_ref} not found"

        try:
            assert_transition(
                trade.status, 
                TradeStatus.REJECTED, 
                REPO_TRADE_TRANSITIONS,
                entity_type="RepoTrade",
                entity_ref=trade_ref
            )
        except ValueError as e:
            return None, str(e)

        trade.status = TradeStatus.REJECTED
        self.audit.log_rejected(
            entity_type=EntityType.REPO_TRADE,
            entity_id=trade_ref,
            rejector_id=rejector_id,
            reason=reason
        )
        return trade, None

    def cancel_trade(self, trade_ref: str, user_id: str, reason: str) -> Tuple[Optional[RepoTrade], Optional[str]]:
        """Cancel a repo trade."""
        trade = self.get_trade(trade_ref)
        if not trade:
            return None, f"Trade {trade_ref} not found"

        try:
            assert_transition(
                trade.status, 
                TradeStatus.CANCELLED, 
                REPO_TRADE_TRANSITIONS,
                entity_type="RepoTrade",
                entity_ref=trade_ref
            )
        except ValueError as e:
            return None, str(e)

        trade.status = TradeStatus.CANCELLED
        self.audit.log_cancelled(
            entity_type=EntityType.REPO_TRADE,
            entity_id=trade_ref,
            user_id=user_id,
            reason=reason
        )
        return trade, None

    def settle_near_leg(
        self, 
        trade_ref: str, 
        user_id: str, 
        bahtnet_ref: str = None, 
        custodian_ref: str = None
    ) -> Tuple[Optional[RepoTrade], Optional[str]]:
        """
        Settle Near Leg (Start).
        Repo: We receive cash (Cash PENDING to SETTLED) + We deliver collateral (Collat PENDING to SETTLED).
        Reverse Repo: We pay cash + Receive collateral.
        """
        trade = self.get_trade(trade_ref)
        if not trade:
            return None, f"Trade {trade_ref} not found"

        if trade.status != TradeStatus.APPROVED:
            return None, f"Trade must be APPROVED to settle (current: {trade.status})"

        # Logic for near leg
        # Both Cash and Collateral must settle. 
        # For MVP, we can treat them as settling together or allow separate calls?
        # Let's assume single call settlements near leg fully.
        
        trade.near_leg_cash_status = "SETTLED"
        trade.near_leg_collateral_status = "SETTLED"
        trade.near_leg_settled_at = datetime.utcnow()
        
        # Transition to ACTIVE
        old_status = trade.status
        trade.status = TradeStatus.ACTIVE
        
        self.audit.log_status_change(
            entity_type=EntityType.REPO_TRADE,
            entity_id=trade_ref,
            user_id=user_id,
            old_status=old_status,
            new_status=TradeStatus.ACTIVE,
            notes=f"Near leg settled. Cash Ref: {bahtnet_ref}, Sec Ref: {custodian_ref}"
        )
        
        return trade, None

    def settle_far_leg(
        self, 
        trade_ref: str, 
        user_id: str
    ) -> Tuple[Optional[RepoTrade], Optional[str]]:
        """
        Settle Far Leg (End).
        Transitions ACTIVE -> MATURED.
        """
        trade = self.get_trade(trade_ref)
        if not trade:
            return None, f"Trade {trade_ref} not found"
        
        if trade.status != TradeStatus.ACTIVE:
             return None, f"Trade must be ACTIVE to settle far leg"

        trade.far_leg_cash_status = "SETTLED"
        trade.far_leg_collateral_status = "SETTLED"
        trade.far_leg_settled_at = datetime.utcnow()
        
        trade.status = TradeStatus.MATURED
        
        self.audit.log_status_change(
            entity_type=EntityType.REPO_TRADE,
            entity_id=trade_ref,
            user_id=user_id,
            old_status=TradeStatus.ACTIVE,
            new_status=TradeStatus.MATURED,
            notes="Far leg settled"
        )
        
        return trade, None

    def get_collateral_summary(self) -> Dict[str, Any]:
        """
        Get summary of collateral positions from active trades.
        """
        # Query active trades (including Approved, Near Leg Settled, Active)
        active_statuses = [
            TradeStatus.APPROVED, 
            TradeStatus.NEAR_LEG_SETTLED, 
            TradeStatus.ACTIVE
        ]
        
        trades = self.db.query(RepoTrade).filter(
            RepoTrade.status.in_(active_statuses)
        ).all()
        
        pledged = Decimal("0")
        received = Decimal("0")
        by_security = {}
        
        for trade in trades:
            mkt_val = trade.collateral_market_value or Decimal("0")
            isin = trade.collateral_isin or "UNKNOWN"
            
            if isin not in by_security:
                by_security[isin] = {
                    "isin": isin, 
                    "security_name": "Unknown", # In real app, join with SecurityMaster
                    "pledged_value": Decimal("0"), 
                    "received_value": Decimal("0")
                }
            
            if trade.trade_type == "REPO":
                pledged += mkt_val
                by_security[isin]["pledged_value"] += mkt_val
            else:
                received += mkt_val
                by_security[isin]["received_value"] += mkt_val

        return {
            "total_pledged_value": pledged,
            "total_received_value": received,
            "net_collateral": received - pledged,
            "by_security": list(by_security.values()),
            "margin_calls_pending": 0  # Placeholder
        }

    def early_terminate_trade(
        self, 
        trade_ref: str, 
        termination_date: date, 
        user_id: str
    ) -> Tuple[Optional[RepoTrade], Optional[str]]:
        """
        Early terminate an active repo trade.
        Recalculates interest up to termination date.
        """
        trade = self.get_trade(trade_ref)
        if not trade:
            return None, f"Trade {trade_ref} not found"
            
        if trade.status not in [TradeStatus.ACTIVE, TradeStatus.NEAR_LEG_SETTLED]:
             return None, f"Trade must be ACTIVE to terminate (current: {trade.status})"

        if termination_date < trade.start_date:
             return None, "Termination date cannot be before start date"

        # Recalculate amounts
        repo_calc = self.calc.calculate_repo_interest(
            near_leg_amount=trade.near_leg_amount,
            repo_rate=trade.repo_rate,
            start_date=trade.start_date,
            end_date=termination_date,
            convention=DayCountConvention(trade.day_count_convention) if trade.day_count_convention else DayCountConvention.ACT_365
        )

        old_status = trade.status
        trade.status = TradeStatus.EARLY_TERMINATED
        trade.is_early_terminated = True
        trade.early_termination_date = termination_date
        trade.end_date = termination_date
        trade.far_leg_amount = repo_calc["far_leg_amount"]
        trade.interest_amount = repo_calc["interest_amount"]
        trade.updated_at = datetime.utcnow()

        self.audit.log_status_change(
            entity_type=EntityType.REPO_TRADE,
            entity_id=trade_ref,
            user_id=user_id,
            old_status=old_status,
            new_status=TradeStatus.EARLY_TERMINATED,
            notes=f"Early terminated on {termination_date}. New Far Leg: {trade.far_leg_amount}"
        )
        
        return trade, None

    def check_margin_call(
        self, 
        trade_ref: str, 
        current_market_price: Decimal
    ) -> Dict[str, Any]:
        """
        Check margin status for a repo trade.
        """
        trade = self.get_trade(trade_ref)
        if not trade:
            return {"error": f"Trade {trade_ref} not found"}
            
        if trade.status not in [TradeStatus.ACTIVE, TradeStatus.NEAR_LEG_SETTLED]:
             return {"error": "Margin call only applicable to active trades"}

        # Recalculate collateral value
        col_calc = self.calc.calculate_collateral_value(
            face_value=trade.collateral_face_value,
            market_price=current_market_price,
            haircut_pct=trade.haircut_pct
        )
        new_val = col_calc["collateral_value"]
        
        # Exposure = Near Leg + Accrued Interest (approx or real)
        # For margin call, usually based on Repurchase Price at that moment?
        # Or just Near Leg amount? 
        # Usually Exposure = Purchase Price (Near Leg) + Accrued Repo Interest.
        # Let's calculate accrued repo interest.
        repo_interest = self.calc.calculate_simple_interest(
            principal=trade.near_leg_amount,
            rate=trade.repo_rate,
            start_date=trade.start_date,
            end_date=date.today(), # As of today
            convention=DayCountConvention(trade.day_count_convention) if trade.day_count_convention else DayCountConvention.ACT_365
        )
        exposure = trade.near_leg_amount + repo_interest

        # Calculate Margin
        margin_res = self.calc.calculate_margin(
            collateral_value=new_val,
            exposure_amount=exposure,
            threshold_pct=trade.margin_call_threshold
        )
        
        # Update trade current margin for record?
        # Maybe separate method to update, but this is "check".
        # We can update trade.current_margin if checking?
        # trade.current_margin = margin_res["margin_pct"]
        # self.db.commit() # Warning: Side effect in GET/Check?
        
        return {
            "trade_ref": trade_ref,
            "current_margin_pct": margin_res["margin_pct"],
            "required_margin_pct": Decimal("100"), # Base coverage
            "margin_call_triggered": margin_res["needs_margin_call"],
            "margin_call_amount": margin_res["margin_call_amount"],
            "margin_call_direction": "DELIVER" if trade.trade_type == "REPO" else "RETURN", # Simplified
            "calculated_at": datetime.utcnow()
        }

