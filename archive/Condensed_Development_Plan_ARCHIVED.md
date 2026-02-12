# Condensed Development Plan - Treasury Management System

**Target Timeline: 10 Weeks (vs 22 weeks original)**  
**Strategy: MVP-First with Parallel Development**

---

## Strategy Overview

### Time-Saving Approaches

| Approach | Time Saved | Implementation |
|----------|-----------|----------------|
| **MVP Scope** | 40% | Phase 1: Bond Trading only (highest volume) |
| **Parallel Development** | 30% | Backend + Frontend + DB simultaneously |
| **Code Generation** | 20% | Auto-generate models, APIs, CRUD from Excel schema |
| **Test-Driven** | -10% | Use Excel test data for immediate validation |
| **Net Reduction** | **~55%** | **22 weeks → 10 weeks** |

---

## 10-Week Sprint Plan

### Sprint 1 (Week 1): Foundation + Auto-Generation
**Goal: Working backend with all master data APIs**

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | Database setup + DDL from Excel | PostgreSQL with 18 tables |
| 2 | FastAPI project scaffold + config | Running API server |
| 3 | **Auto-generate models** from Excel schema | SQLAlchemy models (all tables) |
| 4 | **Auto-generate CRUD APIs** for master data | 5 master table endpoints |
| 5 | Import master data from Excel | Bank codes, securities, counterparties loaded |

**Tools:**
- SQLAlchemy for ORM
- FastAPI-CrudRouter for auto CRUD
- Pandas for Excel import

**Output:** `GET/POST/PUT /api/v1/securities`, `/counterparties`, `/portfolios`, `/entities`

---

### Sprint 2 (Week 2): Bond Trading Core
**Goal: Full bond buy/sell workflow**

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | Bond trade model + validation | bond_trades table with T+2 logic |
| 2 | Trade capture API + limit check | `POST /api/v1/bond-trades` with pre-trade validation |
| 3 | Four-eyes approval workflow | Approval status transitions |
| 4 | ThaiBMA reporting integration | Auto-report within 30 min |
| 5 | Position calculation engine | EOD position build from trades |

**Key Features:**
- Trade validation (business day, T+2, price range)
- Real-time limit checking
- ThaiBMA 30-min reporting
- Position aggregation

---

### Sprint 3 (Week 3): Settlement + Accounting
**Goal: TSD settlement + basic accounting**

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | TSD DVP instruction generation | Settlement messages |
| 2 | Settlement status tracking | SETTLED/FAILED status workflow |
| 3 | Position costing (WAC) | Weighted average cost calculation |
| 4 | Realized P&L calculation | position_realization_events |
| 5 | Basic journal entries | Trade date + Settlement date entries |

**Output:** Complete bond trade lifecycle from entry to settlement

---

### Sprint 4 (Week 4): Frontend MVP
**Goal: Trader UI for bond trading**

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | Next.js setup + component library | Project scaffold with Ant Design |
| 2 | Trade entry form | Bond trade capture UI |
| 3 | Trade blotter + approval | List view, approve/reject actions |
| 4 | Position view | Current holdings display |
| 5 | Dashboard | Limit utilization, pending tasks |

**Tech:** Next.js + TypeScript + Ant Design + React Query

---

### Sprint 5 (Week 5): Interbank + Repo Products
**Goal: All money market products - IB Lending/Borrowing + Repo/RRP**

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | **Interbank Lending** model + API | `POST /api/v1/interbank/lend` |
| 1 | **Interbank Borrowing** model + API | `POST /api/v1/interbank/borrow` |
| 2 | Interbank interest schedule | Floating rate accrual (THOR + spread) |
| 2 | IB limit checking | Pre-trade limit validation |
| 3 | **Repo** trade model + API | `POST /api/v1/repos` (cash borrower) |
| 3 | **Reverse Repo** trade model + API | `POST /api/v1/reverse-repos` (cash lender) |
| 4 | Collateral management | `collateral_positions` allocation/substitution |
| 4 | Repo margin management | Daily MTM + margin call workflow |
| 5 | BAHTNET message generation | ISO20022 pacs.008/pacs.009 message templates (manual input) |
| 5 | Interest accrual batch | Daily accrual for IB + Repo |

**Products Covered:**
- Interbank Lending (Placements)
- Interbank Borrowing (Takings)
- Repo (Bank borrows cash, posts collateral)
- Reverse Repo (Bank lends cash, takes collateral)

**Settlement System Clarification:**
> ⚠️ **BAHTNET**: System generates ISO20022 message files (pacs.008 for credit transfer, pacs.009 for direct debit). Users manually upload to BAHTNET portal - **no API integration**.
> 
> **TSD**: System generates settlement instructions for DVP. Manual submission to TSD system.

---

### Sprint 6 (Week 6): TFRS 9 + Reporting
**Goal: Accounting compliance + BOT reports**

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | Portfolio classification | FVOCI/Amortized Cost/FVTPL logic |
| 2 | ECL calculation engine | Stage 1/2/3 + provision calculation |
| 3 | Accrual + amortization | Daily batch jobs |
| 4 | BOT DER_CPEN export | Regulatory report generation |
| 5 | LCR calculation | Liquidity metrics |

---

### Sprint 7 (Week 7): Risk + Controls
**Goal: Limit management + audit**

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | Limit utilization logging | Immutable audit table |
| 2 | Concentration risk monitoring | Sector/issuer limits |
| 3 | Four-eyes workflow enhancement | Email notifications, escalations |
| 4 | Audit trail queries | User activity reports |
| 5 | Exception management | Settlement failure handling |

---

### Sprint 8 (Week 8): Local Integration + Testing (All Products)
**Goal: E2E validation for ALL products with Excel test data - LOCALLY**

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | **Setup local test environment** | Docker PostgreSQL + Redis running locally |
| 1 | Import all Excel test cases | Sep-Dec 2025 test data loaded into local DB |
| 2 | **Bond Testing (Local)** | Run `pytest app/tests/test_bond_trades.py -v` |
| 2 | Validate buy/sell | Match against `Bond buy_1_V4_*`, `Bond sell_1_V4_*` |
| 2 | Bond position reconciliation | Compare with `V4_Result_*` expected positions |
| 3 | **Interbank Testing (Local)** | Run `pytest app/tests/test_interbank.py -v` |
| 3 | IB Lending validation | Validate vs `IB Lend_V4_*` sheets |
| 3 | IB Borrowing validation | Validate vs `IB Borrow_V4_*` sheets |
| 3 | Interest accrual check | Daily accrual calculation verification |
| 4 | **Repo/RRP Testing (Local)** | Run `pytest app/tests/test_repo.py -v` |
| 4 | Repo validation | Validate vs `Repo_1_V4_*` to `Repo_4_V4_*` |
| 4 | Reverse Repo validation | Validate vs `RRP_1_V4_*` to `RRP_4_V4_*` |
| 4 | Margin calculation check | Collateral value, haircut, margin calls |
| 5 | **Full E2E Testing (Local)** | Run `tests/e2e/test_complete_workflows.py` |
| 5 | Fix all discrepancies | 100% test pass rate locally |
| 5 | Performance validation | All API calls < 500ms locally |

**Local Testing Environment:**
```bash
# Start local infrastructure
docker-compose -f docker-compose.local.yml up -d

# Run all tests locally
pytest app/tests/ -v --tb=short

# Validate against Excel
python scripts/validate_excel_results.py

# Full E2E test
python tests/e2e/test_complete_workflows.py
```

**✅ LOCAL VALIDATION COMPLETE before any deployment**

**Excel Test Sheets Used:**

| Product | Excel Sheets | Validation Focus |
|---------|--------------|------------------|
| **Bond Buy** | `Bond buy_1_V4_Sep25`, `Bond buy_1_V4_Oct25`, `Bond buy_1_31072025` | Trade capture, settlement, position |
| **Bond Sell** | `Bond sell_1_V4_Oct25` | Realized P&L, position reduction |
| **IB Lending** | `IB Lend_V4_Sep25`, `IB Lend_V4_Oct25`, `IB Lend_V4_Nov 25`, `IB Lend_V4_Dec 25` | Deal capture, interest accrual |
| **IB Borrowing** | `IB Borrow_V4_Sep25`, `IB Borrow_V4_Oct25`, `IB Borrow_V4_Nov25`, `IB Borrow_V4_Dec25` | Deal capture, interest expense |
| **Repo** | `Repo_1_V4_Sep25`, `Repo_2_V4_Sep25`, `Repo_2_V4_Oct25`, `Repo_3_V4_Nov25`, `Repo_4_V4_Dec25` | Collateral, margin, lifecycle |
| **Reverse Repo** | `RRP_1_V4_Sep25`, `RRP_2_V4_Sep25`, `RRP_2_V4_Oct25`, `RRP_3_V4_Nov25`, `RRP_4_V4_Dec25` | Cash lending, collateral receive |
| **Expected Results** | `V4_Result_30 Sep 2025` - `V4_Result_31 Dec 2025` | Position reconciliation |

**Testing Approach:**
```python
# Automated validation script
def validate_all_products():
    results = {
        'bonds': validate_bond_trades(),
        'ib_lending': validate_ib_lending(),
        'ib_borrowing': validate_ib_borrowing(),
        'repo': validate_repo_trades(),
        'reverse_repo': validate_reverse_repo_trades()
    }
    return all(r['passed'] for r in results.values())
```

---

### Sprint 9 (Week 9): Local UAT + Polish
**Goal: User acceptance testing in LOCAL environment**

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | **Local Front Office UAT** | Trader tests all 4 products locally |
| 1 | Bond trading workflow | Buy/sell trades, position view |
| 1 | IB Lending/Borrowing | Deal capture, interest view |
| 2 | **Local Middle Office UAT** | Risk/limit management locally |
| 2 | Limit monitoring | Real-time utilization dashboard |
| 2 | Approval workflows | Four-eyes approval process |
| 3 | **Local Back Office UAT** | Settlement, reconciliation locally |
| 3 | Settlement confirmation | T+2 settlement tracking |
| 3 | Exception handling | Failed trade management |
| 4 | Bug fixes + local performance | Response time < 500ms (local) |
| 5 | Documentation | User guides, runbooks |

**UAT Environment:**
- URL: `http://localhost:3000` (local frontend)
- API: `http://localhost:8000` (local backend)
- DB: Local PostgreSQL in Docker

**Sign-off required:**
- [ ] Front Office: All products working locally
- [ ] Middle Office: Limits and risk accurate
- [ ] Back Office: Settlement workflow complete

---

### Sprint 10 (Week 10): Staging → Production
**Goal: Deploy after LOCAL validation complete**

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | **Staging deployment** | Deploy to staging environment |
| 1 | Run automated tests in staging | All tests pass in staging |
| 2 | **Production environment setup** | Cloud deployment ready |
| 2 | Final security hardening | Penetration test pass |
| 3 | **Production data migration** | Master data load |
| 3 | Smoke tests in production | Critical functions verified |
| 4 | **Go-live + parallel run** | Live trading (with old system as backup) |
| 4 | Monitor all products | Real-time monitoring dashboard |
| 5 | **Hypercare support** | Issue resolution, stabilization |

**⚠️ CRITICAL: Only deploy to production AFTER:**
1. ✅ All local tests pass (Week 8)
2. ✅ Local UAT complete (Week 9)
3. ✅ Staging tests pass (Week 10, Day 1)
4. ✅ Smoke tests pass in production (Week 10, Day 3)

---

## Parallel Development Schedule

```
Week:  1    2    3    4    5    6    7    8    9    10
       ├────┴────┴────┤
       │    BACKEND    │
       │  (Foundation) │
                     ├────┴────┴────┤
                     │   FRONTEND   │
                     │     (MVP)    │
       ├─────────────┴──────────────┤
       │      DATABASE + DEVOPS     │
       │         (Throughout)       │
                                  ├────┴────┤
                                  │ TESTING │
                                  │   & UAT │
```

---

## Scope Prioritization (MVP vs Phase 2)

### MVP (Weeks 1-10) - MUST HAVE

| Feature | Priority | Reason |
|---------|----------|--------|
| **Bond Trading (Buy/Sell)** | P0 | Core product, highest volume |
| **ThaiBMA Reporting** | P0 | Regulatory requirement |
| **T+2 Settlement** | P0 | Market standard |
| **Interbank Lending** | P0 | Core product - placements |
| **Interbank Borrowing** | P0 | Core product - takings |
| **Repo (Cash Borrower)** | P0 | Short-term funding |
| **Reverse Repo (Cash Lender)** | P0 | Cash deployment |
| **Counterparty Limits** | P0 | Risk management |
| **Position Management** | P0 | Trading decisions |
| Basic Accounting | P1 | Daily operations |
| TFRS 9 Classification | P1 | Compliance |
| BOT DER_CPEN Report | P1 | Regulatory |

### Phase 2 (Post Go-Live) - NICE TO HAVE

| Feature | Reason |
|---------|--------|
| Advanced Repo Scenarios | Multi-collateral, substitution rules |
| Complex ECL Models | Monte Carlo simulations |
| VaR Calculation | Risk enhancement |
| Full LCR/NSFR | Complete liquidity metrics |
| Advanced Workflows | Enhanced approval chains |
| Mobile App | Desktop-first for traders |
| Cross-Currency | THB only in MVP |

**Note:** MVP includes complete **Interbank Borrowing/Lending** and **Repo/Reverse Repo** with full collateral management, margin calls, and settlement.

---

## Acceleration Techniques

### 1. Code Generation from Excel (Week 1)

```python
# scripts/generate_models.py
# Auto-generate SQLAlchemy models from Excel schema

def generate_model_from_excel(sheet_name):
    df = pd.read_excel('data/source/Treasury_System_Database_V2_Internal.xlsx', 
                       sheet_name=sheet_name)
    
    model_code = f"""
class {sheet_name}(Base):
    __tablename__ = '{sheet_name.lower()}'
    
    {generate_columns(df)}
    
    {generate_relationships(df)}
"""
    return model_code

# Generates 18 model files in 1 day vs 5 days manual
```

### 2. FastAPI CrudRouter (Week 1)

```python
# Auto-generate CRUD endpoints
from fastapi_crudrouter import SQLAlchemyCRUDRouter

router = SQLAlchemyCRUDRouter(
    schema=SecurityMaster,
    db_model=SecurityMasterModel,
    db=get_db,
    prefix="/securities"
)
# Generates GET/POST/PUT/DELETE in 1 line
```

### 3. Excel Test Data Import (Week 8)

```python
# scripts/import_test_data.py
# Import ALL test cases from Excel automatically

# Bond test data
bond_sheets = [
    'Bond buy_1_V4_Sep25',
    'Bond buy_1_V4_Oct25', 
    'Bond buy_1_31072025',
    'Bond sell_1_V4_Oct25',
    'Bond Buy-Sell_V4_Sep25 + Oct25'
]

# Interbank test data
ib_sheets = [
    'IB Lend_V4_Sep25', 'IB Lend_V4_Oct25', 'IB Lend_V4_Nov 25', 'IB Lend_V4_Dec 25',
    'IB Borrow_V4_Sep25', 'IB Borrow_V4_Oct25', 'IB Borrow_V4_Nov25', 'IB Borrow_V4_Dec25'
]

# Repo/RRP test data
repo_sheets = [
    'Repo_1_V4_Sep25', 'Repo_2_V4_Sep25', 'Repo_2_V4_Oct25', 'Repo_3_V4_Nov25', 'Repo_4_V4_Dec25',
    'RRP_1_V4_Sep25', 'RRP_2_V4_Sep25', 'RRP_2_V4_Oct25', 'RRP_3_V4_Nov25', 'RRP_4_V4_Dec25'
]

# Expected results
result_sheets = [
    'V4_Result_30 Sep 2025',
    'V4_Result_31 Oct 2025',
    'V4_Result_30 Nov 2025',
    'V4_Result_31 Dec 2025'
]

all_sheets = bond_sheets + ib_sheets + repo_sheets + result_sheets

for sheet in all_sheets:
    df = pd.read_excel('data/source/Treasury_System_Database_V2_Internal.xlsx',
                       sheet_name=sheet)
    load_into_database(df, table_name=sheet)
```

### 4. Component Library (Week 4)

Use **Ant Design** or **Material-UI** instead of custom components:
- Pre-built forms, tables, modals
- 70% faster UI development
- Consistent design

---

## Team Structure (Accelerated)

| Role | Count | Weeks | Focus |
|------|-------|-------|-------|
| **Tech Lead / Architect** | 1 | 1-10 | Design, code review, integration |
| **Backend Developer** | 2 | 1-8 | APIs, business logic |
| **Frontend Developer** | 1 | 3-8 | UI implementation |
| **Database Developer** | 1 | 1-3 | Schema, optimization |
| **QA Engineer** | 1 | 6-10 | Testing, validation |
| **DevOps** | 0.5 | 1, 9-10 | CI/CD, deployment |

**Total: 6.5 FTEs** (vs 11 FTEs in original plan)

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| **Scope creep** | Strict MVP definition, Phase 2 backlog |
| **Integration issues** | Daily builds, early external connectivity tests |
| **Performance problems** | Load testing in Week 8 |
| **Data quality** | Automated Excel validation in Week 8 |
| **Regulatory compliance** | BOT pre-review in Week 7 |

---

## Success Criteria (Week 10)

### Performance Metrics

| Metric | Target |
|--------|--------|
| **Trade Capture** | All products < 5 seconds |
| **ThaiBMA Reporting** | < 30 minutes from execution |
| **Settlement** | T+2 compliance 100% |
| **Uptime** | 99.5% during market hours |
| **User Adoption** | All traders trained and using |

### Product Coverage

| Product | Test Cases | Excel Validation | Status |
|---------|------------|------------------|--------|
| **Bond Trading** | 50+ | ✅ `Bond buy_1_V4_*`, `Bond sell_1_V4_*` | PASS |
| **Interbank Lending** | 20+ | ✅ `IB Lend_V4_*` (all months) | PASS |
| **Interbank Borrowing** | 20+ | ✅ `IB Borrow_V4_*` (all months) | PASS |
| **Repo** | 30+ | ✅ `Repo_1_V4_*` through `Repo_4_V4_*` | PASS |
| **Reverse Repo** | 30+ | ✅ `RRP_1_V4_*` through `RRP_4_V4_*` | PASS |
| **Position Reconciliation** | 100% | ✅ `V4_Result_*` (all months) | PASS |

### Functional Requirements

| Feature | Bond | IB Lend | IB Borrow | Repo | RRP |
|---------|------|---------|-----------|------|-----|
| Trade Capture | ✅ | ✅ | ✅ | ✅ | ✅ |
| Limit Checking | ✅ | ✅ | ✅ | ✅ | ✅ |
| Settlement (T+2) | ✅ (TSD) | ✅ (BAHTNET) | ✅ (BAHTNET) | ✅ (BAHTNET) | ✅ (BAHTNET) |
| Interest Accrual | ✅ | ✅ | ✅ | ✅ | ✅ |
| Collateral Management | N/A | N/A | N/A | ✅ | ✅ |
| Margin Calls | N/A | N/A | N/A | ✅ | ✅ |
| ThaiBMA Reporting | ✅ | N/A | N/A | N/A | N/A |
| Accounting (TFRS 9) | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## Post-Launch Roadmap

### Month 3: Phase 2A
- Advanced repo scenarios
- Enhanced ECL models
- VaR calculation

### Month 6: Phase 2B
- Mobile dashboard
- Advanced analytics
- AI-powered recommendations

---

## Summary

| Metric | Original | Condensed |
|--------|----------|-----------|
| **Timeline** | 22 weeks | 10 weeks |
| **Team Size** | 11 people | 6.5 people |
| **MVP Scope** | Full features | Bond focus + IB |
| **Parallel Work** | Sequential | Simultaneous |
| **Automation** | Manual | Code generation |
| **Risk Level** | Low | Medium |

**Trade-offs:**
- ✅ Faster time-to-market
- ✅ Lower initial cost
- ✅ Earlier user feedback
- ⚠️ Higher technical debt (to be refactored in Phase 2)
- ⚠️ Requires experienced team

---

## Appendix: Comprehensive Testing Strategy

### Test Data Sources from Excel

Your Excel file contains **comprehensive test data** for all products across multiple months:

```
Treasury System Database V2_Internal.xlsx
│
├── 📁 BOND TEST DATA
│   ├── Bond buy_1_V4_Sep25 (15+ buy scenarios)
│   ├── Bond buy_1_V4_Oct25 (20+ buy scenarios)
│   ├── Bond buy_1_31072025 (July test cases)
│   ├── Bond sell_1_V4_Oct25 (10+ sell scenarios)
│   └── Bond Buy-Sell_V4_Sep25 + Oct25 (combined)
│
├── 📁 INTERBANK LENDING TEST DATA
│   ├── IB Lend_V4_Sep25
│   ├── IB Lend_V4_Oct25
│   ├── IB Lend_V4_Nov 25
│   └── IB Lend_V4_Dec 25
│
├── 📁 INTERBANK BORROWING TEST DATA
│   ├── IB Borrow_V4_Sep25
│   ├── IB Borrow_V4_Sep25_2
│   ├── IB Borrow_V4_Oct25
│   ├── IB Borrow_V4_Nov25
│   └── IB Borrow_V4_Dec25
│
├── 📁 REPO (CASH BORROWER) TEST DATA
│   ├── Repo_1_V4_Sep25 (initial repos)
│   ├── Repo_2_V4_Sep25 (rollovers)
│   ├── Repo_2_V4_Oct25
│   ├── Repo_3_V4_Nov25
│   └── Repo_4_V4_Dec25
│
├── 📁 REVERSE REPO (CASH LENDER) TEST DATA
│   ├── RRP_1_V4_Sep25
│   ├── RRP_2_V4_Sep25
│   ├── RRP_2_V4_Oct25
│   ├── RRP_3_V4_Nov25
│   └── RRP_4_V4_Dec25
│
└── 📁 EXPECTED RESULTS (for validation)
    ├── V4_Result_30 Sep 2025
    ├── V4_Result_31 Oct 2025
    ├── V4_Result_30 Nov 2025
    └── V4_Result_31 Dec 2025
```

### Test Scenarios by Product

#### 1. Interbank Lending (Placements)

| Test Case | Excel Sheet | Validation |
|-----------|-------------|------------|
| Fixed rate lending | IB Lend_V4_Sep25 | Interest calculation = Principal × Rate × Days/365 |
| Floating rate lending | IB Lend_V4_Oct25 | THOR + spread repricing quarterly |
| Early termination | IB Lend_V4_Nov 25 | Break cost calculation |
| Maturity rollover | IB Lend_V4_Dec 25 | Auto-rollover with new rate |
| Limit breach attempt | All | Pre-trade block at 100% |

#### 2. Interbank Borrowing (Takings)

| Test Case | Excel Sheet | Validation |
|-----------|-------------|------------|
| Fixed rate borrowing | IB Borrow_V4_Sep25 | Interest expense accrual |
| Floating rate borrowing | IB Borrow_V4_Oct25 | Rate reset, interest schedule |
| Multiple borrowings | IB Borrow_V4_Sep25_2 | Aggregate limit check |
| Cross-month rollover | IB Borrow_V4_Nov25 | Month-end position reporting |
| BAHTNET settlement | IB Borrow_V4_Dec25 | Settlement confirmation |

#### 3. Repo (Bank Borrows Cash)

| Test Case | Excel Sheet | Validation |
|-----------|-------------|------------|
| Initial repo setup | Repo_1_V4_Sep25 | Collateral allocation, haircut applied |
| Collateral substitution | Repo_2_V4_Sep25 | Replace collateral, margin check |
| Repo rollover | Repo_2_V4_Oct25 | Terminate + new repo |
| Margin call (deficit) | Repo_3_V4_Nov25 | MTM < threshold → margin call |
| Repo maturity | Repo_4_V4_Dec25 | Repayment, collateral release |
| Open repo | All | Daily rate reset, no fixed maturity |

#### 4. Reverse Repo (Bank Lends Cash)

| Test Case | Excel Sheet | Validation |
|-----------|-------------|------------|
| Cash lending setup | RRP_1_V4_Sep25 | Cash out, collateral in |
| Receive collateral | RRP_2_V4_Sep25 | DVP settlement |
| Margin return (surplus) | RRP_2_V4_Oct25 | Excess collateral return |
| Reverse repo maturity | RRP_3_V4_Nov25 | Cash return, collateral release |
| Multiple RRPs | RRP_4_V4_Dec25 | Portfolio aggregation |

### Automated Test Validation Script

```python
# tests/validate_excel_data.py
# Automated validation against Excel test data

import pandas as pd
import pytest
from datetime import datetime

class TestBondTrading:
    """Validate bond trades against Excel: Bond buy_1_V4_*, Bond sell_1_V4_*"""
    
    def test_bond_buy_settlement_amount(self):
        """Validate settlement amount calculation"""
        excel_data = load_excel_sheet('Bond buy_1_V4_Sep25')
        
        for row in excel_data:
            trade = create_bond_trade(row)
            expected = row['SettlementAmount']
            actual = trade.calculate_settlement()
            
            assert abs(actual - expected) < 0.01, \
                f"Trade {row['TradeID']}: Expected {expected}, got {actual}"
    
    def test_bond_position_aggregation(self):
        """Validate position matches V4_Result_*"""
        expected = load_excel_sheet('V4_Result_30 Sep 2025')
        actual = calculate_positions(date='2025-09-30')
        
        assert positions_match(expected, actual)

class TestInterbankLending:
    """Validate IB Lending against Excel: IB Lend_V4_*"""
    
    def test_interbank_interest_accrual(self):
        """Validate daily interest accrual"""
        excel_data = load_excel_sheet('IB Lend_V4_Sep25')
        
        for deal in excel_data:
            expected_accrued = deal['accrued_interest']
            actual_accrued = calculate_accrual(deal)
            
            assert abs(actual_accrued - expected_accrued) < 1.0, \
                f"Deal {deal['DealID']}: Accrual mismatch"
    
    def test_floating_rate_repricing(self):
        """Validate THOR + spread repricing"""
        deal = create_floating_rate_deal()
        
        # After rate reset
        new_thor = get_thor_rate()
        expected_rate = new_thor + deal.spread_bp
        
        assert deal.effective_rate == expected_rate

class TestInterbankBorrowing:
    """Validate IB Borrowing against Excel: IB Borrow_V4_*"""
    
    def test_borrowing_limit_utilization(self):
        """Validate limit consumed on borrowing"""
        deal = create_borrowing_deal()
        
        limit_before = get_limit_available(deal.counterparty_id)
        process_deal(deal)
        limit_after = get_limit_available(deal.counterparty_id)
        
        assert limit_after == limit_before - deal.principal_amount

class TestRepo:
    """Validate Repo against Excel: Repo_1_V4_* through Repo_4_V4_*"""
    
    def test_collateral_haircut_calculation(self):
        """Validate haircut applied correctly"""
        excel_data = load_excel_sheet('Repo_1_V4_Sep25')
        
        for repo in excel_data:
            collateral = get_collateral(repo.CollateralID)
            expected_margin = collateral.market_value * (1 - collateral.haircut)
            
            assert abs(collateral.margin_value - expected_margin) < 0.01
    
    def test_margin_call_generation(self):
        """Validate margin call when exposure > threshold"""
        # Setup repo with collateral
        repo = create_repo_trade()
        
        # Simulate price drop
        drop_collateral_price(repo, by_percent=10)
        
        # Trigger margin process
        margin_call = process_daily_margin(repo)
        
        assert margin_call.MarginCallAmount > 0
        assert margin_call.Status == 'PENDING'
    
    def test_repo_lifecycle(self):
        """Full repo lifecycle: setup → margin → maturity"""
        # Day 0: Setup
        repo = create_repo_trade(status='OPEN')
        
        # Day 1-5: Daily margin
        for day in range(1, 6):
            process_daily_margin(repo, date=f'2025-09-{day:02d}')
        
        # Day 30: Maturity
        repo.maturity_date = '2025-10-01'
        process_maturity(repo)
        
        assert repo.status == 'CLOSED'

class TestReverseRepo:
    """Validate Reverse Repo against Excel: RRP_1_V4_* through RRP_4_V4_*"""
    
    def test_cash_lending_collateral_received(self):
        """Validate cash out = collateral received after haircut"""
        rrp = create_reverse_repo_trade()
        
        cash_lent = rrp.nominal_amount
        collateral_value = sum(c.margin_value for c in rrp.collateral)
        
        # Collateral value >= cash lent (with buffer)
        assert collateral_value >= cash_lent * 0.99
    
    def test_reverse_repo_interest_income(self):
        """Validate interest income accrual on cash lent"""
        rrp = create_reverse_repo_trade(rate=2.5)
        
        # Accrue for 30 days
        interest = calculate_repo_interest(rrp, days=30)
        expected = rrp.nominal_amount * 0.025 * 30 / 365
        
        assert abs(interest - expected) < 1.0

# Run all tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

### Test Execution in Week 8

```bash
# Week 8 Test Execution Plan

# Day 1: Import all test data
python scripts/import_test_data.py

# Day 2: Bond tests
pytest tests/validate_excel_data.py::TestBondTrading -v --tb=short

# Day 3: Interbank tests
pytest tests/validate_excel_data.py::TestInterbankLending -v --tb=short
pytest tests/validate_excel_data.py::TestInterbankBorrowing -v --tb=short

# Day 4: Repo tests
pytest tests/validate_excel_data.py::TestRepo -v --tb=short
pytest tests/validate_excel_data.py::TestReverseRepo -v --tb=short

# Day 5: Full regression
pytest tests/validate_excel_data.py -v --html=report.html
```

---

*Recommended for: Experienced team, clear requirements, need for quick MVP*
