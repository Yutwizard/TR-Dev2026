"""
Treasury Management System - Market Data Service
=================================================

Service for importing and managing ThaiBMA market data.

Features:
- Import Mark2Market CSV files from ThaiBMA
- Price validation and alerts
- Historical price tracking
- Batch import processing
"""

import csv
import os
import uuid
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging

from app.models.market_data import ThaiBMAMarketData, MarketDataImportLog
from app.models.master_data import SecurityMaster

logger = logging.getLogger(__name__)


class PriceValidationError(Exception):
    """Raised when price validation fails"""
    pass


class MarketDataImportError(Exception):
    """Raised when import fails"""
    pass


class MarketDataService:
    """
    Service for managing ThaiBMA market data imports.
    """
    
    # Price movement thresholds for alerts
    PRICE_WARNING_THRESHOLD = Decimal("0.05")  # 5%
    PRICE_ALERT_THRESHOLD = Decimal("0.10")    # 10%
    PRICE_CRITICAL_THRESHOLD = Decimal("0.20") # 20%
    
    def __init__(self, db: Session):
        self.db = db
    
    def import_market_data_file(
        self, 
        file_path: str, 
        import_date: Optional[date] = None,
        user_id: Optional[str] = None
    ) -> MarketDataImportLog:
        """
        Import a ThaiBMA Mark2Market CSV file.
        
        Args:
            file_path: Path to the CSV file
            import_date: The date this data represents (defaults to filename date or today)
            user_id: ID of user performing the import
            
        Returns:
            MarketDataImportLog record
        """
        # Parse file name for date
        file_name = os.path.basename(file_path)
        
        # Extract date from filename (e.g., Mark2Market_30112025.csv -> 2025-11-30)
        if not import_date:
            import_date = self._parse_date_from_filename(file_name)
        
        # Create import log
        batch_id = f"THBMA_{import_date.strftime('%Y%m%d')}_{uuid.uuid4().hex[:8].upper()}"
        import_log = MarketDataImportLog(
            batch_id=batch_id,
            import_date=import_date,
            file_name=file_name,
            file_size_bytes=os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            status="PROCESSING",
            started_at=datetime.now(),
            created_by=user_id
        )
        self.db.add(import_log)
        self.db.commit()
        
        try:
            # Process the file
            stats = self._process_csv_file(file_path, import_date, batch_id, user_id)
            
            # Update import log
            import_log.total_records = stats['total']
            import_log.successful_records = stats['success']
            import_log.failed_records = stats['failed']
            import_log.skipped_records = stats['skipped']
            import_log.price_movement_alerts = stats['price_alerts']
            import_log.missing_securities = stats['missing_securities']
            import_log.status = "COMPLETED"
            import_log.completed_at = datetime.now()
            
            self.db.commit()
            logger.info(f"Market data import completed: {stats['success']}/{stats['total']} records")
            
        except Exception as e:
            import_log.status = "FAILED"
            import_log.error_message = str(e)
            import_log.completed_at = datetime.now()
            self.db.commit()
            logger.error(f"Market data import failed: {e}")
            raise MarketDataImportError(f"Import failed: {e}")
        
        return import_log
    
    def _process_csv_file(
        self, 
        file_path: str, 
        data_date: date, 
        batch_id: str,
        user_id: Optional[str] = None
    ) -> Dict:
        """
        Process the CSV file and import records.
        
        Returns:
            Dict with statistics
        """
        stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'price_alerts': 0,
            'missing_securities': 0
        }
        
        # Build security lookup cache
        security_cache = self._build_security_cache()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            
            # Skip header rows
            header_row = None
            current_section = None
            
            for row in reader:
                stats['total'] += 1
                
                # Skip empty rows
                if not row or not row[0].strip():
                    continue
                
                # Check for date header row
                if 'Source: ThaiBMA' in row[0] or 'November' in row[0] or 'December' in row[0]:
                    continue
                
                # Check for section headers
                if row[0] in ['Government Bonds', 'State Enterprise Bonds', 'Corporate Bonds', 'BOT Bonds']:
                    current_section = row[0]
                    continue
                
                # Check for column header row
                if row[0] == 'BOND':
                    header_row = row
                    continue
                
                # Process data row
                if header_row and row[0] and not row[0].startswith(''):
                    try:
                        result = self._process_data_row(
                            row, data_date, batch_id, file_path, 
                            security_cache, current_section, user_id
                        )
                        
                        if result == 'success':
                            stats['success'] += 1
                        elif result == 'skipped':
                            stats['skipped'] += 1
                        elif result == 'missing_security':
                            stats['missing_securities'] += 1
                            
                    except PriceValidationError as e:
                        stats['price_alerts'] += 1
                        logger.warning(f"Price alert for {row[0]}: {e}")
                        stats['success'] += 1  # Still import with alert
                    except Exception as e:
                        stats['failed'] += 1
                        logger.error(f"Failed to process row {row[0]}: {e}")
        
        return stats
    
    def _process_data_row(
        self, 
        row: List[str], 
        data_date: date, 
        batch_id: str,
        file_path: str,
        security_cache: Dict,
        bond_type: Optional[str],
        user_id: Optional[str] = None
    ) -> str:
        """
        Process a single data row from the CSV.
        
        Returns:
            'success', 'skipped', or 'missing_security'
        """
        # Map CSV columns
        symbol = row[0].strip() if len(row) > 0 else None
        if not symbol:
            return 'skipped'
        
        # Find security by symbol
        security_id = security_cache.get(symbol)
        if not security_id:
            # Try to find by symbol in database
            security = self.db.query(SecurityMaster).filter(
                func.upper(SecurityMaster.symbol) == symbol.upper()
            ).first()
            
            if not security:
                logger.warning(f"Security not found for symbol: {symbol}")
                return 'missing_security'
            
            security_id = security.security_id
            security_cache[symbol] = security_id
        
        # Check if record already exists
        existing = self.db.query(ThaiBMAMarketData).filter(
            ThaiBMAMarketData.security_id == security_id,
            ThaiBMAMarketData.data_date == data_date
        ).first()
        
        if existing:
            logger.debug(f"Record already exists for {symbol} on {data_date}")
            return 'skipped'
        
        # Parse values
        def parse_decimal(val: str) -> Optional[Decimal]:
            if not val or val.strip() in ['', '-', 'N/A']:
                return None
            try:
                return Decimal(val.strip())
            except (InvalidOperation, ValueError):
                return None
        
        def parse_date(val: str) -> Optional[date]:
            if not val or val.strip() in ['', '-']:
                return None
            try:
                # Try different date formats
                for fmt in ['%d-%b-%y', '%d-%b-%Y', '%Y-%m-%d']:
                    try:
                        return datetime.strptime(val.strip(), fmt).date()
                    except ValueError:
                        continue
                return None
            except Exception:
                return None
        
        # Extract fields from CSV
        # Column indices based on ThaiBMA Mark2Market format
        coupon_rate = parse_decimal(row[1]) if len(row) > 1 else None
        maturity_date = parse_date(row[2]) if len(row) > 2 else None
        ttm_years = parse_decimal(row[3]) if len(row) > 3 else None
        
        last_trade_date = parse_date(row[8]) if len(row) > 8 else None
        last_exec_yield = parse_decimal(row[9]) if len(row) > 9 else None
        quoted_date = parse_date(row[10]) if len(row) > 10 else None
        quoted_yield = parse_decimal(row[11]) if len(row) > 11 else None
        max_yield = parse_decimal(row[12]) if len(row) > 12 else None
        min_yield = parse_decimal(row[13]) if len(row) > 13 else None
        model_yield = parse_decimal(row[14]) if len(row) > 14 else None
        
        static_spread = parse_decimal(row[15]) if len(row) > 15 else None
        market_yield = parse_decimal(row[16]) if len(row) > 16 else None
        duration_metric = parse_decimal(row[17]) if len(row) > 17 else None
        
        clean_price = parse_decimal(row[18]) if len(row) > 18 else None
        accrued_interest = parse_decimal(row[19]) if len(row) > 19 else None
        modified_duration = parse_decimal(row[20]) if len(row) > 20 else None
        convexity = parse_decimal(row[21]) if len(row) > 21 else None
        par_value = parse_decimal(row[22]) if len(row) > 22 else None
        index_ratio = parse_decimal(row[25]) if len(row) > 25 else None
        
        # Validate clean price
        if clean_price is None:
            logger.warning(f"No clean price for {symbol}")
            return 'skipped'
        
        # Check for price movement alerts
        self._check_price_movement(security_id, symbol, clean_price, data_date)
        
        # Create record
        market_data = ThaiBMAMarketData(
            data_date=data_date,
            security_id=security_id,
            thaibma_symbol=symbol,
            coupon_rate=coupon_rate,
            maturity_date=maturity_date,
            time_to_maturity_years=ttm_years,
            bond_type=bond_type,
            last_trade_date=last_trade_date,
            last_executed_yield=last_exec_yield,
            quoted_date=quoted_date,
            quoted_yield=quoted_yield,
            max_yield=max_yield,
            min_yield=min_yield,
            model_yield=model_yield,
            static_spread_bp=static_spread,
            market_yield=market_yield,
            duration_metric=duration_metric,
            clean_price=clean_price,
            accrued_interest=accrued_interest,
            modified_duration=modified_duration,
            convexity=convexity,
            par_value=par_value or Decimal("1000"),
            index_ratio=index_ratio,
            import_batch_id=batch_id,
            import_file_name=os.path.basename(file_path),
            is_valid=True,
            created_by=user_id
        )
        
        self.db.add(market_data)
        self.db.flush()
        
        return 'success'
    
    def _check_price_movement(
        self, 
        security_id: str, 
        symbol: str, 
        current_price: Decimal,
        data_date: date
    ):
        """
        Check if price movement exceeds thresholds.
        
        Raises PriceValidationError if significant movement detected.
        """
        # Get previous day's price
        previous_data = self.db.query(ThaiBMAMarketData).filter(
            ThaiBMAMarketData.security_id == security_id,
            ThaiBMAMarketData.data_date < data_date,
            ThaiBMAMarketData.is_valid == True
        ).order_by(ThaiBMAMarketData.data_date.desc()).first()
        
        if not previous_data:
            return
        
        prev_price = previous_data.clean_price
        if prev_price == 0:
            return
        
        change_pct = abs(current_price - prev_price) / prev_price
        
        if change_pct >= self.PRICE_CRITICAL_THRESHOLD:
            raise PriceValidationError(
                f"CRITICAL: Price change {change_pct:.2%} for {symbol} "
                f"(from {prev_price} to {current_price})"
            )
        elif change_pct >= self.PRICE_ALERT_THRESHOLD:
            raise PriceValidationError(
                f"ALERT: Price change {change_pct:.2%} for {symbol} "
                f"(from {prev_price} to {current_price})"
            )
        elif change_pct >= self.PRICE_WARNING_THRESHOLD:
            raise PriceValidationError(
                f"WARNING: Price change {change_pct:.2%} for {symbol} "
                f"(from {prev_price} to {current_price})"
            )
    
    def _build_security_cache(self) -> Dict[str, str]:
        """
        Build a cache of symbol -> security_id mappings.
        """
        cache = {}
        securities = self.db.query(SecurityMaster.security_id, SecurityMaster.symbol).all()
        for sec in securities:
            if sec.symbol:
                cache[sec.symbol.upper()] = sec.security_id
        return cache
    
    def _parse_date_from_filename(self, filename: str) -> date:
        """
        Extract date from filename like Mark2Market_30112025.csv
        """
        try:
            # Remove extension and get date part
            base = os.path.splitext(filename)[0]
            # Format: Mark2Market_DDMMYYYY
            if '_' in base:
                date_str = base.split('_')[1]
                if len(date_str) == 8:
                    day = int(date_str[0:2])
                    month = int(date_str[2:4])
                    year = int(date_str[4:8])
                    return date(year, month, day)
        except Exception as e:
            logger.warning(f"Could not parse date from filename {filename}: {e}")
        
        return date.today()
    
    def get_latest_market_data(
        self, 
        security_id: str, 
        as_of_date: Optional[date] = None
    ) -> Optional[ThaiBMAMarketData]:
        """
        Get the latest market data for a security.
        
        Args:
            security_id: Security ID
            as_of_date: Get data as of this date (defaults to latest)
            
        Returns:
            ThaiBMAMarketData or None
        """
        query = self.db.query(ThaiBMAMarketData).filter(
            ThaiBMAMarketData.security_id == security_id,
            ThaiBMAMarketData.is_valid == True
        )
        
        if as_of_date:
            query = query.filter(ThaiBMAMarketData.data_date <= as_of_date)
        
        return query.order_by(ThaiBMAMarketData.data_date.desc()).first()
    
    def get_market_data_for_date(
        self, 
        data_date: date
    ) -> List[ThaiBMAMarketData]:
        """
        Get all market data for a specific date.
        """
        return self.db.query(ThaiBMAMarketData).filter(
            ThaiBMAMarketData.data_date == data_date,
            ThaiBMAMarketData.is_valid == True
        ).all()
    
    def get_price_history(
        self, 
        security_id: str, 
        from_date: date, 
        to_date: date
    ) -> List[ThaiBMAMarketData]:
        """
        Get price history for a security over a date range.
        """
        return self.db.query(ThaiBMAMarketData).filter(
            ThaiBMAMarketData.security_id == security_id,
            ThaiBMAMarketData.data_date >= from_date,
            ThaiBMAMarketData.data_date <= to_date,
            ThaiBMAMarketData.is_valid == True
        ).order_by(ThaiBMAMarketData.data_date).all()


# Convenience functions for use in other modules
def import_thaibma_market_data(
    db: Session, 
    file_path: str, 
    import_date: Optional[date] = None,
    user_id: Optional[str] = None
) -> MarketDataImportLog:
    """
    Import ThaiBMA market data file.
    
    Convenience function that creates service and runs import.
    """
    service = MarketDataService(db)
    return service.import_market_data_file(file_path, import_date, user_id)


def get_latest_price(
    db: Session, 
    security_id: str, 
    as_of_date: Optional[date] = None
) -> Optional[Decimal]:
    """
    Get the latest clean price for a security.
    
    Returns:
        Clean price as Decimal or None if no data
    """
    service = MarketDataService(db)
    data = service.get_latest_market_data(security_id, as_of_date)
    return data.clean_price if data else None
