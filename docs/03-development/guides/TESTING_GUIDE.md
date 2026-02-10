# Testing Guide

**Version:** 1.0  
**Date:** February 6, 2026  
**Purpose:** Comprehensive testing strategy for Treasury Management System

---

## Table of Contents

1. [Testing Overview](#1-testing-overview)
2. [Test Environment Setup](#2-test-environment-setup)
3. [Unit Testing](#3-unit-testing)
4. [Integration Testing](#4-integration-testing)
5. [End-to-End Testing](#5-end-to-end-testing)
6. [Test Scenarios by Module](#6-test-scenarios-by-module)
7. [Test Data Management](#7-test-data-management)
8. [Performance Testing](#8-performance-testing)
9. [Regression Testing](#9-regression-testing)

---

## 1. Testing Overview

### 1.1 Testing Pyramid

```
           /\
          /  \
         / E2E \        ← 10% - Full workflow validation
        /--------\
       /          \
      / Integration \    ← 30% - API & service testing
     /--------------\
    /                \
   /   Unit Tests     \  ← 60% - Component testing
  /--------------------\
```

### 1.2 Testing Tools

| Level | Tool | Purpose |
|-------|------|---------|
| Unit | pytest | Python unit tests |
| Integration | pytest + httpx | API endpoint tests |
| E2E | Playwright | Full browser automation |
| Performance | Locust | Load testing |
| Coverage | pytest-cov | Code coverage |

### 1.3 Coverage Targets

| Module | Target |
|--------|--------|
| Services | ≥80% |
| Routers | ≥70% |
| Models | ≥90% |
| Overall | ≥75% |

---

## 2. Test Environment Setup

### 2.1 Prerequisites

```bash
# Install test dependencies
cd src/backend
pip install pytest pytest-cov pytest-asyncio httpx

# Verify installation
pytest --version
```

### 2.2 Test Database

```bash
# Start test database (isolated from development)
docker-compose -f docker-compose.test.yml up -d

# Connection string for tests
DATABASE_URL="postgresql://tms_test:tms_test@localhost:5433/treasury_test"
```

### 2.3 pytest.ini Configuration

```ini
[pytest]
testpaths = app/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --color=yes --cov=app --cov-report=html
asyncio_mode = auto
```

### 2.4 Running Tests

```bash
# Run all tests
pytest

# Run specific module
pytest app/tests/test_bond_trades.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest app/tests/test_bond_trades.py::TestBondTrades::test_create_bond_buy

# Run by marker
pytest -m "not slow"
```

---

## 3. Unit Testing

### 3.1 Test Structure

```
app/tests/
├── conftest.py              # Fixtures
├── test_bond_trades.py      # Bond trading tests
├── test_interbank.py        # Interbank tests
├── test_repo.py             # Repo tests
├── test_positions.py        # Position tests
├── test_calculations.py     # Calculation tests
└── test_validations.py      # Validation tests
```

### 3.2 Fixtures (conftest.py)

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import Base, get_db

SQLITE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(SQLITE_URL, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def sample_security():
    return {
        "security_id": "LB28DA",
        "isin": "TH0623038C09",
        "issuer_id": "1",
        "instrument_type": "Gov Bond",
        "maturity_date": "2028-12-17",
        "coupon_rate": 4.85
    }

@pytest.fixture
def sample_counterparty():
    return {
        "counterparty_id": "CP001",
        "legal_name": "Bangkok Bank PCL",
        "short_code": "BBL",
        "bank_code": "002",
        "kyc_status": "APPROVED"
    }
```

### 3.3 Calculation Tests

```python
# test_calculations.py
import pytest
from decimal import Decimal
from app.services.bond_trade_service import (
    calculate_accrued_interest,
    calculate_settlement_amount,
    calculate_yield_to_maturity
)

class TestAccruedInterest:
    def test_act_365_convention(self):
        """Test ACT/365 day count convention"""
        result = calculate_accrued_interest(
            nominal=Decimal("100000000"),
            coupon_rate=Decimal("4.85"),
            last_coupon_date="2026-01-15",
            settlement_date="2026-02-15",
            day_count="ACT/365"
        )
        # 31 days, 4.85% annual
        expected = Decimal("100000000") * Decimal("0.0485") * 31 / 365
        assert abs(result - expected) < Decimal("0.01")
    
    def test_act_360_convention(self):
        """Test ACT/360 day count convention"""
        result = calculate_accrued_interest(
            nominal=Decimal("100000000"),
            coupon_rate=Decimal("2.50"),
            last_coupon_date="2026-01-15",
            settlement_date="2026-02-15",
            day_count="ACT/360"
        )
        expected = Decimal("100000000") * Decimal("0.025") * 31 / 360
        assert abs(result - expected) < Decimal("0.01")

class TestSettlementAmount:
    def test_bond_buy_settlement(self):
        """Test settlement amount for bond purchase"""
        result = calculate_settlement_amount(
            nominal=Decimal("10000000"),
            clean_price=Decimal("102.45"),
            accrued_interest=Decimal("76547.95"),
            trade_type="BUY"
        )
        expected = Decimal("10245000") + Decimal("76547.95")
        assert result == expected
    
    def test_bond_sell_settlement(self):
        """Test settlement amount for bond sale"""
        result = calculate_settlement_amount(
            nominal=Decimal("10000000"),
            clean_price=Decimal("102.45"),
            accrued_interest=Decimal("76547.95"),
            trade_type="SELL"
        )
        expected = Decimal("10245000") + Decimal("76547.95")
        assert result == expected  # Same calculation, different cash flow
```

---

## 4. Integration Testing

### 4.1 API Endpoint Tests

```python
# test_bond_trades_api.py
class TestBondTradesAPI:
    def test_create_trade_success(self, client, sample_security, sample_counterparty):
        # Setup master data
        client.post("/api/v1/master/securities", json=sample_security)
        client.post("/api/v1/master/counterparties", json=sample_counterparty)
        
        # Create trade
        trade = {
            "security_id": "LB28DA",
            "counterparty_id": "CP001",
            "trade_type": "BUY",
            "trade_date": "2026-02-06",
            "settlement_date": "2026-02-08",
            "nominal_amount": 10000000,
            "clean_price_trade": 102.45
        }
        response = client.post("/api/v1/bond-trades", json=trade)
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "CREATED"
        assert "accrued_interest" in data
    
    def test_create_trade_invalid_t2(self, client):
        trade = {
            "trade_date": "2026-02-06",
            "settlement_date": "2026-02-07",  # T+1 (invalid)
            # ... other fields
        }
        response = client.post("/api/v1/bond-trades", json=trade)
        
        assert response.status_code == 400
        assert "T+2" in response.json()["detail"]
    
    def test_four_eyes_approval(self, client):
        # Create trade as trader
        trade_response = client.post("/api/v1/bond-trades", json={...})
        trade_id = trade_response.json()["bond_trade_id"]
        
        # Approve as different user
        approve_response = client.post(
            f"/api/v1/bond-trades/{trade_id}/approve",
            json={"approved": True}
        )
        
        assert approve_response.status_code == 200
        assert approve_response.json()["status"] == "APPROVED"
```

### 4.2 Service Integration Tests

```python
# test_service_integration.py
class TestTradeWorkflow:
    def test_complete_bond_trade_lifecycle(self, db_session):
        """Test: Create → Approve → Report → Settle"""
        from app.services.bond_trade_service import BondTradeService
        
        service = BondTradeService(db_session)
        
        # Step 1: Create
        trade = service.create_trade(trade_data, trader_id="FO001")
        assert trade.status == "CREATED"
        
        # Step 2: Approve
        trade = service.approve_trade(trade.id, approver_id="MO001")
        assert trade.status == "APPROVED"
        
        # Step 3: Report to ThaiBMA
        trade = service.report_to_thaibma(trade.id)
        assert trade.thaibma_reported == True
        
        # Step 4: Settle
        trade = service.settle_trade(trade.id, "TSD123456")
        assert trade.status == "SETTLED"
```

---

## 5. End-to-End Testing

### 5.1 Playwright Setup

```bash
# Install Playwright
pip install playwright pytest-playwright
playwright install chromium
```

### 5.2 E2E Test Example

```python
# tests/e2e/test_trade_entry.py
import pytest
from playwright.sync_api import Page

class TestBondTradeEntry:
    @pytest.fixture
    def logged_in_page(self, page: Page):
        page.goto("http://localhost:3000/login")
        page.fill("#username", "trader001")
        page.fill("#password", "password")
        page.click("button[type='submit']")
        page.wait_for_url("**/dashboard")
        return page
    
    def test_create_bond_buy(self, logged_in_page: Page):
        page = logged_in_page
        
        # Navigate to trade entry
        page.click("text=New Trade")
        page.click("text=Bond Trade")
        
        # Fill trade form
        page.select_option("#trade_type", "BUY")
        page.fill("#security_id", "LB28DA")
        page.fill("#nominal_amount", "10000000")
        page.fill("#clean_price", "102.45")
        
        # Submit
        page.click("button:has-text('Submit')")
        
        # Verify success
        page.wait_for_selector("text=Trade Created Successfully")
        assert "BT2026" in page.inner_text(".trade-id")
```

---

## 6. Test Scenarios by Module

### 6.1 Bond Trading

| ID | Scenario | Expected Result |
|----|----------|-----------------|
| BT-001 | Create bond buy | Status = CREATED, AI calculated |
| BT-002 | Create bond sell | Status = CREATED |
| BT-003 | Invalid T+2 date | Error: TRADE_001 |
| BT-004 | Unapproved counterparty | Error: TRADE_002 |
| BT-005 | Price >20% deviation | Error: PRICE_001 |
| BT-006 | Approve own trade | Error: TRADE_005 |
| BT-007 | ThaiBMA report <30min | thaibma_reported = true |
| BT-008 | Settle trade | Status = SETTLED |
| BT-009 | Cancel pending trade | Status = CANCELLED |
| BT-010 | Cancel settled trade | Error: Cannot cancel |

### 6.2 Interbank Deals

| ID | Scenario | Expected Result |
|----|----------|-----------------|
| IB-001 | Create fixed rate lending | Status = ACTIVE |
| IB-002 | Create floating rate (THOR) | Interest schedule created |
| IB-003 | Exceed placement limit | Error: LIMIT_001 |
| IB-004 | Daily accrual | Accrued interest updated |
| IB-005 | Maturity processing | Status = MATURED, limit released |

### 6.3 Repo Trades

| ID | Scenario | Expected Result |
|----|----------|-----------------|
| RP-001 | Create repo | Status = OPEN |
| RP-002 | Allocate collateral | Collateral linked |
| RP-003 | Insufficient collateral | Error: COLL_001 |
| RP-004 | Daily margin process | Margin call if needed |
| RP-005 | Agree margin call | Status = AGREED |
| RP-006 | Collateral substitution | New collateral allocated |

### 6.4 Limit Management

| ID | Scenario | Expected Result |
|----|----------|-----------------|
| LM-001 | Pre-trade limit check | Pass/Fail returned |
| LM-002 | Limit 80% warning | Warning in response |
| LM-003 | Limit 100% block | Trade rejected |
| LM-004 | Limit release on maturity | Available limit increased |

---

## 7. Test Data Management

### 7.1 Master Data Fixtures

```python
# fixtures/master_data.py
SECURITIES = [
    {"security_id": "LB28DA", "isin": "TH0623038C09", "coupon_rate": 4.85},
    {"security_id": "LB30DA", "isin": "TH0623040C05", "coupon_rate": 3.25},
    {"security_id": "TB25612A", "isin": "TH0655035B00", "coupon_rate": 0}
]

COUNTERPARTIES = [
    {"counterparty_id": "CP001", "short_code": "BBL", "kyc_status": "APPROVED"},
    {"counterparty_id": "CP002", "short_code": "KBANK", "kyc_status": "APPROVED"},
    {"counterparty_id": "CP003", "short_code": "TEST", "kyc_status": "PENDING"}
]
```

### 7.2 Test Data Import Script

```bash
# Import test data
python scripts/import_test_data.py --env test

# Reset test database
python scripts/reset_test_db.py
```

---

## 8. Performance Testing

### 8.1 Locust Configuration

```python
# locustfile.py
from locust import HttpUser, task, between

class TreasuryUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        self.client.post("/api/v1/auth/login", json={
            "username": "loadtest",
            "password": "password"
        })
    
    @task(3)
    def view_positions(self):
        self.client.get("/api/v1/positions/bonds")
    
    @task(1)
    def create_trade(self):
        self.client.post("/api/v1/bond-trades", json={...})
```

### 8.2 Performance Targets

| Endpoint | Target Response | Max Concurrent |
|----------|-----------------|----------------|
| GET /positions | <200ms | 50 |
| POST /bond-trades | <500ms | 25 |
| POST /market-data/import | <30s | 1 |

---

## 9. Regression Testing

### 9.1 Regression Suite

```bash
# Run full regression
pytest -m regression --tb=short

# Run critical path only
pytest -m critical --tb=short
```

### 9.2 CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Appendix: Test Checklist

### Pre-Release Checklist
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] E2E critical path tested
- [ ] Performance targets met
- [ ] Coverage >75%
- [ ] No critical bugs open

---

**Document End**

*For API details, see [API Reference](./API_REFERENCE.md)*  
*For setup, see [Setup Instructions](./SETUP_INSTRUCTIONS.md)*
