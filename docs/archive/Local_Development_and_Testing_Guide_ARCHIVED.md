# Local Development & Testing Guide

**Test Locally First → Validate All Functions → Then Deploy**

---

## Overview

This guide provides a complete local development environment setup for testing all Treasury Management System functions **before** any cloud deployment.

### Why Local First?

| Benefit | Description |
|---------|-------------|
| **Fast Iteration** | No deployment delays, instant code changes |
| **Zero Cost** | No cloud charges during development |
| **Full Control** | Easy debugging, database inspection |
| **Offline Work** | Develop without internet dependency |
| **Safe Testing** | No risk of affecting production data |

---

## Local Development Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    YOUR LOCAL MACHINE                        │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Frontend  │  │   Backend   │  │   Database  │         │
│  │  (Next.js)  │  │  (FastAPI)  │  │ (PostgreSQL)│         │
│  │   :3000     │  │   :8000     │  │   :5432     │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                │
│         └────────────────┴────────────────┘                │
│                          │                                  │
│                   ┌──────▼──────┐                          │
│                   │   Docker    │                          │
│                   │  (Optional) │                          │
│                   └─────────────┘                          │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Redis     │  │  Test Data  │  │   pytest    │         │
│  │   :6379     │  │   (Excel)   │  │   tests     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Local Environment Setup (Week 1, Days 1-2)

### Step 1.0: Prerequisites Checklist

> ⚠️ **Before starting**, ensure these files exist in your project:
> - `docker-compose.local.yml` ✅ (created)
> - `src/backend/requirements.txt` ✅ (created)
> - `scripts/init_db.sql` ✅ (created)
> - `.env.example` ✅ (created)

### Step 1.1: Install Prerequisites

```bash
# 1. Python 3.11.x (recommended - avoid 3.12 for now)
# Download from https://www.python.org/downloads/
python --version  # Should show 3.11.x

# 2. Node.js 18+ (LTS)
# Download from https://nodejs.org/
node --version    # Should show v18.x.x or higher
npm --version

# 3. Docker Desktop (REQUIRED for database)
# Windows: Download from https://www.docker.com/products/docker-desktop/
# Requires: Windows 10/11 Pro/Enterprise/Education with WSL2
# After install, verify:
docker --version
docker-compose --version

# 4. Git
git --version

# 5. VS Code (recommended IDE)
# Download from https://code.visualstudio.com/
```

### Windows-Specific Setup

**Docker Desktop + WSL2 (Required for Windows):**

1. Enable WSL2:
   ```powershell
   # Run PowerShell as Administrator
   wsl --install
   # Restart your computer
   ```

2. Install Docker Desktop from https://www.docker.com/products/docker-desktop/

3. In Docker Desktop Settings:
   - Enable "Use WSL 2 based engine"
   - Enable integration with your WSL distro

**PowerShell Execution Policy Fix:**

If you get "running scripts is disabled" error:

```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 1.2: Project Setup

```bash
# Navigate to project
cd "TR Dev2026"

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
venv\Scripts\activate.bat
# Mac/Linux:
source venv/bin/activate

# Install Python dependencies (use requirements.txt)
cd src/backend
pip install -r requirements.txt
cd ../..

# Copy environment file
copy .env.example .env   # Windows
# cp .env.example .env   # Mac/Linux
```

### Step 1.3: Database Setup (Local PostgreSQL)

```bash
# Option A: Using Docker (RECOMMENDED)
# Create docker-compose.yml for local development
```

Create `docker-compose.local.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: tms_postgres_local
    environment:
      POSTGRES_USER: tms_user
      POSTGRES_PASSWORD: tms_password
      POSTGRES_DB: treasury_local
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init_db.sql:/docker-entrypoint-initdb.d/init.sql
    command: postgres -c log_statement=all -c log_destination=stderr

  redis:
    image: redis:7-alpine
    container_name: tms_redis_local
    ports:
      - "6379:6379"

  adminer:
    image: adminer
    container_name: tms_adminer
    ports:
      - "8080:8080"
    depends_on:
      - postgres

volumes:
  postgres_data:
```

Start local database:

```bash
# Start services
docker-compose -f docker-compose.local.yml up -d

# Check status
docker-compose -f docker-compose.local.yml ps

# View logs
docker-compose -f docker-compose.local.yml logs -f postgres

# Access Adminer (DB GUI) at http://localhost:8080
# System: PostgreSQL
# Server: postgres
# Username: tms_user
# Password: tms_password
# Database: treasury_local
```

---

## Phase 2: Backend Development (Local)

### Step 2.1: FastAPI Project Structure

Create `src/backend/` structure:

```
src/backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── entity_master.py
│   │   ├── counterparty_master.py
│   │   ├── security_master.py
│   │   ├── portfolio_master.py
│   │   ├── interbank_deals.py
│   │   ├── repo_trades.py
│   │   ├── bond_trades.py
│   │   ├── bond_positions.py
│   │   └── limit_utilization.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── security.py
│   │   ├── counterparty.py
│   │   ├── trade.py
│   │   └── position.py
│   ├── routers/             # API endpoints
│   │   ├── __init__.py
│   │   ├── securities.py
│   │   ├── counterparties.py
│   │   ├── bond_trades.py
│   │   ├── interbank.py
│   │   ├── repo.py
│   │   └── positions.py
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── trade_service.py
│   │   ├── position_service.py
│   │   ├── settlement_service.py
│   │   └── accounting_service.py
│   ├── core/                # Core utilities
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── permissions.py
│   │   └── exceptions.py
│   └── tests/               # Unit tests
│       ├── __init__.py
│       ├── test_securities.py
│       ├── test_bond_trades.py
│       ├── test_interbank.py
│       └── test_repo.py
├── alembic/                 # Database migrations
├── scripts/
│   ├── generate_models.py   # Auto-generate from Excel
│   ├── import_test_data.py  # Import Excel test data
│   └── run_tests.sh         # Test runner
├── requirements.txt
└── pytest.ini
```

### Step 2.2: Database Configuration (Local)

Create `src/backend/app/config.py`:

```python
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://tms_user:tms_password@localhost:5432/treasury_local"
    
    # Redis (for caching)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Application
    APP_NAME: str = "Treasury Management System"
    DEBUG: bool = True  # Enable debug mode for local development
    SECRET_KEY: str = "your-secret-key-for-local-development-only"
    
    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Excel Data Path
    EXCEL_DATA_PATH: str = "../../data/source/Treasury_System_Database_V2_Internal.xlsx"
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
```

### Step 2.3: Database Connection

Create `src/backend/app/database.py`:

```python
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

# Create engine with echo=True for local debugging
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,  # Log all SQL queries
    pool_pre_ping=True,
    pool_recycle=300
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
```

### Step 2.4: Run Backend Locally

```bash
cd src/backend

# Install dependencies
pip install -r requirements.txt

# Initialize database (create tables)
python -c "from app.database import init_db; init_db()"

# Run development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# API will be available at:
# - Swagger UI: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
# - Health Check: http://localhost:8000/health
```

---

## Phase 3: Frontend Development (Local)

### Step 3.1: Next.js Setup

```bash
cd src/frontend

# Create Next.js app with TypeScript
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir

# Install dependencies
npm install @ant-design/nextjs-registry axios react-query zustand
npm install -D @types/node @types/react

# Start development server
npm run dev

# Frontend available at http://localhost:3000
```

### Step 3.2: Frontend Configuration (Local)

Create `src/frontend/.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Treasury Management System
```

---

## Phase 4: Local Testing Strategy

### 4.1 Test Data Import (Local)

Create `src/backend/scripts/import_test_data_local.py`:

```python
"""
Import all Excel test data into local PostgreSQL database
Run this after database initialization
"""

import pandas as pd
from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.models import *


def import_master_data(db: Session):
    """Import master data from Excel"""
    excel_path = "../../data/source/Treasury_System_Database_V2_Internal.xlsx"
    
    # Import Bank Codes
    df_banks = pd.read_excel(excel_path, sheet_name='BANK_CODE')
    print(f"Importing {len(df_banks)} bank codes...")
    # ... insert logic
    
    # Import Securities
    df_securities = pd.read_excel(excel_path, sheet_name='V4_Result_30 Sep 2025', 
                                   skiprows=8, nrows=20)
    print(f"Importing {len(df_securities)} securities...")
    # ... insert logic
    
    # Import Counterparties
    df_counterparties = pd.read_excel(excel_path, sheet_name='V4_Result_30 Sep 2025',
                                       skiprows=0, nrows=5)
    print(f"Importing {len(df_counterparties)} counterparties...")
    # ... insert logic
    
    db.commit()
    print("Master data imported successfully!")


def import_test_trades(db: Session):
    """Import test trade data for validation"""
    excel_path = "../../data/source/Treasury_System_Database_V2_Internal.xlsx"
    
    test_sheets = {
        'bond_buys': 'Bond buy_1_V4_Sep25',
        'bond_sells': 'Bond sell_1_V4_Oct25',
        'ib_lending': 'IB Lend_V4_Sep25',
        'ib_borrowing': 'IB Borrow_V4_Sep25',
        'repos': 'Repo_1_V4_Sep25',
        'reverse_repos': 'RRP_1_V4_Sep25'
    }
    
    for trade_type, sheet_name in test_sheets.items():
        try:
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            print(f"Loaded {len(df)} rows from {sheet_name}")
            # ... insert logic based on trade type
        except Exception as e:
            print(f"Error loading {sheet_name}: {e}")
    
    db.commit()
    print("Test trades imported successfully!")


if __name__ == "__main__":
    print("Initializing local database...")
    init_db()
    
    db = SessionLocal()
    try:
        import_master_data(db)
        import_test_trades(db)
        print("\n✅ All test data imported successfully!")
        print("You can now start testing the APIs.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
    finally:
        db.close()
```

Run import:

```bash
cd src/backend
python scripts/import_test_data_local.py
```

### 4.2 Unit Testing (Local)

Create `src/backend/pytest.ini`:

```ini
[pytest]
testpaths = app/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --color=yes
```

Example test: `src/backend/app/tests/test_bond_trades.py`:

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

# Use in-memory SQLite for fast unit tests
SQLITE_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLITE_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup_db():
    """Create fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestBondTrades:
    """Test bond trade functionality locally"""
    
    def test_create_bond_buy(self):
        """Test creating a bond buy trade"""
        # First create required master data
        security_response = client.post("/api/v1/securities", json={
            "security_id": "LB28DA",
            "isin": "TH0623038C09",
            "issuer_id": "1",
            "instrument_type": "Gov Bond",
            "maturity_date": "2028-12-17",
            "coupon_rate": 4.85
        })
        assert security_response.status_code == 201
        
        counterparty_response = client.post("/api/v1/counterparties", json={
            "counterparty_id": "101",
            "legal_name": "Bangkok Bank PCL",
            "short_code": "BBL",
            "bank_code": "002"
        })
        assert counterparty_response.status_code == 201
        
        # Create bond buy trade
        trade_data = {
            "TradeID": "T20250001",
            "SecurityID": "LB28DA",
            "counterparty_id": "101",
            "TradeType": "BUY",
            "TradeDate": "2025-09-01",
            "SettlementDate": "2025-09-03",  # T+2
            "NominalAmount": 10000000,
            "CleanPrice": 102.50,
            "SettlementAmount": 10284520.55  # Calculated
        }
        
        response = client.post("/api/v1/bond-trades", json=trade_data)
        assert response.status_code == 201
        
        result = response.json()
        assert result["TradeID"] == "T20250001"
        assert result["Status"] == "CREATED"
    
    def test_trade_validation_t2_settlement(self):
        """Test T+2 settlement date validation"""
        trade_data = {
            "TradeID": "T20250002",
            "SecurityID": "LB28DA",
            "counterparty_id": "101",
            "TradeType": "BUY",
            "TradeDate": "2025-09-01",
            "SettlementDate": "2025-09-02",  # Wrong: should be 2025-09-03
            "NominalAmount": 10000000,
            "CleanPrice": 102.50
        }
        
        response = client.post("/api/v1/bond-trades", json=trade_data)
        assert response.status_code == 400
        assert "T+2" in response.json()["detail"]
    
    def test_four_eyes_approval(self):
        """Test trade approval workflow"""
        # Create trade
        trade_data = {
            "TradeID": "T20250003",
            "SecurityID": "LB28DA",
            "counterparty_id": "101",
            "TradeType": "BUY",
            "TradeDate": "2025-09-01",
            "SettlementDate": "2025-09-03",
            "NominalAmount": 10000000,
            "CleanPrice": 102.50
        }
        
        # Trader creates trade
        response = client.post("/api/v1/bond-trades", json=trade_data)
        assert response.status_code == 201
        assert response.json()["Status"] == "CREATED"
        
        # Supervisor approves
        approve_response = client.post(
            f"/api/v1/bond-trades/{trade_data['TradeID']}/approve",
            json={"approved": True, "approved_by": "SUPERVISOR001"}
        )
        assert approve_response.status_code == 200
        assert approve_response.json()["Status"] == "APPROVED"


class TestInterbankDeals:
    """Test interbank lending/borrowing locally"""
    
    def test_create_interbank_lending(self):
        """Test IB lending deal"""
        deal_data = {
            "DealID": "IBL2025001",
            "counterparty_id": "101",
            "deal_type": "LEND",
            "principal_amount": 50000000,
            "interest_rate": 2.50,
            "rate_type": "FIXED",
            "value_date": "2025-09-01",
            "maturity_date": "2025-09-08"
        }
        
        response = client.post("/api/v1/interbank/deals", json=deal_data)
        assert response.status_code == 201
        assert response.json()["status"] == "ACTIVE"
    
    def test_interbank_floating_rate(self):
        """Test floating rate IB deal with THOR"""
        deal_data = {
            "DealID": "IBL2025002",
            "counterparty_id": "102",
            "deal_type": "LEND",
            "principal_amount": 100000000,
            "rate_type": "FLOATING",
            "benchmark_rate": "THOR",
            "spread_bp": 25,
            "value_date": "2025-09-01",
            "maturity_date": "2025-12-01"
        }
        
        response = client.post("/api/v1/interbank/deals", json=deal_data)
        assert response.status_code == 201
        
        # Check interest schedule was created
        schedule_response = client.get(
            f"/api/v1/interbank/deals/{deal_data['DealID']}/schedule"
        )
        assert schedule_response.status_code == 200
        assert len(schedule_response.json()) > 0


class TestRepoTrades:
    """Test repo and reverse repo locally"""
    
    def test_create_repo(self):
        """Test repo (cash borrower) with collateral"""
        # Setup: Create security for collateral
        client.post("/api/v1/securities", json={
            "security_id": "BOT25NA",
            "isin": "TH0655035B00",
            "issuer_id": "2",
            "instrument_type": "BOT Bond"
        })
        
        # Create repo trade
        repo_data = {
            "RepoTradeID": "REPO2025001",
            "counterparty_id": "101",
            "trade_type": "REPO",
            "nominal_amount": 100000000,  # Cash borrowed
            "repo_rate": 2.25,
            "value_date": "2025-09-01",
            "maturity_date": "2025-09-02",
            "haircut_percent": 1.0
        }
        
        response = client.post("/api/v1/repos", json=repo_data)
        assert response.status_code == 201
        
        # Allocate collateral
        collateral_data = {
            "SecurityID": "BOT25NA",
            "collateral_quantity": 101000000,  # Higher than cash due to haircut
            "market_value": 101000000
        }
        
        collateral_response = client.post(
            f"/api/v1/repos/{repo_data['RepoTradeID']}/collateral",
            json=collateral_data
        )
        assert collateral_response.status_code == 201
        
        # Verify margin value after haircut
        collateral = collateral_response.json()
        expected_margin = 101000000 * (1 - 0.01)  # 1% haircut
        assert abs(collateral["margin_value"] - expected_margin) < 0.01
    
    def test_repo_margin_call(self):
        """Test margin call generation when collateral value drops"""
        # Create repo with collateral
        # ... setup code ...
        
        # Simulate daily margin process
        margin_response = client.post(
            "/api/v1/repos/REPO2025001/margin-process",
            json={"valuation_date": "2025-09-02"}
        )
        
        # If collateral value dropped, should generate margin call
        result = margin_response.json()
        if result["NetExposure"] > 500000:  # THB 500,000 threshold
            assert result["MarginCallAmount"] > 0


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### 4.3 Integration Testing (Local)

Create `src/backend/scripts/run_local_tests.sh`:

```bash
#!/bin/bash

echo "=========================================="
echo "Running Local Integration Tests"
echo "=========================================="

# Set environment to local
export DATABASE_URL="postgresql://tms_user:tms_password@localhost:5432/treasury_local"
export DEBUG="true"

cd src/backend

echo ""
echo "1. Running unit tests..."
pytest app/tests/ -v --tb=short

echo ""
echo "2. Running integration tests with test data..."
python scripts/import_test_data_local.py
pytest app/tests/integration/ -v --tb=short

echo ""
echo "3. Validating against Excel expected results..."
python scripts/validate_excel_results.py

echo ""
echo "=========================================="
echo "Local testing complete!"
echo "=========================================="
```

### 4.4 End-to-End Testing (Local)

Create `tests/e2e/` for full workflow testing:

```python
"""
E2E Test: Complete trade lifecycle
Run this after backend and frontend are running locally
"""

import requests
import time

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"


def test_complete_bond_trade_lifecycle():
    """
    Test complete bond trade workflow:
    1. Create trade
    2. Approve trade
    3. Confirm settlement
    4. Verify position
    5. Check ThaiBMA reporting
    """
    print("\n=== E2E Test: Bond Trade Lifecycle ===\n")
    
    # Step 1: Create trade
    print("1. Creating bond buy trade...")
    trade = {
        "TradeID": "E2E001",
        "SecurityID": "LB28DA",
        "counterparty_id": "101",
        "TradeType": "BUY",
        "TradeDate": "2025-09-01",
        "SettlementDate": "2025-09-03",
        "NominalAmount": 10000000,
        "CleanPrice": 102.50
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/bond-trades", json=trade)
    assert response.status_code == 201
    print(f"   ✅ Trade created: {response.json()['TradeID']}")
    
    # Step 2: Approve trade
    print("2. Approving trade...")
    approve = requests.post(
        f"{BASE_URL}/api/v1/bond-trades/{trade['TradeID']}/approve",
        json={"approved": True, "approved_by": "SUPERVISOR001"}
    )
    assert approve.status_code == 200
    print(f"   ✅ Trade approved")
    
    # Step 3: Confirm settlement
    print("3. Confirming settlement...")
    confirm = requests.post(
        f"{BASE_URL}/api/v1/bond-trades/{trade['TradeID']}/confirm-settlement"
    )
    assert confirm.status_code == 200
    print(f"   ✅ Trade settled")
    
    # Step 4: Verify position
    print("4. Verifying position...")
    time.sleep(1)  # Wait for position calculation
    position = requests.get(
        f"{BASE_URL}/api/v1/positions",
        params={"SecurityID": trade["SecurityID"]}
    )
    assert position.status_code == 200
    positions = position.json()
    assert len(positions) > 0
    print(f"   ✅ Position created: {positions[0]['NominalAmount']} THB")
    
    # Step 5: Check ThaiBMA reporting
    print("5. Checking ThaiBMA reporting status...")
    trade_detail = requests.get(
        f"{BASE_URL}/api/v1/bond-trades/{trade['TradeID']}"
    )
    assert trade_detail.json()["ThaiBMA_Reported"] == True
    print(f"   ✅ Reported to ThaiBMA")
    
    print("\n✅ E2E Test PASSED!")


def test_interbank_deal_lifecycle():
    """Test IB lending lifecycle"""
    print("\n=== E2E Test: Interbank Lending ===\n")
    
    # Create IB lending deal
    deal = {
        "DealID": "E2E_IB001",
        "counterparty_id": "101",
        "deal_type": "LEND",
        "principal_amount": 50000000,
        "interest_rate": 2.50,
        "rate_type": "FIXED",
        "value_date": "2025-09-01",
        "maturity_date": "2025-09-08"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/interbank/deals", json=deal)
    assert response.status_code == 201
    print(f"✅ IB Lending deal created: {deal['DealID']}")
    
    # Check interest accrual after 1 day
    time.sleep(0.5)
    accrual = requests.get(
        f"{BASE_URL}/api/v1/interbank/deals/{deal['DealID']}/accrual"
    )
    expected_daily = 50000000 * 0.025 / 365
    actual = accrual.json()["accrued_interest"]
    assert abs(actual - expected_daily) < 1.0
    print(f"✅ Interest accrual correct: {actual:.2f} THB")


def test_repo_lifecycle():
    """Test repo lifecycle with margin"""
    print("\n=== E2E Test: Repo with Margin ===\n")
    
    # Create repo
    repo = {
        "RepoTradeID": "E2E_REPO001",
        "counterparty_id": "101",
        "trade_type": "REPO",
        "nominal_amount": 100000000,
        "repo_rate": 2.25,
        "value_date": "2025-09-01",
        "maturity_date": "2025-09-02",
        "haircut_percent": 1.0
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/repos", json=repo)
    assert response.status_code == 201
    print(f"✅ Repo created: {repo['RepoTradeID']}")
    
    # Allocate collateral
    collateral = {
        "SecurityID": "BOT25NA",
        "collateral_quantity": 101000000,
        "market_value": 101000000
    }
    
    coll_response = requests.post(
        f"{BASE_URL}/api/v1/repos/{repo['RepoTradeID']}/collateral",
        json=collateral
    )
    assert coll_response.status_code == 201
    print(f"✅ Collateral allocated")
    
    # Process margin
    margin = requests.post(
        f"{BASE_URL}/api/v1/repos/{repo['RepoTradeID']}/margin-process"
    )
    assert margin.status_code == 200
    print(f"✅ Margin processed: {margin.json()}")


if __name__ == "__main__":
    test_complete_bond_trade_lifecycle()
    test_interbank_deal_lifecycle()
    test_repo_lifecycle()
    print("\n" + "="*50)
    print("ALL E2E TESTS PASSED!")
    print("="*50)
```

---

## Phase 5: Local Validation Checklist

Before considering deployment, verify all functions work locally:

### 5.1 Functional Checklist

| Feature | Local Test Command | Expected Result |
|---------|-------------------|-----------------|
| **Database** | `docker-compose -f docker-compose.local.yml ps` | postgres: Up |
| **Backend** | `curl http://localhost:8000/health` | `{"status": "ok"}` |
| **Frontend** | Open http://localhost:3000 | UI loads |
| **Master Data API** | `curl http://localhost:8000/api/v1/securities` | Returns securities |
| **Bond Trade** | Run `test_bond_trades.py` | All tests pass |
| **IB Lending** | Run `test_interbank.py` | All tests pass |
| **Repo/RRP** | Run `test_repo.py` | All tests pass |
| **Position Calc** | `curl /api/v1/positions` | Correct positions |
| **ThaiBMA Export** | `curl /api/v1/reports/thai-bma` | Returns report |
| **Excel Validation** | Run `validate_excel_results.py` | 100% match |

### 5.2 Performance Checklist (Local)

| Metric | Target | Test Command |
|--------|--------|--------------|
| API Response | < 500ms | `ab -n 1000 -c 10 http://localhost:8000/api/v1/securities` |
| Trade Creation | < 2s | Time `POST /api/v1/bond-trades` |
| Position Query | < 1s | Time `GET /api/v1/positions` |
| DB Query | < 100ms | Enable SQL logging, check query times |

### 5.3 Data Integrity Checklist

| Check | Method |
|-------|--------|
| Master data imported | Query DB: `SELECT COUNT(*) FROM securities` > 0 |
| Test trades imported | Query DB: `SELECT COUNT(*) FROM bond_trades` > 0 |
| Positions calculated | Query DB: `SELECT COUNT(*) FROM bond_positions` > 0 |
| Excel validation | Run: `python scripts/validate_excel_results.py` |
| Limit checking works | Try trade exceeding limit → should block |
| Four-eyes works | Approve trade → status changes |

---

## Phase 6: Local Development Commands

### Daily Development Workflow

```bash
# 1. Start local infrastructure
docker-compose -f docker-compose.local.yml up -d

# 2. Start backend (Terminal 1)
cd src/backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload --port 8000

# 3. Start frontend (Terminal 2)
cd src/frontend
npm run dev

# 4. Run tests (Terminal 3)
cd src/backend
pytest app/tests/ -v -f  # -f for fail fast, re-run on changes

# 5. Access services
open http://localhost:3000    # Frontend
open http://localhost:8000/docs  # API docs
open http://localhost:8080    # Adminer (DB GUI)
```

### Database Management (Local)

```bash
# Reset database
docker-compose -f docker-compose.local.yml down -v
docker-compose -f docker-compose.local.yml up -d

# Backup local database
docker exec tms_postgres_local pg_dump -U tms_user treasury_local > backup.sql

# Restore local database
docker exec -i tms_postgres_local psql -U tms_user treasury_local < backup.sql

# View database logs
docker-compose -f docker-compose.local.yml logs -f postgres
```

---

## Troubleshooting (Local)

### Common Issues

| Issue | Solution |
|-------|----------|
| Port 5432 in use | `docker-compose` uses port 5432, stop local PostgreSQL first |
| Import errors | Ensure `venv` is activated, run `pip install -r requirements.txt` |
| CORS errors | Backend must allow `http://localhost:3000` in CORS settings |
| Database connection refused | Check Docker: `docker-compose ps`, ensure postgres is healthy |
| Test data import fails | Check Excel file path, ensure file exists at `data/source/` |
| Slow queries | Enable EXPLAIN ANALYZE, check missing indexes |

---

## Next Steps After Local Validation

Once **all** checklist items pass locally:

1. ✅ All unit tests pass
2. ✅ All integration tests pass
3. ✅ Excel validation shows 100% match
4. ✅ E2E tests complete successfully
5. ✅ Performance targets met
6. ✅ No console errors

**Then proceed to:**
- [ ] Docker containerization (`docker-compose.yml` for deployment)
- [ ] CI/CD pipeline setup (GitHub Actions)
- [ ] Staging environment deployment
- [ ] Production deployment

---

*Test locally first, deploy with confidence!*
