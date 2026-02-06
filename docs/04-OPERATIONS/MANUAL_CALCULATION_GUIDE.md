# Manual Calculation Guide - Treasury Management System

**Version:** 1.0  
**Date:** February 5, 2026  
**Purpose:** Manual verification procedures for field calculations - use when debugging errors or validating system outputs

---

## 📋 Table of Contents

1. [Bond Trade Calculations](#1-bond-trade-calculations)
2. [Interbank Deal Calculations](#2-interbank-deal-calculations)
3. [Repo Trade Calculations](#3-repo-trade-calculations)
4. [Position & Costing Calculations](#4-position--costing-calculations)
5. [Daily Batch Calculations](#5-daily-batch-calculations)
6. [Troubleshooting Checklist](#6-troubleshooting-checklist)

---

## 1. Bond Trade Calculations

### 1.1 Accrued Interest

**Purpose:** Calculate interest accrued since last coupon payment

**Formula:**
```
Accrued Interest = Face Value × Coupon Rate × (Days Since Last Coupon / Day Count Base)
```

**Step-by-Step Calculation:**

| Step | Action | Formula / Example |
|------|--------|-------------------|
| 1 | Get face value | From `bond_trades.face_value` |
| 2 | Get coupon rate | From `security_master.coupon_rate` |
| 3 | Get day count convention | From `security_master.coupon_day_count_conv` |
| 4 | Calculate days since last coupon | `(settlement_date - last_coupon_date).days` |
| 5 | Determine day count base | ACT/365 = 365, ACT/360 = 360 |
| 6 | Calculate | `Face × (Coupon%/100) × (Days/Base)` |

**Example:**
```
Face Value:      1,000,000 THB
Coupon Rate:     3.50%
Settlement Date: 2026-02-05
Last Coupon:     2025-11-12
Day Count:       ACT/365

Days = (2026-02-05 - 2025-11-12) = 85 days
Accrued = 1,000,000 × 0.035 × (85/365)
        = 1,000,000 × 0.035 × 0.2329
        = 8,150.68 THB
```

**Verification Check:**
```sql
SELECT face_value, accrued_interest, 
       (face_value * coupon_rate * days_count / day_base) AS manual_calc
FROM bond_trades bt
JOIN security_master sm ON bt.security_id = sm.security_id
WHERE trade_id = 'TRADE_ID';
```

---

### 1.2 Settlement Amount (Dirty Price)

**Purpose:** Total amount to be exchanged on settlement date

**Formula:**
```
Settlement Amount = (Face Value × Clean Price / 100) + Accrued Interest
```

**Step-by-Step:**

| Step | Action | Formula |
|------|--------|---------|
| 1 | Calculate clean amount | `Face Value × Clean Price / 100` |
| 2 | Get accrued interest | From Section 1.1 |
| 3 | Sum both | `Clean Amount + Accrued Interest` |

**Example:**
```
Face Value:    1,000,000 THB
Clean Price:   102.50
Accrued:       8,150.68 THB

Clean Amount = 1,000,000 × 102.50 / 100 = 1,025,000 THB
Settlement   = 1,025,000 + 8,150.68 = 1,033,150.68 THB
```

**Debug Query:**
```sql
SELECT 
    face_value,
    clean_price,
    accrued_interest,
    settlement_amount,
    (face_value * clean_price / 100) + accrued_interest AS manual_settlement
FROM bond_trades
WHERE trade_id = 'TRADE_ID';
```

---

### 1.3 Yield to Maturity (YTM)

**Purpose:** Calculate annualized yield based on purchase price

**Approximation Formula (for verification):**
```
YTM ≈ [Annual Coupon + (Face - Price)/Years to Maturity] / [(Face + Price)/2] × 100
```

**Important:** System uses precise bond math library. This is for rough verification only.

**Example:**
```
Face Value:     1,000,000
Purchase Price: 1,025,000 (from clean price 102.50)
Annual Coupon:  35,000 (3.5% of face)
Years to Maturity: 10

YTM ≈ [35,000 + (1,000,000 - 1,025,000)/10] / [(1,000,000 + 1,025,000)/2] × 100
    ≈ [35,000 - 2,500] / [1,012,500] × 100
    ≈ 32,500 / 1,012,500 × 100
    ≈ 3.21%
```

**Verification:** System YTM should be close to this approximation (within 0.1%)

---

## 2. Interbank Deal Calculations

### 2.1 Interest Amount (Fixed Rate)

**Purpose:** Calculate total interest for the deal term

**Formula:**
```
Interest = Principal × Interest Rate × (Tenor Days / Day Count Base)
```

**Step-by-Step:**

| Step | Action | Formula |
|------|--------|---------|
| 1 | Get principal | `interbank_deals.principal_amount` |
| 2 | Get annual rate | `interbank_deals.interest_rate` |
| 3 | Calculate tenor | `(maturity_date - start_date).days` |
| 4 | Get day count base | ACT/365 = 365, ACT/360 = 360 |
| 5 | Calculate | `Principal × (Rate/100) × (Tenor/Base)` |

**Example:**
```
Principal:     100,000,000 THB
Interest Rate: 2.25%
Start Date:    2026-02-05
Maturity Date: 2026-05-05
Day Count:     ACT/365

Tenor = 89 days
Interest = 100,000,000 × 0.0225 × (89/365)
         = 100,000,000 × 0.0225 × 0.2438
         = 548,630.14 THB
```

**Manual Verification Query:**
```sql
SELECT 
    principal_amount,
    interest_rate,
    (maturity_date - start_date) AS tenor_days,
    interest_amount,
    ROUND(principal_amount * (interest_rate/100) * 
          ((maturity_date - start_date)::numeric / 365), 2) AS manual_interest
FROM interbank_deals
WHERE deal_id = 'DEAL_ID';
```

---

### 2.2 Daily Accrued Interest

**Purpose:** Calculate interest accrued to date (for active deals)

**Formula:**
```
Daily Accrual = Principal × Interest Rate × (1 / Day Count Base)
Accrued To Date = Daily Accrual × Days Since Start
```

**Example:**
```
Principal:     100,000,000 THB
Interest Rate: 2.25%
Start Date:    2026-02-05
Today:         2026-02-20

Daily Accrual = 100,000,000 × 0.0225 × (1/365) = 6,164.38 THB/day
Days Active   = 15 days
Accrued       = 6,164.38 × 15 = 92,465.75 THB
```

**Debug Steps:**
1. Check `interbank_deals.accrued_interest` field
2. Verify `last_accrual_date` is current
3. Recalculate manually using formula above
4. If mismatch > 0.01 THB, check for rate resets (floating rate deals)

---

### 2.3 Floating Rate Reset

**Purpose:** Verify floating rate recalculation after THOR reset

**Formula:**
```
New Interest Rate = THOR Rate + Spread (in bps)
```

**Step-by-Step:**

| Step | Action | Example |
|------|--------|---------|
| 1 | Get new THOR rate | e.g., 2.15% |
| 2 | Get spread from deal | e.g., 10 bps = 0.10% |
| 3 | Calculate new rate | 2.15% + 0.10% = 2.25% |
| 4 | Update accrued interest | Use new rate from reset date |

**Verification Query:**
```sql
SELECT 
    d.deal_id,
    d.interest_rate AS current_rate,
    s.reset_rate AS thor_rate,
    d.spread,
    (s.reset_rate + d.spread) AS manual_new_rate
FROM interbank_deals d
JOIN interbank_interest_schedule s ON d.deal_id = s.deal_id
WHERE s.reset_date = CURRENT_DATE;
```

---

## 3. Repo Trade Calculations

### 3.1 Repo Interest

**Purpose:** Calculate interest for repo period

**Formula:**
```
Repo Interest = Near Leg Amount × Repo Rate × (Tenor / Day Count Base)
```

**Example:**
```
Near Leg Amount: 100,000,000 THB
Repo Rate:       2.50%
Start Date:      2026-02-03
End Date:        2026-02-23
Tenor:           20 days

Interest = 100,000,000 × 0.025 × (20/365)
         = 100,000,000 × 0.025 × 0.0548
         = 136,986.30 THB
```

---

### 3.2 Far Leg Amount

**Purpose:** Calculate repurchase amount at maturity

**Formula:**
```
Far Leg = Near Leg + Repo Interest
```

**Example:**
```
Near Leg:   100,000,000 THB
Interest:   136,986.30 THB
Far Leg:    100,136,986.30 THB
```

---

### 3.3 Collateral Value After Haircut

**Purpose:** Verify collateral valuation for margin

**Formula:**
```
Market Value = Face Value × (Market Price / 100)
Collateral Value = Market Value × (1 - Haircut%)
```

**Step-by-Step:**

| Step | Action | Formula |
|------|--------|---------|
| 1 | Get face value | `collateral_face_value` |
| 2 | Get current market price | `security_master.clean_price` or EOD price |
| 3 | Calculate market value | `Face × (Price/100)` |
| 4 | Apply haircut | `Market Value × (1 - Haircut%/100)` |

**Example:**
```
Face Value:    100,000,000 THB
Market Price:  102.50
Haircut:       2.0%

Market Value    = 100,000,000 × 1.025 = 102,500,000 THB
Collateral Value = 102,500,000 × (1 - 0.02) = 100,450,000 THB
```

---

### 3.4 Margin Percentage

**Purpose:** Verify collateral coverage vs cash lent

**Formula:**
```
Margin % = (Collateral Value / Near Leg Amount) × 100
```

**Example:**
```
Collateral Value:   100,450,000 THB
Near Leg Amount:    100,000,000 THB

Margin % = (100,450,000 / 100,000,000) × 100 = 100.45%
```

**Margin Call Trigger:**
```
If Margin % < (100% + Threshold%)
Then Margin Call Required

Example with 2% threshold:
Required: 102%
Current:  100.45%
Shortfall: 1.55% → Margin call triggered
```

---

### 3.5 Margin Call Amount

**Purpose:** Calculate additional collateral needed

**Formula:**
```
Required Collateral = Near Leg × (1 + Required Margin%)
Margin Call Amount = Required Collateral - Current Collateral Value
```

**Example:**
```
Near Leg:             100,000,000 THB
Required Margin:      102% (100% + 2% threshold)
Current Collateral:   100,450,000 THB

Required = 100,000,000 × 1.02 = 102,000,000 THB
Call Amount = 102,000,000 - 100,450,000 = 1,550,000 THB
```

---

## 4. Position & Costing Calculations

### 4.1 Weighted Average Cost (WAC) - After Buy

**Purpose:** Calculate new average cost after purchase

**Formula:**
```
New Total Cost = (Old WAC × Old Nominal) + (New Price × New Nominal)
New Total Nominal = Old Nominal + New Nominal
New WAC = New Total Cost / New Total Nominal
```

**Example:**
```
Existing Position:
  Nominal: 5,000,000 THB
  WAC:     101.25

New Purchase:
  Nominal: 2,000,000 THB
  Price:   102.00

New Total Cost = (101.25 × 5M) + (102.00 × 2M)
               = 506,250,000 + 204,000,000
               = 710,250,000
New Total Nominal = 5M + 2M = 7,000,000 THB
New WAC = 710,250,000 / 7,000,000 = 101.4643
```

**Debug Query:**
```sql
SELECT 
    position_id,
    nominal_amount,
    avg_book_clean_price_pct,
    sum_product_clean,
    total_nominal_in,
    (sum_product_clean / total_nominal_in) AS manual_wac
FROM position_costing
WHERE position_id = 'POSITION_ID';
```

---

### 4.2 Realized P&L (Sell Trade)

**Purpose:** Calculate profit/loss from sale

**Formula:**
```
Realized P&L = (Sell Price - WAC) × Sold Nominal / 100
```

**Example:**
```
WAC:          101.4643
Sell Price:   103.00
Sold Nominal: 3,000,000 THB

P&L = (103.00 - 101.4643) × 3,000,000 / 100
    = 1.5357 × 30,000
    = 46,071 THB (Profit)
```

**Journal Entry Verification:**
```
Debit: Cash                    3,090,000 (103 × 3M / 100)
Credit: Bond Position          3,043,929 (WAC × 3M / 100)
Credit: Realized Gain           46,071
```

---

### 4.3 Unrealized P&L (Mark-to-Market)

**Purpose:** Calculate paper gain/loss on holding

**Formula:**
```
Market Value = (Clean Price × Nominal / 100) + Accrued Interest
Book Value = WAC × Nominal / 100
Unrealized P&L = Market Value - Book Value
```

**Example:**
```
Nominal:       4,000,000 THB (remaining after sale)
WAC:           101.4643
Current Price: 102.75
Accrued:       6,849.32 THB

Market Value = (102.75 × 4M / 100) + 6,849.32
             = 4,110,000 + 6,849.32 = 4,116,849.32

Book Value = 101.4643 × 4M / 100 = 4,058,572

Unrealized P&L = 4,116,849.32 - 4,058,572 = 58,277.32 THB (Gain)
```

---

## 5. Daily Batch Calculations

### 5.1 Accrued Interest Update (Daily)

**Purpose:** Verify daily batch interest accrual

**Formula:**
```
Daily Accrual = Nominal × Coupon Rate × (1 / Day Count Base)
New Accrued = Previous Accrued + Daily Accrual
```

**Batch Verification Steps:**

1. **Before batch:** Record `accrued_interest` values
2. **Run batch:** Execute daily accrual job
3. **Verify:** 
   ```sql
   SELECT 
       position_id,
       accrued_interest,
       LAG(accrued_interest) OVER (ORDER BY valuation_date) AS prev_accrued,
       (nominal * coupon_rate / 365) AS expected_daily
   FROM bond_positions
   WHERE security_id = 'SECURITY_ID'
   ORDER BY valuation_date DESC
   LIMIT 2;
   ```
4. **Check:** Difference should equal expected daily accrual

---

### 5.2 Market Value Update

**Purpose:** Verify MTM calculation after price import

**Formula:**
```
Market Value = (Clean Price × Nominal / 100) + Accrued Interest
```

**Verification Query:**
```sql
SELECT 
    bp.position_id,
    bp.nominal_amount,
    sm.clean_price AS market_price,
    bp.accrued_interest,
    bp.market_value AS system_value,
    ROUND((bp.nominal_amount * sm.clean_price / 100) + bp.accrued_interest, 2) AS manual_value
FROM bond_positions bp
JOIN security_master sm ON bp.security_id = sm.security_id
WHERE bp.position_id = 'POSITION_ID';
```

---

### 5.3 Limit Utilization Calculation

**Purpose:** Verify counterparty limit usage

**Formula:**
```
Utilization % = (Used Amount / Total Credit Line) × 100
Available = Total Credit Line - Used Amount
```

**Example:**
```
Credit Line:    500,000,000 THB
Active Deals:   320,000,000 THB
Pending Deals:   50,000,000 THB

Used Amount = 320M + 50M = 370,000,000 THB
Utilization = (370M / 500M) × 100 = 74%
Available   = 500M - 370M = 130,000,000 THB
```

**Verification Query:**
```sql
SELECT 
    counterparty_id,
    limit_type,
    total_credit_line,
    available_line,
    (total_credit_line - available_line) AS used_amount,
    ((total_credit_line - available_line) / total_credit_line * 100) AS util_pct
FROM limit_utilization
WHERE counterparty_id = 'CPTY_ID'
ORDER BY timestamp DESC
LIMIT 1;
```

---

## 6. Troubleshooting Checklist

### 6.1 General Verification Steps

```
□ Step 1: Identify the field with incorrect value
□ Step 2: Get all input parameters from database
□ Step 3: Perform manual calculation using this guide
□ Step 4: Compare manual result with system value
□ Step 5: If difference > 0.01 THB, investigate further
□ Step 6: Check for rounding differences
□ Step 7: Check for timing issues (batch not run, stale data)
□ Step 8: Check for missing records (accrued not updated, etc.)
```

---

### 6.2 Common Error Patterns

| Symptom | Likely Cause | Verification |
|---------|-------------|--------------|
| Accrued interest too low | Last coupon date incorrect | Check `security_master.coupon_dates` |
| Settlement amount mismatch | Wrong day count convention | Verify `coupon_day_count_conv` |
| WAC calculation error | Missing previous position | Check `position_costing` history |
| Realized P&L incorrect | Wrong WAC used | Verify `last_realization_date` |
| Repo margin wrong | Stale price data | Check `valuation_date` on collateral |
| Limit utilization off | Missing deals in calc | Sum all active deals manually |
| Floating rate wrong | THOR rate not updated | Check `interbank_interest_schedule` |

---

### 6.3 Data Quality Checks

**Check for orphaned records:**
```sql
-- Trades without positions
SELECT bt.trade_id, bt.status
FROM bond_trades bt
LEFT JOIN bond_positions bp ON bt.portfolio_id = bp.portfolio_id 
    AND bt.security_id = bp.security_id
WHERE bt.status = 'SETTLED' 
    AND bp.position_id IS NULL;

-- Positions without trades
SELECT bp.position_id
FROM bond_positions bp
LEFT JOIN bond_trades bt ON bp.portfolio_id = bt.portfolio_id 
    AND bp.security_id = bt.security_id
WHERE bp.nominal_amount > 0
    AND bt.trade_id IS NULL;
```

**Check for negative values:**
```sql
-- Invalid negative amounts
SELECT * FROM bond_trades 
WHERE face_value < 0 
    OR clean_price < 0 
    OR accrued_interest < 0;

SELECT * FROM bond_positions 
WHERE nominal_amount < 0 
    OR book_value < 0;
```

---

### 6.4 Emergency Recalculation Procedures

**If bond position is incorrect:**

1. **Backup current data:**
   ```sql
   CREATE TABLE bond_positions_backup AS SELECT * FROM bond_positions;
   ```

2. **Recalculate from trades:**
   ```sql
   -- Sum all buys and sells by portfolio/security
   SELECT 
       portfolio_id,
       security_id,
       SUM(CASE WHEN trade_side = 'BUY' THEN face_value ELSE -face_value END) AS net_nominal,
       SUM(CASE WHEN trade_side = 'BUY' THEN face_value * clean_price ELSE 0 END) / 
           SUM(CASE WHEN trade_side = 'BUY' THEN face_value ELSE 0 END) AS wac
   FROM bond_trades
   WHERE status = 'SETTLED'
   GROUP BY portfolio_id, security_id;
   ```

3. **Update position:**
   ```sql
   UPDATE bond_positions 
   SET nominal_amount = [calculated_nominal],
       book_value = [calculated_book_value],
       last_updated_timestamp = NOW()
   WHERE position_id = 'POSITION_ID';
   ```

4. **Verify and document:**
   - Compare with manual calculation
   - Document reason for discrepancy
   - Update procedures if needed

---

## 📎 Quick Reference Card

### Day Count Conventions

| Convention | Formula | Use Case |
|------------|---------|----------|
| ACT/365 | Actual days / 365 | Most THB bonds |
| ACT/360 | Actual days / 360 | Some interbank |
| 30/360 | 30-day months / 360 | Some corporate |
| ACT/ACT | Actual / Actual year days | Government bonds |

### Common Formulas Summary

| Calculation | Formula |
|-------------|---------|
| Accrued Interest | `Face × Coupon% × (Days/Base)` |
| Settlement Amount | `(Face × Clean/100) + Accrued` |
| Repo Interest | `Near × Rate% × (Tenor/Base)` |
| Far Leg | `Near + Interest` |
| WAC (Buy) | `(OldCost + NewCost) / (OldQty + NewQty)` |
| Realized P&L | `(Sell - WAC) × Qty / 100` |
| Unrealized P&L | `Market - Book` |
| Margin % | `(Collateral / Loan) × 100` |

---

**Document End**

*For technical support, verify calculations using this guide before escalating.*
