"""
Treasury Management System - ThaiBMA Reporting Service
=======================================================

Service for reporting bond trades to the Thai Bond Market Association (ThaiBMA).

ThaiBMA Requirements:
- All OTC bond trades must be reported within 30 minutes of execution
- Reports include trade details, counterparty, settlement info
- Response includes ThaiBMA reference number

This is a simulation - actual ThaiBMA integration requires API credentials.
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, Dict, Any, List, Tuple
from uuid import uuid4
import logging
import json

from sqlalchemy.orm import Session

from app.models.transactions import BondTrade

logger = logging.getLogger(__name__)


# =============================================================================
# ThaiBMA Message Formats
# =============================================================================

class ThaiBMAReportFormat:
    """
    ThaiBMA report message format.
    Based on ThaiBMA OTC Trade Reporting specifications.
    """
    
    @staticmethod
    def create_trade_report(trade: BondTrade) -> Dict[str, Any]:
        """
        Create ThaiBMA trade report message.
        
        Returns:
            Dictionary with ThaiBMA report format
        """
        return {
            "header": {
                "message_type": "OTC_TRADE_REPORT",
                "sender_id": trade.entity_id,
                "timestamp": datetime.now().isoformat(),
                "report_id": f"RPT{uuid4().hex[:12].upper()}"
            },
            "trade_details": {
                "trade_reference": trade.trade_ref,
                "isin": trade.isin,
                "trade_side": trade.trade_side,
                "trade_type": trade.trade_type,
                "trade_date": trade.trade_date.isoformat(),
                "trade_time": trade.created_at.strftime("%H:%M:%S") if trade.created_at else None,
                "settlement_date": trade.settlement_date.isoformat(),
            },
            "counterparty": {
                "counterparty_id": trade.counterparty_id,
                "counterparty_type": "BANK",  # TODO: Get from counterparty master
            },
            "amounts": {
                "face_value": str(trade.face_value),
                "quantity": str(trade.quantity),
                "clean_price": str(trade.clean_price),
                "yield_rate": str(trade.yield_rate) if trade.yield_rate else None,
                "accrued_interest": str(trade.accrued_interest),
                "settlement_amount": str(trade.settlement_amount),
                "currency": "THB"
            },
            "trader": {
                "trader_id": trade.trader_id,
            }
        }
    
    @staticmethod
    def parse_report_response(response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse ThaiBMA response message.
        
        Returns:
            Parsed response with status and reference
        """
        return {
            "success": response.get("status") == "ACCEPTED",
            "thaibma_ref": response.get("thaibma_reference"),
            "report_time": response.get("receipt_time"),
            "validation_errors": response.get("errors", []),
            "warnings": response.get("warnings", [])
        }


# =============================================================================
# ThaiBMA Reporting Service
# =============================================================================

class ThaiBMAReportingService:
    """
    Service for ThaiBMA trade reporting.
    
    In production, this would connect to ThaiBMA API.
    Currently simulates successful reporting.
    """
    
    # ThaiBMA reporting window (30 minutes)
    REPORTING_WINDOW_MINUTES = 30
    
    def __init__(self, db: Session):
        self.db = db
    
    def report_trade(
        self, 
        trade: BondTrade
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Report a single trade to ThaiBMA.
        
        Args:
            trade: BondTrade to report
            
        Returns:
            Tuple of (success, details)
        """
        # Validate trade is eligible for reporting
        if trade.is_thaibma_reported:
            return False, {
                "error": "Trade already reported to ThaiBMA",
                "thaibma_ref": trade.thaibma_ref
            }
        
        if trade.status not in ["APPROVED", "PENDING_SETTLEMENT", "SETTLED"]:
            return False, {
                "error": f"Trade status '{trade.status}' not eligible for ThaiBMA reporting"
            }
        
        # Check reporting window
        report_deadline = trade.created_at + timedelta(minutes=self.REPORTING_WINDOW_MINUTES)
        is_late = datetime.now() > report_deadline
        
        # Create report message
        report = ThaiBMAReportFormat.create_trade_report(trade)
        
        # Simulate ThaiBMA API call
        logger.info(f"Reporting trade {trade.trade_ref} to ThaiBMA...")
        logger.debug(f"ThaiBMA Report: {json.dumps(report, indent=2, default=str)}")
        
        # Simulate response
        thaibma_ref = self._generate_thaibma_ref()
        report_time = datetime.now()
        
        # Update trade with ThaiBMA reference
        trade.is_thaibma_reported = True
        trade.thaibma_ref = thaibma_ref
        trade.thaibma_report_time = report_time
        trade.updated_at = report_time
        
        # Log result
        logger.info(f"Trade {trade.trade_ref} reported: ThaiBMA Ref = {thaibma_ref}")
        
        return True, {
            "success": True,
            "thaibma_ref": thaibma_ref,
            "report_time": report_time.isoformat(),
            "is_late": is_late,
            "late_by_minutes": max(0, (datetime.now() - report_deadline).total_seconds() / 60) if is_late else 0,
            "report_message": report
        }
    
    def report_multiple_trades(
        self,
        trades: List[BondTrade]
    ) -> Dict[str, Any]:
        """
        Report multiple trades to ThaiBMA.
        
        Args:
            trades: List of trades to report
            
        Returns:
            Summary of reporting results
        """
        results = {
            "total": len(trades),
            "successful": 0,
            "failed": 0,
            "already_reported": 0,
            "details": []
        }
        
        for trade in trades:
            if trade.is_thaibma_reported:
                results["already_reported"] += 1
                results["details"].append({
                    "trade_ref": trade.trade_ref,
                    "status": "ALREADY_REPORTED",
                    "thaibma_ref": trade.thaibma_ref
                })
                continue
            
            success, details = self.report_trade(trade)
            
            if success:
                results["successful"] += 1
                results["details"].append({
                    "trade_ref": trade.trade_ref,
                    "status": "REPORTED",
                    "thaibma_ref": details["thaibma_ref"]
                })
            else:
                results["failed"] += 1
                results["details"].append({
                    "trade_ref": trade.trade_ref,
                    "status": "FAILED",
                    "error": details.get("error")
                })
        
        return results
    
    def get_unreported_trades(
        self,
        max_age_hours: int = 24
    ) -> List[BondTrade]:
        """
        Get approved trades that haven't been reported to ThaiBMA.
        
        Args:
            max_age_hours: Maximum age of trades to include
            
        Returns:
            List of unreported trades
        """
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        
        return self.db.query(BondTrade).filter(
            BondTrade.status.in_(["APPROVED", "PENDING_SETTLEMENT"]),
            BondTrade.is_thaibma_reported == False,
            BondTrade.created_at >= cutoff
        ).order_by(BondTrade.created_at).all()
    
    def get_late_reports(self) -> List[BondTrade]:
        """
        Get trades that were reported late (after 30 min window).
        
        Returns:
            List of late-reported trades
        """
        return self.db.query(BondTrade).filter(
            BondTrade.is_thaibma_reported == True,
            BondTrade.thaibma_report_time > (
                BondTrade.created_at + timedelta(minutes=self.REPORTING_WINDOW_MINUTES)
            )
        ).all()
    
    def get_reporting_summary(
        self,
        report_date: date = None
    ) -> Dict[str, Any]:
        """
        Get ThaiBMA reporting summary for a date.
        
        Args:
            report_date: Date to summarize (default: today)
            
        Returns:
            Reporting statistics
        """
        if report_date is None:
            report_date = date.today()
        
        # Total approved trades for the date
        total_trades = self.db.query(BondTrade).filter(
            BondTrade.trade_date == report_date,
            BondTrade.status.in_(["APPROVED", "PENDING_SETTLEMENT", "SETTLED"])
        ).count()
        
        # Reported trades
        reported = self.db.query(BondTrade).filter(
            BondTrade.trade_date == report_date,
            BondTrade.is_thaibma_reported == True
        ).count()
        
        # Pending reporting
        pending = self.db.query(BondTrade).filter(
            BondTrade.trade_date == report_date,
            BondTrade.status.in_(["APPROVED", "PENDING_SETTLEMENT"]),
            BondTrade.is_thaibma_reported == False
        ).count()
        
        return {
            "report_date": report_date.isoformat(),
            "total_eligible_trades": total_trades,
            "reported": reported,
            "pending_report": pending,
            "reporting_rate_pct": (reported / total_trades * 100) if total_trades > 0 else 0,
            "within_30_min_count": None,  # TODO: Calculate on-time reporting rate
        }
    
    def _generate_thaibma_ref(self) -> str:
        """
        Generate simulated ThaiBMA reference number.
        
        Format: TBMA + YYYYMMDD + HHMMSS + 4-digit random
        """
        now = datetime.now()
        return f"TBMA{now.strftime('%Y%m%d%H%M%S')}{uuid4().hex[:4].upper()}"


# =============================================================================
# Auto-Reporting Job
# =============================================================================

def auto_report_pending_trades(db: Session) -> Dict[str, Any]:
    """
    Job to automatically report pending trades to ThaiBMA.
    
    Should be run every few minutes to ensure 30-min compliance.
    
    Returns:
        Job execution summary
    """
    service = ThaiBMAReportingService(db)
    
    # Get unreported trades
    unreported = service.get_unreported_trades(max_age_hours=1)
    
    if not unreported:
        return {
            "status": "NO_PENDING",
            "message": "No trades pending ThaiBMA reporting"
        }
    
    # Report trades
    results = service.report_multiple_trades(unreported)
    
    logger.info(
        f"ThaiBMA auto-report: {results['successful']}/{results['total']} trades reported"
    )
    
    return {
        "status": "COMPLETED",
        **results
    }
