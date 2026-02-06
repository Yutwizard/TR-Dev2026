# Development Guide

**Version:** 1.0  
**Date:** February 5, 2026

---

## Table of Contents

1. [Technology Stack](#1-technology-stack)
2. [Project Structure](#2-project-structure)
3. [Database Schema](#3-database-schema)
4. [Development Phases](#4-development-phases)
5. [API Specifications](#5-api-specifications)
6. [Testing Strategy](#6-testing-strategy)

---

## 1. Technology Stack

| Layer | Technology | Version |
|-------|------------|---------|
| Backend Framework | FastAPI | 0.100+ |
| Database | PostgreSQL | 14+ |
| ORM | SQLAlchemy | 2.0+ |
| Migration | Alembic | Latest |
| Frontend | React | 18+ |
| Container | Docker | 20+ |

---

## 2. Project Structure

```
src/backend/
├── app/
│   ├── models/              # SQLAlchemy models
│   ├── routers/             # API endpoints
│   ├── services/            # Business logic
│   ├── schemas/             # Pydantic schemas
│   └── core/                # Config, auth, utils
├── alembic/                 # Database migrations
├── scripts/                 # Utility scripts
└── tests/                   # Test suite
```

---

## 3. Database Schema

### 3.1 Core Tables

```sql
-- bond_trades (Aligned with Database Design)
CREATE TABLE bond_trades (
    bond_trade_id VARCHAR(40) PRIMARY KEY,
    portfolio_id VARCHAR(40) REFERENCES portfolio_master(portfolio_id),
    security_id VARCHAR(10) REFERENCES security_master(security_id),
    counterparty_id VARCHAR(40) REFERENCES counterparty_master(counterparty_id),
    trade_type VARCHAR(10),  -- 'Buy' or 'Sell'
    trade_date DATE,
    settlement_date DATE,  -- T+2
    nominal_amount DECIMAL(20,2),
    clean_price_trade DECIMAL(18,6),
    yield_to_maturity DECIMAL(10,6),
    settlement_status VARCHAR(20),
    trader_id VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- limit_utilization (Immutable audit log)
CREATE TABLE limit_utilization (
    limit_id VARCHAR(40) PRIMARY KEY,
    counterparty_id VARCHAR(40) REFERENCES counterparty_master(counterparty_id),
    entity_id VARCHAR(40) REFERENCES entity_master(entity_id),
    limit_type VARCHAR(20),  -- 'PLACEMENT_LIMIT', 'REPO_LIMIT', etc.
    currency CHAR(3) DEFAULT 'THB',
    available_line DECIMAL(20,2),
    total_credit_line DECIMAL(20,2),
    utilization_amount DECIMAL(20,2),
    credit_line_approve_date DATE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_date DATE
);

-- repo_trades
CREATE TABLE repo_trades (
    repo_trade_id VARCHAR(40) PRIMARY KEY,
    counterparty_id VARCHAR(40) REFERENCES counterparty_master(counterparty_id),
    netting_agreement_id VARCHAR(40),
    trade_type VARCHAR(20),
    trade_date TIMESTAMP,
    purchase_date DATE,
    repurchase_date DATE,
    term INT,
    nominal_amount DECIMAL(20,2),
    interest_rate DECIMAL(10,6),
    accrued_interest DECIMAL(20,2),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2 Complete Schema

See [System Design](../01-DESIGN/SYSTEM_DESIGN.md) for full database documentation.

---

## 4. Development Phases

### Phase 1: Foundation (Week 1)
**Goal:** Working backend with master data APIs

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | Database setup | PostgreSQL with 18 tables (now 20 with market data) |
| 2 | FastAPI scaffold | Running API server |
| 3 | Models | SQLAlchemy models |
| 4 | Master data APIs | 5 CRUD endpoints |
| 5 | Data import | Master data loaded |

**Output:** `GET/POST/PUT /api/v1/securities`, `/counterparties`, `/portfolios`

---

### Phase 2: Bond Trading (Week 2) ✅ COMPLETE
**Goal:** Full bond buy/sell workflow

| Day | Task | Deliverable | Status |
|-----|------|-------------|--------|
| 1 | Trade model | bond_trades with T+2 | ✅ Complete |
| 2 | Trade API | POST with validation | ✅ Complete |
| 3 | Approval workflow | Four-eyes approval | ✅ Complete |
| 4 | ThaiBMA reporting | Auto-reporting | ✅ Complete |
| 5 | Settlement | Status workflow | ✅ Complete |

**Output:** Full production-ready bond trading module

---

### Phase 3: Interbank (Week 3-4) 🔄 NOT STARTED
**Goal:** Lending/borrowing with THOR

> **Current Status:** Models exist, routers use mock data

| Day | Task | Deliverable | Status |
|-----|------|-------------|--------|
| 1 | Interbank service | `interbank_service.py` | ❌ Not started |
| 2 | Interest calc | ACT/365 daily accrual | ❌ Not started |
| 3 | Router update | Connect to real DB | ❌ Not started |
| 4 | Maturity | Auto-maturity processing | ❌ Not started |
| 5 | Testing | End-to-end validation | ❌ Not started |

**Dependencies:** Phase 2 complete

---

### Phase 4: Repo (Week 5-6) 🔄 NOT STARTED
**Goal:** Repo/RRP with collateral

> **Current Status:** Models exist, routers use mock data

| Day | Task | Deliverable | Status |
|-----|------|-------------|--------|
| 1 | Repo service | `repo_service.py` | ❌ Not started |
| 2 | Collateral service | `collateral_service.py` | ❌ Not started |
| 3 | Router update | Connect to real DB | ❌ Not started |
| 4 | Margin calls | Daily MTM workflow | ❌ Not started |
| 5 | Substitution | Collateral swap | ❌ Not started |

**Dependencies:** Phase 3 complete |

---

### Phase 5: Testing (Week 7-8)
**Goal:** End-to-end validation

| Week | Focus |
|------|-------|
| 7 | Unit tests, integration tests |
| 8 | UAT with business users |

---

### Phase 6: Deployment (Week 9-10)
**Goal:** Production ready

| Week | Focus |
|------|-------|
| 9 | Performance testing, security review |
| 10 | Production deployment, training |

---

## 5. API Specifications

### 5.1 Master Data APIs

```
GET    /api/v1/master/securities
POST   /api/v1/master/securities
PUT    /api/v1/master/securities/{id}

GET    /api/v1/master/counterparties
POST   /api/v1/master/counterparties
PUT    /api/v1/master/counterparties/{id}
```

### 5.2 Bond Trading APIs

```
GET    /api/v1/bond-trades
POST   /api/v1/bond-trades
GET    /api/v1/bond-trades/{id}
POST   /api/v1/bond-trades/{id}/approve
POST   /api/v1/bond-trades/{id}/cancel
POST   /api/v1/bond-trades/{id}/settle
```

### 5.3 Complete API List

See [System Design](../01-DESIGN/SYSTEM_DESIGN.md) for full API documentation.

---

## 6. Testing Strategy

### 6.1 Test Levels

| Level | Scope | Tools |
|-------|-------|-------|
| Unit | Individual functions | pytest |
| Integration | API endpoints | pytest + httpx |
| E2E | Full workflows | Playwright |

### 6.2 Test Data

Use Excel source data for realistic test scenarios:
- `Treasury_System_Database_V2_Internal.xlsx`

---

**Document End**

*For setup instructions, see [Setup Instructions](./SETUP_INSTRUCTIONS.md)*  
*For system design, see [System Design](../01-DESIGN/SYSTEM_DESIGN.md)*
