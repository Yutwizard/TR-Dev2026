# Field-to-Workflow Mapping - Treasury Management System

**Purpose:** Comprehensive mapping showing which database fields are captured in which workflow step.

**Related Documents:**
- [Transaction Workflows](./TRANSACTION_WORKFLOWS.md) - Step-by-step workflows
- [Field Reference](../01-DESIGN/FIELD_REFERENCE.md) - Field definitions and update rules

**Last Updated:** February 5, 2026

---

## 📋 Legend

| Symbol | Meaning |
|--------|---------|
| 📝 | Trade Capture (Front Office input) |
| ⚙️ | System Generated/Calculated |
| 👤 | Manual Update (Back Office/Middle Office) |
| 🔄 | Daily Batch Update |
| 📅 | Scheduled Event (Coupon, Maturity) |
| 🔒 | Immutable Record |
| 📊 | Setup/Onboarding |

---

## 1. Master Data Tables

### 1.1 entity_master

| Field | Workflow Step | Section | Team | Update Type |
|-------|---------------|---------|------|-------------|
| `entity_id` | 0.1 Step 1.9 | Entity Creation | BO | ⚙️ |
| `entity_name` | 0.1 Step 1.3 | Entity Details | BO | 👤 |
| `entity_short_name` | 0.1 Step 1.3 | Entity Details | BO | 👤 |
| `entity_type` | 0.1 Step 1.3 | Entity Details | BO | 👤 |
| `industry_sector` | 0.1 Step 1.7 | Entity Details | BO | 👤 |
| `country_code` | 0.1 Step 1.5 | Entity Details | BO | 👤 |
| `juristic_registration_number` | 0.1 Step 1.4 | Entity Details | BO | 👤 |
| `registered_capital_amount` | 0.1 Step 1.6 | Entity Details | BO | 👤 |
| `financials_currency` | 0.1 Step 1.6 | Entity Details | BO | 👤 |
| `g_sib_type` | 0.1 Step 1.8 | Entity Details | BO | 👤 |
| `created_date` | 0.1 Step 1.10 | Entity Creation | BO | ⚙️ |
| `last_updated_date` | 0.1 Step 1.11 | Entity Updates | BO | ⚙️ |

---

### 1.2 counterparty_master

| Field | Workflow Step | Section | Team | Update Type |
|-------|---------------|---------|------|-------------|
| `entity_id` | 0.1 Step 2.1 | Counterparty Setup | BO | ⚙️ |
| `counterparty_id` | 0.1 Step 2.11 | Counterparty Creation | BO | ⚙️ |
| `legal_name` | 0.1 Step 2.2 | Counterparty Details | BO | 👤 |
| `short_code` | 0.1 Step 2.3 | Counterparty Details | BO | 👤 |
| `counterparty_type` | 0.1 Step 2.4 | Counterparty Details | BO | 👤 |
| `bank_code` | 0.1 Step 2.5 | Counterparty Details | BO | 👤 |
| `swift_bic` | 0.1 Step 2.6 | Counterparty Details | BO | 👤 |
| `primary_credit_rating` | 0.1 Step 2.7 | Credit Ratings | BO | 👤 |
| `primary_rating_agency` | 0.1 Step 2.7 | Credit Ratings | BO | 👤 |
| `primary_rating_date` | 0.1 Step 2.7 | Credit Ratings | BO | 👤 |
| `created_date` | 0.1 Step 2.12 | Counterparty Creation | BO | ⚙️ |
| `last_updated_date` | 0.1 Step 2.13 | Counterparty Updates | BO | ⚙️ |
| `involved_party_type` | 0.1 Step 2.8 | Counterparty Details | BO | 👤 |
| `customer_code` | 0.1 Step 2.9 | Counterparty Details | BO | 👤 |
| `reside_in_thailand_flag` | 0.1 Step 2.10 | Counterparty Details | BO | 👤 |

---

### 1.3 security_master

| Field | Workflow Step | Section | Team | Update Type |
|-------|---------------|---------|------|-------------|
| `security_id` | 0.2 Step 1.1 | Security Setup | BO | 👤 |
| `isin` | 0.2 Step 1.2 | Security Setup | BO | 👤 |
| `issuer_id` | 0.2 Step 1.3 | Security Setup | BO | 👤 |
| `unique_id` | 0.2 Step 1.4 | Security Setup | BO | 👤 |
| `instrument_type` | 0.2 Step 1.5 | Security Setup | BO | 👤 |
| `issue_date` | 0.2 Step 1.6 | Security Setup | BO | 👤 |
| `maturity_date` | 0.2 Step 1.7 | Security Setup | BO | 👤 |
| `coupon_rate` | 0.2 Step 1.8 | Security Setup | BO | 👤 |
| `coupon_margin` | 0.2 Step 1.10 | Security Setup | BO | 👤 |
| `coupon_reference_rate` | 0.2 Step 1.10 | Security Setup | BO | 👤 |
| `coupon_frequency` | 0.2 Step 1.11 | Security Setup | BO | 👤 |
| `coupon_day_count_conv` | 0.2 Step 1.12 | Security Setup | BO | 👤 |
| `currency` | 0.2 Step 1.13 | Security Setup | BO | 👤 |
| `country` | 0.2 Step 1.14 | Security Setup | BO | 👤 |
| `bond_structure` | 0.2 Step 1.15 | Security Setup | BO | 👤 |
| `rating_tris` | 0.2 Step 1.16 | Security Setup | BO | 👤 |
| `rating_fitch` | 0.2 Step 1.16 | Security Setup | BO | 👤 |
| `is_eligible_bot_repo_collateral` | 0.2 Step 1.17 | Security Setup | BO | 👤 |
| `is_eligible_crm_collateral` | 0.2 Step 1.17 | Security Setup | BO | 👤 |
| `status` | 0.2 Step 1.18 / 4.2 Step 2 | Security Setup / Maturity | BO / System | 👤 / 📅 |
| `status_timestamp` | 0.2 Step 1.20 | Security Setup | BO | ⚙️ |
| `coupon_rate_type` | 0.2 Step 1.9 | Security Setup | BO | 👤 |
| `cross_default` | 0.2 Step 1.19 | Security Setup | BO | 👤 |

---

### 1.4 portfolio_master

| Field | Workflow Step | Section | Team | Update Type |
|-------|---------------|---------|------|-------------|
| `portfolio_id` | 0.5 Step 1.5 | Portfolio Creation | IT | ⚙️ |
| `portfolio_name` | 0.5 Step 1.1 | Portfolio Creation | IT | 👤 |
| `portfolio_manager` | 0.5 Step 1.2 | Portfolio Creation | IT | 👤 |
| `accounting_treatment` | 0.5 Step 1.3 | Portfolio Creation | IT | 👤 |
| `created_timestamp` | 0.5 Step 1.6 | Portfolio Creation | IT | ⚙️ |

---

### 1.5 netting_agreement

| Field | Workflow Step | Section | Team | Update Type |
|-------|---------------|---------|------|-------------|
| `netting_agreement_id` | 0.1 Step 5.1 | Netting Agreement | BO | 👤 |
| `counterparty_id` | 0.1 Step 5.2 | Netting Agreement | BO | 👤 |
| `netting_set_id` | 0.1 Step 5.3 | Netting Agreement | BO | 👤 |
| `agreement_type` | 0.1 Step 5.3 | Netting Agreement | BO | 👤 |
| `netting_type` | 0.1 Step 5.4 | Netting Agreement | BO | 👤 |
| `collateral_contract_type` | 0.1 Step 5.7 | Netting Agreement | BO | 👤 |
| `trade_date` | 0.1 Step 5.6 | Netting Agreement | BO | 👤 |
| `value_date` | 0.1 Step 5.6 | Netting Agreement | BO | 👤 |
| `maturity_date` | 0.1 Step 5.6 | Netting Agreement | BO | 👤 |
| `is_replacement` | 0.1 Step 5.4 | Netting Agreement | BO | 👤 |
| `replaced_agreement_id` | 0.1 Step 5.5 | Netting Agreement | BO | 👤 |
| `settlement_currency` | 0.1 Step 5.8 | Netting Agreement | BO | 👤 |
| `created_at` | 0.1 Step 5.10 | Netting Agreement | BO | ⚙️ |
| `updated_at` | 0.1 Step 5.11 | Netting Agreement | BO | ⚙️ |
| `agreement_status` | 0.1 Step 5.9 | Netting Agreement | BO | 👤 |

---

### 1.6 entity_counterparty

| Field | Workflow Step | Section | Team | Update Type |
|-------|---------------|---------|------|-------------|
| `entity_counterparty_id` | 0.6 Step 1.8 | Entity-Counterparty Mapping | BO | ⚙️ |
| `entity_id` | 0.6 Step 1.1 | Entity-Counterparty Mapping | BO | 👤 |
| `counterparty_id` | 0.6 Step 1.2 | Entity-Counterparty Mapping | BO | 👤 |
| `parent_limit_id` | 0.6 Step 1.3 | Entity-Counterparty Mapping | BO | 👤 |
| `effective_from` | 0.6 Step 1.4 | Entity-Counterparty Mapping | BO | 👤 |
| `effective_to` | 0.6 Step 1.5 | Entity-Counterparty Mapping | BO | 👤 |
| `status` | 0.6 Step 1.6 | Entity-Counterparty Mapping | BO | 👤 |
| `remark` | 0.6 Step 1.7 | Entity-Counterparty Mapping | BO | 👤 |
| `created_date` | 0.6 Step 1.9 | Entity-Counterparty Mapping | BO | ⚙️ |
| `last_updated_date` | 0.6 Step 1.10 | Entity-Counterparty Mapping | BO | ⚙️ |

---

## 2. Transaction Tables

### 2.1 bond_trades

| Field | Workflow Step | Section | Team | Update Type |
|-------|---------------|---------|------|-------------|
| `bond_trade_id` | 1 Step 1.11 | Trade Entry | FO | ⚙️ |
| `portfolio_id` | 1 Step 1.1 | Trade Entry | FO | 📝 |
| `trade_date` | 1 Step 1.5 | Trade Entry | FO | 📝 |
| `settlement_date` | 1 Step 1.8 | Trade Entry | System | ⚙️ |
| `security_id` | 1 Step 1.2 | Trade Entry | FO | 📝 |
| `counterparty_id` | 1 Step 1.3 | Trade Entry | FO | 📝 |
| `trade_type` | 1 Step 1.4 | Trade Entry | FO | 📝 |
| `nominal_amount` | 1 Step 1.6 | Trade Entry | FO | 📝 |
| `clean_price_trade` | 1 Step 1.7 | Trade Entry | FO | 📝 |
| `yield_to_maturity` | 1 Step 1.9 | Trade Entry | System | ⚙️ |
| `settlement_status` | 1 Step 1.10 / 3.3 / 6.2 | Trade Entry / Approval / Settlement | System / MO / BO | ⚙️ / 👤 |

---

### 2.2 bond_transactions

| Field | Workflow Step | Section | Team | Update Type |
|-------|---------------|---------|------|-------------|
| `trade_id` | 1 Step 7.8 / 4.1 Step 3 | Position Update / Coupon Payment | System | ⚙️ |
| `security_id` | 1 Step 7.8 | Position Update | System | ⚙️ |
| `portfolio_id` | 1 Step 7.8 | Position Update | System | ⚙️ |
| `counterparty_id` | 1 Step 7.8 | Position Update | System | ⚙️ |
| `trade_type` | 1 Step 7.8 / 4.1 Step 3 | Position Update / Coupon Payment | System | ⚙️ |
| `trade_date` | 1 Step 7.8 | Position Update | System | ⚙️ |
| `settlement_date` | 1 Step 7.8 | Position Update | System | ⚙️ |
| `maturity_date` | 1 Step 7.8 | Position Update | System | ⚙️ |
| `currency` | 1 Step 7.8 | Position Update | System | ⚙️ |
| `nominal_amount` | 1 Step 7.8 / 4.1 Step 3 | Position Update / Coupon Payment | System | ⚙️ |
| `clean_price` | 0.3.2 Step 3.3 / 1 Step 8.1 | Price Import / EOD Batch | BO / System | 🔄 |
| `clean_price_trade` | 1 Step 7.8 | Position Update | System | ⚙️ |
| `accrued_interest` | 1 Step 8.2 / 4.1 Step 4 | EOD Batch / Coupon Payment | System | 🔄 / 📅 |
| `dirty_price` | 1 Step 7.8 / 1 Step 8.2 | Position Update / EOD Batch | System | 🔄 |
| `classification` | 1 Step 7.8 | Position Update | System | ⚙️ |
| `book_value` | 1 Step 7.8 / 1 Step 8.x | Position Update / Daily Batch | System | 🔄 |
| `market_clean_value` | 1 Step 7.8 | Position Update | System | ⚙️ |
| `market_value` | 1 Step 7.5 / 1 Step 8.3 | Position Update / EOD Batch | System | 🔄 |
| `last_coupon_date` | 4.1 Step 5 | Coupon Payment | System | 📅 |
| `coupon_rate_type` | 1 Step 7.8 | Position Update | System | ⚙️ |
| `coupon_reference_rate` | 1 Step 7.8 | Position Update | System | ⚙️ |
| `coupon_margin` | 1 Step 7.8 | Position Update | System | ⚙️ |
| `coupon_frequency` | 1 Step 7.8 | Position Update | System | ⚙️ |
| `coupon_rate` | 1 Step 7.8 | Position Update | System | ⚙️ |
| `coupon_day_count_conv` | 1 Step 7.8 | Position Update | System | ⚙️ |
| `rating_tris` | 1 Step 7.8 | Position Update | System | ⚙️ |
| `rating_fitch` | 1 Step 7.8 | Position Update | System | ⚙️ |
| `status` | 4.2 Step 3 | Maturity Process | System | 📅 |
| `last_updated_timestamp` | 1 Step 8.5 | EOD Batch | System | 🔄 |
| `valuation_date` | 1 Step 7.8 / 1 Step 8.x | Position Update / Daily Batch | System | 🔄 |

---

### 2.3 interbank_deals

| Field | Workflow Step | Section | Team | Update Type |
|-------|---------------|---------|------|-------------|
| `deal_id` | 2 Step 1.12 | Deal Entry | FO | ⚙️ |
| `trade_date` | 2 Step 1.x | Deal Entry | FO | 📝 |
| `value_date` | 2 Step 1.4 | Deal Entry | FO | 📝 |
| `maturity_date` | 2 Step 1.5 | Deal Entry | FO | 📝 |
| `deal_type` | 2 Step 1.1 | Deal Entry | FO | 📝 |
| `counterparty_id` | 2 Step 1.2 | Deal Entry | FO | 📝 |
| `principal_amount` | 2 Step 1.3 | Deal Entry | FO | 📝 |
| `currency` | 2 Step 1.x | Deal Entry | System | ⚙️ |
| `reference_rate_id` | 2 Step 1.11 | Deal Entry | System | ⚙️ |
| `interest_rate_type` | 2 Step 1.6 | Deal Entry | FO | 📝 |
| `interest_rate` | 2 Step 1.7 / 2 Step 4.3 | Deal Entry / Rate Reset | FO / System | 📝 / 🔄 |
| `reference_rate_tenor` | 2 Step 1.8 | Deal Entry | FO | 📝 |
| `reference_rate` | 2 Step 1.8 | Deal Entry | FO | 📝 |
| `margin` | 2 Step 1.8 | Deal Entry | FO | 📝 |
| `reset_rate` | 2 Step 4.3 | Rate Reset | System | 🔄 |
| `last_reset_date` | 2 Step 4.3 | Rate Reset | System | 🔄 |
| `next_reset_date` | 2 Step 4.3 | Rate Reset | System | 🔄 |
| `day_count_convention` | 2 Step 1.9 | Deal Entry | FO | 📝 |
| `accrued_interest` | 2 Step 4.1 | Daily Accrual | System | 🔄 |
| `status` | 2 Step 2.3 / 2 Step 3.5 / 2 Step 5.5 | Approval / Settlement / Maturity | MO / BO / System | 👤 / 📅 |
| `confirmation_ref` | 2 Step 3.4 | Settlement | BO | 👤 |
| `limit_id` | 2 Step 2.4 | Approval | System | ⚙️ |
| `term` | 2 Step 1.10 | Deal Entry | System | ⚙️ |
| `entity_id` | 2 Step 1.13 | Deal Entry | System | ⚙️ |

---

### 2.4 interbank_interest_schedule

| Field | Workflow Step | Section | Team | Update Type |
|-------|---------------|---------|------|-------------|
| `schedule_id` | 2 Step 1.x (Floating) | Schedule Generation | System | ⚙️ |
| `referencerate_id` | 2 Step 1.x (Floating) | Schedule Generation | System | ⚙️ |
| `deal_id` | 2 Step 1.x (Floating) | Schedule Generation | System | ⚙️ |
| `last_reset_date` | 2 Step 4.3 | Rate Reset | System | 🔄 |
| `next_reset_date` | 2 Step 4.3 | Rate Reset | System | 🔄 |
| `reset_rate` | 2 Step 4.3 | Rate Reset | System | 🔄 |
| `interest_rate` | 2 Step 4.3 | Rate Reset | System | 🔄 |
| `status` | 2 Step 4.3 | Rate Reset | System | 🔄 |

---

### 2.5 repo_trades

| Field | Workflow Step | Section | Team | Update Type |
|-------|---------------|---------|------|-------------|
| `repo_trade_id` | 3 Step 1.18 | Trade Entry | FO | ⚙️ |
| `trade_date` | 3 Step 1.x | Trade Entry | FO | 📝 |
| `trade_type` | 3 Step 1.1 | Trade Entry | FO | 📝 |
| `counterparty_id` | 3 Step 1.2 | Trade Entry | FO | 📝 |
| `netting_agreement_id` | 3 Step 1.3 | Trade Entry | FO | 📝 |
| `netting_set_id` | 3 Step 1.10 | Trade Entry | System | ⚙️ |
| `nominal_amount` | 3 Step 1.4 | Trade Entry | FO | 📝 |
| `purchase_date` | 3 Step 1.5 | Trade Entry | FO | 📝 |
| `repurchase_date` | 3 Step 1.5 | Trade Entry | FO | 📝 |
| `purchase_price` | 3 Step 1.11 | Trade Entry | System | ⚙️ |
| `repurchase_price` | 3 Step 1.12 | Trade Entry | System | ⚙️ |
| `currency` | 3 Step 1.x | Trade Entry | System | ⚙️ |
| `reference_rate_id` | 3 Step 1.16 | Trade Entry | System | ⚙️ |
| `interest_rate_type` | 3 Step 1.6 | Trade Entry | FO | 📝 |
| `interest_rate` | 3 Step 1.7 | Trade Entry | FO | 📝 |
| `reference_rate` | 3 Step 1.8 | Trade Entry | FO | 📝 |
| `margin` | 3 Step 1.8 | Trade Entry | FO | 📝 |
| `day_count_convention` | 3 Step 1.9 | Trade Entry | FO | 📝 |
| `repo_rate` | 3 Step 1.13 | Trade Entry | System | ⚙️ |
| `term` | 3 Step 1.14 | Trade Entry | System | ⚙️ |
| `repo_out_flag` | 3 Step 1.15 | Trade Entry | System | ⚙️ |
| `repo_in_flag` | 3 Step 1.15 | Trade Entry | System | ⚙️ |
| `status` | 3 Step 2.3 / 3 Step 4.3 / 3 Step 9.6 | Approval / Settlement / Maturity | MO / BO / System | 👤 / 📅 |
| `limit_id` | 3 Step 2.3 | Approval | System | ⚙️ |
| `accrued_interest` | 3 Step 8.1 | Daily Accrual | System | 🔄 |
| `entity_id` | 3 Step 1.17 | Trade Entry | System | ⚙️ |

---

## 3. Position & Collateral Tables

### 3.1 collateral_positions

| Field | Workflow Step | Section | Team | Update Type |
|-------|---------------|---------|------|-------------|
| `collateral_id` | 3 Step 3.11 | Collateral Allocation | System | ⚙️ |
| `repo_trade_id` | 3 Step 3.x | Collateral Allocation | BO | 👤 |
| `security_id` | 3 Step 3.2 | Collateral Allocation | BO | 👤 |
| `nominal_amount` | 3 Step 3.3 | Collateral Allocation | BO | 👤 |
| `allocation_date` | 3 Step 3.10 | Collateral Allocation | System | ⚙️ |
| `valuation_price` | 3 Step 5.1 | Daily Margin Mgmt | System | 🔄 |
| `market_value` | 3 Step 3.6 / 3 Step 5.2 | Collateral Allocation / Daily MTM | System | 🔄 |
| `haircut_percentage` | 3 Step 3.4 | Collateral Allocation | System | ⚙️ |
| `collateral_value_after_haircut` | 3 Step 3.7 / 3 Step 5.3 | Collateral Allocation / Daily MTM | System | 🔄 |
| `margin_call_id` | 3 Step 6b.3 (if margin call) | Margin Settlement | System | 👤 |
| `currency` | 3 Step 3.x | Collateral Allocation | System | ⚙️ |

---

### 3.2 bond_positions

| Field | Workflow Step | Section | Team | Update Type |
|-------|---------------|---------|------|-------------|
| `position_id` | 1 Step 6.3 | Settlement Confirmation | System | ⚙️ |
| `security_id` | 1 Step 6.3 | Settlement Confirmation | System | ⚙️ |
| `portfolio_id` | 1 Step 6.3 | Settlement Confirmation | System | ⚙️ |
| `open_date` | 1 Step 7.4 | Position Update | System | ⚙️ |
| `maturity_date` | 1 Step 6.3 | Settlement Confirmation | System | ⚙️ |
| `currency` | 1 Step 6.3 | Settlement Confirmation | System | ⚙️ |
| `nominal_amount` | 1 Step 7.1 | Position Update | System | ⏱️ |
| `unencumbrance` | 1 Step 8.x | EOD Batch | System | 🔄 |
| `encumbrance` | 1 Step 8.x | EOD Batch | System | 🔄 |
| `unenc_from_reverse_repo` | 1 Step 8.x | EOD Batch | System | 🔄 |
| `rehypothecation` | 1 Step 8.x | EOD Batch | System | 🔄 |
| `avg_book_clean_price_pct` | 1 Step 7.2 / 1 Step 6.4 | Position Update / Costing | System | ⏱️ |
| `book_value` | 1 Step 7.3 / 1 Step 8.x | Position Update / EOD Batch | System | 🔄 |
| `valuation_date` | 1 Step 8.x | EOD Batch | System | 🔄 |
| `clean_price` | 0.3.2 Step 3.3 / 1 Step 8.1 | Price Import / EOD Batch | BO / System | 🔄 |
| `accrued_interest` | 1 Step 8.2 / 4.1 Step 4 | EOD Batch / Coupon Payment | System | 🔄 / 📅 |
| `dirty_price` | 1 Step 8.2 | EOD Batch | System | 🔄 |
| `market_value` | 1 Step 7.5 / 1 Step 8.3 | Position Update / EOD Batch | System | 🔄 |
| `realized_gain_loss` | 1 Step 7.6 | Position Update | System | ⏱️ |
| `unrealized_gain_loss` | 1 Step 8.4 | EOD Batch | System | 🔄 |
| `status` | 4.2 Step 2 | Maturity Process | System | 📅 |
| `last_updated_timestamp` | 1 Step 8.5 | EOD Batch | System | 🔄 |
| `market_rate` | 1 Step 8.x | EOD Batch | System | 🔄 |

---

### 3.3 position_costing

| Field | Workflow Step | Section | Team | Update Type |
|-------|---------------|---------|------|-------------|
| `costing_id` | 1 Step 6.4 | Settlement Confirmation | System | ⚙️ |
| `position_id` | 1 Step 6.4 | Settlement Confirmation | System | ⚙️ |
| `cost_method` | 1 Step 6.4 | Settlement Confirmation | System | ⚙️ |
| `avg_book_price_pct` | 1 Step 6.4 / 1 Step 7.2 | Settlement / Position Update | System | ⏱️ |
| `sum_product_clean` | 1 Step 6.4 | Settlement Confirmation | System | ⏱️ |
| `total_nominal_in` | 1 Step 6.4 | Settlement Confirmation | System | ⏱️ |
| `cumulative_sold_nominal` | 1 Step 7.6 | Position Update | System | ⏱️ |
| `realized_gain_loss_to_date` | 1 Step 7.6 | Position Update | System | ⏱️ |
| `last_realization_date` | 1 Step 7.6 | Position Update | System | ⏱️ |

---

### 3.4 position_realization_events

| Field | Workflow Step | Section | Team | Update Type |
|-------|---------------|---------|------|-------------|
| `realization_id` | 1 Step 7.7 | Position Update | System | 🔒 |
| `position_id` | 1 Step 7.7 | Position Update | System | 🔒 |
| `trade_id` | 1 Step 7.7 | Position Update | System | 🔒 |
| `event_date` | 1 Step 7.7 | Position Update | System | 🔒 |
| `sold_nominal` | 1 Step 7.7 | Position Update | System | 🔒 |
| `sell_clean_price_pct` | 1 Step 7.7 | Position Update | System | 🔒 |
| `avg_book_price_pct` | 1 Step 7.7 | Position Update | System | 🔒 |
| `realized_gainloss` | 1 Step 7.7 | Position Update | System | 🔒 |
| `accrued_int_realized` | 1 Step 7.7 | Position Update | System | 🔒 |
| `method_used` | 1 Step 7.7 | Position Update | System | 🔒 |
| `created_at` | 1 Step 7.7 | Position Update | System | 🔒 |

---

## 4. Control & Risk Tables

### 4.1 margin_calls

| Field | Workflow Step | Section | Team | Update Type |
|-------|---------------|---------|------|-------------|
| `margin_call_id` | 3 Step 5.6 | Daily Margin Mgmt | System | ⚙️ |
| `counterparty_id` | 3 Step 5.6 | Daily Margin Mgmt | System | ⚙️ |
| `repo_trade_id` | 3 Step 5.6 | Daily Margin Mgmt | System | ⚙️ |
| `valuation_date` | 3 Step 5.1 | Daily Margin Mgmt | System | ⚙️ |
| `call_currency` | 3 Step 5.6 | Daily Margin Mgmt | System | ⚙️ |
| `call_type` | 3 Step 5.6 | Daily Margin Mgmt | System | 🔄 |
| `call_amount` | 3 Step 5.6 | Daily Margin Mgmt | System | 🔄 |
| `due_time` | 3 Step 5.6 | Daily Margin Mgmt | System | 🔄 |
| `status` | 3 Step 6a.4 / 3 Step 6b.11 | MO Agreement / BO Settlement | MO / BO | 👤 |
| `created_timestamp` | 3 Step 5.6 | Daily Margin Mgmt | System | ⚙️ |

---

### 4.2 cash_margin_movements

| Field | Workflow Step | Section | Team | Update Type |
|-------|---------------|---------|------|-------------|
| `cash_margin_movement_id` | 3 Step 6b.2 | Margin Settlement | System | ⚙️ |
| `margin_call_id` | 3 Step 6b.2 | Margin Settlement | System | ⚙️ |
| `counterparty_id` | 3 Step 6b.2 | Margin Settlement | System | ⚙️ |
| `repo_trade_id` | 3 Step 6b.2 | Margin Settlement | System | ⚙️ |
| `call_currency` | 3 Step 6b.2 | Margin Settlement | System | ⚙️ |
| `movement_type` | 3 Step 6b.3 | Margin Settlement | BO | 👤 |
| `amount` | 3 Step 6b.3 | Margin Settlement | BO | 👤 |
| `outstanding_balance` | 3 Step 6b.6 | Margin Settlement | System | ⚙️ |
| `value_date` | 3 Step 6b.5 | Margin Settlement | BO | 👤 |
| `created_timestamp` | 3 Step 6b.2 | Margin Settlement | System | ⚙️ |
| `bank_account_code` | 3 Step 6b.4 | Margin Settlement | BO | 👤 |
| `daily_accrued_int_receivable` | 3 Step 8.3 | Daily Accrual | System | 🔄 |
| `accrued_int_receivable` | 3 Step 8.3 | Daily Accrual | System | 🔄 |
| `interest_on_margin_code` | 3 Step 6b.7 | Margin Settlement | System | ⚙️ |
| `interest_on_margin_rate` | 3 Step 6b.7 | Margin Settlement | System | ⚙️ |
| `day_count_basis` | 3 Step 6b.8 | Margin Settlement | System | ⚙️ |
| `accrual_days` | 3 Step 8.3 | Daily Accrual | System | 🔄 |
| `interest_direction` | 3 Step 8.3 | Daily Accrual | System | ⚙️ |

---

### 4.3 limit_utilization

| Field | Workflow Step | Section | Team | Update Type |
|-------|---------------|---------|------|-------------|
| `limit_id` | 0.1 Step 4.6 | Limit Configuration | System | 🔒 |
| `counterparty_id` | 0.1 Step 4.x | Limit Configuration | System | 🔒 |
| `limit_type` | 0.1 Step 4.1 | Limit Configuration | MO | 🔒 |
| `currency` | 0.1 Step 4.3 | Limit Configuration | MO | 🔒 |
| `available_line` | 0.1 Step 4.5 | Limit Configuration | System | 🔒 |
| `total_credit_line` | 0.1 Step 4.2 | Limit Configuration | MO | 🔒 |
| `utilization_amount` | 1 Step 2.5 / 2 Step 2.4 / 3 Step 2.3 | Limit Check | System | 🔒 |
| `credit_line_approve_date` | 0.1 Step 4.4 | Limit Configuration | MO | 🔒 |
| `timestamp` | 0.1 Step 4.7 | Limit Configuration | System | 🔒 |
| `created_date` | 0.1 Step 4.8 | Limit Configuration | System | 🔒 |
| `entity_id` | 0.1 Step 4.9 | Limit Configuration | System | 🔒 |

---

## 5. Summary by Workflow Section

| Section | Tables Covered | Field Count |
|---------|----------------|-------------|
| 0.1 Client Onboarding | entity_master, counterparty_master, limit_utilization, netting_agreement | 50+ |
| 0.2 Bond Setup | security_master | 25+ |
| 0.3 Market Data | security_master, bond_positions, collateral_positions | 15+ |
| 0.4 Pre-Transaction Check | (Reference only) | - |
| 0.5 Portfolio Setup | portfolio_master | 5 |
| 0.6 Entity-Counterparty | entity_counterparty | 10 |
| 1. Bond Trade | bond_trades, bond_positions, bond_transactions, position_costing, position_realization_events, limit_utilization | 60+ |
| 2. Interbank Deal | interbank_deals, interbank_interest_schedule, limit_utilization | 25+ |
| 3. Repo Trade | repo_trades, collateral_positions, margin_calls, cash_margin_movements, limit_utilization | 50+ |
| 4. Scheduled Events | bond_transactions, bond_positions, security_master, interbank_deals, repo_trades | 30+ |

---

## 6. Fields Not in Active Workflows

The following fields are system-managed and do not require explicit workflow documentation:

| Field | Table | Reason |
|-------|-------|--------|
| `created_at`, `updated_at` | Multiple | Automatic system timestamps |
| `last_updated_timestamp` | Multiple | Automatic system timestamps |
| `last_updated_date` | Multiple | Automatic system timestamps |

---

**Document End**

*For detailed workflow steps, see [Transaction Workflows](./TRANSACTION_WORKFLOWS.md)*  
*For field definitions, see [Field Reference](../01-DESIGN/FIELD_REFERENCE.md)*
