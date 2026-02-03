# Treasury System - Detailed Design Input by Team

**Document Purpose:** Comprehensive reference for design inputs required from each team, field mappings, and data update responsibilities.

**Source:** `\data\source\Treasury_System_Database_V2_Internal.xlsx` (Extracted to `\data\extracted\`)

**Status:** Review Draft  
**Last Updated:** February 3, 2026  
**Next Review:** [To be scheduled]

---

## Table of Contents

1. [Team Responsibilities Overview](#1-team-responsibilities-overview)
2. [Front Office (Trading Team)](#2-front-office-trading-team)
3. [Middle Office (Risk & Compliance)](#3-middle-office-risk--compliance)
4. [Back Office (Settlement, Operations & Accounting)](#4-back-office-settlement-operations--accounting)
5. [IT Admin Team](#5-it-admin-team)
6. [Transaction Lifecycle - Fields by Stage](#6-transaction-lifecycle---fields-by-stage)
7. [Market Data Management](#7-market-data-management)
8. [Data Update Frequency](#8-data-update-frequency)
9. [Reference Data Tables](#9-reference-data-tables)
10. [Appendix A: Actual Database Table Structures](#appendix-a-actual-database-table-structures)
11. [Appendix B: Field Mapping Quick Reference](#appendix-b-field-mapping-quick-reference)

---

## 1. Team Responsibilities Overview

| Team | Primary Functions | Key Tables | Data Nature |
|------|-------------------|------------|-------------|
| **Front Office** | Trade capture, pricing, execution | `bond_trades`, `interbank_deals`, `repo_trades` | Event-driven |
| **Middle Office** | Limit checking, risk monitoring, ECL | `limit_utilization`, `margin_calls`, `bond_positions` | Control/Derived |
| **Back Office** | Settlement, collateral, master data, accounting, **daily ThaiBMA price updates** | `collateral_positions`, `cash_margin_movements`, `position_costing`, `security_master`, `counterparty_master` | Transaction/Master |
| **IT Admin** | User management, reference data, security master, portfolio setup | `users`, `roles`, `reference_data` | Configuration |

**Note on IT Admin Access:** IT Admin has special permissions to manage ALL tables for system maintenance and emergency fixes, but generally should not make routine data changes.

---

## 2. Front Office (Trading Team)

### 2.1 Trade Capture Requirements

| Input Field | Description | Validation Rules | Table |
|-------------|-------------|------------------|-------|
| `bond_trade_id` | Unique identifier | Auto-generated | `bond_trades` |
| `security_id` | Trading symbol (ThaiBMA) | Must exist in `security_master` | `bond_trades` |
| `counterparty_id` | Counterparty reference | KYC status must be 'APPROVED' | `bond_trades` |
| `portfolio_id` | Book assignment | Must exist in `portfolio_master` | `bond_trades` |
| `trade_type` | Buy or Sell | Enum validation | `bond_trades` |
| `trade_date` | Transaction date | Must be business day | `bond_trades` |
| `settlement_date` | T+2 settlement | Auto-calculated, editable with override | `bond_trades` |
| `nominal_amount` | Face value | > 0, multiple of 1,000 | `bond_trades` |
| `clean_price_trade` | Percentage price | ±10% from last price (warning) | `bond_trades` |
| `trader_id` | Executing trader | Must be active user | `bond_trades` |

### 2.2 Interbank Deal Capture

| Input Field | Description | Validation Rules | Table |
|-------------|-------------|------------------|-------|
| `deal_id` | Unique deal ID | Auto-generated | `interbank_deals` |
| `deal_type` | Lend or Borrow | Enum validation | `interbank_deals` |
| `principal_amount` | Notional amount | > 0 | `interbank_deals` |
| `interest_rate` | All-in rate | > 0 | `interbank_deals` |
| `interest_rate_type` | Fixed or Floating | Determines schedule generation | `interbank_deals` |
| `reference_rate` | THOR for floating | Auto-populated if FLOATING | `interbank_deals` |
| `margin` | Spread in percentage | Decimal, can be negative | `interbank_deals` |
| `value_date` | Start date | >= Trade date | `interbank_deals` |
| `maturity_date` | End date | > value_date | `interbank_deals` |

### 2.3 Repo/Reverse Repo Capture

| Input Field | Description | Validation Rules | Table |
|-------------|-------------|------------------|-------|
| `repo_trade_id` | Unique repo ID | Auto-generated | `repo_trades` |
| `trade_type` | Repo, ReverseRepo, or Rehypothecation | Bank's perspective | `repo_trades` |
| `nominal_amount` | Face value of securities | > 0 | `repo_trades` |
| `interest_rate` | Annual repo rate | > 0 | `repo_trades` |
| `interest_rate_type` | Fixed or Floating | Enum validation | `repo_trades` |
| `purchase_price` | Cash received/paid on day 1 | Calculated | `repo_trades` |
| `repurchase_price` | Cash paid/received on day 2 | Calculated | `repo_trades` |
| `open_repo_flag` | Open/term indicator | Boolean | `repo_trades` |
| `maturity_date` | For term repos | Nullable if open | `repo_trades` |

### 2.4 Trader UI Requirements

- **Trade Entry Form:** Real-time validation, price/yield conversion
- **Trade Blotter:** Filter by date, status, counterparty, portfolio
- **Pending Approvals:** View trades requiring four-eyes approval
- **Position View:** Current holdings by portfolio
- **ThaiBMA Reporting Status:** Countdown timer for 30-minute deadline

---

## 3. Middle Office (Risk & Compliance)

### 3.1 Limit Management

#### Limit Types to Configure:

| Limit Type | Description | Check Timing | Table |
|------------|-------------|--------------|-------|
| `SINGLE_TXN` | Maximum single transaction | Pre-trade | `limit_utilization` |
| `AGGREGATE` | Total exposure per counterparty | Pre-trade + daily | `limit_utilization` |
| `TENOR` | Maximum maturity allowed | Pre-trade | `limit_utilization` |
| `CONCENTRATION` | Sector/issuer limits | Daily monitoring | `limit_utilization` |
| `REPO_LIMIT` | Repo-specific limits | Pre-trade | `limit_utilization` |
| `PLACEMENT_LIMIT` | Interbank placement limits | Pre-trade | `limit_utilization` |

#### Limit Utilization Record Structure (from Excel):

```
limit_utilization table:
- limit_id (PK) - Unique identifier
- counterparty_id (FK → counterparty_master)
- limit_type - REPO_LIMIT, PLACEMENT_LIMIT, etc.
- currency - ISO 4217 currency code
- available_line - Available credit line before event
- total_credit_line - Total approved credit line
- utilization_amount - Amount consumed (+) or released (-)
- credit_line_approve_date - วันที่อนุมัติวงเงิน
- timestamp - Event timestamp (GMT+7)
- created_date - Day-1 creation date
- entity_id (FK → entity_master)
```

#### Alert Thresholds:

| Utilization | Action | Notification |
|-------------|--------|--------------|
| 80% | Warning (Amber) | Dashboard + Email |
| 90% | High Warning | Dashboard + Email + SMS |
| 100% | Hard Block | Trade rejected |
| >100% | Critical (Red) | Immediate escalation |

### 3.2 TFRS 9 / ECL Management

#### ECL Stage Determination:

| Stage | Trigger | ECL Measurement | Update Frequency |
|-------|---------|-----------------|------------------|
| **Stage 1** | No significant deterioration | 12-month ECL | Monthly |
| **Stage 2** | Significant credit deterioration | Lifetime ECL | On trigger |
| **Stage 3** | Credit-impaired (objective evidence) | Lifetime ECL | On trigger |

#### ECL Input Parameters:

| Parameter | Source | Update Frequency | Field |
|-----------|--------|------------------|-------|
| PD (Probability of Default) | Internal model / Rating | Monthly | Calculated |
| LGD (Loss Given Default) | Historical data | Annual | Calculated |
| EAD (Exposure at Default) | Position amount | Daily | `bond_positions` |
| Macroeconomic factors | GDP, unemployment | Quarterly | External feed |

#### Portfolio Classification (from Excel):

| Accounting Treatment | Description | Business Model |
|---------------------|-------------|----------------|
| `AMC` (Amortized Cost) | Hold-to-Collect | Long-term holding |
| `FVOCI` | Hold-to-Collect-and-Sell | Strategic selling |
| `FVTPL` | Trading | Active trading |

### 3.3 Margin Management

#### Daily Margin Calculation:

| Field | Description | Calculation | Table |
|-------|-------------|-------------|-------|
| `call_type` | CALL, RETURN, or NONE | Based on exposure vs collateral | `margin_calls` |
| `call_amount` | Final margin amount after MTA/threshold | Absolute value | `margin_calls` |
| `due_time` | Contractual deadline | Per GMRA/CSA terms | `margin_calls` |
| `status` | Pending, Agreed, Settled, Cancelled | Workflow status | `margin_calls` |

#### Margin Call Workflow:

```
Status: Pending → Agreed → Settled
           ↓
        Cancelled (exception)
```

---

## 4. Back Office (Settlement, Operations & Accounting)

### 4.1 Settlement Processing

#### Bond Trade Settlement:

| Settlement System | Security Type | DVP Model | Cutoff Time |
|-------------------|---------------|-----------|-------------|
| **TSD** | Corporate bonds | Model 1 (gross, trade-by-trade) | 14:00 same-day |
| **BAHTNET** | Government bonds | RTGS | Real-time |

#### Settlement Status Workflow:

| Status | Description | Updated By | Next Action |
|--------|-------------|------------|-------------|
| `Pending` | Awaiting settlement | System | Monitor |
| `Settled` | Settlement complete | Back Office / Interface | Archive |
| `Failed` | Settlement failed | System | Exception handling |

#### Settlement Fields to Update:

| Field | Description | Updated When | Table |
|-------|-------------|--------------|-------|
| `settlement_status` | Current status | On status change | `bond_trades`, `interbank_deals`, `repo_trades` |
| `confirmation_ref` | ISO 20022 confirmation ref | On confirmation | `interbank_deals` |

### 4.2 Collateral Management

#### Collateral Allocation (from Excel):

| Field | Description | Validation | Table |
|-------|-------------|------------|-------|
| `collateral_id` | Unique allocation ID | Auto-generated | `collateral_positions` |
| `repo_trade_id` | Parent repo | FK validation | `collateral_positions` |
| `security_id` | Collateral security | FK → security_master | `collateral_positions` |
| `nominal_amount` | Face value pledged | > 0 | `collateral_positions` |
| `valuation_price` | Clean price at MTM | From ThaiBMA | `collateral_positions` |
| `market_value` | Nominal × Price + Accrued | Calculated | `collateral_positions` |
| `haircut_percentage` | GMRA/CRM haircut | From haircut_table | `collateral_positions` |
| `collateral_value_after_haircut` | Final margin value | Calculated | `collateral_positions` |
| `allocation_date` | When allocated | Date | `collateral_positions` |
| `margin_call_id` | Link if from margin call | FK → margin_calls | `collateral_positions` |

#### Collateral Substitution Workflow:

1. **Initiate:** Request to substitute collateral
2. **Validate:** New collateral meets margin requirements
3. **Allocate:** Add new collateral position
4. **Release:** Mark old collateral as released
5. **Update:** Recalculate margin values

### 4.3 Cash Margin Movements (from Excel)

| Field | Description | Movement Type | Table |
|-------|-------------|---------------|-------|
| `cash_margin_movement_id` | Unique ID | - | `cash_margin_movements` |
| `margin_call_id` | Related margin call | FK | `cash_margin_movements` |
| `repo_trade_id` | Underlying repo | FK | `cash_margin_movements` |
| `movement_type` | PAY or RECEIVE | From bank's perspective | `cash_margin_movements` |
| `amount` | Signed cash amount | Positive = receive, Negative = pay | `cash_margin_movements` |
| `outstanding_balance` | Running net balance | Cumulative SUM(amount) | `cash_margin_movements` |
| `value_date` | Settlement date | Business day | `cash_margin_movements` |
| `daily_accrued_int_receivable` | Interest for this day | On posted margin | `cash_margin_movements` |
| `accrued_int_receivable` | Cumulative interest | Rolling sum | `cash_margin_movements` |
| `interest_on_margin_rate` | GMRA interest rate | Annual rate | `cash_margin_movements` |

### 4.4 Master Data Maintenance

#### Counterparty Master Updates:

| Event | Fields to Update | Approved By | Tables |
|-------|------------------|-------------|--------|
| **New Counterparty** | All fields | Credit Risk | `entity_master`, `counterparty_master`, `entity_counterparty` |
| **KYC Renewal** | Status update | Compliance | `counterparty_master` |
| **Limit Change** | `total_credit_line` | Credit Committee | `limit_utilization` |
| **Rating Update** | `primary_credit_rating`, `rating_tris`, `rating_fitch` | Credit Risk | `counterparty_master`, `security_master` |

#### Security Master Updates (Co-managed with IT Admin):

| Event | Fields to Update | Source | Responsible | Frequency |
|-------|------------------|--------|-------------|-----------|
| **New Security Setup** | `security_id`, `isin`, `issuer_id`, `unique_id`, `instrument_type`, `issue_date`, `maturity_date`, `coupon_rate`, `coupon_frequency`, `day_count_conv` | ThaiBMA / Prospectus | **IT Admin** | On new issue |
| **Daily Price Update** | `clean_price`, `market_rate`, `accrued_interest_%` | ThaiBMA EOD file | **Back Office** | **Daily (Working Day)** |
| **Rating Changes** | `rating_tris`, `rating_fitch` | TRIS/Fitch feeds | **Back Office** | On rating change |
| **Maturity Processing** | `status` | Calendar | **Back Office** | On maturity |
| **Status Updates** | `is_eligible_bot_repo_collateral`, `is_eligible_crm_collateral` | Policy changes | **Back Office** | As needed |

#### Back Office Daily Price Update Procedure:

**Step 1: Download (17:00)**
- Log into ThaiBMA portal (https://www.thaibma.or.th)
- Download EOD price file (MTM data)
- Filename format: `THAIBMA_MTM_YYYYMMDD.csv`

**Step 2: Validate (17:15)**
- Check all active securities have prices
- Validate price movements (±5% threshold)
- Check for missing or zero prices

**Step 3: Import (17:30)**
- Import via "Market Data Upload" function
- System validates and updates `security_master`
- Log any exceptions for manual review

**Step 4: Trigger Batch (18:00)**
- Accrued interest calculation starts automatically
- System calculates for all positions: `Nominal × Coupon% × 1/365`

**Step 5: Verify (18:30)**
- Check `bond_positions.accrued_interest` updated
- Verify `bond_positions.market_value` recalculated
- Review exception reports

#### Portfolio Master Updates (IT Admin Responsibility):

| Field | Description | Configuration Notes |
|-------|-------------|---------------------|
| `portfolio_id` | Unique identifier | System-generated |
| `portfolio_name` | Display name | AMC - Govt Bonds, FVOCI - Corp, etc. |
| `portfolio_manager` | Responsible person | Trader name |
| `accounting_treatment` | AMC, FVOCI, FVTPL | Drives accounting treatment |
| `created_timestamp` | Creation time | Auto |

**Note:** Portfolio changes require Treasury/Accounting approval before IT Admin implements.

### 4.5 Position Costing & Accounting (from Excel)

#### Weighted Average Cost (WAC) Calculation:

| Field | Description | Calculation | Table |
|-------|-------------|-------------|-------|
| `cost_method` | WAC, FIFO, LIFO | Configuration | `position_costing` |
| `avg_book_price_pct` | Running weighted-avg clean price % | Changes only on new buys | `position_costing` |
| `sum_product_clean` | Σ(clean% × nominal) for WAC audit | Calculated | `position_costing` |
| `total_nominal_in` | Σ buys/transfers-in nominal | Running total | `position_costing` |
| `cumulative_sold_nominal` | Σ nominal sold so far | Running total | `position_costing` |
| `realized_gain_loss_to_date` | Cumulative realized P&L | Calculated | `position_costing` |

#### Realized P&L Formula:

```
realized_gainloss = (sell_clean_price_pct - avg_book_price_pct) × sold_nominal
```

#### Realization Event Record (from Excel):

| Field | Description | Source | Table |
|-------|-------------|--------|-------|
| `realization_id` | Row ID | Auto | `position_realization_events` |
| `position_id` | Source position | FK | `position_realization_events` |
| `trade_id` | Triggering trade | FK | `position_realization_events` |
| `event_date` | Sale/transfer date | Trade date | `position_realization_events` |
| `sold_nominal` | Quantity sold | Trade nominal | `position_realization_events` |
| `sell_clean_price_pct` | Trade clean price | Trade price | `position_realization_events` |
| `avg_book_price_pct` | WAC at sale | From costing | `position_realization_events` |
| `realized_gainloss` | Clean price P&L | Calculated | `position_realization_events` |
| `accrued_int_realized` | Coupon interest received | Cash received | `position_realization_events` |
| `method_used` | WAC/FIFO/LIFO | At time of calc | `position_realization_events` |

**Note:** `position_realization_events` is IMMUTABLE - never updated or deleted.

### 4.6 Bond Position Accounting (from Excel)

| Field | Description | Calculation | Update Frequency | Table |
|-------|-------------|-------------|------------------|-------|
| `nominal_amount` | Current outstanding face | Net Buy & Sell | Real-time | `bond_positions` |
| `unencumbrance` | Free (not pledged) | Σ Buy - Σ Sell - Σ Repo | Daily | `bond_positions` |
| `encumbrance` | Pledged as collateral | Σ Repo | Daily | `bond_positions` |
| `unenc_from_reverse_repo` | From Reverse Repo unencumbered | Σ ReverseRepo - Σ Rehypothecation | Daily | `bond_positions` |
| `rehypothecation` | Re-pledged securities | Σ Rehypothecation | Daily | `bond_positions` |
| `avg_book_clean_price_pct` | WAC for remaining position | Changes only on buys | On trade | `bond_positions` |
| `book_value` | Carrying amount at amortized cost | Clean Price × Nominal ÷ 100 | Daily | `bond_positions` |
| `accrued_interest` | Accrued coupon interest | Nominal × Coupon% × Days/365 | **Daily (System Batch)** | `bond_positions` |
| `market_value` | (Price% × Nominal/100) + Accrued | Calculated | **Daily (System Batch)** | `bond_positions` |
| `realized_gain_loss` | Realized P&L from sales | Calculated | On sale | `bond_positions` |
| `unrealized_gain_loss` | MTM P&L on remaining amount | MarketValue - BookValue | **Daily** | `bond_positions` |

#### Daily Accrued Interest Process:

**System Calculation (18:00 Daily Batch):**
```
For each active bond position:
    Daily Accrual = NominalAmount × CouponRate% × (1/365)
    AccruedInterest = AccruedInterest + DailyAccrual
    
On Coupon Payment Date:
    AccruedInterest = 0 (reset)
    Create Coupon transaction in bond_transactions
```

**Back Office Daily Responsibilities:**
1. **Import ThaiBMA prices** (17:00) - Required input for valuation
2. **Verify batch completion** (18:30) - Check accrued interest calculated
3. **Review exceptions** (19:00) - Handle any calculation errors
4. **Confirm GL posting** (19:30) - Journal entries for accruals

### 4.7 EOD Batch Jobs (Back Office Monitored):

| Job | Schedule | Tables Updated | Duration Target |
|-----|----------|----------------|-----------------|
| **Position Build** | 18:00 | `bond_positions` | < 30 minutes |
| **Costing Update** | After each trade | `position_costing` | < 5 minutes |
| **Accrual Calculation** | 18:30 | Journal entries | < 15 minutes |
| **MTM Valuation** | 19:00 | `bond_positions` | < 15 minutes |
| **ECL Calculation** | Monthly, 20:00 | `bond_positions` | < 1 hour |
| **Journal Generation** | 19:30 | GL interface | < 15 minutes |
| **ThaiBMA Reporting** | Every 5 min | `bond_trades` | < 1 minute |
| **Margin Calculation** | 17:00 | `margin_calls` | < 30 minutes |

---

## 5. IT Admin Team

### 5.1 User Management

#### User Table Structure:

| Field | Description | Validation | Table |
|-------|-------------|------------|-------|
| `user_id` | Unique ID | Auto-generated | `users` |
| `username` | Login name | Unique, 6-20 chars | `users` |
| `email` | Email address | Valid format | `users` |
| `role` | System role | Enum | `users` |
| `department` | Department | Free text | `users` |
| `is_active` | Active flag | Boolean | `users` |
| `created_at` | Creation timestamp | Auto | `users` |

#### Role Definitions:

| Role | Permissions | Approval Authority |
|------|-------------|-------------------|
| `FRONT_OFFICE` | Trade capture, view positions | Self (up to limit) |
| `MIDDLE_OFFICE` | Limit admin, risk reports, approve trades | Four-eyes approval |
| `BACK_OFFICE` | Settlement, collateral, master data, accounting | Settlement confirmation |
| `IT_ADMIN` | User management, reference data, security master, portfolio setup | System configuration |
| `READ_ONLY` | View only | - |

#### Password Policy:

| Requirement | Value |
|-------------|-------|
| Minimum length | 12 characters |
| Complexity | Upper, lower, number, special char |
| Expiry | 90 days |
| History | Last 5 passwords cannot be reused |
| Lockout | 5 failed attempts = 30 min lockout |
| Session timeout | 30 minutes idle |

### 5.2 Reference Data Management (IT Admin Responsibility)

| Data Type | Purpose | Update Frequency | Source |
|-----------|---------|------------------|--------|
| **BANK_CODE** | BOT official bank codes | When BOT updates | BOT website |
| **Haircut Table** | BOT standard haircuts | When BOT updates | BOT notification |
| **Involved_Party_Type** | BOT institution types | When BOT updates | BOT reference |
| **Customer_type_master** | Internal classification | When policy changes | Internal policy |
| **Holiday Calendar** | Business day calculation | Annual | BOT holidays |
| **Stage_master** | TFRS 9 stage definitions | Rarely | Accounting policy |
| **Govt_agency_code** | Government agency codes | When updates | BOT reference |
| **Resident_definition** | MFSMCG residency rules | Rarely | BOT guidelines |

### 5.3 Security Master Management (IT Admin - Initial Setup)

#### IT Admin Setup Responsibilities:

| Event | Fields to Configure | Source |
|-------|---------------------|--------|
| **New Security Setup** | `security_id`, `isin`, `issuer_id`, `unique_id`, `instrument_type`, `issue_date`, `maturity_date`, `coupon_rate`, `coupon_frequency`, `coupon_day_count_conv`, `currency`, `country`, `bond_structure`, `coupon_rate_type` | ThaiBMA / Prospectus |
| **System Flags** | `is_eligible_bot_repo_collateral`, `is_eligible_crm_collateral` | Policy |

#### Back Office Updates (Day-to-Day):

| Event | Fields to Update |
|-------|------------------|
| **Rating Changes** | `rating_tris`, `rating_fitch` |
| **Price Updates** | Market data (auto from ThaiBMA) |
| **Maturity Processing** | `status` |
| **Status Updates** | `cross_default` |

### 5.4 Portfolio Setup (IT Admin Responsibility)

#### Portfolio Master Configuration (from Excel):

| Field | Description | Configuration |
|-------|-------------|---------------|
| `portfolio_id` | Unique identifier | System-generated |
| `portfolio_name` | Display name | AMC - Govt Bonds, FVOCI - Corp, Trading |
| `portfolio_manager` | Responsible manager | Trader/Desk name |
| `accounting_treatment` | AMC, FVOCI, FVTPL | Treasury/Accounting approved |
| `created_timestamp` | Creation time | Auto |

**Note:** Portfolio changes require Treasury/Accounting approval before IT Admin implements.

### 5.5 Special Access Rights

#### IT Admin Super User Access:

| Access Type | Scope | Usage Guidelines |
|-------------|-------|------------------|
| **Read Access** | All tables | For troubleshooting, reporting |
| **Write Access** | All tables | Emergency fixes only - requires approval |
| **Schema Changes** | Database structure | Change management process required |
| **User Management** | `users`, `roles`, `permissions` | Standard responsibility |

#### Emergency Change Procedure:

1. **Request:** Documented request from department head
2. **Approval:** IT Manager + Business Owner approval
3. **Execution:** IT Admin makes change
4. **Audit:** Log all changes in change log
5. **Verification:** Business confirms fix
6. **Review:** Post-incident review if needed

**General Rule:** IT Admin CAN manage all tables but SHOULD NOT make routine data changes - these should be done by respective business teams.

---

## 6. Transaction Lifecycle - Fields by Stage

### 6.1 Bond Trade Lifecycle

```
CREATED → PENDING_APPROVAL → APPROVED → CONFIRMED → SETTLED
   ↓           ↓              ↓           ↓
CANCELLED   REJECTED       REJECTED    FAILED
```

#### Stage 1: Trade Entry (Front Office)

| Action | Fields Updated | System Actions |
|--------|----------------|----------------|
| Create trade | `bond_trade_id`, `security_id`, `portfolio_id`, `counterparty_id`, `trade_type`, `trade_date`, `settlement_date`, `nominal_amount`, `clean_price_trade`, `trader_id`, `settlement_status='Pending'` | Calculate `yield_to_maturity` |

#### Stage 2: Validation & Limit Check (System)

| Action | Fields Updated | System Actions |
|--------|----------------|----------------|
| Validate | - | Check business day, T+2, price range, KYC |
| Limit check | New record in `limit_utilization` | Check available line |

#### Stage 3: Approval (Middle Office)

| Action | Fields Updated | By Whom |
|--------|----------------|---------|
| Approve | Proceed to settlement | Middle Office |
| Reject | `settlement_status='Failed'`, rollback limit | Middle Office |

#### Stage 4: ThaiBMA Reporting (System)

| Action | Fields Updated | Timing |
|--------|----------------|--------|
| Report to ThaiBMA | Trade reported | Within 30 minutes |
| Alert monitoring | - | Amber at 20 min, Red at 28 min |

#### Stage 5: Settlement (Back Office)

| Action | Fields Updated | By Whom |
|--------|----------------|---------|
| Settlement confirmation | `settlement_status='Settled'` | Back Office |
| Failed settlement | `settlement_status='Failed'` | System |

#### Stage 6: Daily Accrued Interest & Position Update (System - EOD Batch)

| Action | Fields Updated | Trigger | Table |
|--------|----------------|---------|-------|
| Import ThaiBMA prices | `clean_price`, `market_rate` | Back Office input (17:00) | `security_master` |
| Calculate accrued interest | `accrued_interest` += DailyAccrual | Daily batch (18:00) | `bond_positions` |
| Update market value | `market_value` | Daily batch (19:00) | `bond_positions` |
| Update costing | `total_nominal_in`, `sum_product_clean`, `avg_book_price_pct` | On trade | `position_costing` |
| Realized P&L (sell) | New record | On sale | `position_realization_events` |

**Daily Batch Schedule:**
```
17:00 - Back Office imports ThaiBMA EOD prices
18:00 - System calculates accrued interest for all positions
19:00 - System updates market values
19:30 - GL journal entries generated for accruals
```

---

### 6.2 Interbank Deal Lifecycle

```
CREATED → APPROVED → SETTLED → ACTIVE → MATURED
   ↓         ↓          ↓
CANCELLED REJECTED   FAILED
```

#### Stage 1: Deal Entry (Front Office)

| Action | Fields Updated | System Actions |
|--------|----------------|----------------|
| Create deal | `deal_id`, `deal_type`, `counterparty_id`, `principal_amount`, `interest_rate`, `interest_rate_type`, `value_date`, `maturity_date`, `term`, `status='Active'` | Calculate tenor |

#### Stage 2: Floating Rate Schedule (if applicable)

| Action | Fields Updated | Table |
|--------|----------------|-------|
| Generate schedule | `reference_rate`, `margin`, `reset_rate`, `interest_rate` | `interbank_interest_schedule` |

#### Stage 3: Daily Accrual (System)

| Action | Fields Updated | Frequency |
|--------|----------------|-----------|
| Calculate accrual | `accrued_interest` | Daily |
| Reprice (floating) | `reset_rate`, `interest_rate` | Per reset period |

#### Stage 4: Maturity (System)

| Action | Fields Updated | Table |
|--------|----------------|-------|
| Mark matured | `status='Matured'` | `interbank_deals` |
| Release limit | New record | `limit_utilization` |
| Final interest | Journal entry | - |

---

### 6.3 Repo Trade Lifecycle

```
CREATED → COLLATERAL_ALLOCATED → SETTLED → OPEN → [Daily MTM] → REPAID → CLOSED
   ↓                              ↓          ↓
CANCELLED                      FAILED    MARGIN_CALL (if needed)
                                     ↓
                                  SUBSTITUTION
```

#### Stage 1: Trade Entry (Front Office)

| Action | Fields Updated | System Actions |
|--------|----------------|----------------|
| Create repo | `repo_trade_id`, `trade_type`, `counterparty_id`, `nominal_amount`, `interest_rate`, `purchase_date`, `repurchase_date`, `status='Active'` | Calculate `purchase_price`, `repurchase_price` |

#### Stage 2: Collateral Allocation (Back Office)

| Action | Fields Updated | Table |
|--------|----------------|-------|
| Allocate collateral | `collateral_id`, `security_id`, `nominal_amount`, `allocation_date`, `haircut_percentage`, `collateral_value_after_haircut` | `collateral_positions` |
| Validate | - | Check collateral_value_after_haircut >= requirement |

#### Stage 3: Settlement (Back Office)

| Action | Fields Updated | System Actions |
|--------|----------------|----------------|
| Settle | `status='Active'` | Cash movement |

#### Stage 4: Daily Margin Management (System)

| Action | Fields Updated | Frequency |
|--------|----------------|-----------|
| Update MTM | `market_value`, `collateral_value_after_haircut` | Daily (from ThaiBMA) |
| Calculate exposure | `margin_calls` record | Daily |
| Generate margin call | `call_amount`, `call_type`, `status='Pending'` | If threshold breached |

#### Stage 5: Maturity/Close (Back Office)

| Action | Fields Updated | System Actions |
|--------|----------------|----------------|
| Repayment | `status='Matured'` | Cash movement |
| Release collateral | Collateral released | `collateral_positions` |
| Final interest | Journal entries | Accrued repo interest |

---

## 7. Market Data Management

### 7.1 ThaiBMA Price Feeds & Daily Accrued Interest Process

**Critical Daily Process (Working Days Only):**

| Step | Process | Responsible | System Action | Timing |
|------|---------|-------------|---------------|--------|
| **1** | **Import ThaiBMA Prices** | Back Office | Download/Import ThaiBMA EOD prices | 17:00 - 18:00 |
| **2** | **Update Security Master** | Back Office | Update `security_master` with latest prices | 18:00 |
| **3** | **Calculate Accrued Interest** | System (Batch) | Calculate daily accrued interest for all positions | 18:30 |
| **4** | **Update Positions** | System (Batch) | Update `bond_positions.accrued_interest`, `market_value` | 19:00 |
| **5** | **Update Collateral** | System (Batch) | Update `collateral_positions.market_value` | 19:00 |

#### Price Input from ThaiBMA (Back Office Daily Task):

| Data Element | Frequency | Input Method | Tables Updated | Responsible |
|--------------|-----------|--------------|----------------|-------------|
| **Bond Prices (Clean)** | Daily EOD | Manual upload/import from ThaiBMA file/API | `security_master` (price fields) | **Back Office** |
| **Accrued Interest %** | Daily EOD | From ThaiBMA MTM data | `bond_positions.accrued_interest` | **System (calculated)** |
| **THOR Rate** | Daily | From ThaiBMA | `interbank_interest_schedule` | **System (auto)** |
| **Yield/Market Rate** | Daily EOD | From ThaiBMA | `bond_positions.market_rate` | **Back Office** |

#### Back Office Daily Checklist (Working Days):

```
□ 17:00 - Download ThaiBMA EOD price file from ThaiBMA portal
□ 17:15 - Validate price file completeness (all active securities)
□ 17:30 - Import prices into security_master
□ 17:45 - Verify price reasonableness (±5% threshold check)
□ 18:00 - Trigger EOD batch jobs
□ 18:30 - Verify accrued interest calculations completed
□ 19:00 - Verify position valuations updated correctly
□ 19:15 - Review exception reports (stale prices, missing data)
```

#### Accrued Interest Calculation (System Batch):

| Field | Calculation Method | Update Frequency | Table |
|-------|-------------------|------------------|-------|
| `accrued_interest` | Nominal × Coupon% × Days/365 | **Daily** | `bond_positions` |
| `accrued_interest` | Principal × Rate% × Days/365 | **Daily** | `interbank_deals` |
| `accrued_interest` | Cash × RepoRate% × Days/365 | **Daily** | `repo_trades` |
| `daily_accrued_int_receivable` | Balance × MarginRate × 1/365 | **Daily** | `cash_margin_movements` |

**Day Count Conventions:**
- **ACT/365**: Actual days divided by 365 (most common)
- **30/360**: 30-day month, 360-day year (for specific bonds)
- **ACT/ACT**: Actual days divided by actual year days

### 7.2 Price Validation Rules

| Check | Threshold | Action |
|-------|-----------|--------|
| Stale price | > 1 day old | Warning |
| Price movement | ±5% from previous day | Alert |
| Price movement | ±10% from previous day | Require override |
| Missing price | Any | Use last available + alert |

### 7.3 Haircut Matrix (BOT Standard)

#### Haircut Percentages:

| Collateral Type | 0-5 Years | 5-10 Years | 10-20 Years | >20 Years |
|-----------------|-----------|------------|-------------|-----------|
| **T-Bills, Gov Bonds, BOT Bonds** | 1.0% | 1.5% | 2.5% | 3.0% |
| **SOE (Gov Guaranteed)** | 1.5% | 3.0% | 4.5% | 5.5% |
| **Corporate AAA** | 5.0% | 10.0% | 15.0% | 20.0% |
| **Corporate AA** | 10.0% | 15.0% | 20.0% | 25.0% |

#### Variation Margin Percentages:

| Collateral Type | 0-5 Years | 5-10 Years | 10-20 Years | >20 Years |
|-----------------|-----------|------------|-------------|-----------|
| **T-Bills, Gov Bonds, BOT Bonds** | 0.75% | 1.0% | 2.0% | 2.0% |
| **SOE (Gov Guaranteed)** | 1.0% | 2.0% | 3.0% | 3.0% |

### 7.4 Credit Rating Updates

| Rating Agency | Frequency | Source | Tables Updated |
|---------------|-----------|--------|----------------|
| **TRIS Rating** | On change | TRIS website/API | `security_master.rating_tris` |
| **Fitch** | On change | Fitch feed | `security_master.rating_fitch` |

---

## 8. Data Update Frequency

### 8.1 Real-Time Updates (Event-Driven)

| Table/Event | Trigger | Performance Target |
|-------------|---------|-------------------|
| `bond_trades` | Trade capture | < 500ms response |
| `interbank_deals` | Deal capture | < 500ms response |
| `repo_trades` | Repo capture | < 500ms response |
| `limit_utilization` | Pre-trade check | < 100ms |
| `collateral_positions` | Allocation | < 500ms |

### 8.2 Daily Batch Updates (Working Days)

| Job | Schedule | Tables Updated | Duration Target | Depends On |
|-----|----------|----------------|-----------------|------------|
| **Import ThaiBMA Prices** | 17:00 | `security_master` | < 15 minutes | Back Office input |
| **Price Validation** | 17:15 | Price exceptions | < 10 minutes | ThaiBMA import |
| **Margin Calculation** | 17:30 | `margin_calls` | < 30 minutes | Price update |
| **Accrued Interest Calc** | 18:00 | `bond_positions`, `interbank_deals`, `repo_trades` | < 20 minutes | Working day check |
| **Position Build** | 18:30 | `bond_positions` | < 30 minutes | Accrued interest |
| **MTM Valuation** | 19:00 | `bond_positions.market_value` | < 15 minutes | ThaiBMA prices |
| **Costing Update** | 19:15 | `position_costing` | < 10 minutes | Position build |
| **Journal Generation** | 19:30 | GL interface | < 15 minutes | All above |
| **ThaiBMA Reporting** | Every 5 min | `bond_trades` | < 1 minute | Real-time |
| **ECL Calculation** | Monthly, 20:00 | `bond_positions` | < 1 hour | Month-end |

#### Weekend/Holiday Handling:

| Day Type | Process | Action |
|----------|---------|--------|
| **Weekend** | No ThaiBMA prices | Use last available price + 2 days accrued interest |
| **Holiday** | No ThaiBMA prices | Use last available price + N days accrued interest |
| **First Working Day** | Catch-up | Import accumulated accrued interest, new prices |

#### Accrued Interest Calculation Rules:

```python
# Daily Accrued Interest Formula
if coupon_frequency in ['Semi-Annual', 'Annual']:
    daily_accrued = (nominal_amount × coupon_rate) / 365
    
# Cumulative accrued (resets on coupon payment)
accrued_interest += daily_accrued

# On coupon payment date:
if today == coupon_payment_date:
    accrued_interest = 0  # Reset for new period
    # Create coupon transaction in bond_transactions
```

### 8.3 Periodic Updates

| Data Type | Frequency | Responsible |
|-----------|-----------|-------------|
| **Security Master** | New issues | IT Admin (setup), Back Office (updates) |
| **Counterparty Master** | Onboarding/Changes | Back Office |
| **Haircut Table** | When BOT updates | IT Admin |
| **Bank Codes** | When BOT updates | IT Admin |
| **Holiday Calendar** | Annual | IT Admin |
| **User Access** | As needed | IT Admin |
| **Portfolio Setup** | Rarely - Treasury approval required | IT Admin |

### 8.4 Immutable Tables (Append-Only)

| Table | Append Event | Retention |
|-------|--------------|-----------|
| `limit_utilization` | Every limit change | 5 years |
| `position_realization_events` | Every sale | 5 years |
| `cash_margin_movements` | Every cash movement | 5 years |
| `margin_calls` | Daily margin calc | 5 years |

---

## 9. Reference Data Tables

### 9.1 BANK_CODE

**Purpose:** BOT official bank codes for all financial institutions  
**Records:** 485 banks and financial institutions  
**Maintenance:** BOT updates (IT Admin updates system)  
**Usage:** `counterparty_master.bank_code` validation

**Key Fields:**
- `REFERENCE_CODE` (e.g., "001", "004")
- `FI_NAME_THAI` (Thai name)
- `FI_NAME_ENGLISH` (English name)
- `OPEN_DATE` (Establishment date)

**Common Codes:**
| Code | Short Name | Full Name |
|------|------------|-----------|
| 001 | BOT | Bank of Thailand |
| 002 | BBL | Bangkok Bank PCL |
| 004 | KBANK | Kasikornbank PCL |
| 006 | KTB | Krung Thai Bank PCL |
| 014 | SCB | Siam Commercial Bank PCL |
| 025 | BAY | Bank of Ayudhya PCL |
| 011 | TTB | TMBThanachart Bank PCL |

### 9.2 Haircut Table

**Purpose:** BOT standard haircut matrix for repo collateral  
**Source:** BOT Notification (Sheet: `Haircut_table`)  
**Maintenance:** BOT updates (IT Admin updates system)  
**Usage:** `collateral_positions.haircut_percentage`

### 9.3 Involved Party Type

**Purpose:** BOT standardized institution types for regulatory reporting  
**Example:** 176039 = Commercial Bank (Thai)  
**Usage:** `counterparty_master.involved_party_type`  
**Maintenance:** BOT updates (IT Admin updates system)

### 9.4 Customer Type Master

**Purpose:** Bank-defined customer classification  
**Example:** 2008 = Financial Institution - Resident  
**Usage:** `counterparty_master.customer_code`  
**Maintenance:** Internal policy (IT Admin manages)

### 9.5 Stage Master

**Purpose:** TFRS 9 stage definitions  
**Values:**
| Stage | Description | ECL Type |
|-------|-------------|----------|
| 1 | No significant deterioration | 12-month ECL |
| 2 | Significant credit deterioration | Lifetime ECL |
| 3 | Credit-impaired | Lifetime ECL |

**Maintenance:** Rarely changes (IT Admin manages)

### 9.6 Holiday Calendar

**Purpose:** Thai business day calculation  
**Fields:** Date, Description, IsHoliday, IsWeekend  
**Maintenance:** Annual update by IT Admin  
**Usage:** Settlement date calculation, accrual days

---

## Appendix A: Actual Database Table Structures

**Source:** Extracted from `Treasury_System_Database_V2_Internal.xlsx` (Sheet: `All Table_V4_Clean`)

> **Note:** The following tables are defined exactly as per the source Excel file. All field names, data types, and descriptions match the source data.

### A.1 Master Data Tables

---

#### Table: entity_master

**Description:** This table represents the authoritative, enterprise-wide obligor registry. It stores the top-level identity of each customer group, legal entity, or economic group used for credit risk, Basel, TFRS 9, Moody's mapping, and BOT DER_CPEN.Entity Id.

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| entity_id | VARCHAR(40) | Top-level unique identifier: entity_short_name + juristic_registration_number | BBL0107536000374 | PK | No |
| entity_name | VARCHAR(255) | Full legal name of the entity/obligor | Bangkok Bank PCL | - | No |
| entity_short_name | VARCHAR(10) | Short name / abbreviation used in risk reporting | BBL | - | Yes |
| entity_type | VARCHAR(50) | Basel/Moody's classification (BANK, BANK_SOV, PSE, CORP_HVCRE, etc.) | BANK | - | No |
| industry_sector | VARCHAR(50) | User-defined industry sector for concentration analysis | FINANCIALS | - | Yes |
| country_code | CHAR(3) | Country of domicile | TH | - | No |
| juristic_registration_number | VARCHAR(20) | เลขจดทะเบียนนิติบุคคล (13 digits for Thai) | 0107536000374 | - | No |
| registered_capital_amount | DECIMAL(20,2) | ทุนจดทะเบียน | 40000000000 | - | Yes |
| financials_currency | CHAR(3) | Currency for financials | THB | - | Yes |
| g_sib_type | CHAR(1) | G-SIB / D-SIB classification (G/D/NULL) | D | - | Yes |
| created_date | DATE | Record creation timestamp | 2024-01-10 | - | No |
| last_updated_date | DATE | Record last update timestamp | 2025-07-15 | - | Yes |

---

#### Table: counterparty_master

**Description:** This table serves as the single, authoritative repository for all external and internal entities with which the bank conducts treasury business.

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| entity_id | VARCHAR(40) | Entity reference | BBL0107536000374 | FK → entity_master | No |
| counterparty_id | VARCHAR(40) | Unique system-generated identifier | 101 | PK | Yes |
| legal_name | VARCHAR(255) | The full legal name of the entity | Bangkok Bank PCL | - | No |
| short_code | VARCHAR(50) | Short code for UI (e.g., BBL) | BBL | - | Yes |
| counterparty_type | VARCHAR(50) | Type (Commercial Bank, SOE, Corporate, etc.) | Commercial Bank | - | No |
| bank_code | VARCHAR(13) | BOT-assigned code from BANK_CODE sheet | 001 | - | Yes |
| swift_bic | VARCHAR(11) | SWIFT Business Identifier Code | BKKBTHBK | - | Yes |
| primary_credit_rating | VARCHAR(10) | Primary credit rating | AA+ | - | Yes |
| primary_rating_agency | VARCHAR(50) | Rating agency (Fitch, TRIS, etc.) | TRIS Rating | - | Yes |
| primary_rating_date | DATE | Date rating assigned | 2025-07-15 | - | Yes |
| created_date | DATE | Record creation timestamp | 2024-01-10 | - | No |
| last_updated_date | DATE | Last update timestamp | 2025-07-15 | - | Yes |
| involved_party_type | INT | BOT standardized type code | 176039 | - | No |
| customer_code | VARCHAR(10) | Bank-defined classification | 2008 | - | No |
| reside_in_thailand_flag | BOOLEAN | MFSMCG residency (TRUE = Resident) | TRUE | - | No |

---

#### Table: security_master

**Description:** This table is a comprehensive catalog of every financial instrument the bank can trade or hold, aligned with standards from the Thai Bond Market Association (ThaiBMA).

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| security_id | VARCHAR(10) | Official trading symbol (ThaiBMA) | LB28DA | PK | No |
| isin | VARCHAR(12) | International Securities Identification Number | TH0623038C09 | PK | No |
| issuer_id | VARCHAR(40) | 1=Govt, 2=BOT, 3=SOE, 4=Corporate | 1 | PK | No |
| unique_id | VARCHAR(20) | BOT report ID (BANK_CODE or Govt Agency) | 001 | PK | No |
| instrument_type | VARCHAR(20) | T-Bill, Gov Bond, Corp Bond, SOE Bond, BOT Bond | Gov Bond | - | No |
| issue_date | DATE | Date security was issued | 2018-12-17 | - | No |
| maturity_date | DATE | Date security matures | 2028-12-17 | - | No |
| coupon_rate | DECIMAL(10,6) | Nominal coupon rate (0 for zero-coupon) | 2.75 | - | Yes |
| coupon_margin | DECIMAL(10,6) | Spread over reference rate | 0.1 | - | Yes |
| coupon_reference_rate | VARCHAR(20) | Floating benchmark (NULL if fixed) | THBFIX6M | - | Yes |
| coupon_frequency | VARCHAR(20) | Semi-Annual, Quarterly, etc. | Semi-Annual | - | No |
| coupon_day_count_conv | VARCHAR(20) | Actual/365, 30/360, etc. | Actual/365 | - | No |
| currency | VARCHAR(3) | ISO 4217 currency code | THB | - | No |
| country | VARCHAR(3) | Country Code | TH | - | No |
| bond_structure | VARCHAR(20) | ZERO, Bullet, Amortizing | Bullet | - | No |
| rating_tris | VARCHAR(8) | TRIS Rating (blank for Govt/MOF) | A- | - | Yes |
| rating_fitch | VARCHAR(8) | Fitch Rating | A-(tha) | - | Yes |
| is_eligible_bot_repo_collateral | BOOLEAN | Eligible for BOT repo operations | 1 | - | No |
| is_eligible_crm_collateral | BOOLEAN | Eligible for Credit Risk Mitigation | 1 | - | No |
| status | VARCHAR(20) | Active, Matured, Defaulted | Active | - | No |
| status_timestamp | DATETIME | Timestamp in GMT+7 | 2024-02-01 11:00:00 | - | Yes |
| coupon_rate_type | VARCHAR(10) | Fixed or Floating | Fixed | - | No |
| cross_default | BOOLEAN | Cross-default flag | False | - | No |

---

#### Table: portfolio_master

**Description:** This table allows for the logical segregation of the bank's treasury positions according to their strategic intent.

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| portfolio_id | VARCHAR(40) | Unique identifier | 201 | PK | No |
| portfolio_name | VARCHAR(100) | Accounting classification + Asset type | AMC - Govt Bonds | - | No |
| portfolio_manager | VARCHAR(100) | Responsible manager name | John Doe | - | No |
| accounting_treatment | VARCHAR(50) | AMC, FVOCI, or FVTPL | FVOCI | - | No |
| created_timestamp | DATETIME | Creation timestamp GMT+7 | 2024-02-01 11:00:00 | - | No |

---

#### Table: netting_agreement

**Description:** Master information for netting and collateral agreements (ISDA, CSA, GMRA, GMSLA).

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| netting_agreement_id | VARCHAR(40) | Unique identifier | GMRA_2023_KB | PK | No |
| counterparty_id | VARCHAR(40) | Links to Counterparty_Master | 101 | FK | No |
| netting_set_id | VARCHAR(40) | Logical netting set identifier | 20001 | - | No |
| agreement_type | VARCHAR(10) | GMRA, ISDA, etc. | GMRA | - | No |
| netting_type | VARCHAR(20) | CLOSE_OUT, COLLATERAL, SET_OFF | COLLATERAL | - | No |
| collateral_contract_type | VARCHAR(12) | REP, BAL, OTC | REP | - | No |
| trade_date | DATE | Signature/execution date | 2023-06-15 | - | No |
| value_date | DATE | Effective date | 2023-07-01 | - | No |
| maturity_date | DATE | Expiry/termination date | 2025-06-30 | - | Yes |
| is_replacement | TINYINT | 1=replaces earlier agreement | 0 | - | No |
| replaced_agreement_id | VARCHAR(40) | Previous agreement ID | - | FK | Yes |
| settlement_currency | VARCHAR(3) | Primary settlement currency | THB | - | Yes |
| created_at | DATETIME | Creation timestamp GMT+7 | 2025-03-01 10:30:00 | - | No |
| updated_at | DATETIME | Last update timestamp GMT+7 | 2025-03-25 18:45:00 | - | Yes |
| agreement_status | VARCHAR(20) | Active, Matured, In-Default | Active | - | No |

---

### A.2 Transaction Tables

---

#### Table: bond_trades

**Description:** Records all outright purchases and sales of bonds for the bank's investment portfolios.

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| bond_trade_id | VARCHAR(40) | Unique identifier (≥90000) | 90001 | PK | No |
| portfolio_id | VARCHAR(40) | Links to Portfolio_Master | 201 | FK | No |
| trade_date | DATE | Trade execution date | 2025-09-05 | - | No |
| settlement_date | DATE | T+2 settlement date | 2025-09-09 | - | No |
| security_id | VARCHAR(10) | Links to Security_Master | LB28DA | FK | No |
| counterparty_id | VARCHAR(40) | Links to Counterparty_Master | 101 | FK | No |
| trade_type | VARCHAR(10) | Buy or Sell | Buy | - | No |
| nominal_amount | DECIMAL(20,2) | Face value traded | 50000000 | - | No |
| clean_price_trade | DECIMAL(18,6) | Agreed price as of trade date | 169.8 | - | No |
| yield_to_maturity | DECIMAL(10,6) | Calculated yield | 2.805 | - | Yes |
| settlement_status | VARCHAR(20) | Pending, Settled, Failed | Pending | - | No |

---

#### Table: bond_transactions

**Description:** Captures all bond trading activities at transaction level with full details.

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| trade_id | VARCHAR(40) | Unique ID (≥90000 or CPN_ prefix) | 90001 | PK | No |
| security_id | VARCHAR(10) | Links to Security_Master | LB28DA | FK | No |
| portfolio_id | VARCHAR(40) | Links to Portfolio_Master | 301 | FK | No |
| counterparty_id | VARCHAR(40) | Links to Counterparty_Master | 112 | FK | No |
| trade_type | VARCHAR(20) | Buy, Sell, Repo, ReverseRepo, Coupon | Buy | - | No |
| trade_date | DATE | Trade execution date | 2025-09-05 | - | No |
| settlement_date | DATE | T+2 settlement date | 2025-09-09 | - | No |
| maturity_date | DATE | Bond maturity date | 2061-06-17 | - | No |
| currency | VARCHAR(3) | ISO 4217 currency | THB | - | No |
| nominal_amount | DECIMAL(20,2) | Face value | 100000000 | - | No |
| clean_price | DECIMAL(18,6) | Clean price at reporting date | 170.8 | - | Yes |
| clean_price_trade | DECIMAL(18,6) | Agreed price at trade date | 169.8 | - | Yes |
| accrued_interest | DECIMAL(20,2) | Accrued coupon since last payment | 45694.44 | - | Yes |
| dirty_price | DECIMAL(20,6) | Total paid incl. accrued | 171.21 | - | Yes |
| classification | VARCHAR(10) | AMC, FVOCI, FVTPL | FVOCI | - | No |
| book_value | DECIMAL(20,2) | Carrying amount | 171180000 | - | No |
| market_clean_value | DECIMAL(20,2) | Market value excl. accrued | 171500000 | - | Yes |
| market_value | DECIMAL(20,2) | Current MTM fair value | 172200000 | - | Yes |
| last_coupon_date | DATE | Last coupon date | 2025-12-17 | - | Yes |
| coupon_rate_type | VARCHAR(10) | Fixed or Floating | Fixed | - | No |
| coupon_reference_rate | VARCHAR(20) | Benchmark if floating | - | - | Yes |
| coupon_margin | DECIMAL(10,6) | Spread over reference | 0.1 | - | Yes |
| coupon_frequency | VARCHAR(20) | Monthly, Quarterly, Semi-Annual | Quarterly | - | No |
| coupon_rate | DECIMAL(10,6) | Nominal coupon rate | 4.85 | - | No |
| coupon_day_count_conv | VARCHAR(20) | 30/360, ACT/365, etc. | 30/360 | - | No |
| rating_tris | VARCHAR(8) | TRIS rating | A- | - | Yes |
| rating_fitch | VARCHAR(8) | Fitch rating | A-(tha) | - | Yes |
| status | VARCHAR(20) | Active, Matured, In-Default | Active | - | No |
| last_updated_timestamp | DATETIME | Last update GMT+7 | 2025-10-03 17:00:00 | - | No |
| valuation_date | DATE | Latest valuation date | 2025-09-30 | - | No |

---

#### Table: interbank_deals

**Description:** Records all interbank lending (placements) and borrowing (takings) transactions.

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| deal_id | VARCHAR(40) | Unique identifier | 40001 | PK | No |
| trade_date | DATETIME | Execution timestamp GMT+7 | 2025-09-05 10:30:00 | - | No |
| value_date | DATE | Start date | 2025-09-05 | - | No |
| maturity_date | DATE | End date | 2025-09-08 | - | No |
| deal_type | VARCHAR(10) | Lend or Borrow | Lend | - | No |
| counterparty_id | VARCHAR(40) | Links to Counterparty_Master | 101 | FK | No |
| principal_amount | DECIMAL(20,2) | Notional amount | 250000000 | - | No |
| currency | VARCHAR(3) | ISO 4217 currency | THB | - | No |
| reference_rate_id | VARCHAR(20) | ReferenceRate + Tenor + DealID | THOR1M45001 | - | Yes |
| interest_rate_type | VARCHAR(10) | Fixed or Floating | Fixed | - | No |
| interest_rate | DECIMAL(10,6) | Current applicable rate (% p.a.) | 2.25 | - | No |
| reference_rate_tenor | VARCHAR(10) | O/N, 1M, 3M, 6M | 1M | - | Yes |
| reference_rate | VARCHAR(20) | THOR, THORA, SOFR, or FIX | THOR | - | No |
| margin | DECIMAL(10,6) | Spread over reference | 0.26161 | - | Yes |
| reset_rate | DECIMAL(10,6) | Benchmark rate on LastResetDate | 2.05 | - | Yes |
| last_reset_date | DATE | Start of current interest period | 2025-05-09 | - | Yes |
| next_reset_date | DATE | End of current period | 2025-05-10 | - | Yes |
| day_count_convention | VARCHAR(20) | Actual/365, etc. | Actual/365 | - | No |
| accrued_interest | DECIMAL(20,2) | Calculated interest to date | 46232.88 | - | Yes |
| status | VARCHAR(20) | Active, Matured, Defaulted | Active | - | No |
| confirmation_ref | VARCHAR(50) | ISO 20022 confirmation ref | CONF-ISO-45001 | - | Yes |
| limit_id | VARCHAR(40) | Links to limit_utilization | 45 | FK | Yes |
| term | INT | Term in days | 7 | - | No |
| entity_id | VARCHAR(40) | Links to Entity_Master | BBL0107536000374 | FK | No |

---

#### Table: interbank_interest_schedule

**Description:** Child table for floating rate interest periods and resets.

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| schedule_id | VARCHAR(40) | Primary key for interest period | 1 | PK | No |
| referencerate_id | VARCHAR(20) | Links to interbank_deals | THOR1M | FK | No |
| deal_id | VARCHAR(40) | Links to parent deal | 50001 | FK | No |
| last_reset_date | DATE | Start of interest period | 2025-01-03 | - | No |
| next_reset_date | DATE | End/next reset date | 2025-02-03 | - | No |
| reset_rate | DECIMAL(10,6) | Benchmark fixing rate | 2.05 | - | Yes |
| interest_rate | DECIMAL(10,6) | ResetRate + Margin | 2.15 | - | Yes |
| status | VARCHAR(20) | Active, Planned, Closed | Active | - | No |

---

#### Table: repo_trades

**Description:** Captures master details of each REPO or Reverse REPO transaction.

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| repo_trade_id | VARCHAR(40) | Unique ID (≥70000) | 70001 | PK | No |
| trade_date | DATETIME | Execution timestamp GMT+7 | 2025-09-05 14:00:00 | - | No |
| trade_type | VARCHAR(20) | Repo, ReverseRepo, Rehypothecation | Repo | - | No |
| counterparty_id | VARCHAR(40) | Links to Counterparty_Master | 215 | FK | No |
| netting_agreement_id | VARCHAR(40) | GMRA/CSA agreement ID | GMRA_2023_KB | - | Yes |
| netting_set_id | VARCHAR(40) | Netting set identifier | 20001 | - | Yes |
| nominal_amount | DECIMAL(20,2) | Face value of securities | 100000000 | - | No |
| purchase_date | DATE | Start date (first leg) | 2025-09-08 | - | No |
| repurchase_date | DATE | End date (second leg) | 2025-09-15 | - | No |
| purchase_price | DECIMAL(20,2) | Cash on day 1 | 100000000 | - | No |
| repurchase_price | DECIMAL(20,2) | Cash on day 2 | 100038356.2 | - | No |
| currency | VARCHAR(3) | ISO 4217 currency | THB | - | No |
| reference_rate_id | VARCHAR(20) | reference_rate + repo_trade_id | THOR1M | - | Yes |
| interest_rate_type | VARCHAR(10) | Fixed or Floating | Fixed | - | No |
| interest_rate | DECIMAL(10,6) | Current applicable repo rate | 2.25 | - | No |
| reference_rate | VARCHAR(20) | THOR, THORA, SOFR, or FIX | FIX | - | No |
| margin | DECIMAL(10,6) | Spread for floating repos | - | - | Yes |
| day_count_convention | VARCHAR(20) | Actual/365, etc. | Actual/365 | - | No |
| repo_rate | DECIMAL(10,6) | Implied repo rate | 2 | - | Yes |
| term | INT | Term in days | 7 | - | No |
| repo_out_flag | BOOLEAN | Securities out as collateral | 1 | - | No |
| repo_in_flag | BOOLEAN | Securities received via Reverse Repo | 0 | - | No |
| status | VARCHAR(20) | Active, Matured, In-Default | Active | - | No |
| limit_id | VARCHAR(40) | Links to limit_utilization | 45 | FK | Yes |
| accrued_interest | DECIMAL(20,2) | Interest accrued to date | 46232.88 | - | Yes |
| entity_id | VARCHAR(40) | Links to Entity_Master | BBL0107536000374 | FK | No |

---

### A.3 Position & Collateral Tables

---

#### Table: collateral_positions

**Description:** Child table to Repo_Trades, logging all securities allocated as collateral.

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| collateral_id | VARCHAR(20) | Unique allocation ID (RepoTradeID_SecurityID_seq) | 77002_LB28DA_1 | PK | No |
| repo_trade_id | VARCHAR(40) | Links to parent Repo_Trades | 77002 | PK | No |
| security_id | VARCHAR(10) | Links to Security_Master | LB28DA | FK | No |
| nominal_amount | DECIMAL(20,2) | Face value pledged | 102500000 | - | No |
| allocation_date | DATE | Date allocated | 2025-09-08 | - | No |
| valuation_price | DECIMAL(18,6) | Clean price at last MTM | 100.1 | - | Yes |
| market_value | DECIMAL(20,2) | Nominal × Price + Accrued | 102602500 | - | Yes |
| haircut_percentage | DECIMAL(5,2) | Haircut for margining | 2 | - | Yes |
| collateral_value_after_haircut | DECIMAL(20,2) | Final value for margining | 100550450 | - | Yes |
| margin_call_id | INT | Links to margin_calls if applicable | - | FK | Yes |
| currency | VARCHAR(3) | ISO 4217 currency | THB | - | No |

---

#### Table: bond_positions

**Description:** Maintains current holding details for each bond investment per portfolio.

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| position_id | VARCHAR(40) | Unique position identifier | 1 | PK | No |
| security_id | VARCHAR(10) | Bond/security identifier | LB28DA | FK | No |
| portfolio_id | VARCHAR(40) | Portfolio classification | 301 | FK | No |
| open_date | DATE | Position creation date | 2025-09-09 | - | No |
| maturity_date | DATE | Bond maturity date | 2061-06-17 | - | No |
| currency | VARCHAR(3) | ISO 4217 currency | THB | - | No |
| nominal_amount | DECIMAL(20,2) | Current outstanding face | 100000000 | - | No |
| unencumbrance | DECIMAL(20,2) | Free (not pledged) amount | 100000000 | - | No |
| encumbrance | DECIMAL(20,2) | Pledged as collateral | 0 | - | No |
| unenc_from_reverse_repo | DECIMAL(20,2) | From Reverse Repo unencumbered | 0 | - | No |
| rehypothecation | DECIMAL(20,2) | Re-pledged securities | 0 | - | No |
| avg_book_clean_price_pct | DECIMAL(12,6) | WAC for remaining position | 169.8 | - | No |
| book_value | DECIMAL(20,2) | Carrying amount at amortized cost | 171800000 | - | No |
| valuation_date | DATE | Latest valuation date | 2025-09-30 | - | No |
| clean_price | DECIMAL(12,6) | Market clean price % | 171.5 | - | Yes |
| accrued_interest | DECIMAL(20,2) | Accrued coupon interest | 700000 | - | Yes |
| dirty_price | DECIMAL(20,6) | Total paid incl. accrued | 171.21 | - | Yes |
| market_value | DECIMAL(20,2) | (Price% × Nominal/100) + Accrued | 172200000 | - | Yes |
| realized_gain_loss | DECIMAL(20,2) | Realized P&L from sales | 0 | - | Yes |
| unrealized_gain_loss | DECIMAL(20,2) | MTM P&L on remaining | 400000 | - | Yes |
| status | VARCHAR(20) | Active, Matured, In-Default | Active | - | No |
| last_updated_timestamp | DATETIME | Last update GMT+7 | 2025-03-10 17:00:00 | - | No |
| market_rate | DECIMAL(10,6) | ThaiBMA market yield % | 1.22 | - | Yes |

---

#### Table: position_costing

**Description:** Maintains cost basis and realized P&L state for each bond position.

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| costing_id | VARCHAR(40) | Row ID | 1 | PK | No |
| position_id | VARCHAR(40) | Links to bond_positions | 1 | FK | No |
| cost_method | VARCHAR(8) | WAC, FIFO, LIFO | WAC | - | No |
| avg_book_price_pct | DECIMAL(12,6) | Running weighted-avg clean price % | 100.45 | - | Yes |
| sum_product_clean | DECIMAL(20,6) | Σ(clean% × nominal) for audit | 100450000 | - | No |
| total_nominal_in | DECIMAL(20,2) | Σ buys/transfers-in nominal | 100000000 | - | No |
| cumulative_sold_nominal | DECIMAL(20,2) | Σ nominal sold so far | 20000000 | - | No |
| realized_gain_loss_to_date | DECIMAL(20,2) | Cumulative realized P&L | 45000 | - | No |
| last_realization_date | DATE | Last sell/transfer date | 2025-10-29 | - | Yes |

---

#### Table: position_realization_events

**Description:** Immutable journal of realized P&L events for bond positions.

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| realization_id | VARCHAR(40) | Row ID | 1 | PK | No |
| position_id | VARCHAR(40) | Links to position sold | 1 | FK | No |
| trade_id | VARCHAR(40) | Reference to triggering trade | 93005 | FK | No |
| event_date | DATE | Sale or transfer date | 2025-10-29 | - | No |
| sold_nominal | DECIMAL(20,2) | Nominal amount sold | 20000000 | - | Yes |
| sell_clean_price_pct | DECIMAL(12,6) | Trade clean price % | 102 | - | Yes |
| avg_book_price_pct | DECIMAL(12,6) | WAC at sale time | 100.45 | - | Yes |
| realized_gainloss | DECIMAL(20,2) | (SellClean - AvgBook) × SoldNominal | 31000 | - | Yes |
| accrued_int_realized | DECIMAL(20,2) | Coupon interest received | 25000 | - | Yes |
| method_used | VARCHAR(8) | WAC/FIFO/LIFO at time of calc | WAC | - | No |
| created_at | DATETIME | Event record creation GMT+7 | 2025-10-29 17:25:00 | - | No |

---

### A.4 Control & Risk Tables

---

#### Table: margin_calls

**Description:** Records daily margin call events from collateralized trading (GMRA, CSA).

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| margin_call_id | VARCHAR(40) | Unique identifier | 1 | PK | No |
| counterparty_id | VARCHAR(40) | Links to Counterparty_Master | 215 | FK | No |
| repo_trade_id | VARCHAR(40) | Links to Repo_Trades | 70001 | FK | Yes |
| valuation_date | DATE | MTM calculation date | 2025-10-06 | - | No |
| call_currency | VARCHAR(3) | Currency (typically THB) | THB | - | No |
| call_type | VARCHAR(12) | CALL, RETURN, or NONE | CALL | - | No |
| call_amount | DECIMAL(20,2) | Net margin after MTA/threshold | 2100000 | - | No |
| due_time | DATETIME | Contractual deadline GMT+7 | 2025-10-07 11:00:00 | - | Yes |
| status | VARCHAR(20) | Pending, Agreed, Settled, Cancelled | Pending | - | No |
| created_timestamp | DATETIME | Record creation GMT+7 | 2025-10-06 18:05:00 | - | No |

---

#### Table: cash_margin_movements

**Description:** Records all cash-based collateral movements under GMRA.

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| cash_margin_movement_id | VARCHAR(40) | Unique identifier | 1 | PK | No |
| margin_call_id | VARCHAR(40) | Links to Margin_Call | 1 | FK | Yes |
| counterparty_id | VARCHAR(40) | Links to Counterparty_Master | 215 | FK | No |
| repo_trade_id | VARCHAR(40) | Links to Repo_Trades | 77002 | FK | Yes |
| call_currency | VARCHAR(3) | Currency | THB | - | No |
| movement_type | VARCHAR(12) | PAY or RECEIVE | PAY | - | No |
| amount | DECIMAL(20,2) | Signed cash amount | 2100000 | - | No |
| outstanding_balance | DECIMAL(20,2) | Running net balance | 2100000 | - | No |
| value_date | DATE | Settlement date | 2025-10-07 | - | No |
| created_timestamp | DATETIME | Record creation GMT+7 | 2025-10-06 20:15:00 | - | No |
| bank_account_code | VARCHAR(20) | Internal GL/nostro account | IB-MARGIN-BBL-001 | - | Yes |
| daily_accrued_int_receivable | DECIMAL(20,2) | Interest for this day | 85.32 | - | Yes |
| accrued_int_receivable | DECIMAL(20,2) | Cumulative interest | 420.15 | - | Yes |
| interest_on_margin_code | VARCHAR(30) | Reference rate (e.g., TH_MPC) | TH_MPC | - | Yes |
| interest_on_margin_rate | DECIMAL(9,6) | Effective annualized rate % | 1.5 | - | Yes |
| day_count_basis | VARCHAR(10) | ACT/365, etc. | ACT/365 | - | Yes |
| accrual_days | INTEGER | Days covered by accrual | 1 | - | Yes |
| interest_direction | VARCHAR(20) | RECEIVABLE or NONE | RECEIVABLE | - | No |

---

#### Table: limit_utilization

**Description:** Chronological, auditable record of credit line changes per counterparty.

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| limit_id | VARCHAR(40) | Unique identifier | 1001 | PK | No |
| counterparty_id | VARCHAR(40) | Counterparty | 101 | FK | No |
| limit_type | VARCHAR(20) | PLACEMENT_LIMIT, REPO_LIMIT, etc. | REPO_LIMIT | - | No |
| currency | VARCHAR(3) | ISO 4217 currency | THB | - | No |
| available_line | DECIMAL(20,2) | Available before event | 800000000 | - | No |
| total_credit_line | DECIMAL(20,2) | Total approved credit line | 1000000000 | - | No |
| utilization_amount | DECIMAL(20,2) | Amount consumed (+) or released (-) | 200000000 | - | No |
| credit_line_approve_date | DATE | วันที่อนุมัติวงเงิน | 2025-09-05 | - | Yes |
| timestamp | DATETIME | Event timestamp GMT+7 | 2025-09-05 10:30:01 | - | No |
| created_date | DATE | Day-1 creation date | 2025-09-05 | - | Yes |
| entity_id | VARCHAR(40) | Links to Entity_Master | BBL0107536000374 | FK | No |

---

#### Table: entity_counterparty

**Description:** Maps counterparties to entities and parent limits.

| Column Name | Data Type | Description | Example | PK/FK | Allow Null |
|-------------|-----------|-------------|---------|-------|------------|
| entity_counterparty_id | VARCHAR(40) | Unique mapping ID | 1 | PK | No |
| entity_id | VARCHAR(40) | Entity/Obligor ID (วงเงินแม่) | BBL0107536000374 | FK | No |
| counterparty_id | VARCHAR(40) | Counterparty using parent limit | 101 | FK | No |
| parent_limit_id | VARCHAR(40) | Parent/Group Limit ID | 1001 | FK | No |
| effective_from | DATE | Start date of validity | 2025-01-01 | - | No |
| effective_to | DATE | End date (NULL = active) | - | - | Yes |
| status | VARCHAR(20) | ACTIVE, INACTIVE | ACTIVE | - | No |
| remark | VARCHAR(255) | Free-text note | Group KBank – shared limit | - | Yes |
| created_date | DATE | Record creation | 2025-01-01 | - | No |
| last_updated_date | DATETIME | Last update GMT+7 | 2025-02-10 18:30:00 | - | Yes |

---

## Appendix B: Field Mapping Quick Reference

### B.1 DER_CPEN Reporting Mapping

| DER_CPEN Field | Source Table | Source Column |
|----------------|--------------|---------------|
| Entity Id | `entity_master` | `entity_id` |
| Entity Name | `entity_master` | `entity_name` |
| Country Code | `entity_master` | `country_code` |
| Industry Code | `entity_master` | `industry_sector` |
| Involved Party Type | `counterparty_master` | `involved_party_type` |
| Residency Flag | `counterparty_master` | `reside_in_thailand_flag` |
| Total Exposure | `bond_positions` | `book_value` or `market_value` |

### B.2 ThaiBMA Trade Reporting Mapping

| ThaiBMA Field | Source Table | Source Column |
|---------------|--------------|---------------|
| Transaction Date | `bond_trades` | `trade_date` |
| Reference Number | `bond_trades` | `bond_trade_id` |
| ISIN | `security_master` | `isin` |
| Counterparty Code | `counterparty_master` | `short_code` |
| Buy/Sell Indicator | `bond_trades` | `trade_type` (BUY=P, SELL=S) |
| Nominal Amount | `bond_trades` | `nominal_amount` |
| Clean Price | `bond_trades` | `clean_price_trade` |
| Settlement Amount | Calculated | CleanPrice × Nominal / 100 |
| Settlement Date | `bond_trades` | `settlement_date` |

### B.3 BAHTNET Message Mapping

| MT103 Field | Source Table(s) | Source Column(s) |
|-------------|-----------------|------------------|
| Sender | Config | Our BIC |
| Receiver | `counterparty_master` | `swift_bic` |
| Transaction Reference | Generated | UMID |
| Value Date | `interbank_deals` | `value_date` |
| Currency | `interbank_deals` | `currency` (THB) |
| Amount | `interbank_deals` | `principal_amount` |
| Beneficiary | `counterparty_master` | `legal_name` |
| Beneficiary Account | `interbank_deals` | Settlement account |
| Remittance Info | Concatenated | Deal type + DealID |

---

## Review Notes

### Team Responsibilities Summary:

| Team | Primary Responsibilities |
|------|-------------------------|
| **Front Office** | Trade capture, pricing, execution |
| **Middle Office** | Limit management, risk monitoring, TFRS 9/ECL, approval workflow |
| **Back Office** | Settlement, collateral, master data (counterparty), accounting (costing, P&L, journals) |
| **IT Admin** | User management, reference data, security master setup, portfolio setup, emergency fixes |

### Co-Management Clarification:

| Data | Primary Owner | Secondary/Support |
|------|---------------|-------------------|
| **Security Master** | IT Admin (initial setup) | Back Office (day-to-day updates) |
| **Portfolio Master** | IT Admin | Treasury/Accounting (approval) |
| **Counterparty Master** | Back Office | Credit Risk (approval for new) |
| **Reference Data** | IT Admin | All teams (consumption) |

### Pending Decisions:

- [ ] Confirm four-eyes approval thresholds
- [ ] Validate ECL calculation methodology (simplified vs full model)
- [ ] Confirm BAHTNET integration method (API vs manual file upload)
- [ ] Determine TSD message format (SWIFT MT vs proprietary)
- [ ] Approve password policy requirements
- [ ] Confirm retention period for immutable tables
- [ ] Define escalation procedure for IT Admin emergency changes

### Change Log:

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-02-03 | 0.1 | Initial draft | [Name] |
| 2026-02-03 | 0.2 | Removed Accounting section, merged into Back Office; Updated IT Admin responsibilities | [Name] |
| 2026-02-03 | 0.3 | Added Appendix A with actual table structures from Excel source file; Updated all field names to match source data | [Name] |
| 2026-02-03 | 0.4 | Added detailed daily batch process for accrued interest calculation; Clarified Back Office daily ThaiBMA price update responsibility; Added weekend/holiday handling procedures | [Name] |

---

*Document for review - please mark changes and return for update.*
