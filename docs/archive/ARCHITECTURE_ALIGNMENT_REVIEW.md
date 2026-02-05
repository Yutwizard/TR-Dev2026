# Architecture to Database Alignment Review

**Date:** February 3, 2026  
**Purpose:** Identify and document alignment issues between architecture docs and database design

---

## 🎯 Critical Alignment Issues Found

### 1. Naming Convention Mismatch

| Architecture Doc | Database Design | Status |
|-----------------|-----------------|--------|
| `TradeID` | `bond_trade_id` | ❌ Mismatch |
| `PortfolioID` | `portfolio_id` | ❌ Mismatch |
| `SecurityID` | `security_id` | ❌ Mismatch |
| `RepoTradeID` | `repo_trade_id` | ❌ Mismatch |
| `CollateralID` | `collateral_id` | ❌ Mismatch |
| `UtilizationID` | `limit_id` | ❌ Mismatch |
| `PositionID` | `position_id` | ❌ Mismatch |
| `counterparty_id` | `counterparty_id` | ✅ Match |
| `entity_id` | `entity_id` | ✅ Match |

**Standard:** Database design uses `snake_case` consistently  
**Action:** Update architecture documents to use snake_case

---

### 2. Field Name Differences

| Table | Architecture | Database Design | Issue |
|-------|-------------|-----------------|-------|
| `bond_trades` | `CleanPrice` | `clean_price_trade` | Different field names |
| `bond_trades` | `AccruedInterest` | `yield_to_maturity` (calculated) | Different purpose |
| `bond_trades` | `SettlementAmount` | Not stored (calculated) | Architecture expects stored |
| `bond_trades` | `ThaiBMA_Reported` | Not in design | Missing in design |
| `bond_trades` | `ApprovedBy`, `ApprovedAt` | Not detailed | Missing details |

**Action:** Update architecture SQL to match actual database fields

---

### 3. Data Type Differences

| Field | Architecture | Database Design | Issue |
|-------|-------------|-----------------|-------|
| `limit_utilization.UtilizationID` | `BIGINT AUTO_INCREMENT` | `VARCHAR(40)` | Different type |
| `repo_trades.tenor_days` | `GENERATED ALWAYS AS` | `INT` (calculated in app) | Different approach |
| `bond_trades.Yield` | `DECIMAL(10,6)` | Not stored | Yield calculated on-the-fly |

**Action:** Align data types with database design

---

### 4. Missing Tables in Architecture

| Table | In Design | In Architecture | Status |
|-------|-----------|-----------------|--------|
| `bond_transactions` | ✅ Yes | ⚠️ Partial | Referenced but not detailed |
| `interbank_interest_schedule` | ✅ Yes | ⚠️ Partial | Child table not detailed |
| `entity_counterparty` | ✅ Yes | ⚠️ Missing | Not in architecture SQL |

**Action:** Add missing table definitions to architecture

---

### 5. Enum Value Differences

#### Status Fields

**Architecture:**
```sql
Status ENUM('CREATED', 'PENDING_APPROVAL', 'APPROVED', 'CONFIRMED', 'SETTLED', 'CANCELLED')
```

**Database Design:**
- `bond_trades.settlement_status`: 'Pending', 'Settled', 'Failed' (simpler)
- Workflow states: CREATED → PENDING_APPROVAL → APPROVED → CONFIRMED → SETTLED

**Action:** Architecture has more granular states - align or document difference

#### Limit Types

**Architecture (Already Updated):**
```sql
LimitType ENUM('SINGLE_TXN', 'PLACEMENT_LIMIT', 'REPO_LIMIT', 'TENOR', 'CONCENTRATION')
```

**Database Design:**
- `REPO_LIMIT`, `PLACEMENT_LIMIT`, `SINGLE_TXN`, `TENOR`, `CONCENTRATION`

**Status:** ✅ Already aligned (AGGREGATE removed)

---

## ✅ Correct Field Mappings (Aligned)

### bond_trades

| Architecture (Current) | Database Design | Should Be |
|----------------------|-----------------|-----------|
| `TradeID` | `bond_trade_id` | `bond_trade_id` |
| `PortfolioID` | `portfolio_id` | `portfolio_id` |
| `SecurityID` | `security_id` | `security_id` |
| `counterparty_id` | `counterparty_id` | `counterparty_id` |
| `TradeType` | `trade_type` | `trade_type` |
| `TradeDate` | `trade_date` | `trade_date` |
| `SettlementDate` | `settlement_date` | `settlement_date` |
| `NominalAmount` | `nominal_amount` | `nominal_amount` |
| `CleanPrice` | `clean_price_trade` | `clean_price_trade` |
| `Status` | `settlement_status` | `settlement_status` |

### limit_utilization

| Architecture (Current) | Database Design | Should Be |
|----------------------|-----------------|-----------|
| `UtilizationID` | `limit_id` | `limit_id` |
| `LimitID` | Same concept | `limit_id` (confusing - two IDs?) |
| `counterparty_id` | `counterparty_id` | `counterparty_id` |
| `entity_id` | `entity_id` | `entity_id` |
| `LimitType` | `limit_type` | `limit_type` |
| `LimitAmount` | `total_credit_line` | `total_credit_line` |

**Note:** Architecture has both `UtilizationID` (PK) and `LimitID` (logical), but database only has `limit_id`. This needs clarification.

---

## 🔧 Required Updates

### High Priority (Must Fix)

1. **Naming Convention**: Update all architecture SQL to use `snake_case`
2. **Field Names**: Align `clean_price_trade`, remove `SettlementAmount` if calculated
3. **Data Types**: Fix `limit_id` type from BIGINT to VARCHAR(40)
4. **Missing Tables**: Add `entity_counterparty`, complete `bond_transactions`

### Medium Priority (Should Fix)

5. **Status Enums**: Align workflow states or document differences
6. **ThaiBMA Fields**: Add reporting fields if needed
7. **Audit Fields**: Clarify `created_at`, `updated_at` vs `CreatedAt`, `UpdatedAt`

### Low Priority (Nice to Have)

8. **Generated Columns**: Decide on `tenor_days` approach (DB calculated vs app calculated)
9. **Yield Storage**: Decide if yield should be stored or calculated

---

## 📋 Recommended SQL Template (Aligned)

```sql
-- Aligned bond_trades (matching database design)
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
    yield_to_maturity DECIMAL(10,6),  -- Calculated, nullable
    settlement_status VARCHAR(20),  -- 'Pending', 'Settled', 'Failed'
    trader_id VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- ThaiBMA reporting tracked separately or in bond_transactions
);

-- Aligned limit_utilization (matching database design)
CREATE TABLE limit_utilization (
    limit_id VARCHAR(40) PRIMARY KEY,  -- Single ID, not UtilizationID + LimitID
    counterparty_id VARCHAR(40) REFERENCES counterparty_master(counterparty_id),
    entity_id VARCHAR(40) REFERENCES entity_master(entity_id),
    limit_type VARCHAR(20),  -- 'PLACEMENT_LIMIT', 'REPO_LIMIT', etc.
    currency CHAR(3) DEFAULT 'THB',
    available_line DECIMAL(20,2),
    total_credit_line DECIMAL(20,2),
    utilization_amount DECIMAL(20,2),
    credit_line_approve_date DATE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_date DATE,
    -- Immutable: append-only
);
```

---

## ✅ Alignment Status Summary

| Document | Alignment Status | Priority |
|----------|-----------------|----------|
| `Data_to_Architecture_Mapping_and_Development_Guide.md` | ⚠️ Needs Update | High |
| `Treasury_System_Architecture_and_Implementation_Guide.md` | ⚠️ Needs Review | Medium |
| `Treasury_System_Detailed_Design_Input.md` | ✅ Current/Authoritative | - |
| `Field_Update_Matrix.md` | ✅ Aligned with Design | - |
| `TRANSACTION_PROCESS_GUIDE.md` | ✅ Aligned with Design | - |

**Note:** `Treasury_System_Detailed_Design_Input.md` should be considered the authoritative source as it's based on the actual Excel data file.

---

## 🎯 Next Steps

1. Update `Data_to_Architecture_Mapping_and_Development_Guide.md` SQL examples
2. Remove or deprecate `UtilizationID` concept (use only `limit_id`)
3. Standardize on `snake_case` throughout architecture docs
4. Add missing table definitions
5. Review and align status enums

---

**Review Completed:** February 3, 2026  
**Authoritative Source:** `Treasury_System_Detailed_Design_Input.md` (based on Treasury_System_Database_V2_Internal.xlsx)
