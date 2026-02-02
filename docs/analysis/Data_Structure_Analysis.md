# Treasury System Data Structure Analysis

**Source:** Treasury System Database V2_Internal.xlsx  
**Total Sheets:** 76  
**Analysis Date:** February 2026

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Core Master Data Tables](#2-core-master-data-tables)
3. [Transaction Tables](#3-transaction-tables)
4. [Position & Analytical Tables](#4-position--analytical-tables)
5. [Control & Risk Management Tables](#5-control--risk-management-tables)
6. [Product-Specific Table Relationships](#6-product-specific-table-relationships)
7. [BOT Regulatory Report Mapping](#7-bot-regulatory-report-mapping)
8. [Key Data Elements for Regulatory Compliance](#8-key-data-elements-for-regulatory-compliance)

---

## 1. Executive Summary

### 1.1 Data Model Overview

The Excel file contains a comprehensive data model designed to support a Thai Commercial Bank Treasury System with the following scope:

| Product | Coverage |
|---------|----------|
| **Interbank Lending/Borrowing** | THB placements and takings with Thai banks |
| **Repo/Reverse Repo** | Bilateral repos with BOT and private market repos |
| **Bond Trading** | T-Bills, T-Bonds, BOT Bonds, SOE Bonds, Corporate Bonds |

### 1.2 Table Categories

| Category | Table Count | Purpose |
|----------|-------------|---------|
| **Master Data** | 7 | Static reference data |
| **Transaction** | 6 | Event-driven deal capture |
| **Position** | 2 | Derived holding information |
| **Analytical** | 3 | Costing, P&L, realization |
| **Control** | 3 | Limits, margin, audit |

### 1.3 Key Design Principles

1. **Dual Master Structure:** `entity_master` (obligor level) + `counterparty_master` (operational level)
2. **Immutable Audit Trail:** `limit_utilization`, `position_realization_events` are append-only
3. **BOT Compliance-First:** Fields aligned with BOT DER_CPEN, ThaiBMA standards
4. **TFRS 9 Ready:** Business model classification, ECL staging support

---

## 2. Core Master Data Tables

### 2.1 entity_master

**Purpose:** Enterprise-wide obligor registry for credit risk, Basel, TFRS 9, Moody's mapping

| Column | Data Type | Description | Regulatory Use |
|--------|-----------|-------------|----------------|
| entity_id | VARCHAR(40) | PK - entity_short_name + juristic_registration_number | BOT DER_CPEN.Entity Id, Moody's ENTITY_CODE |
| entity_name | VARCHAR(255) | Full legal name | KYC, reporting |
| entity_short_name | VARCHAR(10) | Short abbreviation | Risk reporting |
| entity_type | VARCHAR(50) | Basel/Moody's classification (BANK, BANK_SOV, PSE, CORP_HVCRE, etc.) | RW calculation, EAD grouping |
| industry_sector | VARCHAR(50) | Moody's INDUSTRY_SECTOR | Concentration analysis |
| country_code | CHAR(3) | Country of domicile | Country risk, Basel mapping |
| juristic_registration_number | VARCHAR(20) | เลขจดทะเบียนนิติบุคคล (13 digits Thai) | KYC, BOT reporting |
| registered_capital_amount | DECIMAL(20,2) | ทุนจดทะเบียน | Credit assessment |
| g_sib_type | CHAR(1) | G-SIB / D-SIB classification (G/D/NULL) | Systemic risk |

**Key Business Rules:**
- entity_id constructed as: `entity_short_name + juristic_registration_number`
- Referenced by counterparty_master.entity_id (FK)
- Maintained by Credit Risk / KYC teams

---

### 2.2 counterparty_master

**Purpose:** Authoritative repository for all entities conducting treasury business

| Column | Data Type | Description | Regulatory Use |
|--------|-----------|-------------|----------------|
| entity_id | VARCHAR(40) | FK → entity_master | Group-level risk aggregation |
| counterparty_id | VARCHAR(40) | PK - System-generated identifier | Transaction linking |
| legal_name | VARCHAR(255) | Full legal name | Contracts, confirmations |
| short_code | VARCHAR(50) | UI identifier | Trading screens |
| counterparty_type | VARCHAR(50) | Commercial Bank, SOE, Corporate, Central Bank | Classification |
| bank_code | VARCHAR(13) | BOT-assigned code (e.g., "001") | BOT reporting |
| swift_bic | VARCHAR(11) | SWIFT BIC | Settlement messaging |
| primary_credit_rating | VARCHAR(10) | Credit rating (AA+, AA, etc.) | Risk weighting |
| primary_rating_agency | VARCHAR(50) | TRIS Rating, Fitch, Moody's, S&P | Validation |
| primary_rating_date | DATE | Rating date | Staleness check |
| involved_party_type | INT | BOT standardized institution type (from Involved_Party_Type sheet) | BOT statistical reports |
| customer_code | VARCHAR(10) | Bank-defined classification (from Customer_type_master) | Interest calculation, FCC |
| reside_in_thailand_flag | BOOLEAN | MFSMCG residency classification | Resident/non-resident reporting |

**Key Business Rules:**
- Every counterparty maps to one entity (entity_id FK)
- bank_code must match BOT official list
- involved_party_type from BOT standardized list (176039 = Commercial Bank, etc.)

---

### 2.3 security_master

**Purpose:** Comprehensive catalog of tradable instruments aligned with ThaiBMA standards

| Column | Data Type | Description | Example |
|--------|-----------|-------------|---------|
| security_id | VARCHAR(10) | PK - Trading symbol (ThaiBMA) | LB28DA |
| isin | VARCHAR(12) | PK - ISIN | TH0623038C09 |
| issuer_id | VARCHAR(40) | 1=Govt, 2=BOT, 3=SOE, 4=Corporate | 1 |
| unique_id | VARCHAR(20) | BOT report ID: BANK_CODE for BOT bonds, Govt Agency code for others | 001, 176015 |
| instrument_type | VARCHAR(20) | T-Bill, Gov Bond, Corp Bond, SOE Bond, BOT Bond | Gov Bond |
| issue_date | DATE | Issue date | 2018-12-17 |
| maturity_date | DATE | Maturity date | 2028-12-17 |
| coupon_rate | DECIMAL(5,2) | Annual coupon % | 4.85 |
| coupon_frequency | VARCHAR(20) | Semi-Annual, Annual, At Maturity | Semi-Annual |
| coupon_day_count_conv | VARCHAR(20) | Actual/365, Actual/Actual | Actual/365 |
| currency | CHAR(3) | THB | THB |
| country | CHAR(2) | TH | TH |
| bond_structure | VARCHAR(50) | Bullet, ZERO, Amortizing | Bullet |
| rating_tris | VARCHAR(10) | TRIS rating | AAA |
| rating_fitch | VARCHAR(10) | Fitch rating | AAA(tha) |
| is_eligible_bot_repo_collateral | BOOLEAN | BOT repo eligibility | TRUE |
| is_eligible_crm_collateral | BOOLEAN | Credit risk mitigation eligibility | TRUE |
| coupon_rate_type | VARCHAR(10) | Fixed, Floating | Fixed |
| cross_default | BOOLEAN | Cross-default clause flag | FALSE |

**Key Business Rules:**
- Composite PK: (security_id, isin, issuer_id, unique_id)
- issuer_id mapping: 1=Govt Thailand, 2=BOT, 3=SOE, 4=Corporate
- unique_id source varies by issuer type (see mapping rules)

---

### 2.4 portfolio_master

**Purpose:** Logical segregation of treasury positions by strategic intent

| Column | Description |
|--------|-------------|
| portfolio_id | PK - Unique identifier |
| portfolio_name | Name (e.g., "HTM Portfolio", "Trading Book") |
| portfolio_type | Classification: HOLD_TO_COLLECT, HOLD_TO_COLLECT_AND_SELL, TRADING |
| accounting_classification | AMORTIZED_COST, FVOCI, FVTPL |
| business_model | TFRS 9 business model designation |

**Key Business Rules:**
- portfolio_type determines TFRS 9 classification
- Used for limit monitoring and risk aggregation

---

### 2.5 netting_agreement

**Purpose:** Master information for netting and collateral agreements (ISDA, GMRA)

| Column | Description |
|--------|-------------|
| NettingAgreementID | PK |
| counterparty_id | FK → counterparty_master |
| agreement_type | ISDA, GMRA, etc. |
| effective_date | Agreement start |
| expiry_date | Agreement end |
| margin_threshold | Minimum transfer amount |
| rounding_amount | Margin rounding rule |

---

## 3. Transaction Tables

### 3.1 interbank_deals

**Purpose:** Records all interbank lending (placements) and borrowing (takings)

| Column | Data Type | Description |
|--------|-----------|-------------|
| DealID | VARCHAR(40) | PK |
| counterparty_id | FK | Counterparty |
| LimitID | FK | Limit reference |
| entity_id | FK | Entity reference |
| deal_type | LEND, BORROW | Transaction type |
| currency | CHAR(3) | THB |
| principal_amount | DECIMAL(20,2) | Notional |
| interest_rate | DECIMAL(7,4) | All-in rate |
| rate_type | FIXED, FLOATING |
| benchmark_rate | VARCHAR(10) | THOR, etc. |
| spread_bp | INT | Spread in basis points |
| value_date | DATE | Start date |
| maturity_date | DATE | End date |
| tenor_days | INT | Calculated tenor |
| settlement_account | VARCHAR(20) | BAHTNET account |
| status | ACTIVE, MATURED, CANCELLED |

**Child Table:** interbank_interest_schedule
- ScheduleID (PK)
- DealID (FK)
- period_start_date
- period_end_date
- benchmark_rate
- effective_rate
- accrued_interest

---

### 3.2 repo_trades

**Purpose:** Master details of each REPO or Reverse REPO transaction

| Column | Data Type | Description |
|--------|-----------|-------------|
| RepoTradeID | VARCHAR(40) | PK |
| counterparty_id | FK | Counterparty |
| NettingAgreementID | FK | GMRA agreement |
| LimitID | FK | Limit reference |
| entity_id | FK | Entity reference |
| trade_type | REPO, REVERSE_REPO | Bank's perspective |
| trade_date | DATE | Transaction date |
| value_date | DATE | Settlement date |
| maturity_date | DATE | Repo maturity |
| tenor_days | INT | Calculated |
| currency | CHAR(3) | THB |
| nominal_amount | DECIMAL(20,2) | Cash leg |
| repo_rate | DECIMAL(7,4) | Annual rate |
| repo_rate_type | FIXED, FLOATING |
| haircut_percent | DECIMAL(5,2) | From haircut_table |
| collateral_market_value | DECIMAL(20,2) | Pre-haircut value |
| settlement_amount | DECIMAL(20,2) | Cash after haircut |
| open_repo_flag | BOOLEAN | Open/term repo |
| call_date | DATE | For callable repos |
| settlement_system | BAHTNET, TSD |
| status | OPEN, CLOSED, MATURED |

**Child Table:** collateral_positions
- CollateralID (PK)
- RepoTradeID (FK)
- SecurityID (FK → security_master)
- collateral_quantity
- market_value
- haircut_applied
- margin_value

---

### 3.3 bond_trades / bond_transactions

**Purpose:** Records all outright bond purchases and sales

| Column | Data Type | Description |
|--------|-----------|-------------|
| TradeID / BondTradeID | VARCHAR(40) | PK |
| PortfolioID | FK → portfolio_master |
| SecurityID | FK → security_master |
| counterparty_id | FK | For OTC trades |
| TradeType | BUY, SELL |
| TradeDate | DATE |
| SettlementDate | DATE | T+2 |
| NominalAmount | DECIMAL(20,2) | Face value |
| CleanPrice | DECIMAL(10,6) | Percentage |
| AccruedInterest | DECIMAL(20,2) | Calculated |
| DirtyPrice | DECIMAL(10,6) | Clean + AI |
| SettlementAmount | DECIMAL(20,2) | Cash settlement |
| Yield | DECIMAL(10,6) | Yield to maturity |
| SettlementSystem | TSD, BAHTNET |
| TraderID | VARCHAR(20) | Front office |
| Status | CREATED, CONFIRMED, SETTLED |

---

## 4. Position & Analytical Tables

### 4.1 bond_positions

**Purpose:** Current holding details for each bond investment

| Column | Data Type | Description |
|--------|-----------|-------------|
| PositionID | VARCHAR(40) | PK |
| SecurityID | FK | Bond held |
| PortfolioID | FK | Portfolio assignment |
| NominalAmount | DECIMAL(20,2) | Current face value |
| AverageCost | DECIMAL(20,6) | Weighted average cost |
| BookCost | DECIMAL(20,2) | Total cost basis |
| AmortizedCost | DECIMAL(20,2) | TFRS 9 carrying amount |
| AccruedInterest | DECIMAL(20,2) | Accrued income |
| MarketValue | DECIMAL(20,2) | MTM value |
| UnrealizedPnL | DECIMAL(20,2) | MTM - BookCost |
| ECLStage | 1, 2, 3 | Impairment stage |
| ECLProvision | DECIMAL(20,2) | Impairment allowance |
| CarryingAmount | DECIMAL(20,2) | AmortizedCost - Provision |

---

### 4.2 position_costing

**Purpose:** Cost basis and realized P&L tracking

| Column | Description |
|--------|-------------|
| CostingID | PK |
| PositionID | FK → bond_positions |
| TotalNominalPurchased | Cumulative buys |
| TotalCost | Cumulative cost |
| WeightedAvgCost | Per unit |
| CumulativeRealizedPnL | From sales |
| LastUpdated | Timestamp |

---

### 4.3 position_realization_events

**Purpose:** Immutable journal of realized P&L (append-only)

| Column | Description |
|--------|-------------|
| RealizationID | PK |
| PositionID | FK |
| TradeID | FK → triggering trade |
| RealizationDate | Date of realization |
| NominalAmountSold | Quantity |
| SaleCleanPrice | Sale price |
| WACAtSale | Cost basis |
| RealizedPnL | Gain/loss |
| CreatedAt | Timestamp (immutable) |

---

## 5. Control & Risk Management Tables

### 5.1 limit_utilization

**Purpose:** Immutable audit log of all credit limit impacts

| Column | Description |
|--------|-------------|
| LimitID | PK |
| counterparty_id | FK |
| entity_id | FK |
| LimitType | SINGLE_TXN, AGGREGATE, TENOR, CONCENTRATION |
| LimitAmount | Approved limit |
| UtilizedAmount | Current usage |
| AvailableAmount | Remaining |
| UtilizationPercent | % used |
| TransactionID | Reference to deal |
| EventType | NEW_TRADE, MATURITY, CANCELLATION |
| Timestamp | Event time |
| CreatedBy | User/system |

**Key Business Rules:**
- Append-only (no updates/deletes)
- Pre-trade checking against available amount
- Warning at 80%, hard block at 100%

---

### 5.2 margin_calls

**Purpose:** Daily margin call events for collateralized trading

| Column | Description |
|--------|-------------|
| MarginCallID | PK |
| counterparty_id | FK |
| RepoTradeID | FK |
| ValuationDate | MTM date |
| ExposureAmount | Current exposure |
| CollateralValue | Posted collateral |
| NetExposure | Exposure - Collateral |
| ThresholdAmount | Min transfer amount |
| MarginCallAmount | Call/delivery amount |
| MarginCallType | DELIVERY, RETURN |
| Status | PENDING, AGREED, SETTLED, DISPUTED |
| DueDate | Settlement deadline |

---

### 5.3 cash_margin_movements

**Purpose:** Cash collateral movement tracking

| Column | Description |
|--------|-------------|
| CashMarginMovementID | PK |
| MarginCallID | FK |
| counterparty_id | FK |
| MovementType | POST, RECEIVE, RETURN, ADJUST |
| Currency | THB |
| Amount | Movement amount |
| InterestRate | Rate on cash margin |
| AccruedInterest | Interest receivable/payable |
| OutstandingBalance | Running balance |
| SettlementDate | Value date |
| BAHTNETReference | Settlement reference |

---

## 6. Product-Specific Table Relationships

### 6.1 Interbank Lending/Borrowing

```
entity_master (1)
    ↓ entity_id
counterparty_master (N)
    ↓ counterparty_id
Limit_Utilization (1:N per limit type)
    ↓ LimitID
Interbank_Deals (1)
    ↓ DealID
Interbank_Interest_Schedule (N periods)
```

---

### 6.2 Repo/Reverse Repo

```
entity_master (1)
    ↓ entity_id
counterparty_master (N)
    ↓ counterparty_id
Netting_Agreement (1:1 or 1:N)
    ↓ NettingAgreementID
Limit_Utilization
    ↓ LimitID
Repo_Trades (1)
    ↓ RepoTradeID
Collateral_Positions (N securities)
    ↓ SecurityID
Security_Master
```

---

### 6.3 Bond Trading

```
entity_master
counterparty_master (for OTC)
    ↓
Portfolio_Master (1)
    ↓ PortfolioID
Bond_Trades / Bond_Transactions (N)
    ↓ TradeID
Bond_Positions (1 per security-portfolio)
    ↓ PositionID
Position_Costing (1)
Position_Realization_Events (N)
```

---

## 7. BOT Regulatory Report Mapping

### 7.1 DER_CPEN (Derivative and Credit Exposure Notification)

| DER_CPEN Field | Source Table | Source Column |
|----------------|--------------|---------------|
| Entity Id | entity_master | entity_id |
| Entity Name | entity_master | entity_name |
| Country Code | entity_master | country_code |
| Industry Code | entity_master | industry_sector |
| Involved Party Type | counterparty_master | involved_party_type |
| Residency Flag | counterparty_master | reside_in_thailand_flag |

### 7.2 Liquidity Coverage Ratio (LCR)

| LCR Component | Source Tables | Calculation |
|---------------|---------------|-------------|
| HQLA Level 1 | security_master + bond_positions | is_eligible_crm_collateral = TRUE |
| Cash Outflows | interbank_deals (BORROW) | maturing within 30 days |
| Cash Inflows | interbank_deals (LEND) + repo_trades | maturing within 30 days |

### 7.3 ThaiBMA Trade Reporting

| ThaiBMA Field | Source Table | Source Column |
|---------------|--------------|---------------|
| Trade Date | bond_trades | TradeDate |
| Settlement Date | bond_trades | SettlementDate |
| ISIN | security_master | isin |
| Nominal Amount | bond_trades | NominalAmount |
| Clean Price | bond_trades | CleanPrice |
| Counterparty | counterparty_master | short_code |

---

## 8. Key Data Elements for Regulatory Compliance

### 8.1 TFRS 9 / IFRS 9 Compliance

| Requirement | Implementation |
|-------------|----------------|
| **Business Model Assessment** | portfolio_master.business_model |
| **SPPI Test** | security_master.coupon_rate_type, bond_structure |
| **Classification** | portfolio_master.accounting_classification |
| **ECL Stage 1** | bond_positions.ECLStage = 1 (12-month ECL) |
| **ECL Stage 2** | bond_positions.ECLStage = 2 (Lifetime ECL) |
| **ECL Stage 3** | bond_positions.ECLStage = 3 (Credit-impaired) |
| **Amortized Cost** | bond_positions.AmortizedCost calculation |
| **FVOCI** | Dual tracking in bond_positions |

### 8.2 Basel III Compliance

| Requirement | Implementation |
|-------------|----------------|
| **EAD Calculation** | Sum of exposures from all transaction tables |
| **Risk Weight** | Based on entity_master.entity_type + security_master.rating |
| **LCR HQLA** | security_master.is_eligible_crm_collateral |
| **Large Exposures** | Aggregation at entity_master level |
| **Concentration Risk** | industry_sector, country_code grouping |

### 8.3 Haircut Matrix (BOT Standard)

| Collateral Type | 0-5 Years | 5-10 Years | 10-20 Years | >20 Years |
|-----------------|-----------|------------|-------------|-----------|
| **Haircut %** |
| T-Bills, Gov Bonds, BOT Bonds | 1.0% | 1.5% | 2.5% | 3.0% |
| SOE (Gov guaranteed) | 1.5% | 3.0% | 4.5% | 5.5% |
| **Variation Margin %** |
| T-Bills, Gov Bonds, BOT Bonds | 0.75% | 1.0% | 2.0% | 2.0% |
| SOE (Gov guaranteed) | 1.0% | 2.0% | 3.0% | 3.0% |

---

## Appendix A: Field Mapping Summary

### A.1 Involved Party Type Codes (from Involved_Party_Type sheet)

| Code | Description |
|------|-------------|
| 176039 | Commercial Bank (Thai) |
| (others from sheet) | |

### A.2 Customer Type Codes (from Customer_type_master sheet)

| Code | Description |
|------|-------------|
| 2008 | Financial Institution - Resident |
| (others from sheet) | |

### A.3 Bank Code Reference (sample from BANK_CODE sheet)

| Bank Code | Short Name | Full Name |
|-----------|------------|-----------|
| 001 | BBL | Bangkok Bank PCL |
| 004 | KBANK | Kasikornbank PCL |
| 006 | KTB | Krungthai Bank PCL |
| 022 | CIMB | CIMB Thai Bank PCL |
| 084 | SCB | Siam Commercial Bank PCL |

---

## Appendix B: Data Quality Rules

| Table | Critical Validation |
|-------|---------------------|
| entity_master | entity_id format: short_name + juristic_id (13 digits) |
| counterparty_master | bank_code must exist in BANK_CODE sheet |
| counterparty_master | involved_party_type must exist in Involved_Party_Type |
| security_master | isin format: TH + 9 digits + check digit |
| security_master | issuer_id mapping must be valid (1-4) |
| interbank_deals | maturity_date > value_date |
| repo_trades | collateral_value >= settlement_amount / (1 - haircut) |
| bond_positions | ECLStage in (1, 2, 3) |

---

## Appendix C: Integration Points

| External System | Tables Affected | Integration Method |
|-----------------|-----------------|-------------------|
| **ThaiBMA** | security_master (prices) | API/FTP |
| **BAHTNET** | interbank_deals, repo_trades, cash_margin_movements | SWIFT MT |
| **TSD** | bond_trades, bond_positions | DVP messaging |
| **Core Banking** | limit_utilization (GL postings) | Batch/API |
| **BOT Reporting Portal** | Aggregate from all tables | Regulatory reports |

---

*Document generated from: Treasury System Database V2_Internal.xlsx*  
*Analysis covers 76 sheets with comprehensive data model for Thai Treasury operations*
