"""
EOD Batch Processor - Treasury Management System
=================================================

Runs End-of-Day processes for all active modules:
1. Interbank: Daily Accrual Update
2. Interbank: Maturity Processing
3. (Future) Repo: Mark-to-Market & Margin Check
4. (Future) Bond: Valuation Update

Usage:
    python scripts/run_eod_batch.py [--date YYYY-MM-DD]
"""

import sys
import os
import argparse
import logging
from datetime import date, datetime

# Add src/backend to python path to allow imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(project_root, "src", "backend"))

from app.database import get_sync_db
from app.services.interbank_service import InterbankService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/eod_batch.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def run_batch(process_date: date):
    logger.info(f"Starting EOD Batch for Date: {process_date}")
    
    # Using a context manager for the DB session
    db_gen = get_sync_db()
    db = next(db_gen)
    
    try:
        service = InterbankService(db)
        
        # 1. Update Daily Accrual
        logger.info("Step 1: Updating Daily Accrual (Interbank)...")
        accrual_count = service.update_daily_accrual(process_date)
        logger.info(f" -> Updated accrual for {accrual_count} deals.")
        
        # 2. Process Maturities
        logger.info("Step 2: Processing Maturities (Interbank)...")
        matured_count = service.process_maturities(process_date)
        logger.info(f" -> Processed {matured_count} maturing deals.")
        
        # Commit all changes
        db.commit()
        logger.info("Batch completed successfully.")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Batch failed: {str(e)}", exc_info=True)
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run EOD Batch Process")
    parser.add_argument("--date", type=str, help="Process date (YYYY-MM-DD)", default=None)
    args = parser.parse_args()
    
    if args.date:
        try:
            target_date = datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            logger.error("Invalid date format. Use YYYY-MM-DD")
            sys.exit(1)
    else:
        target_date = date.today()
        
    # Ensure logs directory exists
    if not os.path.exists("logs"):
        os.makedirs("logs")
        
    run_batch(target_date)
