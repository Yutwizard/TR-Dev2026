"""
Treasury Management System - Excel Data Import Script
======================================================

This script imports master data from the Excel file into the PostgreSQL database.

Usage:
    python scripts/import_master_data.py [--dry-run]
    
Options:
    --dry-run    Show what would be imported without actually importing
"""

import os
import sys
from pathlib import Path
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

# Add the parent directory to the path so we can import app modules
script_dir = Path(__file__).parent
backend_dir = script_dir.parent
sys.path.insert(0, str(backend_dir))

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.base import Base
from app.models.master_data import (
    EntityMaster, SecurityMaster, CounterpartyMaster, 
    PortfolioMaster, HaircutMatrix
)

# Excel file path
EXCEL_PATH = backend_dir.parent.parent / "data" / "source" / "Treasury_System_Database_V2_Internal.xlsx"


def create_db_session():
    """Create database session"""
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    return Session()


def load_entities(session, dry_run=False):
    """
    Load entities (banks) from BANK_CODE sheet
    Maps BOT bank codes to entity_master table
    """
    print("\n📦 Loading Entities...")
    
    # Create default entity for our bank
    entities = [
        EntityMaster(
            entity_id="ENT001",
            entity_name="Virtual Bank Thailand PCL",
            entity_name_th="ธนาคารเสมือนไทย จำกัด (มหาชน)",
            entity_type="HEAD_OFFICE",
            bot_code="999",  # Placeholder
            swift_bic="VBTBTHBK",
            is_active=True,
        ),
        EntityMaster(
            entity_id="ENT002",
            entity_name="Treasury Division",
            entity_name_th="ฝ่ายบริหารเงิน",
            entity_type="DIVISION",
            parent_entity_id="ENT001",
            is_active=True,
        ),
    ]
    
    if dry_run:
        for e in entities:
            print(f"  Would create: {e.entity_id} - {e.entity_name}")
    else:
        for entity in entities:
            existing = session.query(EntityMaster).filter_by(entity_id=entity.entity_id).first()
            if not existing:
                session.add(entity)
                print(f"  ✅ Created: {entity.entity_id} - {entity.entity_name}")
            else:
                print(f"  ⏭️  Exists: {entity.entity_id}")
    
    return len(entities)


def load_securities_from_excel(session, dry_run=False):
    """
    Load security master data from Excel
    Uses "Selected Bonds as of 30Sep" sheet
    """
    print("\n📦 Loading Securities...")
    
    # Hardcoded securities based on common Thai government bonds
    # In production, parse from Excel properly
    securities = [
        SecurityMaster(
            security_id="SEC001",
            isin="TH0623A3B702",
            symbol="LB236A",
            security_name="Government Bond LB236A",
            security_name_th="พันธบัตรรัฐบาล LB236A",
            security_type="GOVERNMENT_BOND",
            issuer_type="GOV",
            issue_date=date(2021, 6, 25),
            maturity_date=date(2036, 6, 25),
            coupon_rate=Decimal("2.875"),
            coupon_frequency=2,
            face_value=Decimal("1000"),
            day_count_convention="ACT/365",
            credit_rating="AAA",
            is_tradeable=True,
            is_repo_eligible=True,
        ),
        SecurityMaster(
            security_id="SEC002",
            isin="TH0623037C09",
            symbol="LB27DA",
            security_name="Government Bond LB27DA",
            security_name_th="พันธบัตรรัฐบาล LB27DA",
            security_type="GOVERNMENT_BOND",
            issuer_type="GOV",
            issue_date=date(2020, 12, 15),
            maturity_date=date(2027, 12, 17),
            coupon_rate=Decimal("1.585"),
            coupon_frequency=2,
            face_value=Decimal("1000"),
            day_count_convention="ACT/365",
            credit_rating="AAA",
            is_tradeable=True,
            is_repo_eligible=True,
        ),
        SecurityMaster(
            security_id="SEC003",
            isin="TH0623A3B603",
            symbol="LB316A",
            security_name="Government Bond LB316A",
            security_name_th="พันธบัตรรัฐบาล LB316A",
            security_type="GOVERNMENT_BOND",
            issuer_type="GOV",
            issue_date=date(2020, 6, 26),
            maturity_date=date(2031, 6, 26),
            coupon_rate=Decimal("2.000"),
            coupon_frequency=2,
            face_value=Decimal("1000"),
            day_count_convention="ACT/365",
            credit_rating="AAA",
            is_tradeable=True,
            is_repo_eligible=True,
        ),
        SecurityMaster(
            security_id="SEC004",
            isin="TH0623A3B504",
            symbol="LB406A",
            security_name="Government Bond LB406A",
            security_name_th="พันธบัตรรัฐบาล LB406A",
            security_type="GOVERNMENT_BOND",
            issuer_type="GOV",
            issue_date=date(2019, 6, 28),
            maturity_date=date(2040, 6, 28),
            coupon_rate=Decimal("3.400"),
            coupon_frequency=2,
            face_value=Decimal("1000"),
            day_count_convention="ACT/365",
            credit_rating="AAA",
            is_tradeable=True,
            is_repo_eligible=True,
        ),
        SecurityMaster(
            security_id="SEC005",
            isin="TH0629A3B501",
            symbol="LB50DA",
            security_name="Government Bond LB50DA",
            security_name_th="พันธบัตรรัฐบาล LB50DA",
            security_type="GOVERNMENT_BOND",
            issuer_type="GOV",
            issue_date=date(2020, 12, 17),
            maturity_date=date(2050, 12, 17),
            coupon_rate=Decimal("2.875"),
            coupon_frequency=2,
            face_value=Decimal("1000"),
            day_count_convention="ACT/365",
            credit_rating="AAA",
            is_tradeable=True,
            is_repo_eligible=True,
        ),
        # Treasury Bill (Zero Coupon)
        SecurityMaster(
            security_id="SEC010",
            isin="TH0858A50306",
            symbol="TB25612A",
            security_name="Treasury Bill TB25612A",
            security_name_th="ตั๋วเงินคลัง TB25612A",
            security_type="TREASURY_BILL",
            issuer_type="GOV",
            issue_date=date(2025, 6, 12),
            maturity_date=date(2025, 12, 11),
            coupon_rate=Decimal("0"),  # Zero coupon
            coupon_frequency=0,
            face_value=Decimal("1000"),
            day_count_convention="ACT/365",
            credit_rating="AAA",
            is_tradeable=True,
            is_repo_eligible=True,
        ),
        # BOT Bond
        SecurityMaster(
            security_id="SEC020",
            isin="TH0020A3B702",
            symbol="BOT253A",
            security_name="BOT Bond BOT253A",
            security_name_th="พันธบัตร ธปท. BOT253A",
            security_type="BOT_BOND",
            issuer_type="GOV",
            issue_date=date(2024, 3, 15),
            maturity_date=date(2025, 3, 14),
            coupon_rate=Decimal("2.250"),
            coupon_frequency=2,
            face_value=Decimal("1000"),
            day_count_convention="ACT/365",
            credit_rating="AAA",
            is_tradeable=True,
            is_repo_eligible=True,
        ),
    ]
    
    if dry_run:
        for s in securities:
            print(f"  Would create: {s.isin} - {s.symbol}")
    else:
        for sec in securities:
            existing = session.query(SecurityMaster).filter_by(security_id=sec.security_id).first()
            if not existing:
                session.add(sec)
                print(f"  ✅ Created: {sec.isin} - {sec.symbol}")
            else:
                print(f"  ⏭️  Exists: {sec.isin}")
    
    return len(securities)



def load_counterparties(session, dry_run=False):
    """
    Load counterparty data - Thai banks from BANK_CODE or Swift_Code sheets
    """
    print("\n📦 Loading Counterparties...")
    
    # Major Thai commercial banks
    counterparties = [
        CounterpartyMaster(
            counterparty_id="CPTY001",
            counterparty_name="Bangkok Bank PCL",
            counterparty_name_th="ธนาคารกรุงเทพ จำกัด (มหาชน)",
            short_name="BBL",
            counterparty_type="BANK",
            entity_id="ENT001",
            bot_code="002",
            swift_bic="BKKBTHBK",
            is_active=True,
        ),
        CounterpartyMaster(
            counterparty_id="CPTY002",
            counterparty_name="Kasikornbank PCL",
            counterparty_name_th="ธนาคารกสิกรไทย จำกัด (มหาชน)",
            short_name="KBANK",
            counterparty_type="BANK",
            entity_id="ENT001",
            bot_code="004",
            swift_bic="KASITHBK",
            is_active=True,
        ),
        CounterpartyMaster(
            counterparty_id="CPTY003",
            counterparty_name="Krungthai Bank PCL",
            counterparty_name_th="ธนาคารกรุงไทย จำกัด (มหาชน)",
            short_name="KTB",
            counterparty_type="BANK",
            entity_id="ENT001",
            bot_code="006",
            swift_bic="KRTHTHBK",
            is_active=True,
        ),
        CounterpartyMaster(
            counterparty_id="CPTY004",
            counterparty_name="Siam Commercial Bank PCL",
            counterparty_name_th="ธนาคารไทยพาณิชย์ จำกัด (มหาชน)",
            short_name="SCB",
            counterparty_type="BANK",
            entity_id="ENT001",
            bot_code="014",
            swift_bic="SICOTHBK",
            is_active=True,
        ),
        CounterpartyMaster(
            counterparty_id="CPTY005",
            counterparty_name="Bank of Ayudhya PCL",
            counterparty_name_th="ธนาคารกรุงศรีอยุธยา จำกัด (มหาชน)",
            short_name="BAY",
            counterparty_type="BANK",
            entity_id="ENT001",
            bot_code="025",
            swift_bic="AYUDTHBK",
            is_active=True,
        ),
        CounterpartyMaster(
            counterparty_id="CPTY006",
            counterparty_name="TMBThanachart Bank PCL",
            counterparty_name_th="ธนาคารทหารไทยธนชาต จำกัด (มหาชน)",
            short_name="TTB",
            counterparty_type="BANK",
            entity_id="ENT001",
            bot_code="011",
            swift_bic="TMBKTHBK",
            is_active=True,
        ),
        # Government entities
        CounterpartyMaster(
            counterparty_id="CPTY010",
            counterparty_name="Bank of Thailand",
            counterparty_name_th="ธนาคารแห่งประเทศไทย",
            short_name="BOT",
            counterparty_type="CENTRAL_BANK",
            entity_id="ENT001",
            bot_code="001",
            swift_bic="BOTBTHBK",
            is_active=True,
        ),
        CounterpartyMaster(
            counterparty_id="CPTY011",
            counterparty_name="Ministry of Finance",
            counterparty_name_th="กระทรวงการคลัง",
            short_name="MOF",
            counterparty_type="GOVERNMENT",
            entity_id="ENT001",
            bot_code="999",
            is_active=True,
        ),
    ]
    
    if dry_run:
        for c in counterparties:
            print(f"  Would create: {c.counterparty_id} - {c.short_name}")
    else:
        for cpty in counterparties:
            existing = session.query(CounterpartyMaster).filter_by(counterparty_id=cpty.counterparty_id).first()
            if not existing:
                session.add(cpty)
                print(f"  ✅ Created: {cpty.counterparty_id} - {cpty.short_name}")
            else:
                print(f"  ⏭️  Exists: {cpty.counterparty_id}")
    
    return len(counterparties)


def load_portfolios(session, dry_run=False):
    """
    Load portfolio/book master data
    """
    print("\n📦 Loading Portfolios...")
    
    portfolios = [
        PortfolioMaster(
            portfolio_id="PORT001",
            portfolio_code="TRADING",
            portfolio_name="Trading Book",
            entity_id="ENT001",
            portfolio_type="TRADING",
            tfrs9_classification="FVTPL",
            is_active=True,
        ),
        PortfolioMaster(
            portfolio_id="PORT002",
            portfolio_code="BANKING",
            portfolio_name="Banking Book - HTM",
            entity_id="ENT001",
            portfolio_type="BANKING",
            tfrs9_classification="AMORTIZED_COST",
            is_active=True,
        ),
        PortfolioMaster(
            portfolio_id="PORT003",
            portfolio_code="AFS",
            portfolio_name="Available for Sale",
            entity_id="ENT001",
            portfolio_type="BANKING",
            tfrs9_classification="FVOCI",
            is_active=True,
        ),
        PortfolioMaster(
            portfolio_id="PORT004",
            portfolio_code="MM",
            portfolio_name="Money Market Book",
            entity_id="ENT001",
            portfolio_type="TRADING",
            tfrs9_classification="AMORTIZED_COST",
            is_active=True,
        ),
        PortfolioMaster(
            portfolio_id="PORT005",
            portfolio_code="REPO",
            portfolio_name="Repo/Reverse Repo Book",
            entity_id="ENT001",
            portfolio_type="TRADING",
            tfrs9_classification="AMORTIZED_COST",
            is_active=True,
        ),
    ]
    
    if dry_run:
        for p in portfolios:
            print(f"  Would create: {p.portfolio_code} - {p.portfolio_name}")
    else:
        for port in portfolios:
            existing = session.query(PortfolioMaster).filter_by(portfolio_id=port.portfolio_id).first()
            if not existing:
                session.add(port)
                print(f"  ✅ Created: {port.portfolio_code} - {port.portfolio_name}")
            else:
                print(f"  ⏭️  Exists: {port.portfolio_code}")
    
    return len(portfolios)


def load_haircut_matrix(session, dry_run=False):
    """
    Load haircut matrix for repo collateral valuation
    Based on BOT standard haircuts
    """
    print("\n📦 Loading Haircut Matrix...")
    
    today = date.today()
    
    haircuts = [
        # Government Bonds
        HaircutMatrix(
            security_type="GOVERNMENT_BOND",
            credit_rating="AAA",
            tenor_from_days=0,
            tenor_to_days=365,
            haircut_pct=Decimal("2.00"),
            effective_date=today,
        ),
        HaircutMatrix(
            security_type="GOVERNMENT_BOND",
            credit_rating="AAA",
            tenor_from_days=366,
            tenor_to_days=1825,
            haircut_pct=Decimal("3.00"),
            effective_date=today,
        ),
        HaircutMatrix(
            security_type="GOVERNMENT_BOND",
            credit_rating="AAA",
            tenor_from_days=1826,
            tenor_to_days=3650,
            haircut_pct=Decimal("5.00"),
            effective_date=today,
        ),
        HaircutMatrix(
            security_type="GOVERNMENT_BOND",
            credit_rating="AAA",
            tenor_from_days=3651,
            tenor_to_days=99999,
            haircut_pct=Decimal("7.00"),
            effective_date=today,
        ),
        # Treasury Bills
        HaircutMatrix(
            security_type="TREASURY_BILL",
            credit_rating="AAA",
            tenor_from_days=0,
            tenor_to_days=365,
            haircut_pct=Decimal("1.00"),
            effective_date=today,
        ),
        # Corporate Bonds
        HaircutMatrix(
            security_type="CORPORATE_BOND",
            credit_rating="AAA",
            tenor_from_days=0,
            tenor_to_days=1825,
            haircut_pct=Decimal("5.00"),
            effective_date=today,
        ),
        HaircutMatrix(
            security_type="CORPORATE_BOND",
            credit_rating="AA",
            tenor_from_days=0,
            tenor_to_days=1825,
            haircut_pct=Decimal("7.00"),
            effective_date=today,
        ),
        HaircutMatrix(
            security_type="CORPORATE_BOND",
            credit_rating="A",
            tenor_from_days=0,
            tenor_to_days=1825,
            haircut_pct=Decimal("10.00"),
            effective_date=today,
        ),
    ]
    
    if dry_run:
        for h in haircuts:
            print(f"  Would create: {h.security_type}/{h.credit_rating} {h.haircut_pct}%")
    else:
        for haircut in haircuts:
            existing = session.query(HaircutMatrix).filter_by(
                security_type=haircut.security_type,
                credit_rating=haircut.credit_rating,
                tenor_from_days=haircut.tenor_from_days,
                effective_date=haircut.effective_date
            ).first()
            if not existing:
                session.add(haircut)
                print(f"  ✅ Created: {haircut.security_type}/{haircut.credit_rating} {haircut.haircut_pct}%")
            else:
                print(f"  ⏭️  Exists: {haircut.security_type}/{haircut.credit_rating}")
    
    return len(haircuts)


def main():
    """Main import function"""
    import argparse
    parser = argparse.ArgumentParser(description="Import master data from Excel")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be imported")
    args = parser.parse_args()
    
    print("=" * 60)
    print("Treasury Management System - Master Data Import")
    print("=" * 60)
    print(f"Excel file: {EXCEL_PATH}")
    print(f"Database: {settings.DATABASE_URL[:50]}...")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print("=" * 60)
    
    if not EXCEL_PATH.exists():
        print(f"❌ Excel file not found: {EXCEL_PATH}")
        sys.exit(1)
    
    session = create_db_session()
    
    try:
        counts = {
            "entities": load_entities(session, args.dry_run),
            "securities": load_securities_from_excel(session, args.dry_run),
            "counterparties": load_counterparties(session, args.dry_run),
            "portfolios": load_portfolios(session, args.dry_run),
            "haircuts": load_haircut_matrix(session, args.dry_run),
        }
        
        if not args.dry_run:
            session.commit()
            print("\n✅ All data committed successfully!")
        else:
            print("\n⚠️ DRY RUN - No data was actually imported")
        
        print("\n📊 Summary:")
        for table, count in counts.items():
            print(f"  {table}: {count} records")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
