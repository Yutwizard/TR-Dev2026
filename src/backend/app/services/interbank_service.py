"""
Treasury Management System - Interbank Deal Service
===================================================

Core business logic for interbank lending and borrowing:
- Deal creation and validation
- Interest calculations (via CalculationEngine)
- Four-eyes approval workflow (via StateMachine)
- Limit checking (placement limits)
- Audit logging (via AuditService)
- Maturity and accrual processing
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from uuid import uuid4
import logging

from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_

from app.models.transactions import InterbankDeal
from app.models.master_data import CounterpartyMaster
from app.models.limits import LimitDefinition, LimitUtilization
from app.core.enums import (
    TradeStatus, TradeSide, InterbankDealType, 
    DayCountConvention, EntityType, AuditAction
)
from app.core.state_machine import (
    assert_transition, INTERBANK_DEAL_TRANSITIONS, validate_transition
)
from app.services.calculation_engine import CalculationEngine
from app.services.audit_service import AuditService
from app.services.calendar_service import is_thai_business_day

logger = logging.getLogger(__name__)


class InterbankService:
    """
    Service for managing the lifecycle of interbank deals.
    """

    def __init__(self, db: Session):
        self.db = db
        self.calc = CalculationEngine()
        self.audit = AuditService(db)

    def _generate_deal_ref(self, prefix: str = "IB-") -> str:
        """
        Generate a unique deal reference.
        Format: IB-YYYYMMDD-XXX
        """
        today = date.today()
        date_str = today.strftime("%Y%m%d")
        
        # Count today's interbank deals
        count = self.db.query(func.count(InterbankDeal.deal_id)).filter(
            func.date(InterbankDeal.created_at) == today
        ).scalar() or 0
        
        seq = count + 1
        return f"{prefix}{date_str}-{seq:03d}"

    def _check_counterparty_limit(self, counterparty_id: str, amount: Decimal) -> Dict[str, Any]:
        """
        Check if the new deal amount breaches the counterparty limit.
        Only considers ACTIVE and PENDING_APPROVAL placements.
        """
        # 1. Find the limit definition (assume type 'COUNTERPARTY')
        # In a real system, we might have multiple limit types.
        limit_def = self.db.query(LimitDefinition).filter(
            LimitDefinition.counterparty_id == counterparty_id,
            LimitDefinition.limit_type == "COUNTERPARTY",
            LimitDefinition.status == "APPROVED",
            LimitDefinition.effective_date <= date.today(),
            (LimitDefinition.expiry_date == None) | (LimitDefinition.expiry_date >= date.today())
        ).first()

        if not limit_def:
            return {"status": "SUCCESS", "message": "No specific limit defined for this counterparty"}

        # 2. Calculate current exposure
        # Sum of principal for all active/pending placements with this counterparty
        current_exposure = self.db.query(func.sum(InterbankDeal.principal_amount)).filter(
            InterbankDeal.counterparty_id == counterparty_id,
            InterbankDeal.deal_type == InterbankDealType.PLACEMENT,
            InterbankDeal.status.in_([TradeStatus.PENDING_APPROVAL, TradeStatus.APPROVED, TradeStatus.ACTIVE])
        ).scalar() or Decimal("0")

        # 3. Check breach
        total_exposure = current_exposure + amount
        
        if total_exposure > limit_def.limit_amount:
             return {
                 "status": "BREACH",
                 "message": f"Counterparty limit breach! Limit: {limit_def.limit_amount:,.2f}, "
                            f"Current: {current_exposure:,.2f}, New Total: {total_exposure:,.2f}"
             }
        
        # 4. Check warning
        warning_threshold = limit_def.limit_amount * (limit_def.warning_threshold_pct / Decimal("100"))
        if total_exposure > warning_threshold:
             return {
                 "status": "WARNING",
                 "message": f"Counterparty limit warning (> {limit_def.warning_threshold_pct}%). "
                            f"Limit: {limit_def.limit_amount:,.2f}, New Total: {total_exposure:,.2f}"
             }

        return {
            "status": "SUCCESS", 
            "message": f"Limit check passed. Utilization: {(total_exposure/limit_def.limit_amount)*100:.1f}%"
        }

    def create_deal(
        self,
        deal_type: str,
        counterparty_id: str,
        portfolio_id: str,
        principal_amount: Decimal,
        interest_rate: Decimal,
        start_date: date,
        maturity_date: date,
        trader_id: str,
        entity_id: str = "BANK001",
        currency: str = "THB",
        rate_type: str = "FIXED",
        day_count_convention: str = "ACT/365",
        external_ref: Optional[str] = None,
        spread: Decimal = Decimal("0"),
        reference_rate: Optional[str] = None,
        **kwargs
    ) -> Tuple[Optional[InterbankDeal], Dict[str, Any]]:
        """
        Create a new interbank deal with validation and calculations.
        """
        validation_details = {"errors": [], "warnings": []}

        # 1. Validation
        if maturity_date <= start_date:
            validation_details["errors"].append("Maturity date must be after start date")

        # Business day check (optional based on system config, but recommended)
        if not is_thai_business_day(start_date):
             validation_details["warnings"].append(f"Start date {start_date} is not a Thai business day")

        # Counterparty check
        cp = self.db.query(CounterpartyMaster).filter(
            CounterpartyMaster.counterparty_id == counterparty_id,
            CounterpartyMaster.is_active == True
        ).first()
        if not cp:
            validation_details["errors"].append(f"Counterparty {counterparty_id} not found or inactive")

        if validation_details["errors"]:
            return None, validation_details

        # 2. Calculations
        calc_results = self.calc.calculate_interbank_amounts(
            principal_amount, 
            interest_rate, 
            start_date, 
            maturity_date, 
            day_count_convention
        )

        # 3. Limit Checking (Only for Lending/Placements)
        if deal_type == InterbankDealType.PLACEMENT:
            limit_result = self._check_counterparty_limit(counterparty_id, principal_amount)
            if limit_result["status"] == "BREACH":
                validation_details["errors"].append(limit_result["message"])
            elif limit_result["status"] == "WARNING":
                validation_details["warnings"].append(limit_result["message"])
            
            validation_details["limit_check"] = limit_result

        # 4. Persistence
        deal_ref = self._generate_deal_ref()
        deal = InterbankDeal(
            deal_id=f"IBD-{uuid4().hex[:8].upper()}",
            deal_ref=deal_ref,
            external_ref=external_ref,
            entity_id=entity_id,
            counterparty_id=counterparty_id,
            portfolio_id=portfolio_id,
            deal_type=deal_type,
            deal_date=date.today(),
            start_date=start_date,
            maturity_date=maturity_date,
            currency=currency,
            principal_amount=principal_amount,
            rate_type=rate_type,
            interest_rate=interest_rate,
            spread=spread,
            reference_rate=reference_rate,
            day_count_convention=day_count_convention,
            interest_amount=calc_results["interest_amount"],
            accrued_interest=Decimal("0"),
            maturity_amount=calc_results["maturity_amount"],
            status=TradeStatus.PENDING_APPROVAL,
            trader_id=trader_id,
            start_settlement_status="PENDING",
            maturity_settlement_status="PENDING"
        )

        self.db.add(deal)
        
        # 5. Audit Trail
        self.audit.log_created(
            entity_type=EntityType.INTERBANK_DEAL,
            entity_id=deal_ref,
            user_id=trader_id,
            new_values={
                "principal": str(principal_amount),
                "rate": str(interest_rate),
                "type": deal_type,
                "status": TradeStatus.PENDING_APPROVAL
            }
        )

        return deal, validation_details

    def get_deal(self, deal_ref: str) -> Optional[InterbankDeal]:
        """
        Get a deal by reference.
        """
        return self.db.query(InterbankDeal).filter(InterbankDeal.deal_ref == deal_ref).first()

    def list_deals(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Dict[str, Any] = None
    ) -> Tuple[List[InterbankDeal], int]:
        """
        List deals with filtering and pagination.
        Returns (items, total_count).
        """
        query = self.db.query(InterbankDeal)
        
        if filters:
            if filters.get("status"):
                query = query.filter(InterbankDeal.status == filters["status"])
            if filters.get("deal_type"):
                query = query.filter(InterbankDeal.deal_type == filters["deal_type"])
            if filters.get("counterparty_id"):
                query = query.filter(InterbankDeal.counterparty_id == filters["counterparty_id"])
            if filters.get("date_from"):
                query = query.filter(InterbankDeal.deal_date >= filters["date_from"])
            if filters.get("date_to"):
                query = query.filter(InterbankDeal.deal_date <= filters["date_to"])

        total = query.count()
        items = query.order_by(InterbankDeal.created_at.desc()).offset(skip).limit(limit).all()
        
        return items, total

    def approve_deal(self, deal_ref: str, approver_id: str) -> Tuple[Optional[InterbankDeal], Optional[str]]:
        """
        Approve an interbank deal. Enforces four-eyes principle.
        """
        deal = self.db.query(InterbankDeal).filter(InterbankDeal.deal_ref == deal_ref).first()
        if not deal:
            return None, f"Deal {deal_ref} not found"

        # Four-eyes check
        if deal.trader_id == approver_id:
            return None, "Approver cannot be the same as the trader (Four-Eyes Principle)"

        # State transition validation
        try:
            assert_transition(
                deal.status, 
                TradeStatus.APPROVED, 
                INTERBANK_DEAL_TRANSITIONS,
                entity_type="InterbankDeal",
                entity_ref=deal_ref
            )
        except ValueError as e:
            return None, str(e)

        old_status = deal.status
        deal.status = TradeStatus.APPROVED
        deal.approver_id = approver_id
        deal.approved_at = datetime.utcnow()

        # Log audit
        self.audit.log_approved(
            entity_type=EntityType.INTERBANK_DEAL,
            entity_id=deal_ref,
            approver_id=approver_id
        )
        
        self.audit.log_status_change(
            entity_type=EntityType.INTERBANK_DEAL,
            entity_id=deal_ref,
            user_id=approver_id,
            old_status=old_status,
            new_status=TradeStatus.APPROVED
        )

        return deal, None

    def reject_deal(self, deal_ref: str, rejector_id: str, reason: str) -> Tuple[Optional[InterbankDeal], Optional[str]]:
        """
        Reject a deal.
        """
        deal = self.db.query(InterbankDeal).filter(InterbankDeal.deal_ref == deal_ref).first()
        if not deal:
            return None, f"Deal {deal_ref} not found"

        try:
            assert_transition(
                deal.status, 
                TradeStatus.REJECTED, 
                INTERBANK_DEAL_TRANSITIONS,
                entity_type="InterbankDeal",
                entity_ref=deal_ref
            )
        except ValueError as e:
            return None, str(e)

        old_status = deal.status
        deal.status = TradeStatus.REJECTED
        
        self.audit.log_rejected(
            entity_type=EntityType.INTERBANK_DEAL,
            entity_id=deal_ref,
            rejector_id=rejector_id,
            reason=reason
        )

        return deal, None

    def cancel_deal(self, deal_ref: str, user_id: str, reason: str) -> Tuple[Optional[InterbankDeal], Optional[str]]:
        """
        Cancel a deal (e.g., if DRAFT or PENDING_APPROVAL).
        """
        deal = self.db.query(InterbankDeal).filter(InterbankDeal.deal_ref == deal_ref).first()
        if not deal:
            return None, f"Deal {deal_ref} not found"

        try:
            assert_transition(
                deal.status, 
                TradeStatus.CANCELLED, 
                INTERBANK_DEAL_TRANSITIONS,
                entity_type="InterbankDeal",
                entity_ref=deal_ref
            )
        except ValueError as e:
            return None, str(e)

        old_status = deal.status
        deal.status = TradeStatus.CANCELLED
        
        self.audit.log_cancelled(
            entity_type=EntityType.INTERBANK_DEAL,
            entity_id=deal_ref,
            user_id=user_id,
            reason=reason
        )

        return deal, None

    def settle_start_leg(self, deal_ref: str, user_id: str, bahtnet_ref: str) -> Tuple[Optional[InterbankDeal], Optional[str]]:
        """
        Record settlement of the start leg (near leg).
        Transitions deal to ACTIVE.
        """
        deal = self.db.query(InterbankDeal).filter(InterbankDeal.deal_ref == deal_ref).first()
        if not deal:
            return None, f"Deal {deal_ref} not found"

        if deal.status != TradeStatus.APPROVED:
            return None, f"Deal must be APPROVED to settle (current: {deal.status})"

        deal.start_settlement_status = "SETTLED"
        deal.start_settled_at = datetime.utcnow()
        deal.start_bahtnet_ref = bahtnet_ref
        
        # Transition to ACTIVE
        old_status = deal.status
        deal.status = TradeStatus.ACTIVE

        self.audit.log_status_change(
            entity_type=EntityType.INTERBANK_DEAL,
            entity_id=deal_ref,
            user_id=user_id,
            old_status=old_status,
            new_status=TradeStatus.ACTIVE,
            notes=f"Start leg settled via {bahtnet_ref}"
        )

        return deal, None

    def update_daily_accrual(self, valuation_date: date = None) -> int:
        """
        Batch process to update daily interest accrual for all ACTIVE deals.
        """
        if not valuation_date:
            valuation_date = date.today()

        active_deals = self.db.query(InterbankDeal).filter(
            InterbankDeal.status == TradeStatus.ACTIVE,
            InterbankDeal.start_date <= valuation_date,
            InterbankDeal.maturity_date > valuation_date
        ).all()

        updated_count = 0
        for deal in active_deals:
            # Re-calculate daily amount using engine
            daily_amt = self.calc.calculate_daily_accrual(
                deal.principal_amount, 
                deal.interest_rate, 
                deal.day_count_convention
            )
            
            # Days since start
            accrued_days = (valuation_date - deal.start_date).days
            deal.accrued_interest = (daily_amt * accrued_days).quantize(Decimal("0.01"))
            updated_count += 1

        self.db.flush()
        return updated_count

    def process_maturities(self, valuation_date: date = None) -> int:
        """
        Identify deals reaching maturity and tag them for settlement.
        """
        if not valuation_date:
            valuation_date = date.today()

        maturing_deals = self.db.query(InterbankDeal).filter(
            InterbankDeal.status == TradeStatus.ACTIVE,
            InterbankDeal.maturity_date <= valuation_date
        ).all()

        matured_count = 0
        for deal in maturing_deals:
            old_status = deal.status
            deal.status = TradeStatus.MATURED
            
            # Final interest check
            deal.accrued_interest = deal.interest_amount
            
            self.audit.log_status_change(
                entity_type=EntityType.INTERBANK_DEAL,
                entity_id=deal.deal_ref,
                user_id="SYSTEM",
                old_status=old_status,
                new_status=TradeStatus.MATURED,
                notes="Automatic maturity processing"
            )
            matured_count += 1

        return matured_count
