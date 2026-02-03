# Field Update Matrix - Treasury Management System

**Purpose:** Comprehensive reference showing which fields are updated when, by what process, and under what conditions.

**Related Documents:**
- [Treasury System Detailed Design Input](./Treasury_System_Detailed_Design_Input.md) - Main design document with team responsibilities and table structures

**Last Updated:** February 3, 2026

---

## 📋 Legend

| Symbol | Meaning |
|--------|---------|
| 🔄 | Daily Batch Update |
| 📝 | Deal Input (Trade Capture) |
| ⏱️ | Real-time Event |
| 📅 | Scheduled Event (Coupon, Maturity) |
| 👤 | Manual Update (Back Office/Middle Office) |
| 🔒 | System Calculated (Immutable after set) |

---

## 1. Master Data Tables

### 1.1 entity_master

| Field | Update Type | When | By Whom | Notes |
|-------|-------------|------|---------|-------|
| `entity_id` | 🔒 | Onboarding | IT Admin | Immutable once set |
| `entity_name` | 👤 | Name change | Back Office + Approval | Rare |
| `entity_short_name` | 👤 | Rebranding | Back Office | Rare |
| `entity_type` | 👤 | Rating change | Credit Risk | When rating changes |
| `industry_sector` | 👤 | Annual review | Credit Risk | Annual |
| `country_code` | 🔒 | Onboarding | IT Admin | Rarely changes |
| `juristic_registration_number` | 🔒 | Onboarding | IT Admin | Never changes |
| `registered_capital_amount` | 👤 | Capital change | Back Office | When reported |
| `financials_currency` | 🔒 | Onboarding | IT Admin | Fixed |
| `g_sib_type` | 👤 | BOT update | IT Admin | When BOT updates |
| `created_date` | 🔒 | Creation | System | Auto |
| `last_updated_date` | ⏱️ | Any change | System | Auto timestamp |

**Update Frequency:** Mostly static, updates on counterparty lifecycle events

---

### 1.2 counterparty_master

| Field | Update Type | When | By Whom | Notes |
|-------|-------------|------|---------|-------|
| `entity_id` | 🔒 | Onboarding | System | FK to entity_master |
| `counterparty_id` | 🔒 | Onboarding | System | Auto-generated |
| `legal_name` | 👤 | Name change | Back Office | Rare |
| `short_code` | 🔒 | Onboarding | Back Office | Fixed |
| `counterparty_type` | 👤 | Reclassification | Credit Risk | Rare |
| `bank_code` | 🔒 | Onboarding | IT Admin | BOT code |
| `swift_bic` | 👤 | BIC change | Back Office | Rare |
| `primary_credit_rating` | 👤 | Rating update | Back Office | On rating agency update |
| `primary_rating_agency` | 👤 | Rating update | Back Office | On rating agency update |
| `primary_rating_date` | 👤 | Rating update | Back Office | On rating agency update |
| `created_date` | 🔒 | Creation | System | Auto |
| `last_updated_date` | ⏱️ | Any change | System | Auto timestamp |
| `involved_party_type` | 🔒 | Onboarding | IT Admin | BOT classification |
| `customer_code` | 🔒 | Onboarding | IT Admin | Internal code |
| `reside_in_thailand_flag` | 🔒 | Onboarding | IT Admin | MFSMCG rule |

**Update Frequency:** Static + Rating updates (event-driven)

---

### 1.3 security_master

| Field | Update Type | When | By Whom | Notes |
|-------|-------------|------|---------|-------|
| `security_id` | 🔒 | New issue | IT Admin | ThaiBMA symbol |
| `isin` | 🔒 | New issue | IT Admin | Fixed |
| `issuer_id` | 🔒 | New issue | IT Admin | 1=Govt, 2=BOT, 3=SOE, 4=Corp |
| `unique_id` | 🔒 | New issue | IT Admin | BOT report ID |
| `instrument_type` | 🔒 | New issue | IT Admin | T-Bill, Gov Bond, Corp Bond, etc. |
| `issue_date` | 🔒 | New issue | IT Admin | Fixed |
| `maturity_date` | 🔒 | New issue | IT Admin | Fixed |
| `coupon_rate` | 🔒 | New issue | IT Admin | Fixed |
| `coupon_margin` | 🔒 | New issue | IT Admin | For floating rate |
| `coupon_reference_rate` | 🔒 | New issue | IT Admin | For floating rate |
| `coupon_frequency` | 🔒 | New issue | IT Admin | Semi-Annual, Quarterly |
| `coupon_day_count_conv` | 🔒 | New issue | IT Admin | ACT/365, 30/360, etc. |
| `currency` | 🔒 | New issue | IT Admin | THB |
| `country` | 🔒 | New issue | IT Admin | TH |
| `bond_structure` | 🔒 | New issue | IT Admin | ZERO, Bullet, Amortizing |
| `rating_tris` | 👤 | Rating change | Back Office | On TRIS update |
| `rating_fitch` | 👤 | Rating change | Back Office | On Fitch update |
| `is_eligible_bot_repo_collateral` | 👤 | Policy change | Back Office | When policy changes |
| `is_eligible_crm_collateral` | 👤 | Policy change | Back Office | When policy changes |
| `status` | 📅 | Maturity/Default | System | Auto on maturity date |
| `status_timestamp` | ⏱️ | Status change | System | Auto timestamp |
| `coupon_rate_type` | 🔒 | New issue | IT Admin | Fixed or Floating |
| `cross_default` | 👤 | Default event | Back Office | On cross-default event |

**Special Update Cases:**
- **Status = Matured:** Automatically set when `CURRENT_DATE > maturity_date`
- **Daily Price Update:** Does NOT update security_master directly - updates bond_positions via batch

---

### 1.4 portfolio_master

| Field | Update Type | When | By Whom | Notes |
|-------|-------------|------|---------|-------|
| `portfolio_id` | 🔒 | Creation | System | Auto-generated |
| `portfolio_name` | 👤 | Creation/Change | IT Admin | Treasury approval required |
| `portfolio_manager` | 👤 | Assignment | IT Admin | When trader changes |
| `accounting_treatment` | 🔒 | Creation | IT Admin | AMC, FVOCI, FVTPL - requires approval |
| `created_timestamp` | 🔒 | Creation | System | Auto |

**Update Frequency:** Rare - only when new portfolio created or manager changes

---

### 1.5 netting_agreement

| Field | Update Type | When | By Whom | Notes |
|-------|-------------|------|---------|-------|
| `netting_agreement_id` | 🔒 | Agreement signed | Back Office | GMRA_YYYY_CP |
| `counterparty_id` | 🔒 | Agreement signed | Back Office | Links to counterparty |
| `netting_set_id` | 🔒 | Agreement signed | Back Office | Logical ID |
| `agreement_type` | 🔒 | Agreement signed | Back Office | GMRA, ISDA, CSA |
| `netting_type` | 🔒 | Agreement signed | Back Office | CLOSE_OUT, COLLATERAL, SET_OFF |
| `collateral_contract_type` | 🔒 | Agreement signed | Back Office | REP, BAL, OTC |
| `trade_date` | 🔒 | Agreement signed | Back Office | Signature date |
| `value_date` | 🔒 | Agreement signed | Back Office | Effective date |
| `maturity_date` | 🔒 | Agreement signed | Back Office | Expiry date |
| `is_replacement` | 🔒 | Agreement signed | Back Office | 1=replaces earlier |
| `replaced_agreement_id` | 🔒 | If replacement | Back Office | Previous agreement |
| `settlement_currency` | 🔒 | Agreement signed | Back Office | THB |
| `created_at` | 🔒 | Creation | System | Auto |
| `updated_at` | ⏱️ | Any change | System | Auto timestamp |
| `agreement_status` | 👤 | Status change | Back Office | Active, Matured, In-Default |

**Update Frequency:** Static + status updates on agreement lifecycle

---

## 2. Transaction Tables

### 2.1 bond_trades

| Field | Update Type | When | By Whom | Notes |
|-------|-------------|------|---------|-------|
| `bond_trade_id` | 🔒 | Trade capture | System | ≥90000, auto-generated |
| `portfolio_id` | 📝 | Trade capture | Front Office | Selected from dropdown |
| `trade_date` | 📝 | Trade capture | Front Office | Must be business day |
| `settlement_date` | 🔒 | Trade capture | System | T+2 auto, editable with override |
| `security_id` | 📝 | Trade capture | Front Office | Must exist in security_master |
| `counterparty_id` | 📝 | Trade capture | Front Office | KYC must be APPROVED |
| `trade_type` | 📝 | Trade capture | Front Office | Buy or Sell |
| `nominal_amount` | 📝 | Trade capture | Front Office | > 0, multiple of 1,000 |
| `clean_price_trade` | 📝 | Trade capture | Front Office | ±10% from last price warning |
| `yield_to_maturity` | 🔒 | Trade capture | System | Auto-calculated |
| `settlement_status` | 👤/📅 | Settlement | Back Office/System | Pending → Settled/Failed |

**Settlement Status Workflow:**
```
CREATED → PENDING_APPROVAL → APPROVED → CONFIRMED → SETTLED
                                      ↓
                                   FAILED (Back Office updates)
```

**Special Update Cases:**
- **TSD Settlement (Corporate Bonds):** `settlement_status` updated when MT544/MT545 received
- **BAHTNET Settlement (Govt Bonds):** `settlement_status` updated after manual portal confirmation
- **Failed Settlement:** Back Office manually updates to 'Failed' and handles exception

---

### 2.2 bond_transactions

| Field | Update Type | When | By Whom | Notes |
|-------|-------------|------|---------|-------|
| `trade_id` | 🔒 | Trade capture | System | ≥90000 or CPN_ prefix |
| `security_id` | 📝 | Trade capture | Front Office | From trade |
| `portfolio_id` | 📝 | Trade capture | Front Office | From trade |
| `counterparty_id` | 📝 | Trade capture | Front Office | From trade |
| `trade_type` | 📝 | Trade capture | Front Office | Buy, Sell, Repo, ReverseRepo, **Coupon** |
| `trade_date` | 📝 | Trade capture | Front Office | Execution date |
| `settlement_date` | 🔒 | Trade capture | System | T+2 |
| `maturity_date` | 🔒 | Trade capture | System | From security_master |
| `currency` | 🔒 | Trade capture | System | THB |
| `nominal_amount` | 📝 | Trade capture | Front Office | Face value |
| `clean_price` | 🔄 | Daily batch | System | From ThaiBMA EOD |
| `clean_price_trade` | 🔒 | Trade capture | Front Office | Trade price |
| `accrued_interest` | 🔄 | Daily batch | System | Calculated daily |
| `dirty_price` | 🔒 | Trade capture | System | Clean + Accrued |
| `classification` | 🔒 | Trade capture | System | From portfolio_master |
| `book_value` | 🔄 | Daily batch | System | Clean Price × Nominal / 100 |
| `market_clean_value` | 🔄 | Daily batch | System | Market price × Nominal |
| `market_value` | 🔄 | Daily batch | System | Market clean + Accrued |
| `last_coupon_date` | 📅 | Coupon payment | System | Updated on coupon date |
| `coupon_rate_type` | 🔒 | Trade capture | System | From security_master |
| `coupon_reference_rate` | 🔒 | Trade capture | System | From security_master |
| `coupon_margin` | 🔒 | Trade capture | System | From security_master |
| `coupon_frequency` | 🔒 | Trade capture | System | From security_master |
| `coupon_rate` | 🔒 | Trade capture | System | From security_master |
| `coupon_day_count_conv` | 🔒 | Trade capture | System | From security_master |
| `rating_tris` | 🔄/👤 | Daily/Rating chg | System/Back Office | Auto or manual update |
| `rating_fitch` | 🔄/👤 | Daily/Rating chg | System/Back Office | Auto or manual update |
| `status` | 👤/📅 | Lifecycle | System/Back Office | Active, Matured, In-Default |
| `last_updated_timestamp` | ⏱️ | Any update | System | Auto timestamp |
| `valuation_date` | 🔄 | Daily batch | System | Last valuation date |

**Special Update Cases:**
- **Coupon Payment:** New transaction created with `trade_type = 'Coupon'`, `accrued_interest` reset to 0
- **Maturity:** `status = 'Matured'` auto-set when `CURRENT_DATE > maturity_date`
- **Daily Price:** `clean_price`, `market_value` updated from ThaiBMA EOD file

---

### 2.3 interbank_deals

| Field | Update Type | When | By Whom | Notes |
|-------|-------------|------|---------|-------|
| `deal_id` | 🔒 | Deal capture | System | Auto-generated |
| `trade_date` | 📝 | Deal capture | Front Office | Timestamp GMT+7 |
| `value_date` | 📝 | Deal capture | Front Office | Start date |
| `maturity_date` | 📝 | Deal capture | Front Office | End date |
| `deal_type` | 📝 | Deal capture | Front Office | Lend or Borrow |
| `counterparty_id` | 📝 | Deal capture | Front Office | Links to counterparty |
| `principal_amount` | 📝 | Deal capture | Front Office | Notional |
| `currency` | 🔒 | Deal capture | System | THB |
| `reference_rate_id` | 🔒 | Deal capture | System | THOR + Tenor + DealID |
| `interest_rate_type` | 📝 | Deal capture | Front Office | Fixed or Floating |
| `interest_rate` | 📝/🔄 | Deal capture/Reset | Front Office/System | Current applicable rate |
| `reference_rate_tenor` | 📝 | Deal capture | Front Office | O/N, 1M, 3M, 6M |
| `reference_rate` | 📝 | Deal capture | Front Office | THOR, THORA, SOFR, FIX |
| `margin` | 📝 | Deal capture | Front Office | Spread over reference |
| `reset_rate` | 🔄 | Rate reset | System | Benchmark fixing |
| `last_reset_date` | 🔄 | Rate reset | System | Start of period |
| `next_reset_date` | 🔄 | Rate reset | System | End of period |
| `day_count_convention` | 📝 | Deal capture | Front Office | ACT/365, etc. |
| `accrued_interest` | 🔄 | Daily batch | System | Calculated daily |
| `status` | 👤/📅 | Lifecycle | Back Office/System | Active, Matured, Defaulted |
| `confirmation_ref` | 👤 | Confirmation | Back Office | ISO 20022 ref |
| `limit_id` | 🔒 | Deal capture | System | Links to limit_utilization |
| `term` | 🔒 | Deal capture | System | Days between value_date and maturity_date |
| `entity_id` | 🔒 | Deal capture | System | From counterparty |

**Special Update Cases:**
- **Floating Rate Reset:** `reset_rate`, `interest_rate`, `last_reset_date`, `next_reset_date` updated on reset date
- **Daily Accrual:** `accrued_interest` updated daily at 18:00 batch
- **Maturity:** `status = 'Matured'` on maturity_date, limit released

---

### 2.4 interbank_interest_schedule

| Field | Update Type | When | By Whom | Notes |
|-------|-------------|------|---------|-------|
| `schedule_id` | 🔒 | Schedule gen | System | Auto-generated |
| `referencerate_id` | 🔒 | Schedule gen | System | Links to deal |
| `deal_id` | 🔒 | Schedule gen | System | Parent deal |
| `last_reset_date` | 🔄 | Rate reset | System | Start of period |
| `next_reset_date` | 🔄 | Rate reset | System | End/next reset |
| `reset_rate` | 🔄 | Rate reset | System | Benchmark fixing |
| `interest_rate` | 🔄 | Rate reset | System | ResetRate + Margin |
| `status` | 🔄 | Schedule lifecycle | System | Active, Planned, Closed |

**Update Frequency:** On each rate reset for floating rate deals

---

### 2.5 repo_trades

| Field | Update Type | When | By Whom | Notes |
|-------|-------------|------|---------|-------|
| `repo_trade_id` | 🔒 | Trade capture | System | ≥70000, auto-generated |
| `trade_date` | 📝 | Trade capture | Front Office | Timestamp GMT+7 |
| `trade_type` | 📝 | Trade capture | Front Office | Repo, ReverseRepo, Rehypothecation |
| `counterparty_id` | 📝 | Trade capture | Front Office | Links to counterparty |
| `netting_agreement_id` | 📝 | Trade capture | Front Office | GMRA/CSA agreement |
| `netting_set_id` | 📝 | Trade capture | Front Office | Netting set |
| `nominal_amount` | 📝 | Trade capture | Front Office | Face value |
| `purchase_date` | 📝 | Trade capture | Front Office | Start date |
| `repurchase_date` | 📝 | Trade capture | Front Office | End date (nullable for open) |
| `purchase_price` | 🔒 | Trade capture | System | Calculated |
| `repurchase_price` | 🔒 | Trade capture | System | Calculated |
| `currency` | 🔒 | Trade capture | System | THB |
| `reference_rate_id` | 🔒 | Trade capture | System | Reference rate + repo_trade_id |
| `interest_rate_type` | 📝 | Trade capture | Front Office | Fixed or Floating |
| `interest_rate` | 📝 | Trade capture | Front Office | Current repo rate |
| `reference_rate` | 📝 | Trade capture | Front Office | THOR, THORA, SOFR, FIX |
| `margin` | 📝 | Trade capture | Front Office | Spread for floating |
| `day_count_convention` | 📝 | Trade capture | Front Office | ACT/365 |
| `repo_rate` | 🔒 | Trade capture | System | Implied repo rate |
| `term` | 🔒 | Trade capture | System | Days |
| `repo_out_flag` | 🔒 | Trade capture | System | 1=securities out |
| `repo_in_flag` | 🔒 | Trade capture | System | 1=securities in |
| `status` | 👤/📅 | Lifecycle | Back Office/System | Active, Matured, In-Default |
| `limit_id` | 🔒 | Trade capture | System | Links to limit_utilization |
| `accrued_interest` | 🔄 | Daily batch | System | Calculated daily |
| `entity_id` | 🔒 | Trade capture | System | From counterparty |

**Special Update Cases:**
- **Open Repo:** `repurchase_date` is NULL, runs until terminated
- **Daily Accrual:** `accrued_interest` updated daily at 18:00 batch
- **Maturity:** `status = 'Matured'` on `repurchase_date`, collateral released

---

## 3. Position & Collateral Tables

### 3.1 collateral_positions

| Field | Update Type | When | By Whom | Notes |
|-------|-------------|------|---------|-------|
| `collateral_id` | 🔒 | Allocation | System | RepoTradeID_SecurityID_seq |
| `repo_trade_id` | 🔒 | Allocation | Back Office | Parent repo trade |
| `security_id` | 🔒 | Allocation | Back Office | Allocated security |
| `nominal_amount` | 🔒 | Allocation | Back Office | Face value pledged |
| `allocation_date` | 🔒 | Allocation | System | Date allocated |
| `valuation_price` | 🔄 | Daily batch | System | Clean price from ThaiBMA |
| `market_value` | 🔄 | Daily batch | System | Nominal × Price + Accrued |
| `haircut_percentage` | 🔒 | Allocation | System | From haircut_matrix |
| `collateral_value_after_haircut` | 🔄 | Daily batch | System | Market value × (1 - Haircut) |
| `margin_call_id` | 👤 | Margin call | System | Links if from margin call |
| `currency` | 🔒 | Allocation | System | THB |

**Special Update Cases:**
- **Daily MTM:** `valuation_price`, `market_value`, `collateral_value_after_haircut` updated daily
- **Collateral Substitution:** Old collateral released, new collateral record created
- **Margin Call:** New collateral may be allocated with `margin_call_id` populated

---

### 3.2 bond_positions

| Field | Update Type | When | By Whom | Notes |
|-------|-------------|------|---------|-------|
| `position_id` | 🔒 | Position creation | System | Auto-generated |
| `security_id` | 🔒 | Position creation | System | Security identifier |
| `portfolio_id` | 🔒 | Position creation | System | Portfolio classification |
| `open_date` | 🔒 | Position creation | System | Creation date |
| `maturity_date` | 🔒 | Position creation | System | From security_master |
| `currency` | 🔒 | Position creation | System | THB |
| `nominal_amount` | ⏱️ | Trade | System | Updated on each buy/sell |
| `unencumbrance` | 🔄 | Daily batch | System | Free amount |
| `encumbrance` | 🔄 | Daily batch | System | Pledged amount |
| `unenc_from_reverse_repo` | 🔄 | Daily batch | System | From Reverse Repo |
| `rehypothecation` | 🔄 | Daily batch | System | Re-pledged |
| `avg_book_clean_price_pct` | ⏱️ | Buy trade | System | WAC updated on buys |
| `book_value` | 🔄 | Daily batch | System | Carrying amount |
| `valuation_date` | 🔄 | Daily batch | System | Latest valuation |
| `clean_price` | 🔄 | Daily batch | System | Market price from ThaiBMA |
| `accrued_interest` | 🔄 | Daily batch | System | **18:00 batch calculation** |
| `dirty_price` | 🔄 | Daily batch | System | Clean + Accrued |
| `market_value` | 🔄 | Daily batch | System | (Price × Nominal/100) + Accrued |
| `realized_gain_loss` | ⏱️ | Sell trade | System | Updated on sale |
| `unrealized_gain_loss` | 🔄 | Daily batch | System | MTM P&L |
| `status` | 👤/📅 | Lifecycle | System/Back Office | Active, Matured, In-Default |
| `last_updated_timestamp` | ⏱️ | Any update | System | Auto timestamp |
| `market_rate` | 🔄 | Daily batch | System | ThaiBMA market yield |

**Daily Batch Update Order (18:00-19:00):**
```
1. Import ThaiBMA prices → clean_price, market_rate
2. Calculate accrued_interest (based on day count convention)
3. Calculate dirty_price, market_value
4. Calculate unrealized_gain_loss
5. Update encumbrance (from repo positions)
6. Update timestamp
```

**Special Update Cases:**
- **Buy Trade:** `nominal_amount` += buy amount, `avg_book_clean_price_pct` recalculated (WAC)
- **Sell Trade:** `nominal_amount` -= sell amount, `realized_gain_loss` updated, if fully sold → position closed
- **Repo Out:** `encumbrance` increases, `unencumbrance` decreases
- **Reverse Repo:** `unenc_from_reverse_repo` increases
- **Coupon Payment:** `accrued_interest` = 0 (reset), new coupon transaction created
- **Maturity:** `status = 'Matured'`, position archived

---

### 3.3 position_costing

| Field | Update Type | When | By Whom | Notes |
|-------|-------------|------|---------|-------|
| `costing_id` | 🔒 | Position creation | System | Auto-generated |
| `position_id` | 🔒 | Position creation | System | Links to bond_positions |
| `cost_method` | 🔒 | Position creation | System | WAC, FIFO, LIFO |
| `avg_book_price_pct` | ⏱️ | Buy trade | System | Running WAC |
| `sum_product_clean` | ⏱️ | Buy trade | System | Σ(clean% × nominal) |
| `total_nominal_in` | ⏱️ | Buy trade | System | Σ buys |
| `cumulative_sold_nominal` | ⏱️ | Sell trade | System | Σ sales |
| `realized_gain_loss_to_date` | ⏱️ | Sell trade | System | Cumulative P&L |
| `last_realization_date` | ⏱️ | Sell trade | System | Last sale date |

**Update Frequency:** 
- On each BUY: `avg_book_price_pct`, `sum_product_clean`, `total_nominal_in` updated
- On each SELL: `cumulative_sold_nominal`, `realized_gain_loss_to_date`, `last_realization_date` updated

---

### 3.4 position_realization_events

| Field | Update Type | When | By Whom | Notes |
|-------|-------------|------|---------|-------|
| `realization_id` | 🔒 | Sale | System | Auto-generated |
| `position_id` | 🔒 | Sale | System | Position sold |
| `trade_id` | 🔒 | Sale | System | Triggering trade |
| `event_date` | 🔒 | Sale | System | Sale date |
| `sold_nominal` | 🔒 | Sale | System | Amount sold |
| `sell_clean_price_pct` | 🔒 | Sale | System | Trade price |
| `avg_book_price_pct` | 🔒 | Sale | System | WAC at sale |
| `realized_gainloss` | 🔒 | Sale | System | (Sell - Avg) × Sold |
| `accrued_int_realized` | 🔒 | Sale | System | Coupon interest |
| `method_used` | 🔒 | Sale | System | WAC/FIFO/LIFO |
| `created_at` | 🔒 | Sale | System | Timestamp |

**⚠️ IMMUTABLE TABLE - Never updated or deleted after creation**

---

## 4. Control & Risk Tables

### 4.1 margin_calls

| Field | Update Type | When | By Whom | Notes |
|-------|-------------|------|---------|-------|
| `margin_call_id` | 🔒 | Margin calc | System | Auto-generated |
| `counterparty_id` | 🔒 | Margin calc | System | Links to counterparty |
| `repo_trade_id` | 🔒 | Margin calc | System | Links to repo trade |
| `valuation_date` | 🔒 | Margin calc | System | MTM date |
| `call_currency` | 🔒 | Margin calc | System | THB |
| `call_type` | 🔄 | Daily calc | System | CALL, RETURN, NONE |
| `call_amount` | 🔄 | Daily calc | System | Net margin after MTA/threshold |
| `due_time` | 🔄 | Margin calc | System | Contractual deadline |
| `status` | 👤 | Workflow | Middle Office | Pending → Agreed → Settled |
| `created_timestamp` | 🔒 | Creation | System | Auto timestamp |

**Daily Margin Calculation Process (17:00):**
```
For each repo trade:
    1. Get collateral market values (updated from ThaiBMA prices)
    2. Calculate exposure (repo repurchase price)
    3. Compare collateral_value_after_haircut vs exposure
    4. If breach > threshold: Create/Update margin_call
    5. Set call_type (CALL if collateral < exposure, RETURN if >)
    6. Set due_time (T+1 11:00 per GMRA)
```

**Special Update Cases:**
- **Margin Call Triggered:** New record created, `status = 'Pending'`, Middle Office notified
- **Agreement Reached:** `status = 'Agreed'` (Middle Office updates)
- **Settlement Complete:** `status = 'Settled'` (Back Office updates after cash movement)
- **Call Cancelled:** `status = 'Cancelled'` (rare exception)

---

### 4.2 cash_margin_movements

| Field | Update Type | When | By Whom | Notes |
|-------|-------------|------|---------|-------|
| `cash_margin_movement_id` | 🔒 | Cash movement | System | Auto-generated |
| `margin_call_id` | 🔒 | Cash movement | System | Related margin call |
| `counterparty_id` | 🔒 | Cash movement | System | Links to counterparty |
| `repo_trade_id` | 🔒 | Cash movement | System | Links to repo |
| `call_currency` | 🔒 | Cash movement | System | THB |
| `movement_type` | 🔒 | Cash movement | Back Office | PAY or RECEIVE |
| `amount` | 🔒 | Cash movement | Back Office | Signed amount |
| `outstanding_balance` | 🔒 | Cash movement | System | Running net balance |
| `value_date` | 🔒 | Cash movement | Back Office | Settlement date |
| `created_timestamp` | 🔒 | Creation | System | Timestamp |
| `bank_account_code` | 👤 | Cash movement | Back Office | GL/nostro account |
| `daily_accrued_int_receivable` | 🔄 | Daily batch | System | Interest for day |
| `accrued_int_receivable` | 🔄 | Daily batch | System | Cumulative interest |
| `interest_on_margin_code` | 🔒 | Cash movement | System | Reference rate |
| `interest_on_margin_rate` | 🔒 | Cash movement | System | Annual rate |
| `day_count_basis` | 🔒 | Cash movement | System | ACT/365 |
| `accrual_days` | 🔄 | Daily batch | System | Days covered |
| `interest_direction` | 🔒 | Cash movement | System | RECEIVABLE or NONE |

**Daily Accrual Calculation (on posted margin):**
```
daily_interest = outstanding_balance × interest_on_margin_rate × (1/365)
accrued_int_receivable += daily_interest
```

---

### 4.3 limit_utilization

| Field | Update Type | When | By Whom | Notes |
|-------|-------------|------|---------|-------|
| `limit_id` | 🔒 | Limit change | System | Auto-generated |
| `counterparty_id` | 🔒 | Limit change | System | Links to counterparty |
| `limit_type` | 🔒 | Limit change | Middle Office | PLACEMENT_LIMIT, REPO_LIMIT, etc. |
| `currency` | 🔒 | Limit change | Middle Office | THB |
| `available_line` | 🔒 | Limit change | System | Before event |
| `total_credit_line` | 🔒 | Limit change | Middle Office | Approved limit |
| `utilization_amount` | 🔒 | Limit change | System | +consume, -release |
| `credit_line_approve_date` | 🔒 | Limit change | Middle Office | Approval date |
| `timestamp` | 🔒 | Limit change | System | Event timestamp |
| `created_date` | 🔒 | Limit change | System | Day-1 date |
| `entity_id` | 🔒 | Limit change | System | From counterparty |

**⚠️ IMMUTABLE TABLE - Append only, never updated**

**Events that create new limit_utilization records:**
1. **New Limit Approved:** `total_credit_line` set, `available_line` = `total_credit_line`
2. **Trade Consumes Limit:** `utilization_amount` = +trade_amount, `available_line` decreases
3. **Maturity Releases Limit:** `utilization_amount` = -matured_amount, `available_line` increases
4. **Limit Amendment:** New record with updated `total_credit_line`

---

### 4.4 entity_counterparty

| Field | Update Type | When | By Whom | Notes |
|-------|-------------|------|---------|-------|
| `entity_counterparty_id` | 🔒 | Mapping creation | System | Auto-generated |
| `entity_id` | 🔒 | Mapping creation | Back Office | Parent entity |
| `counterparty_id` | 🔒 | Mapping creation | Back Office | Counterparty |
| `parent_limit_id` | 🔒 | Mapping creation | Middle Office | Group limit |
| `effective_from` | 🔒 | Mapping creation | Back Office | Start date |
| `effective_to` | 👤 | Deactivation | Back Office | End date (NULL = active) |
| `status` | 👤 | Status change | Back Office | ACTIVE, INACTIVE |
| `remark` | 👤 | Any time | Back Office | Notes |
| `created_date` | 🔒 | Creation | System | Auto |
| `last_updated_date` | ⏱️ | Any change | System | Auto timestamp |

**Update Frequency:** Rare - only when counterparty joins/leaves entity group

---

## 5. Summary by Update Frequency

### 🔄 Daily Batch Updates (18:00-19:00)

| Table | Fields | Process |
|-------|--------|---------|
| `bond_positions` | `clean_price`, `accrued_interest`, `dirty_price`, `market_value`, `unrealized_gain_loss`, `book_value`, `unencumbrance`, `encumbrance`, `unenc_from_reverse_repo`, `rehypothecation`, `valuation_date`, `market_rate` | Accrued Interest & MTM |
| `collateral_positions` | `valuation_price`, `market_value`, `collateral_value_after_haircut` | Daily MTM |
| `interbank_deals` | `accrued_interest` | Daily accrual |
| `repo_trades` | `accrued_interest` | Daily accrual |
| `cash_margin_movements` | `daily_accrued_int_receivable`, `accrued_int_receivable`, `accrual_days` | Margin interest accrual |
| `bond_transactions` | `clean_price`, `book_value`, `market_value`, `market_clean_value`, `valuation_date` | Daily MTM |

### 📝 Deal Input (Trade Capture)

| Table | Key Input Fields | By Whom |
|-------|-----------------|---------|
| `bond_trades` | `portfolio_id`, `trade_date`, `security_id`, `counterparty_id`, `trade_type`, `nominal_amount`, `clean_price_trade` | Front Office |
| `interbank_deals` | `trade_date`, `value_date`, `maturity_date`, `deal_type`, `counterparty_id`, `principal_amount`, `interest_rate_type`, `interest_rate`, `reference_rate`, `margin`, `day_count_convention` | Front Office |
| `repo_trades` | `trade_date`, `trade_type`, `counterparty_id`, `netting_agreement_id`, `nominal_amount`, `purchase_date`, `repurchase_date`, `interest_rate_type`, `interest_rate`, `reference_rate`, `margin`, `day_count_convention` | Front Office |

### 📅 Scheduled Events

| Event | Table(s) | Fields Updated | Trigger |
|-------|----------|----------------|---------|
| **Coupon Payment** | `bond_positions`, `bond_transactions` | `accrued_interest` = 0, new Coupon transaction | `CURRENT_DATE = coupon_payment_date` |
| **Bond Maturity** | `bond_positions`, `bond_transactions`, `security_master` | `status = 'Matured'` | `CURRENT_DATE > maturity_date` |
| **Interbank Maturity** | `interbank_deals` | `status = 'Matured'`, limit released | `CURRENT_DATE > maturity_date` |
| **Repo Maturity** | `repo_trades`, `collateral_positions` | `status = 'Matured'`, collateral released | `CURRENT_DATE > repurchase_date` |
| **Floating Rate Reset** | `interbank_deals`, `interbank_interest_schedule` | `reset_rate`, `interest_rate`, reset dates | `CURRENT_DATE = next_reset_date` |

### 👤 Manual Updates (Back Office)

| Table | Fields | When |
|-------|--------|------|
| `bond_trades` | `settlement_status` | After TSD/BAHTNET confirmation |
| `interbank_deals` | `settlement_status`, `confirmation_ref` | After confirmation |
| `repo_trades` | `settlement_status` | After settlement |
| `margin_calls` | `status` | Workflow progression |
| `cash_margin_movements` | `movement_type`, `amount`, `value_date`, `bank_account_code` | Cash margin posting |
| `counterparty_master` | `rating_tris`, `rating_fitch`, `primary_credit_rating` | Rating updates |
| `security_master` | `rating_tris`, `rating_fitch`, `status` | Rating/maturity updates |

---

## 6. Special Update Scenarios

### 6.1 Margin Call Scenario (REPO)

```
Day 1: Repo trade created and settled
       └── collateral_positions created with haircut

Daily (17:00):
    1. Update collateral_positions.market_value from ThaiBMA prices
    2. Compare collateral_value_after_haircut vs repo exposure
    3. IF collateral < exposure - threshold:
        CREATE margin_calls record
        SET call_type = 'CALL'
        SET status = 'Pending'
        NOTIFY Middle Office

Day N: Middle Office agrees to call
       UPDATE margin_calls.status = 'Agreed'
       
Day N+1: Back Office receives cash margin
         CREATE cash_margin_movements record
         UPDATE margin_calls.status = 'Settled'
         (May CREATE new collateral_positions if securities added)
```

---

### 6.2 Coupon Payment Scenario

```
On Coupon Payment Date:
    1. System identifies all positions with `last_coupon_date` = today
    2. For each position:
        a. Calculate coupon amount = Nominal × CouponRate × Frequency
        b. CREATE bond_transactions record:
           - trade_type = 'Coupon'
           - nominal_amount = coupon amount
           - trade_date = today
        c. UPDATE bond_positions:
           - accrued_interest = 0 (reset)
           - last_coupon_date = today
    3. Generate GL journal entries for coupon received/paid
```

---

### 6.3 Bond Maturity Scenario

```
On Maturity Date:
    1. System identifies all positions with maturity_date = today
    2. UPDATE bond_positions.status = 'Matured' for each
    3. UPDATE bond_transactions.status = 'Matured'
    4. UPDATE security_master.status = 'Matured'
    5. Create final redemption transaction (if held to maturity)
    6. Generate GL entries for principal redemption
    7. Position archived (no longer in active positions view)
```

---

### 6.4 Collateral Substitution Scenario

```
Step 1: Initiate substitution request
        CREATE new collateral_positions record for new securities
        SET margin_call_id = reference if from margin call

Step 2: Validate new collateral meets requirements
        CHECK collateral_value_after_haircut >= requirement

Step 3: Release old collateral
        UPDATE old collateral record (mark as released)
        OR DELETE if fully released (based on retention policy)

Step 4: Recalculate margin
        UPDATE repo margin calculations
```

---

### 6.5 Limit Breach Scenario

```
Pre-Trade Check:
    1. Calculate proposed_utilization = current_utilization + new_trade
    2. IF proposed_utilization > total_credit_line:
        REJECT trade with "Limit Exceeded" error
    3. IF proposed_utilization > 90% of limit:
        WARN "Approaching limit" but allow

On Trade Approval:
    CREATE limit_utilization record:
        - utilization_amount = +trade_amount
        - available_line = previous_available - trade_amount

On Maturity:
    CREATE limit_utilization record:
        - utilization_amount = -matured_amount (negative)
        - available_line = previous_available + matured_amount
```

---

**End of Field Update Matrix**
