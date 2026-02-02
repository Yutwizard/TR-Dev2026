"""
Treasury Management System - Position Service
==============================================

Service for managing bond positions and calculating EOD position snapshots.

Features:
- Real-time position tracking
- EOD position snapshot generation
- Cost basis calculations (Average Cost, FIFO)
- P&L calculations (Realized and Unrealized)
"""

from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
import logging

from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, or_, case

from app.models.transactions import BondTrade
from app.models.positions import BondPosition, NetPosition
from app.models.master_data import SecurityMaster

logger = logging.getLogger(__name__)


# =============================================================================
# Costing Methods
# =============================================================================

class CostingMethod(str, Enum):
    """Position costing method"""
    AVERAGE_COST = "AVERAGE_COST"
    FIFO = "FIFO"
    LIFO = "LIFO"
    SPECIFIC_ID = "SPECIFIC_ID"


# =============================================================================
# Position Calculation
# =============================================================================

class PositionService:
    """
    Service for managing security positions.
    """
    
    def __init__(self, db: Session, costing_method: CostingMethod = CostingMethod.AVERAGE_COST):
        self.db = db
        self.costing_method = costing_method
    
    def get_position(
        self,
        security_id: str,
        portfolio_id: str,
        position_date: date = None,
        entity_id: str = "ENT001"
    ) -> Optional[BondPosition]:
        """
        Get current position for a security in a portfolio.
        
        Args:
            security_id: Security ID
            portfolio_id: Portfolio ID
            position_date: Date of position (default: today)
            entity_id: Entity ID
            
        Returns:
            BondPosition or None if no position exists
        """
        if position_date is None:
            position_date = date.today()
            
        return self.db.query(BondPosition).filter(
            BondPosition.security_id == security_id,
            BondPosition.portfolio_id == portfolio_id,
            BondPosition.entity_id == entity_id,
            BondPosition.position_date == position_date
        ).first()
    
    def get_latest_position(
        self,
        security_id: str,
        portfolio_id: str,
        entity_id: str = "ENT001"
    ) -> Optional[BondPosition]:
        """
        Get the most recent position for a security in a portfolio.
        """
        return self.db.query(BondPosition).filter(
            BondPosition.security_id == security_id,
            BondPosition.portfolio_id == portfolio_id,
            BondPosition.entity_id == entity_id
        ).order_by(BondPosition.position_date.desc()).first()
    
    def get_portfolio_positions(
        self,
        portfolio_id: str,
        position_date: date = None,
        entity_id: str = "ENT001",
        include_zero: bool = False
    ) -> List[BondPosition]:
        """
        Get all positions for a portfolio on a given date.
        
        Args:
            portfolio_id: Portfolio ID
            position_date: Date of position (default: today)
            entity_id: Entity ID
            include_zero: Include positions with zero quantity
            
        Returns:
            List of positions
        """
        if position_date is None:
            position_date = date.today()
            
        query = self.db.query(BondPosition).filter(
            BondPosition.portfolio_id == portfolio_id,
            BondPosition.entity_id == entity_id,
            BondPosition.position_date == position_date
        )
        
        if not include_zero:
            query = query.filter(BondPosition.quantity != 0)
        
        return query.order_by(BondPosition.security_id).all()
    
    def calculate_position_from_trades(
        self,
        security_id: str,
        portfolio_id: str,
        entity_id: str = "ENT001",
        as_of_date: date = None
    ) -> Dict[str, Any]:
        """
        Calculate position by aggregating all settled trades.
        
        This is the source of truth for position calculation.
        
        Args:
            security_id: Security ID
            portfolio_id: Portfolio ID  
            entity_id: Entity ID
            as_of_date: Calculate position as of this date (default: today)
            
        Returns:
            Dictionary with position details
        """
        if as_of_date is None:
            as_of_date = date.today()
        
        # Get all settled trades for this security/portfolio
        trades = self.db.query(BondTrade).filter(
            BondTrade.security_id == security_id,
            BondTrade.portfolio_id == portfolio_id,
            BondTrade.entity_id == entity_id,
            BondTrade.settlement_date <= as_of_date,
            BondTrade.settlement_status == "SETTLED"
        ).order_by(BondTrade.settlement_date, BondTrade.created_at).all()
        
        if not trades:
            return {
                "security_id": security_id,
                "portfolio_id": portfolio_id,
                "quantity": Decimal("0"),
                "face_value": Decimal("0"),
                "cost_amount": Decimal("0"),
                "cost_price": Decimal("0"),
                "realized_pnl": Decimal("0"),
                "trade_count": 0
            }
        
        # Get security for ISIN
        security = self.db.query(SecurityMaster).filter(
            SecurityMaster.security_id == security_id
        ).first()
        
        # Calculate position using average cost method
        total_quantity = Decimal("0")
        total_face_value = Decimal("0")
        total_cost = Decimal("0")
        realized_pnl = Decimal("0")
        
        for trade in trades:
            if trade.trade_side == "BUY":
                # Add to position
                total_quantity += trade.quantity
                total_face_value += trade.face_value
                total_cost += trade.settlement_amount
            else:
                # Remove from position
                # Calculate realized P&L using average cost
                if total_quantity > 0:
                    avg_cost_per_unit = total_cost / total_quantity
                    cost_of_sold = avg_cost_per_unit * trade.quantity
                    realized_pnl += trade.settlement_amount - cost_of_sold
                    
                    total_quantity -= trade.quantity
                    total_face_value -= trade.face_value
                    total_cost -= cost_of_sold
        
        # Calculate average cost price
        cost_price = (total_cost / total_face_value * 100) if total_face_value > 0 else Decimal("0")
        
        return {
            "security_id": security_id,
            "portfolio_id": portfolio_id,
            "isin": security.isin if security else None,
            "quantity": total_quantity.quantize(Decimal("0.000001")),
            "face_value": total_face_value.quantize(Decimal("0.01")),
            "cost_amount": total_cost.quantize(Decimal("0.01")),
            "cost_price": cost_price.quantize(Decimal("0.000001")),
            "realized_pnl": realized_pnl.quantize(Decimal("0.01")),
            "trade_count": len(trades)
        }
    
    def create_or_update_position(
        self,
        position_date: date,
        entity_id: str,
        portfolio_id: str,
        security_id: str,
        isin: str,
        face_value: Decimal,
        quantity: Decimal,
        cost_price: Decimal,
        cost_amount: Decimal,
        market_price: Decimal = None,
        tfrs9_classification: str = "FVPL"
    ) -> BondPosition:
        """
        Create or update a bond position for a date.
        """
        position = self.get_position(security_id, portfolio_id, position_date, entity_id)
        
        if not position:
            position = BondPosition(
                position_date=position_date,
                entity_id=entity_id,
                portfolio_id=portfolio_id,
                security_id=security_id,
                isin=isin,
                face_value=face_value,
                quantity=quantity,
                cost_price=cost_price,
                cost_amount=cost_amount,
                tfrs9_classification=tfrs9_classification
            )
            self.db.add(position)
        else:
            position.face_value = face_value
            position.quantity = quantity
            position.cost_price = cost_price
            position.cost_amount = cost_amount
        
        if market_price:
            position.market_price = market_price
            position.market_value = (quantity * market_price).quantize(Decimal("0.01"))
            position.unrealized_pnl = position.market_value - cost_amount
        
        position.available_quantity = quantity - position.pledged_quantity
        
        return position
    
    def calculate_unrealized_pnl(
        self,
        position: BondPosition,
        market_price: Decimal
    ) -> Decimal:
        """
        Calculate unrealized P&L for a position.
        
        Args:
            position: The position
            market_price: Current market price (clean price)
            
        Returns:
            Unrealized P&L amount
        """
        if position.quantity <= 0:
            return Decimal("0")
        
        # Market value = Face Value × Market Price / 100
        market_value = (position.face_value * market_price / Decimal("100")).quantize(Decimal("0.01"))
        
        # Unrealized P&L = Market Value - Cost Amount
        unrealized = market_value - position.cost_amount
        
        return unrealized
    
    def create_eod_positions(
        self,
        position_date: date = None,
        market_prices: Dict[str, Decimal] = None,
        entity_id: str = "ENT001"
    ) -> List[BondPosition]:
        """
        Create EOD position snapshots for all positions.
        
        This should be run at end of day to capture position state.
        
        Args:
            position_date: Date of snapshot (default: today)
            market_prices: Dictionary of security_id -> market price
            entity_id: Entity ID
            
        Returns:
            List of created positions
        """
        if position_date is None:
            position_date = date.today()
        
        if market_prices is None:
            market_prices = {}
        
        logger.info(f"Creating EOD positions for {position_date}")
        
        # Get all unique security/portfolio combinations from trades
        combinations = self.db.query(
            BondTrade.security_id,
            BondTrade.portfolio_id
        ).filter(
            BondTrade.entity_id == entity_id,
            BondTrade.settlement_date <= position_date,
            BondTrade.settlement_status == "SETTLED"
        ).distinct().all()
        
        positions = []
        
        for security_id, portfolio_id in combinations:
            # Calculate position from trades
            calc = self.calculate_position_from_trades(
                security_id, portfolio_id, entity_id, position_date
            )
            
            if calc["quantity"] <= 0:
                continue
            
            # Get market price
            market_price = market_prices.get(security_id, calc["cost_price"])
            
            # Get portfolio for TFRS9 classification
            from app.models.master_data import PortfolioMaster
            portfolio = self.db.query(PortfolioMaster).filter(
                PortfolioMaster.portfolio_id == portfolio_id
            ).first()
            tfrs9 = portfolio.tfrs9_classification if portfolio else "FVPL"
            
            # Create position
            position = self.create_or_update_position(
                position_date=position_date,
                entity_id=entity_id,
                portfolio_id=portfolio_id,
                security_id=security_id,
                isin=calc["isin"],
                face_value=calc["face_value"],
                quantity=calc["quantity"],
                cost_price=calc["cost_price"],
                cost_amount=calc["cost_amount"],
                market_price=market_price,
                tfrs9_classification=tfrs9
            )
            
            positions.append(position)
        
        logger.info(f"Created {len(positions)} EOD positions for {position_date}")
        
        return positions
    
    def get_position_summary(
        self,
        position_date: date = None,
        entity_id: str = "ENT001"
    ) -> Dict[str, Any]:
        """
        Get summary of all positions for an entity.
        
        Returns:
            Position summary with totals
        """
        if position_date is None:
            position_date = date.today()
        
        positions = self.db.query(BondPosition).filter(
            BondPosition.entity_id == entity_id,
            BondPosition.position_date == position_date,
            BondPosition.quantity != 0
        ).all()
        
        total_cost = sum(p.cost_amount for p in positions)
        total_market_value = sum(p.market_value or p.cost_amount for p in positions)
        total_unrealized = sum(p.unrealized_pnl or Decimal("0") for p in positions)
        
        # Group by portfolio
        by_portfolio = {}
        for p in positions:
            if p.portfolio_id not in by_portfolio:
                by_portfolio[p.portfolio_id] = {
                    "positions": 0,
                    "total_cost": Decimal("0"),
                    "market_value": Decimal("0"),
                    "unrealized_pnl": Decimal("0")
                }
            by_portfolio[p.portfolio_id]["positions"] += 1
            by_portfolio[p.portfolio_id]["total_cost"] += p.cost_amount
            by_portfolio[p.portfolio_id]["market_value"] += p.market_value or p.cost_amount
            by_portfolio[p.portfolio_id]["unrealized_pnl"] += p.unrealized_pnl or Decimal("0")
        
        return {
            "entity_id": entity_id,
            "position_date": position_date.isoformat(),
            "total_positions": len(positions),
            "total_cost": str(total_cost),
            "total_market_value": str(total_market_value),
            "total_unrealized_pnl": str(total_unrealized),
            "by_portfolio": {
                k: {key: str(v) if isinstance(v, Decimal) else v for key, v in val.items()}
                for k, val in by_portfolio.items()
            }
        }


# =============================================================================
# EOD Job
# =============================================================================

def run_eod_position_process(
    db: Session,
    process_date: date = None,
    market_prices: Dict[str, Decimal] = None
) -> Dict[str, Any]:
    """
    Run end-of-day position processing.
    
    This should be scheduled to run daily after market close.
    
    Steps:
    1. Calculate positions from trades
    2. Mark-to-market using EOD prices
    3. Create position records
    
    Args:
        db: Database session
        process_date: Processing date
        market_prices: EOD market prices
        
    Returns:
        Processing summary
    """
    if process_date is None:
        process_date = date.today()
    
    logger.info(f"Starting EOD position processing for {process_date}")
    
    service = PositionService(db)
    
    # Create EOD positions
    positions = service.create_eod_positions(
        position_date=process_date,
        market_prices=market_prices or {}
    )
    
    # Get summary
    summary = service.get_position_summary(position_date=process_date)
    
    return {
        "process_date": process_date.isoformat(),
        "positions_created": len(positions),
        "position_summary": summary
    }
