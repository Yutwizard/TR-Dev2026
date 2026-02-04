# Transaction Process Guide - Treasury Management System

**Purpose:** Step-by-step workflow for all transaction types with responsible teams and field updates at each stage.

**Related Documents:**
- [Field Update Matrix](./Field_Update_Matrix.md) - Field-level update details
- [Treasury System Detailed Design Input](./Treasury_System_Detailed_Design_Input.md) - Team responsibilities
- [Stakeholder Review Checklist](./STAKEHOLDER_REVIEW_CHECKLIST.md) - Approval requirements

**Last Updated:** February 3, 2026

---

## 📋 Legend

| Icon | Meaning |
|------|---------|
| 👤 | Manual Action (User input required) |
| ⚙️ | System Action (Automatic) |
| ✅ | Validation/Check |
| 📧 | Notification/Alert |
| 🔒 | Immutable Record (Cannot be changed) |

**Team Abbreviations:**
- **FO** = Front Office (Trading)
- **MO** = Middle Office (Risk)
- **BO** = Back Office (Operations/Settlement)
- **IT** = IT Admin

---

## 1. Bond Trade - Buy/Sell

### Overview
Outright purchase or sale of bonds for investment portfolios.

**Participating Teams:** FO → MO → BO

**Total Time:** T+2 settlement (trade date + 2 business days)

---

### Step 1: Trade Entry (Front Office)

**Responsible:** Front Office Trader

| # | Action | Fields to Input/Update | Validation |
|---|--------|------------------------|------------|
| 1.1 | 👤 Select portfolio | `portfolio_id` | Must exist in `portfolio_master` |
| 1.2 | 👤 Select security | `security_id` | Must exist in `security_master`, status='Active' |
| 1.3 | 👤 Select counterparty | `counterparty_id` | KYC status must be 'APPROVED' |
| 1.4 | 👤 Input trade type | `trade_type` = BUY or SELL | Enum validation |
| 1.5 | 👤 Input trade date | `trade_date` | Must be business day (check Holiday Calendar) |
| 1.6 | 👤 Input nominal amount | `nominal_amount` | > 0, multiple of 1,000 |
| 1.7 | 👤 Input clean price | `clean_price_trade` | ±10% from last price = warning |
| 1.8 | ⚙️ System calculates | `settlement_date` = T+2 | Auto-calculated, editable with override |
| 1.9 | ⚙️ System calculates | `yield_to_maturity` | From price using bond math |
| 1.10 | ⚙️ System sets | `settlement_status` = 'PENDING_APPROVAL' | Auto on creation |
| 1.11 | ⚙️ System generates | `bond_trade_id` | ≥90000, auto-generated |

**System Validations:**
- ✅ Business day check (Thai holidays)
- ✅ KYC status check
- ✅ Price range warning (±10%)
- ✅ Portfolio exists
- ✅ Security is tradeable

**Notifications:**
- 📧 Middle Office: "Trade pending approval"

**Tables Updated:**
- `bond_trades` - New record created

---

### Step 2: Pre-Trade Limit Check (System)

**Responsible:** System (Automatic)

| # | Action | Fields Checked | Result |
|---|--------|----------------|--------|
| 2.1 | ⚙️ Check counterparty limit | `limit_utilization` | Calculate current exposure |
| 2.2 | ⚙️ Calculate proposed utilization | - | Current + new trade amount |
| 2.3 | ⚙️ Compare to limit | `total_credit_line` | If > 100% → BLOCK |
| 2.4 | ⚙️ Warning threshold | - | If > 90% → WARN but allow |
| 2.5 | ⚙️ Create limit record | `limit_utilization` | New record (append-only) |

**Validation Results:**
- ✅ PASS: Proceed to approval
- ❌ BLOCK: "Limit Exceeded" error, trade rejected
- ⚠️ WARNING: "Approaching limit", allow with acknowledgment

**Tables Updated:**
- `limit_utilization` - New record: `utilization_amount` = +trade_amount

---

### Step 3: Four-Eyes Approval (Middle Office)

**Responsible:** Middle Office Risk Manager

| # | Action | Fields to Update | Notes |
|--------|--------|------------------|-------|
| 3.1 | 👤 Review trade details | All trade fields | Verify accuracy |
| 3.2 | 👤 Check limit utilization | `limit_utilization` | Confirm within limits |
| 3.3 | 👤 Decision | `settlement_status` | APPROVE or REJECT |
| 3.4 | ⚙️ If APPROVED | `settlement_status` = 'APPROVED' | Proceed to confirmation |
| 3.5 | ⚙️ If REJECTED | `settlement_status` = 'REJECTED' | Reverse limit utilization |
| 3.6 | ⚙️ Log approval | - | Audit trail with approver ID |

**Rejection Handling:**
- Reverse limit utilization (negative record)
- Notify Front Office with reason
- Trade archived

**Notifications:**
- 📧 Front Office: "Trade approved" or "Trade rejected"
- 📧 Back Office: "Approved trade ready for settlement"

**Tables Updated:**
- `bond_trades` - Update `settlement_status`
- `limit_utilization` - If rejected: new record with negative utilization

---

### Step 4: ThaiBMA Reporting (System/Front Office)

**Responsible:** System (Auto) + Front Office Monitor

| # | Action | Fields/Process | Timing |
|--------|--------|----------------|--------|
| 4.1 | ⚙️ Generate ThaiBMA report | Trade details in ThaiBMA format | Within 30 minutes of trade |
| 4.2 | ⚙️ Submit to ThaiBMA | Via API/portal | Auto or manual |
| 4.3 | ⚙️ Track deadline | 30-minute countdown | Alert at 20 min (Amber), 28 min (Red) |
| 4.4 | 👤 Monitor (FO) | ThaiBMA portal | Confirm successful reporting |

**Late Reporting:**
- ⚠️ After 30 minutes: Flag as late
- 📧 Alert to compliance
- Manual intervention required

---

### Step 5: Settlement Preparation (Back Office)

**Responsible:** Back Office Settlement Officer

| # | Action | Fields to Check | Notes |
|--------|--------|-----------------|-------|
| 5.1 | 👤 Review settlement instructions | `settlement_date`, `nominal_amount`, `counterparty_id` | T+2 confirmation |
| 5.2 | 👤 Check settlement system | - | TSD (Corporate) or BAHTNET (Govt) |
| 5.3 | ⚙️ Generate instructions | MT540/MT541 (TSD) or MT103 (BAHTNET) | Auto-generated |
| 5.4 | 👤 For TSD | Send SWIFT message | Direct to TSD |
| 5.5 | 👤 For BAHTNET | Download file, upload to BAHTNET portal | Manual process |

**BAHTNET Settlement Process:**
```
Step 1: System generates MT103 file
Step 2: Back Office downloads file
Step 3: Login to BAHTNET portal (https://www.bahtnet.net)
Step 4: Upload MT103 file
Step 5: Confirm transaction in portal
Step 6: Wait for settlement confirmation
```

---

### Step 6: Settlement Confirmation (Back Office)

**Responsible:** Back Office Settlement Officer

| # | Action | Fields to Update | Source |
|--------|--------|------------------|--------|
| 6.1 | 👤 Receive confirmation | - | TSD: MT544/MT545; BAHTNET: Portal confirmation |
| 6.2 | 👤 Update status | `settlement_status` = 'SETTLED' | Manual update |
| 6.3 | ⚙️ Create position | `bond_positions` | New or updated position |
| 6.4 | ⚙️ Update costing | `position_costing` | WAC recalculation |

**If Settlement Fails:**
- 👤 Update `settlement_status` = 'FAILED'
- 👤 Initiate exception handling
- 📧 Notify Front Office and Middle Office

**Tables Updated:**
- `bond_trades` - Update `settlement_status`
- `bond_positions` - Create/update position
- `position_costing` - Update WAC (Buy only)

---

### Step 7: Position Update (System)

**Responsible:** System (Automatic on settlement)

| # | Action | Fields Updated | Calculation |
|--------|--------|----------------|-------------|
| 7.1 | ⚙️ Update position | `bond_positions.nominal_amount` | += Buy, -= Sell |
| 7.2 | ⚙️ Calculate WAC | `avg_book_clean_price_pct` | (Sum of costs) / (Total nominal) |
| 7.3 | ⚙️ Update book value | `book_value` | Nominal × WAC Price / 100 |
| 7.4 | ⚙️ If SELL | `realized_gain_loss` | (Sell price - WAC) × Sold nominal |
| 7.5 | ⚙️ If SELL | Create realization event | `position_realization_events` | Immutable record |

**For SELL Trades:**
- Calculate realized P&L
- Reduce position nominal
- If fully sold: Archive position

**Tables Updated:**
- `bond_positions` - Position quantities and values
- `position_costing` - Running WAC totals
- `position_realization_events` - Immutable P&L record (Sell only)

---

### Step 8: Daily EOD Batch (System - 18:00 Daily)

**Responsible:** System (Automatic) + Back Office Monitor

| # | Action | Fields Updated | Process |
|--------|--------|----------------|---------|
| 8.1 | 👤 Import ThaiBMA prices | `security_master.clean_price` | BO at 17:00 |
| 8.2 | ⚙️ Calculate accrued interest | `bond_positions.accrued_interest` | Daily accrual based on DCC |
| 8.3 | ⚙️ Calculate market value | `bond_positions.market_value` | (Price × Nom/100) + Accrued |
| 8.4 | ⚙️ Calculate unrealized P&L | `unrealized_gain_loss` | Market value - Book value |
| 8.5 | ⚙️ Update timestamp | `last_updated_timestamp` | GMT+7 |

**Accrued Interest Formula:**
```
Daily Accrued = Nominal × Coupon% × (1/DayCountBase)
Where DayCountBase from security_master.coupon_day_count_conv:
  - ACT/365: 365
  - ACT/360: 360
  - 30/360: 360
  - ACT/ACT: Actual days in year
```

**Tables Updated:**
- `bond_positions` - Accrued interest, market value, unrealized P&L

---

## 2. Interbank Deal - Lending/Borrowing

### Overview
THB placements (lending) and takings (borrowing) with Thai banks.

**Participating Teams:** FO → MO → BO

**Total Time:** Value date to Maturity date

---

### Step 1: Deal Entry (Front Office)

**Responsible:** Front Office Money Market Dealer

| # | Action | Fields to Input/Update | Validation |
|--------|--------|------------------------|------------|
| 1.1 | 👤 Select deal type | `deal_type` = LEND or BORROW | Bank's perspective |
| 1.2 | 👤 Select counterparty | `counterparty_id` | KYC approved |
| 1.3 | 👤 Input principal | `principal_amount` | > 0 |
| 1.4 | 👤 Input value date | `value_date` | >= Trade date |
| 1.5 | 👤 Input maturity date | `maturity_date` | > Value date |
| 1.6 | 👤 Select rate type | `interest_rate_type` = FIXED or FLOATING | - |
| 1.7 | 👤 Input interest rate | `interest_rate` | All-in rate for fixed |
| 1.8 | 👤 If FLOATING | `reference_rate`, `margin`, `reference_rate_tenor` | THOR + spread |
| 1.9 | 👤 Select day count | `day_count_convention` | ACT/365, ACT/360, 30/360 |
| 1.10 | ⚙️ System calculates | `term` | Days between value and maturity |
| 1.11 | ⚙️ System generates | `deal_id` | Auto-generated |
| 1.12 | ⚙️ System sets | `status` = 'PENDING_APPROVAL' | - |

**Floating Rate Setup:**
- If `interest_rate_type` = 'FLOATING':
  - System generates `interbank_interest_schedule`
  - Calculate reset dates based on tenor

**Tables Updated:**
- `interbank_deals` - New record
- `interbank_interest_schedule` - If floating rate

---

### Step 2: Limit Check & Approval (Middle Office)

**Responsible:** Middle Office Risk Manager

| # | Action | Fields to Update | Notes |
|--------|--------|------------------|-------|
| 2.1 | 👤 Review deal | All fields | Check counterparty, amount, tenor |
| 2.2 | ⚙️ Check limit | `limit_utilization` | Placement limit check |
| 2.3 | 👤 Approve/Reject | `status` = 'APPROVED' or 'REJECTED' | Four-eyes approval |
| 2.4 | ⚙️ If approved | Update limit utilization | Record created |

**Tables Updated:**
- `interbank_deals` - Update `status`
- `limit_utilization` - New record

---

### Step 3: Settlement (Back Office)

**Responsible:** Back Office Settlement Officer

| # | Action | Fields to Update | Process |
|--------|--------|------------------|---------|
| 3.1 | 👤 Prepare BAHTNET | - | Generate MT103 |
| 3.2 | 👤 Upload to portal | - | Manual BAHTNET process |
| 3.3 | 👤 Confirm value date | - | Cash moves on value_date |
| 3.4 | 👤 Update status | `status` = 'ACTIVE' | After confirmation |

**Tables Updated:**
- `interbank_deals` - Update `status`

---

### Step 4: Daily Accrual (System - 18:00 Daily)

**Responsible:** System (Automatic)

| # | Action | Fields Updated | Calculation |
|--------|--------|----------------|-------------|
| 4.1 | ⚙️ Calculate daily accrual | `accrued_interest` | Principal × Rate% × (1/DayCountBase) |
| 4.2 | ⚙️ If FLOATING | Check reset date | If today = next_reset_date, fix rate |
| 4.3 | ⚙️ Update schedule | `interbank_interest_schedule` | Update reset_rate, interest_rate |

**Floating Rate Reset:**
- On `next_reset_date`:
  - Get current THOR fixing
  - Calculate new rate: `reset_rate` + `margin`
  - Update `interest_rate`
  - Move `next_reset_date` forward by tenor

**Tables Updated:**
- `interbank_deals` - `accrued_interest`
- `interbank_interest_schedule` - Rate resets

---

### Step 5: Maturity (System + Back Office)

**Responsible:** System (Auto-detect) + Back Office (Confirmation)

| # | Action | Fields Updated | Process |
|--------|--------|----------------|---------|
| 5.1 | ⚙️ Auto-detect | `maturity_date` = Today | System identifies maturing deals |
| 5.2 | ⚙️ Calculate final amount | Principal + Accrued interest | Settlement amount |
| 5.3 | 👤 Receive principal + interest | - | BAHTNET receipt |
| 5.4 | 👤 Confirm settlement | - | Verify amount correct |
| 5.5 | ⚙️ Update status | `status` = 'MATURED' | Auto or manual |
| 5.6 | ⚙️ Release limit | `limit_utilization` | New record (negative) |

**Tables Updated:**
- `interbank_deals` - `status` = 'MATURED'
- `limit_utilization` - Limit released

---

## 3. Repo Trade - Repo/Reverse Repo

### Overview
Sale and repurchase of securities (Repo = lend cash, take collateral; Reverse Repo = borrow cash, give collateral).

**Participating Teams:** FO → MO → BO (Collateral) → BO (Settlement)

**Total Time:** Purchase date to Repurchase date

---

### Step 1: Trade Entry (Front Office)

**Responsible:** Front Office Repo Trader

| # | Action | Fields to Input/Update | Validation |
|--------|--------|------------------------|------------|
| 1.1 | 👤 Select trade type | `trade_type` = Repo, ReverseRepo, Rehypothecation | Bank's perspective |
| 1.2 | 👤 Select counterparty | `counterparty_id` | Must have GMRA agreement |
| 1.3 | 👤 Select GMRA | `netting_agreement_id` | Must exist and be Active |
| 1.4 | 👤 Input nominal | `nominal_amount` | Face value of securities |
| 1.5 | 👤 Input dates | `purchase_date`, `repurchase_date` | Start and end dates |
| 1.6 | 👤 Select rate type | `interest_rate_type` = FIXED or FLOATING | - |
| 1.7 | 👤 Input repo rate | `interest_rate` | Annual repo rate |
| 1.8 | 👤 If FLOATING | `reference_rate`, `margin` | THOR + spread |
| 1.9 | 👤 Select day count | `day_count_convention` | Typically ACT/365 |
| 1.10 | ⚙️ System calculates | `purchase_price` | Cash on day 1 |
| 1.11 | ⚙️ System calculates | `repurchase_price` | Cash on day 2 (includes interest) |
| 1.12 | ⚙️ System generates | `repo_trade_id` | ≥70000 |

**Tables Updated:**
- `repo_trades` - New record

---

### Step 2: Limit Check & Approval (Middle Office)

**Responsible:** Middle Office Risk Manager

| # | Action | Fields to Update | Notes |
|--------|--------|------------------|-------|
| 2.1 | 👤 Review trade | All fields | Check GMRA, counterparty |
| 2.2 | ⚙️ Check repo limit | `limit_utilization` | REPO_LIMIT check |
| 2.3 | 👤 Approve/Reject | `status` | Four-eyes approval |

**Tables Updated:**
- `repo_trades` - Update `status`
- `limit_utilization` - New record

---

### Step 3: Collateral Allocation (Back Office)

**Responsible:** Back Office Collateral Manager

| # | Action | Fields to Input/Update | Process |
|--------|--------|------------------------|---------|
| 3.1 | 👤 Identify required collateral | `nominal_amount`, `haircut_percentage` | Calculate after haircut |
| 3.2 | 👤 Select securities | `security_id` | From available inventory |
| 3.3 | 👤 Input allocated nominal | `nominal_amount` | May be > trade nominal due to haircut |
| 3.4 | ⚙️ Get haircut | `haircut_percentage` | From haircut_matrix |
| 3.5 | ⚙️ Get price | `valuation_price` | From ThaiBMA |
| 3.6 | ⚙️ Calculate market value | `market_value` | Nominal × Price / 100 |
| 3.7 | ⚙️ Calculate after haircut | `collateral_value_after_haircut` | Market value × (1 - Haircut%) |
| 3.8 | ✅ Validate | - | Collateral value must >= Repo exposure |
| 3.9 | 👤 Confirm allocation | - | If valid, proceed |
| 3.10 | ⚙️ Create record | `collateral_id` | Auto-generated |

**Haircut Example:**
```
Trade Nominal: 100,000,000 THB
Required Collateral Value: 100,000,000 THB
Haircut: 2%
Securities Nominal Needed: 100,000,000 / (1 - 0.02) = 102,040,816 THB
```

**Tables Updated:**
- `collateral_positions` - New record(s)

---

### Step 4: Settlement - First Leg (Back Office)

**Responsible:** Back Office Settlement Officer

| # | Action | Fields to Update | Notes |
|--------|--------|------------------|-------|
| 4.1 | 👤 Transfer cash | - | Via BAHTNET |
| 4.2 | 👤 Receive securities | - | Via TSD/BAHTNET |
| 4.3 | 👤 Update status | `status` = 'ACTIVE' | After both legs confirmed |

**For Repo (Bank lending cash):**
- Pay cash, receive securities as collateral

**For Reverse Repo (Bank borrowing cash):**
- Receive cash, pledge securities as collateral

**Tables Updated:**
- `repo_trades` - Update `status`

---

### Step 5: Daily Margin Management (System - 17:00 Daily)

**Responsible:** System (Auto) + Middle Office (Monitoring)

| # | Action | Fields Updated | Process |
|--------|--------|----------------|---------|
| 5.1 | ⚙️ Update collateral prices | `collateral_positions.valuation_price` | From ThaiBMA |
| 5.2 | ⚙️ Recalculate market value | `market_value` | New price × Nominal |
| 5.3 | ⚙️ Recalculate after haircut | `collateral_value_after_haircut` | Apply haircut |
| 5.4 | ⚙️ Calculate exposure | Repo repurchase price | Current obligation |
| 5.5 | ⚙️ Compare | Collateral vs Exposure | If shortfall → Margin call |
| 5.6 | ⚙️ If breach > threshold | Create `margin_calls` | New record |

**Margin Call Creation:**
- `call_type` = 'CALL' (need more collateral) or 'RETURN' (excess collateral)
- `call_amount` = Net amount after MTA/threshold
- `due_time` = T+1 11:00 (per GMRA)
- `status` = 'PENDING'

**Tables Updated:**
- `collateral_positions` - Daily MTM
- `margin_calls` - If threshold breached

---

### Step 6: Margin Call Workflow (Middle Office + Back Office)

**Step 6a: Middle Office Agreement**

**Responsible:** Middle Office Risk Manager

| # | Action | Fields to Update | Notes |
|--------|--------|------------------|-------|
| 6a.1 | 📧 Receive notification | - | Margin call pending |
| 6a.2 | 👤 Review call | `call_amount`, `due_time` | Verify calculation |
| 6a.3 | 👤 Negotiate if needed | - | With counterparty |
| 6a.4 | 👤 Update status | `status` = 'AGREED' | Confirm call |
| 6a.5 | 📧 Notify Back Office | - | Ready for settlement |

**Step 6b: Back Office Settlement**

**Responsible:** Back Office Collateral/Settlement

| # | Action | Fields to Update | Notes |
|--------|--------|------------------|-------|
| 6b.1 | 📧 Receive agreement | - | From Middle Office |
| 6b.2 | 👤 If CASH margin | Create `cash_margin_movements` | PAY or RECEIVE |
| 6b.3 | 👤 If COLLATERAL | Create new `collateral_positions` | Additional securities |
| 6b.4 | 👤 Settle by due time | - | T+1 11:00 |
| 6b.5 | 👤 Update margin status | `margin_calls.status` = 'SETTLED' | After confirmation |
| 6b.6 | 👤 If cash margin | `cash_margin_movements` | Record movement |

**Cash Margin Interest:**
- Posted margin earns interest at GMRA rate
- Daily accrual on `cash_margin_movements.accrued_int_receivable`

**Tables Updated:**
- `margin_calls` - Workflow status
- `cash_margin_movements` - If cash margin posted
- `collateral_positions` - If additional securities posted

---

### Step 7: Collateral Substitution (Optional - Back Office)

**When:** Counterparty requests to substitute collateral

**Responsible:** Back Office Collateral Manager

| # | Action | Fields to Update | Process |
|--------|--------|------------------|---------|
| 7.1 | 👤 Receive substitution request | - | From counterparty |
| 7.2 | 👤 Identify new securities | `security_id` | Proposed replacement |
| 7.3 | ⚙️ Validate new collateral | - | Check eligibility, haircut, value |
| 7.4 | ✅ Check sufficiency | `collateral_value_after_haircut` | Must meet requirement |
| 7.5 | 👤 If valid | Create new `collateral_positions` | New allocation |
| 7.6 | 👤 Release old collateral | Mark old as released | Or delete per policy |
| 7.7 | ⚙️ Recalculate margin | - | Update totals |

**Tables Updated:**
- `collateral_positions` - New allocation + old release

---

### Step 8: Daily Accrual (System - 18:00 Daily)

**Responsible:** System (Automatic)

| # | Action | Fields Updated | Calculation |
|--------|--------|----------------|-------------|
| 8.1 | ⚙️ Calculate repo interest | `repo_trades.accrued_interest` | Cash × RepoRate × (1/365) |
| 8.2 | ⚙️ If floating | Check reset date | Update if needed |
| 8.3 | ⚙️ If cash margin | `cash_margin_movements` | Interest on posted margin |

**Tables Updated:**
- `repo_trades` - `accrued_interest`
- `cash_margin_movements` - Margin interest accrual

---

### Step 9: Maturity/Repurchase (Back Office)

**Responsible:** Back Office Settlement Officer

| # | Action | Fields to Update | Process |
|--------|--------|------------------|---------|
| 9.1 | ⚙️ Auto-detect | `repurchase_date` = Today | System identifies |
| 9.2 | ⚙️ Calculate final | Principal + Accrued interest | Repurchase price |
| 9.3 | 👤 Settle second leg | - | Via BAHTNET/TSD |
| 9.4 | 👤 Return collateral | Release `collateral_positions` | Securities returned |
| 9.5 | 👤 Return cash margin | If any posted | Via `cash_margin_movements` |
| 9.6 | 👤 Update status | `status` = 'MATURED' | Trade complete |
| 9.7 | ⚙️ Release limit | `limit_utilization` | New record (negative) |

**Tables Updated:**
- `repo_trades` - `status` = 'MATURED'
- `collateral_positions` - Released
- `limit_utilization` - Limit released

---

## 4. Scheduled Events (System-Driven)

### 4.1 Coupon Payment Process

**Trigger:** `CURRENT_DATE = coupon_payment_date`

**Frequency:** Per security's `coupon_frequency` (Semi-Annual, Quarterly, etc.)

**Participating Teams:** System (Auto) + Back Office (Verification)

| Step | Action | Responsible | Fields Updated | Process |
|------|--------|-------------|----------------|---------|
| 1 | ⚙️ Identify positions | System | - | All positions with coupon today |
| 2 | ⚙️ Calculate coupon | System | - | Nominal × CouponRate × Frequency |
| 3 | ⚙️ Create transaction | System | `bond_transactions` | Type='Coupon', amount=coupon |
| 4 | ⚙️ Reset accrued interest | System | `bond_positions.accrued_interest` | Set to 0 |
| 5 | ⚙️ Update last coupon | System | `bond_positions.last_coupon_date` | Today |
| 6 | 👤 Verify receipt | Back Office | - | Confirm cash received |
| 7 | ⚙️ Generate GL | System | - | Journal entries |

**Tables Updated:**
- `bond_transactions` - New coupon transaction
- `bond_positions` - Accrued interest reset

---

### 4.2 Bond Maturity Process

**Trigger:** `CURRENT_DATE > maturity_date`

**Participating Teams:** System (Auto) + Back Office (Confirmation)

| Step | Action | Responsible | Fields Updated | Process |
|------|--------|-------------|----------------|---------|
| 1 | ⚙️ Identify maturities | System | - | All bonds past maturity |
| 2 | ⚙️ Update position status | System | `bond_positions.status` | 'MATURED' |
| 3 | ⚙️ Update transaction status | System | `bond_transactions.status` | 'MATURED' |
| 4 | ⚙️ Update security status | System | `security_master.status` | 'MATURED' |
| 5 | 👤 Confirm redemption | Back Office | - | Verify principal received |
| 6 | ⚙️ Final position close | System | - | Archive position |
| 7 | ⚙️ Generate GL | System | - | Redemption entries |

**Tables Updated:**
- `bond_positions` - Status
- `bond_transactions` - Status
- `security_master` - Status

---

## 5. Summary Tables by Team

### Front Office Actions

| Transaction | Action | Fields to Input |
|-------------|--------|-----------------|
| Bond Trade | Create trade | portfolio_id, security_id, counterparty_id, trade_type, nominal_amount, clean_price_trade |
| Interbank | Create deal | deal_type, counterparty_id, principal_amount, value_date, maturity_date, interest_rate_type, interest_rate |
| Repo | Create trade | trade_type, counterparty_id, netting_agreement_id, nominal_amount, purchase_date, repurchase_date, interest_rate_type, interest_rate |

### Middle Office Actions

| Transaction | Action | Fields to Update |
|-------------|--------|------------------|
| All Trades | Four-eyes approval | settlement_status (APPROVED/REJECTED) |
| Margin Calls | Agree to call | status (PENDING → AGREED) |
| Limit Management | Configure limits | limit_utilization (new records) |

### Back Office Actions

| Transaction | Action | Fields to Update |
|-------------|--------|------------------|
| Bond Trade | Confirm settlement | settlement_status (SETTLED/FAILED) |
| Interbank | BAHTNET settlement | status (ACTIVE/MATURED) |
| Repo | Collateral allocation | collateral_positions (CREATE) |
| Repo | Margin settlement | margin_calls.status (SETTLED), cash_margin_movements (CREATE) |
| Repo | Substitution | collateral_positions (CREATE new, RELEASE old) |
| Daily Process | ThaiBMA import | security_master.clean_price |
| All | Maturity processing | status (MATURED) |

### System Actions (Automatic)

| Process | Fields Updated | Frequency |
|---------|----------------|-----------|
| Accrued Interest Calculation | bond_positions.accrued_interest, interbank_deals.accrued_interest, repo_trades.accrued_interest | Daily 18:00 |
| MTM Valuation | bond_positions.market_value, collateral_positions.market_value | Daily 19:00 |
| Margin Calculation | margin_calls (CREATE/UPDATE) | Daily 17:00 |
| Coupon Payment | bond_transactions (CREATE), bond_positions.accrued_interest (RESET) | On coupon date |
| Maturity Processing | status='MATURED' (multiple tables) | On maturity date |
| Limit Utilization | limit_utilization (CREATE) | On trade/maturity |

---

## 6. Process Flow Diagrams

### Bond Trade - Full Lifecycle
```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Step 1    │───→│   Step 2     │───→│   Step 3    │───→│   Step 4     │───→│   Step 5    │
│ Trade Entry │    │ Limit Check  │    │  Approval   │    │ ThaiBMA     │    │ Settlement  │
│    (FO)     │    │   (System)   │    │    (MO)     │    │  Reporting  │    │    (BO)     │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘    └─────────────┘
                                                                                      │
                                                                                      ▼
┌─────────────┐    ┌──────────────┐                                                   │
│   Step 8    │◄───│   Step 7     │◄──────────────────────────────────────────────────┘
│ Daily Batch │    │ Position Upd │
│  (System)   │    │  (System)    │
└─────────────┘    └──────────────┘
```

### Repo Trade - With Margin Call
```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│ Trade Entry │───→│   Approval   │───→│ Collateral  │───→│ Settlement  │
│    (FO)     │    │    (MO)      │    │ Allocation  │    │  1st Leg    │
└─────────────┘    └──────────────┘    │    (BO)     │    │    (BO)     │
                                       └─────────────┘    └──────────────┘
                                                                   │
                              ┌────────────────────────────────────┘
                              ▼
                       ┌──────────────┐
                       │ Daily Margin │◄────────────────────┐
                       │    (System)  │                     │
                       └──────────────┘                     │
                              │                            │
            ┌─────────────────┴─────────────────┐          │
            │ No Breach                         │ Breach   │
            ▼                                   ▼          │
    ┌──────────────┐                    ┌──────────────┐   │
    │   Continue   │                    │ Margin Call  │   │
    │   Accrual    │                    │   Created    │   │
    └──────────────┘                    └──────────────┘   │
                                               │           │
                                               ▼           │
                                        ┌──────────────┐   │
                                        │ MO Agreement │   │
                                        │    (MO)      │   │
                                        └──────────────┘   │
                                               │           │
                                               ▼           │
                                        ┌──────────────┐   │
                                        │ BO Settlement│───┘
                                        │    (BO)      │
                                        └──────────────┘
```

---

**End of Transaction Process Guide**
