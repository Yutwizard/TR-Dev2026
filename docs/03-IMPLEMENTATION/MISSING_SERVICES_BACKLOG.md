# Missing Services Backlog

**Project:** Treasury Management System  
**Created:** February 5, 2026  
**Purpose:** Track incomplete services from Sprint 2 for future implementation

---

## 📋 Overview

Sprint 2 was focused on Bond Trading which is **100% complete**. However, Interbank and Repo modules were only implemented as API stubs with mock data. This document tracks what needs to be built to complete these modules.

| Module | Models | Routers | Services | Status |
|--------|--------|---------|----------|--------|
| Bond Trading | ✅ | ✅ | ✅ | **Complete** |
| Interbank | ✅ | ✅ | ✅ | **Complete** |
| Repo | ✅ | ⚠️ Mock | ❌ | **Pending** |

---

## 🔴 High Priority: Missing Service Files

### ✅ COMPLETED: `app/services/interbank_service.py`

**Purpose:** Core business logic for interbank lending/borrowing deals

**Required Functions:**

```python
# Deal Management
create_interbank_deal(db: Session, deal_data: InterbankDealCreate, trader_id: str) -> InterbankDeal
approve_interbank_deal(db: Session, deal_id: str, approver_id: str) -> InterbankDeal
cancel_interbank_deal(db: Session, deal_id: str, reason: str) -> InterbankDeal
get_interbank_deal(db: Session, deal_id: str) -> Optional[InterbankDeal]
list_interbank_deals(db: Session, filters: DealFilters) -> List[InterbankDeal]

# Interest Calculations
calculate_interest_amount(principal: Decimal, rate: Decimal, tenor_days: int, dcc: str) -> Decimal
calculate_accrued_interest(deal: InterbankDeal, as_of_date: date) -> Decimal
calculate_maturity_amount(deal: InterbankDeal) -> Decimal

# Floating Rate Management
create_interest_schedule(deal: InterbankDeal) -> InterbankInterestSchedule
update_floating_rate(deal: InterbankDeal, new_thor_rate: Decimal) -> Decimal
get_next_reset_date(deal: InterbankDeal) -> date

# Settlement
settle_start_leg(db: Session, deal_id: str, bahtnet_ref: str) -> InterbankDeal
settle_maturity_leg(db: Session, deal_id: str, bahtnet_ref: str) -> InterbankDeal
generate_bahtnet_instruction(deal: InterbankDeal, leg: str) -> dict

# Maturity Processing
process_maturity(db: Session, deal_id: str) -> InterbankDeal
get_maturing_deals(db: Session, days_ahead: int) -> List[InterbankDeal]

# Limit Integration
check_placement_limit(db: Session, counterparty_id: str, amount: Decimal) -> LimitCheckResult
update_limit_utilization(db: Session, deal: InterbankDeal, action: str)
```

**Database Tables Used:**
- `interbank_deals`
- `interbank_interest_schedule`
- `limit_utilization`

**Estimated Effort:** 1-2 days

---

### 2. `app/services/repo_service.py`

**Purpose:** Core business logic for repo/reverse repo transactions

**Required Functions:**

```python
# Trade Management
create_repo_trade(db: Session, trade_data: RepoTradeCreate, trader_id: str) -> RepoTrade
approve_repo_trade(db: Session, trade_id: str, approver_id: str) -> RepoTrade
cancel_repo_trade(db: Session, trade_id: str, reason: str) -> RepoTrade
get_repo_trade(db: Session, trade_id: str) -> Optional[RepoTrade]
list_repo_trades(db: Session, filters: RepoFilters) -> List[RepoTrade]

# Interest & Pricing
calculate_repo_interest(near_leg: Decimal, rate: Decimal, tenor_days: int) -> Decimal
calculate_far_leg_amount(near_leg: Decimal, interest: Decimal) -> Decimal
calculate_repo_rate_from_prices(near_price: Decimal, far_price: Decimal, tenor: int) -> Decimal

# Settlement
settle_near_leg_cash(db: Session, trade_id: str, ref: str) -> RepoTrade
settle_near_leg_collateral(db: Session, trade_id: str) -> RepoTrade
settle_far_leg_cash(db: Session, trade_id: str, ref: str) -> RepoTrade
settle_far_leg_collateral(db: Session, trade_id: str) -> RepoTrade

# Early Termination
calculate_early_termination(trade: RepoTrade, termination_date: date) -> EarlyTerminationResult
process_early_termination(db: Session, trade_id: str, termination_date: date) -> RepoTrade

# Reporting
calculate_collateral_summary(db: Session, portfolio_id: Optional[str]) -> CollateralSummary
get_pending_margin_calls(db: Session) -> List[MarginCall]
```

**Database Tables Used:**
- `repo_trades`
- `limit_utilization`

**Estimated Effort:** 1-2 days

---

### 3. `app/services/collateral_service.py`

**Purpose:** Collateral allocation, valuation, and margin call management

**Required Functions:**

```python
# Collateral Allocation
allocate_collateral(db: Session, trade: RepoTrade, security_id: str, face_value: Decimal) -> CollateralPosition
release_collateral(db: Session, trade: RepoTrade) -> None
substitute_collateral(db: Session, trade: RepoTrade, new_security_id: str, new_face_value: Decimal) -> CollateralPosition

# Valuation
calculate_collateral_market_value(collateral: CollateralPosition, current_price: Decimal) -> Decimal
calculate_collateral_value_after_haircut(market_value: Decimal, haircut_pct: Decimal) -> Decimal
update_collateral_market_values(db: Session, prices: Dict[str, Decimal]) -> int

# Margin Management
calculate_margin_percentage(collateral_value: Decimal, loan_amount: Decimal) -> Decimal
calculate_margin_call_amount(trade: RepoTrade, current_margin_pct: Decimal) -> Decimal
trigger_margin_call(db: Session, trade: RepoTrade, amount: Decimal) -> MarginCall
agree_margin_call(db: Session, margin_call_id: str, approver_id: str) -> MarginCall
settle_margin_call(db: Session, margin_call_id: str, bahtnet_ref: str) -> MarginCall

# Daily MTM
daily_collateral_valuation(db: Session, date: date) -> List[MarginCallResult]
check_margin_thresholds(db: Session) -> List[MarginCall]

# Reports
get_collateral_by_security(db: Session, security_id: str) -> List[CollateralPosition]
get_collateral_by_counterparty(db: Session, counterparty_id: str) -> CollateralReport
get_margin_call_history(db: Session, from_date: date, to_date: date) -> List[MarginCall]
```

**Database Tables Used:**
- `collateral_positions`
- `margin_calls`
- `cash_margin_movements`

**Estimated Effort:** 1-2 days

---

## 🟡 Medium Priority: Router Updates

### ✅ COMPLETED: Update `app/routers/interbank.py`

**Current:** Uses `MOCK_INTERBANK_DEALS` list  
**Required:** Connect to database via `interbank_service.py`

**Changes Needed:**
```python
# Replace this:
MOCK_INTERBANK_DEALS = [...]

# With this:
from app.services.interbank_service import (
    create_interbank_deal,
    approve_interbank_deal,
    get_interbank_deal,
    list_interbank_deals,
    # ... etc
)

# Update all endpoints to use:
async def create_interbank_deal(
    deal: InterbankDealCreate,
    db: Session = Depends(get_db),  # Add this
    current_user: UserInToken = Depends(get_current_active_user)
):
    # Use real service instead of mock
    return create_interbank_deal(db, deal, current_user.user_id)
```

**Estimated Effort:** 4-6 hours

---

### 5. Update `app/routers/repo.py`

**Current:** Uses `MOCK_REPO_TRADES` list  
**Required:** Connect to database via `repo_service.py` and `collateral_service.py`

**Changes Needed:**
```python
# Replace this:
MOCK_REPO_TRADES = [...]

# With this:
from app.services.repo_service import (
    create_repo_trade,
    approve_repo_trade,
    # ... etc
)
from app.services.collateral_service import (
    calculate_margin_call,
    get_collateral_summary,
    # ... etc
)
```

**Estimated Effort:** 4-6 hours

---

## 🟢 Low Priority: Batch Jobs & Scheduled Tasks

### 6. Daily Accrual Job

**File:** `app/jobs/daily_accrual.py` (new)

**Purpose:** Calculate daily interest accrual for interbank deals and repos

```python
async def run_daily_accrual(db: Session, date: date):
    """
    Run at 18:00 daily
    1. Calculate accrued interest for all active interbank deals
    2. Calculate accrued interest for all active repos
    3. Update position tables
    4. Generate GL entries
    """
    pass
```

**Estimated Effort:** 1 day

---

### 7. Maturity Processing Job

**File:** `app/jobs/maturity_processing.py` (new)

**Purpose:** Process maturing interbank deals and repos

```python
async def process_maturities(db: Session, date: date):
    """
    Run at start of day (08:00)
    1. Identify deals maturing today
    2. Generate settlement instructions
    3. Send notifications to Back Office
    4. Release limit utilization on settlement
    """
    pass
```

**Estimated Effort:** 1 day

---

### 8. Margin Call Job

**File:** `app/jobs/margin_call.py` (new)

**Purpose:** Daily MTM and margin call detection

```python
async def run_margin_call_process(db: Session, date: date):
    """
    Run at 17:00 daily (after ThaiBMA price import)
    1. Update collateral market values
    2. Calculate margin percentages
    3. Identify trades below threshold
    4. Create margin call records
    5. Notify Middle Office
    """
    pass
```

**Estimated Effort:** 1 day

---

## 📊 Summary Table

| # | Service/File | Priority | Effort | Dependencies |
|---|--------------|----------|--------|--------------|
| 1 | `interbank_service.py` | 🟢 Done | 0 days | None |
| 2 | `repo_service.py` | 🔴 High | 1-2 days | None |
| 3 | `collateral_service.py` | 🔴 High | 1-2 days | None |
| 4 | Update `interbank.py` router | 🟢 Done | 0 hrs | #1 |
| 5 | Update `repo.py` router | 🟡 Medium | 4-6 hrs | #2, #3 |
| 6 | Daily accrual job | 🟢 Low | 1 day | #1, #2 |
| 7 | Maturity processing job | 🟢 Low | 1 day | #1, #2 |
| 8 | Margin call job | 🟢 Low | 1 day | #3 |

**Total Estimated Effort:** 6-9 days (1.5-2 weeks)

---

## 🎯 Recommended Implementation Order

### Week 1: Core Services
1. Create `interbank_service.py`
2. Create `repo_service.py`
3. Create `collateral_service.py`
4. Update routers to use real DB
5. Write unit tests

### Week 2: Batch Jobs & Integration
6. Daily accrual job
7. Maturity processing job
8. Margin call job
9. Integration testing
10. Documentation update

---

## 📝 Notes

- All SQLAlchemy models are already created and ready
- Database schema is complete (18 tables)
- API contracts are defined in current routers (use same request/response models)
- Can be developed in parallel with Sprint 3 frontend work

---

**Last Updated:** February 5, 2026  
**Next Review:** Before Sprint 3 planning
