# Phase 0: Architecture Cleanup — Complete

**Date**: 2026-02-10  
**Status**: ✅ COMPLETE  
**Sprint**: Pre-Sprint 3 Architecture Cleanup

---

## Summary

Phase 0 establishes shared architectural components that ALL product modules (Bond, Interbank, Repo) will use consistently in Sprint 3 and beyond. This eliminates the fragmented patterns discovered during the architecture review.

---

## What Was Built

### 0.1 Unified Enums (`app/core/enums.py`) ✅

**Problem solved**: Enums were duplicated in 3 locations with different values:
- `models/transactions.py` → `TradeStatus`, `TradeSide`, `DealType`
- `schemas/transactions.py` → `TradeStatus`, `TradeSide`, `InterbankDealType`, `RateType`
- `routers/interbank.py` → `DealType`, `DealStatus`, `SettlementStatus`, `RateType` (all different from above!)

**Solution**: Single source of truth with ALL enums:

| Category | Enums |
|----------|-------|
| Trade Status | `TradeStatus` (11 values incl. ACTIVE, MATURED, MARGIN_CALL) |
| Trade Direction | `TradeSide` (BUY, SELL, LEND, BORROW) |
| Product Types | `BondTradeType`, `InterbankDealType`, `RepoTradeType`, `RepoSubType` |
| Rate & Convention | `RateType`, `DayCountConvention` (4 conventions), `ReferenceRate` |
| Settlement | `SettlementStatus`, `SettlementChannel` |
| Master Data | `EntityStatus`, `SecurityStatus` |
| Limits | `LimitType` |
| Accounting | `AccountingClassification` (TFRS 9) |
| Audit | `AuditAction` (12 action types), `EntityType` (8 entity types) |

### 0.2 Calculation Engine (`app/services/calculation_engine.py`) ✅

**Problem solved**: Interest calculations were scattered and inconsistent:
- `bond_trade_service.py` → hardcoded ACT/365 only
- `routers/interbank.py` → inline ACT/365 and ACT/360 calculation
- Design docs mentioned 4 conventions; only 1 was implemented correctly

**Solution**: Centralized calculation engine with:

| Function | Used By |
|----------|---------|
| `calculate_day_count_fraction()` | All products |
| `calculate_simple_interest()` | Interbank, Repo |
| `calculate_accrued_interest()` | Bonds |
| `calculate_daily_accrual()` | EOD batch processing |
| `calculate_bond_trade_amounts()` | Bond trades |
| `calculate_repo_interest()` | Repo trades |
| `calculate_collateral_value()` | Repo collateral |
| `calculate_margin()` | Repo margin calls |
| `calculate_interbank_amounts()` | Interbank deals |
| `CalculationEngine` class | Dependency injection wrapper |

Supports all 4 day count conventions: ACT/365, ACT/360, 30/360, ACT/ACT.

### 0.3 State Machine (`app/core/state_machine.py`) ✅

**Problem solved**: Status transitions were checked with `if deal.status != "PENDING_APPROVAL"` scattered across routers. No consistent lifecycle enforcement.

**Solution**: Explicit transition maps for all 3 products:

```
Bond Trade:
  DRAFT → PENDING_APPROVAL → APPROVED → PENDING_SETTLEMENT → SETTLED
    ↓         ↓                  ↓
  CANCELLED  REJECTED         CANCELLED
              ↓
            DRAFT (re-submit)

Interbank Deal:
  DRAFT → PENDING_APPROVAL → APPROVED → ACTIVE → MATURED
    ↓         ↓                  ↓         ↓
  CANCELLED  REJECTED         CANCELLED  CANCELLED (early termination)

Repo Trade:
  DRAFT → PENDING_APPROVAL → APPROVED → PENDING_SETTLEMENT → ACTIVE → MATURED
    ↓         ↓                  ↓                               ↓
  CANCELLED  REJECTED         CANCELLED                     MARGIN_CALL → ACTIVE
```

Utility functions:
- `validate_transition()` → Check if transition is allowed
- `assert_transition()` → Raise error if not allowed (for services)
- `get_allowed_transitions()` → Get valid next states
- `is_terminal_state()` → Check if state is final
- `get_cancellable_states()` → Get states from which cancellation is possible

### 0.4 Transaction Audit Log (`app/models/audit.py` + `app/services/audit_service.py`) ✅

**Problem solved**: No systematic audit trail for financial transactions. The existing `AuditLog` in `users.py` was designed for login/system events only (text-based, no JSON, no correlation).

**Solution**: 

**`TransactionAuditLog` model** (table: `transaction_audit_log`):
- JSON-based `old_values` / `new_values` for proper state tracking
- `correlation_id` for grouping related actions (e.g., create + limit check)
- Indexed on entity, user, action, timestamp, and correlation

**`AuditService`** with convenience methods:
- `log_created()` → Trade/deal creation
- `log_status_change()` → Any status transition
- `log_approved()` → Four-eyes approval
- `log_rejected()` → Rejection with reason
- `log_cancelled()` → Cancellation with reason
- `log_settled()` → Settlement confirmation
- `log_limit_check()` → Limit check results
- `log_thaibma_reported()` → ThaiBMA reporting
- `log_margin_call()` → Repo margin events

### 0.5 Package Exports Updated ✅

- `app/core/__init__.py` → Exports all enums and state machine functions
- `app/services/__init__.py` → Exports calculation engine and audit service
- `app/models/__init__.py` → Exports `TransactionAuditLog`

---

## Files Created / Modified

### New Files (5)
| File | Purpose | Lines |
|------|---------|-------|
| `app/core/enums.py` | Unified enums | ~170 |
| `app/core/state_machine.py` | Deal lifecycle rules | ~260 |
| `app/models/audit.py` | Transaction audit model | ~130 |
| `app/services/calculation_engine.py` | Financial calculations | ~370 |
| `app/services/audit_service.py` | Audit service | ~220 |

### Modified Files (3)
| File | Change |
|------|--------|
| `app/core/__init__.py` | Added enum + state machine exports |
| `app/services/__init__.py` | Added calculation engine + audit exports |
| `app/models/__init__.py` | Added TransactionAuditLog export |

---

## Migration Required

After Phase 0, you need to generate a database migration for the new `transaction_audit_log` table:

```bash
cd src/backend
alembic revision --autogenerate -m "add_transaction_audit_log_table"
alembic upgrade head
```

---

## How Services Should Use These Components

### Example: Creating an Interbank Deal (Sprint 3 pattern)

```python
# app/services/interbank_service.py

from app.core.enums import TradeStatus, InterbankDealType, DayCountConvention, EntityType
from app.core.state_machine import assert_transition, INTERBANK_DEAL_TRANSITIONS
from app.services.calculation_engine import calculate_interbank_amounts
from app.services.audit_service import AuditService

class InterbankService:
    def __init__(self, db: Session):
        self.db = db
        self.audit = AuditService(db)
        self.calc = CalculationEngine()
    
    def create_deal(self, ...) -> InterbankDeal:
        # 1. Calculate amounts (using centralized engine)
        amounts = self.calc.calculate_interbank_amounts(
            principal, rate, start_date, maturity_date, 
            DayCountConvention.ACT_365
        )
        
        # 2. Create deal with proper enums
        deal = InterbankDeal(
            status=TradeStatus.PENDING_APPROVAL,
            deal_type=InterbankDealType.PLACEMENT,
            ...
        )
        
        # 3. Audit trail
        self.audit.log_created(
            entity_type=EntityType.INTERBANK_DEAL,
            entity_id=deal.deal_ref,
            user_id=trader_id,
            new_values={"status": TradeStatus.PENDING_APPROVAL, ...}
        )
        
        return deal
    
    def approve_deal(self, deal_ref, approver_id) -> InterbankDeal:
        deal = self._get_deal(deal_ref)
        
        # State machine enforcement
        assert_transition(
            deal.status, TradeStatus.APPROVED,
            INTERBANK_DEAL_TRANSITIONS,
            entity_type="Interbank Deal",
            entity_ref=deal_ref
        )
        
        deal.status = TradeStatus.APPROVED
        
        self.audit.log_approved(
            entity_type=EntityType.INTERBANK_DEAL,
            entity_id=deal_ref,
            approver_id=approver_id
        )
```

---

# Pending Work After Phase 0

## Phase 1: Interbank Service Implementation (Sprint 3A)

| # | Task | Priority | Est. Effort | Details |
|---|------|----------|-------------|---------|
| 1.1 | Create `interbank_service.py` | 🔴 High | 1 day | Full service class: create, approve, reject, cancel, early terminate, daily accrual. Use calculation engine + state machine + audit service. |
| 1.2 | Refactor `routers/interbank.py` | 🔴 High | 0.5 day | Remove ALL inline enums, schemas, mock data. Make router thin — delegates to service. Import schemas from `schemas/transactions.py`. |
| 1.3 | Update `schemas/transactions.py` interbank schemas | 🟡 Medium | 0.5 day | Ensure schemas match the model fields exactly. Add `InterbankDealList` response. Add approval/rejection request schemas. |
| 1.4 | Interbank limit checking | 🟡 Medium | 0.5 day | Integrate with existing `LimitDefinition` model using `PLACEMENT_LIMIT` type. |
| 1.5 | Daily accrual batch job | 🟡 Medium | 0.5 day | Background task to calculate and record daily accrued interest for all active deals. |
| 1.6 | Maturity processing | 🟡 Medium | 0.5 day | Auto-detect mature deals, trigger settlement workflow. |
| 1.7 | Unit tests for interbank | 🟡 Medium | 1 day | Test service layer, calculation accuracy, state transitions, four-eyes principle. |

## Phase 2: Repo Service Implementation (Sprint 3B)

| # | Task | Priority | Est. Effort | Details |
|---|------|----------|-------------|---------|
| 2.1 | Create `repo_service.py` | 🔴 High | 1.5 days | Full service: create, approve, cancel, near/far leg settlement, early termination. Complex because of dual legs. |
| 2.2 | Create `collateral_service.py` | 🔴 High | 1 day | Collateral allocation, valuation, haircut application, margin monitoring. |
| 2.3 | Refactor `routers/repo.py` | 🔴 High | 0.5 day | Same as interbank: remove mock data, thin router, delegate to service. |
| 2.4 | Margin call workflow | 🟡 Medium | 1 day | Daily MTM → margin check → margin call generation → notification → resolution tracking. |
| 2.5 | Update `schemas/transactions.py` repo schemas | 🟡 Medium | 0.5 day | Add `RepoTradeList`, margin call request/response schemas. |
| 2.6 | BOT BRP integration stubs | 🟢 Low | 0.5 day | Prepare for BOT Bilateral Repo Program integration. |
| 2.7 | Unit tests for repo | 🟡 Medium | 1 day | Test repo + collateral calculations, margin calls, dual-leg settlement. |

## Phase 3: Cross-Cutting & Integration (Sprint 3C)

| # | Task | Priority | Est. Effort | Details |
|---|------|----------|-------------|---------|
| 3.1 | Refactor `bond_trade_service.py` | 🟡 Medium | 0.5 day | Replace inline calculations with `CalculationEngine`. Add state machine enforcement. Add audit trail calls. |
| 3.2 | EOD batch orchestrator | 🟡 Medium | 1 day | Coordinates: daily accrual (IB), MTM + margin check (repo), position rebuilds, settlement date checks. |
| 3.3 | Database migration | 🔴 High | 0.5 day | Generate and run Alembic migration for `transaction_audit_log` table. |
| 3.4 | Integration testing | 🟡 Medium | 1 day | End-to-end tests: create → approve → settle for all 3 products. |
| 3.5 | Update API documentation | 🟢 Low | 0.5 day | Regenerate OpenAPI docs, update the interactive portal. |
| 3.6 | Clean up enum duplicates | 🟡 Medium | 0.5 day | Update `models/transactions.py` and `schemas/transactions.py` to import from `core/enums.py` instead of re-defining. |

## Phase 4: Frontend Preparation (Post Sprint 3)

| # | Task | Priority | Est. Effort | Details |
|---|------|----------|-------------|---------|
| 4.1 | API response standardization | 🟡 Medium | 0.5 day | Ensure all endpoints use `PaginatedResponse` and `APIResponse` wrappers consistently. |
| 4.2 | WebSocket notifications | 🟢 Low | 1 day | Real-time notifications for pending approvals, margin calls, settlement alerts. |
| 4.3 | Frontend component design | 🟢 Low | 1 day | Design React components for deal entry, approval queue, position dashboard. |

---

## Recommended Implementation Order

```
Week 1 (Sprint 3A):
├── Day 1: Migration + Refactor bond service (3.3, 3.1)
├── Day 2: Interbank service (1.1)
├── Day 3: Interbank router refactor + schemas (1.2, 1.3)
├── Day 4: Interbank limits + accrual (1.4, 1.5)
└── Day 5: Interbank tests (1.7)

Week 2 (Sprint 3B):
├── Day 1: Repo service (2.1)
├── Day 2: Repo service continued + collateral (2.1, 2.2)
├── Day 3: Repo router refactor (2.3, 2.5)
├── Day 4: Margin call workflow (2.4)
└── Day 5: Repo tests (2.7)

Week 3 (Sprint 3C):
├── Day 1: EOD batch orchestrator (3.2)
├── Day 2: Clean up enum duplicates (3.6)
├── Day 3: Integration testing (3.4)
├── Day 4: API docs + fixes (3.5)
└── Day 5: Review, buffer, stakeholder demo
```

---

## Key Architecture Principles Enforced

1. **Routers are THIN** → Parse request → Call service → Return response
2. **Services own business logic** → Validation, calculations, workflow, audit
3. **Enums are CENTRALIZED** → Only `app/core/enums.py` defines them
4. **Calculations are SHARED** → Only `calculation_engine.py` does financial math
5. **State transitions are EXPLICIT** → `state_machine.py` defines allowed transitions
6. **Audit is MANDATORY** → Every state change must have an audit record
7. **Four-eyes principle** → Enforced in services, not routers
