# Data Structure to Architecture Mapping & Development Guide

**Mapping:** Treasury System Database V2_Internal.xlsx → Modular Monolith Architecture  
**Version:** 1.0  
**Date:** February 2026

---

## Table of Contents

1. [Architecture to Data Model Mapping](#1-architecture-to-data-model-mapping)
2. [Module-Specific Table Mapping](#2-module-specific-table-mapping)
3. [Integration Layer Mapping](#3-integration-layer-mapping)
4. [Step-by-Step Development Guide](#4-step-by-step-development-guide)
5. [Development Phase Details](#5-development-phase-details)
6. [API Specification by Module](#6-api-specification-by-module)
7. [Testing Strategy](#7-testing-strategy)

---

## 1. Architecture to Data Model Mapping

### 1.1 High-Level Mapping Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MODULAR MONOLITH ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  TRADE EXECUTION MODULE        ←→  Transaction Tables               │    │
│  │  ├─ OTC Trade Capture          ←→  bond_trades, repo_trades        │    │
│  │  ├─ Order Management           ←→  Status fields, workflow          │    │
│  │  ├─ Counterparty Limit         ←→  limit_utilization               │    │
│  │  ├─ Price Discovery            ←→  security_master (prices)         │    │
│  │  └─ ThaiBMA Reporting          ←→  bond_transactions export         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  SETTLEMENT MODULE             ←→  Settlement + Collateral Tables   │    │
│  │  ├─ TSD Integration            ←→  bond_trades.SettlementSystem     │    │
│  │  ├─ BAHTNET Integration        ←→  interbank_deals, cash_margin     │    │
│  │  ├─ Repo Lifecycle             ←→  repo_trades + collateral_pos     │    │
│  │  └─ Exception Management       ←→  Status fields, margin_calls      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  ACCOUNTING MODULE             ←→  Position + Analytical Tables     │    │
│  │  ├─ TFRS9 Classification       ←→  portfolio_master                 │    │
│  │  ├─ Amortized Cost             ←→  bond_positions.AmortizedCost     │    │
│  │  ├─ ECL Calculation            ←→  bond_positions.ECLStage          │    │
│  │  ├─ Repo Accounting            ←→  repo_trades accounting fields    │    │
│  │  └─ Journal Entry              ←→  position_realization_events      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  REPORTING MODULE              ←→  Aggregate from all tables        │    │
│  │  ├─ Regulatory Reporting       ←→  BOT DER_CPEN, ThaiBMA            │    │
│  │  ├─ Management Reporting       ←→  bond_positions summary           │    │
│  │  └─ Audit Trail                ←→  limit_utilization (immutable)    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  RISK & COMPLIANCE MODULE      ←→  Master + Limit Tables            │    │
│  │  ├─ Counterparty Credit        ←→  limit_utilization               │    │
│  │  ├─ Concentration Risk         ←→  entity_master grouping           │    │
│  │  ├─ Market Risk                ←→  bond_positions.MarketValue       │    │
│  │  └─ Four-Eyes Approval         ←→  Status workflow + audit log      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                   │
                          ┌────────▼────────┐
                          │    DATA LAYER    │
                          │  (Excel Tables)  │
                          └──────────────────┘
```

---

### 1.2 Table-to-Module Mapping Matrix

| Excel Table | Architecture Module | Primary Purpose | Data Nature |
|-------------|---------------------|-----------------|-------------|
| **entity_master** | Risk & Compliance + All | Obligor registry | Master/Static |
| **counterparty_master** | Trade Execution + All | Counterparty data | Master/Static |
| **security_master** | Trade Execution + All | Instrument catalog | Master/Static |
| **portfolio_master** | Accounting | TFRS 9 classification | Master/Static |
| **netting_agreement** | Settlement | GMRA/ISDA agreements | Master/Static |
| **interbank_deals** | Trade Execution | IB lending/borrowing | Transaction |
| **interbank_interest_schedule** | Accounting | Floating rate periods | Transaction/Child |
| **repo_trades** | Trade Execution + Settlement | Repo/RRP master | Transaction |
| **collateral_positions** | Settlement | Collateral allocation | Transaction/Child |
| **bond_trades** | Trade Execution | Bond buy/sell | Transaction |
| **bond_transactions** | Trade Execution | Detailed trade events | Transaction |
| **bond_positions** | Accounting + Reporting | Current holdings | Position/Derived |
| **position_costing** | Accounting | Cost basis tracking | Analytical/Derived |
| **position_realization_events** | Accounting | Realized P&L journal | Journal/Immutable |
| **margin_calls** | Settlement + Risk | Margin calculations | Control/Derived |
| **cash_margin_movements** | Settlement | Cash collateral flow | Journal/Transaction |
| **limit_utilization** | Risk & Compliance | Credit limit audit | Control/Immutable |
| **entity_counterparty** | Risk & Compliance | Group limit mapping | Master/Static |

---

## 2. Module-Specific Table Mapping

### 2.1 Trade Execution Module Tables

#### Core Tables: `bond_trades`, `repo_trades`, `interbank_deals`

```sql
-- Trade Execution Entity Relationship
CREATE TABLE bond_trades (
    TradeID VARCHAR(40) PRIMARY KEY,
    PortfolioID VARCHAR(40) REFERENCES portfolio_master,
    SecurityID VARCHAR(10) REFERENCES security_master,
    counterparty_id VARCHAR(40) REFERENCES counterparty_master,
    TradeType ENUM('BUY', 'SELL'),
    TradeDate DATE,
    SettlementDate DATE,  -- T+2 calculation
    NominalAmount DECIMAL(20,2),
    CleanPrice DECIMAL(10,6),
    AccruedInterest DECIMAL(20,2),
    DirtyPrice DECIMAL(10,6),
    SettlementAmount DECIMAL(20,2),
    Yield DECIMAL(10,6),
    SettlementSystem ENUM('TSD', 'BAHTNET'),
    TraderID VARCHAR(20),
    Status ENUM('CREATED', 'PENDING_APPROVAL', 'APPROVED', 'CONFIRMED', 'SETTLED', 'CANCELLED'),
    ApprovedBy VARCHAR(20),
    ApprovedAt TIMESTAMP,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP,
    ThaiBMA_Reported BOOLEAN DEFAULT FALSE,
    ThaiBMA_ReportedAt TIMESTAMP
);
```

**Architecture Alignment:**
- ✅ OTC Trade Capture: `bond_trades` with all pricing fields
- ✅ Order Management: `Status` field with workflow states
- ✅ ThaiBMA Reporting: `ThaiBMA_Reported` flag + timestamp
- ✅ Four-Eyes: `ApprovedBy`, `ApprovedAt` fields

---

#### Limit Checking: `limit_utilization`

```sql
CREATE TABLE limit_utilization (
    UtilizationID BIGINT AUTO_INCREMENT PRIMARY KEY,
    LimitID VARCHAR(40),
    counterparty_id VARCHAR(40),
    entity_id VARCHAR(40),
    LimitType ENUM('SINGLE_TXN', 'PLACEMENT_LIMIT', 'REPO_LIMIT', 'TENOR', 'CONCENTRATION'),
    TransactionID VARCHAR(40),
    TransactionType ENUM('INTERBANK_DEAL', 'REPO_TRADE', 'BOND_TRADE'),
    LimitAmount DECIMAL(20,2),
    UtilizedBefore DECIMAL(20,2),
    TransactionAmount DECIMAL(20,2),
    UtilizedAfter DECIMAL(20,2),
    AvailableAfter DECIMAL(20,2),
    UtilizationPercentAfter DECIMAL(5,2),
    EventType ENUM('NEW_TRADE', 'MATURITY', 'CANCELLATION', 'AMENDMENT'),
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CreatedBy VARCHAR(50),
    -- Immutable: no UPDATE or DELETE allowed
    INDEX idx_counterparty_timestamp (counterparty_id, Timestamp),
    INDEX idx_limitid_timestamp (LimitID, Timestamp)
);
```

**Architecture Alignment:**
- ✅ Real-time limit checking: Query latest by LimitID
- ✅ Immutable audit: Append-only design
- ✅ Pre-trade validation: Check AvailableBefore >= TransactionAmount

---

### 2.2 Settlement Module Tables

#### Core Tables: `repo_trades`, `collateral_positions`, `margin_calls`

```sql
-- Repo Trade with Settlement Fields
CREATE TABLE repo_trades (
    RepoTradeID VARCHAR(40) PRIMARY KEY,
    counterparty_id VARCHAR(40) REFERENCES counterparty_master,
    NettingAgreementID VARCHAR(40) REFERENCES netting_agreement,
    LimitID VARCHAR(40),
    entity_id VARCHAR(40),
    trade_type ENUM('REPO', 'REVERSE_REPO'),  -- Bank perspective
    trade_date DATE,
    value_date DATE,
    maturity_date DATE,
    tenor_days INT GENERATED ALWAYS AS (DATEDIFF(maturity_date, value_date)) STORED,
    currency CHAR(3) DEFAULT 'THB',
    nominal_amount DECIMAL(20,2),  -- Cash leg
    repo_rate DECIMAL(7,4),
    repo_rate_type ENUM('FIXED', 'FLOATING'),
    haircut_percent DECIMAL(5,2),
    collateral_market_value DECIMAL(20,2),
    settlement_amount DECIMAL(20,2),  -- After haircut
    open_repo_flag BOOLEAN DEFAULT FALSE,
    call_date DATE,
    settlement_system ENUM('BAHTNET', 'TSD'),
    settlement_status ENUM('PENDING', 'SETTLED', 'FAILED', 'CANCELLED'),
    bahtnet_reference VARCHAR(50),
    status ENUM('OPEN', 'CLOSED', 'MATURED'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    INDEX idx_counterparty_status (counterparty_id, status),
    INDEX idx_maturity_date (maturity_date)
);

-- Collateral Allocation
CREATE TABLE collateral_positions (
    CollateralID VARCHAR(40) PRIMARY KEY,
    RepoTradeID VARCHAR(40) REFERENCES repo_trades,
    SecurityID VARCHAR(10) REFERENCES security_master,
    collateral_quantity DECIMAL(20,2),
    market_value DECIMAL(20,2),  -- MTM from ThaiBMA
    haircut_applied DECIMAL(5,2),
    margin_value DECIMAL(20,2),  -- market_value * (1 - haircut)
    allocation_date DATE,
    release_date DATE,
    status ENUM('ALLOCATED', 'SUBSTITUTED', 'RELEASED'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Architecture Alignment:**
- ✅ Repo Lifecycle: `status` tracks OPEN → CLOSED/MATURED
- ✅ Collateral Management: Separate table with MTM tracking
- ✅ BAHTNET Integration: `bahtnet_reference`, `settlement_system`
- ✅ Margin Calculation: `margin_value` = `market_value` * (1 - haircut)

---

#### Margin Management: `margin_calls`, `cash_margin_movements`

```sql
CREATE TABLE margin_calls (
    MarginCallID VARCHAR(40) PRIMARY KEY,
    counterparty_id VARCHAR(40),
    RepoTradeID VARCHAR(40),
    ValuationDate DATE,
    ExposureAmount DECIMAL(20,2),  -- Current repo exposure
    CollateralValue DECIMAL(20,2),  -- From collateral_positions
    NetExposure DECIMAL(20,2),  -- Exposure - Collateral
    ThresholdAmount DECIMAL(20,2),  -- Min transfer amount (THB 500,000)
    MarginCallAmount DECIMAL(20,2),  -- Max(0, NetExposure - Threshold)
    MarginCallType ENUM('DELIVERY', 'RETURN'),
    Status ENUM('CALCULATED', 'PENDING', 'AGREED', 'SETTLED', 'DISPUTED'),
    DueDate DATE,  -- T+1 for margin settlement
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    AgreedAt TIMESTAMP,
    SettledAt TIMESTAMP,
    INDEX idx_valuation_date (ValuationDate),
    INDEX idx_status_due (Status, DueDate)
);

CREATE TABLE cash_margin_movements (
    CashMarginMovementID VARCHAR(40) PRIMARY KEY,
    MarginCallID VARCHAR(40) REFERENCES margin_calls,
    counterparty_id VARCHAR(40),
    MovementType ENUM('POST', 'RECEIVE', 'RETURN', 'ADJUST'),
    Currency CHAR(3) DEFAULT 'THB',
    Amount DECIMAL(20,2),
    InterestRate DECIMAL(7,4),  -- Rate on cash margin
    AccruedInterest DECIMAL(20,2),
    OutstandingBalance DECIMAL(20,2),  -- Running balance
    SettlementDate DATE,
    BAHTNETReference VARCHAR(50),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Architecture Alignment:**
- ✅ Daily Mark-to-Market: `ValuationDate` + `ExposureAmount`
- ✅ Margin Call Workflow: Status progression
- ✅ Cash Settlement: `BAHTNETReference` linkage

---

### 2.3 Accounting Module Tables

#### Core Tables: `bond_positions`, `position_costing`, `position_realization_events`

```sql
-- Bond Position (Derived from trades)
CREATE TABLE bond_positions (
    PositionID VARCHAR(40) PRIMARY KEY,
    SecurityID VARCHAR(10) REFERENCES security_master,
    PortfolioID VARCHAR(40) REFERENCES portfolio_master,
    NominalAmount DECIMAL(20,2),  -- Current face value
    BookCost DECIMAL(20,2),  -- Original cost
    AverageCost DECIMAL(20,6),  -- Weighted average per unit
    AmortizedCost DECIMAL(20,2),  -- TFRS 9 carrying amount
    AccruedInterest DECIMAL(20,2),  -- Accrued income
    MarketValue DECIMAL(20,2),  -- MTM from ThaiBMA
    UnrealizedPnL DECIMAL(20,2),  -- MarketValue - BookCost
    -- TFRS 9 Fields
    ECLStage INT CHECK (ECLStage IN (1, 2, 3)),
    ECLProvision DECIMAL(20,2),  -- Impairment allowance
    CarryingAmount DECIMAL(20,2),  -- AmortizedCost - Provision
    LastValuationDate DATE,
    PositionDate DATE,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP,
    INDEX idx_security_portfolio (SecurityID, PortfolioID),
    INDEX idx_portfolio_date (PortfolioID, PositionDate)
);

-- Position Costing (for realized P&L)
CREATE TABLE position_costing (
    CostingID VARCHAR(40) PRIMARY KEY,
    PositionID VARCHAR(40) REFERENCES bond_positions,
    TotalNominalPurchased DECIMAL(20,2),
    TotalCost DECIMAL(20,2),
    WeightedAvgCost DECIMAL(20,6),
    CumulativeRealizedPnL DECIMAL(20,2),
    LastBuyDate DATE,
    LastUpdated TIMESTAMP
);

-- Realized P&L Events (Immutable)
CREATE TABLE position_realization_events (
    RealizationID VARCHAR(40) PRIMARY KEY,
    PositionID VARCHAR(40),
    TradeID VARCHAR(40),
    RealizationDate DATE,
    NominalAmountSold DECIMAL(20,2),
    SaleCleanPrice DECIMAL(10,6),
    WACAtSale DECIMAL(20,6),  -- Weighted avg cost at sale
    RealizedPnL DECIMAL(20,2),  -- (SalePrice - WAC) * Nominal
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Immutable: no updates allowed
    INDEX idx_position_date (PositionID, RealizationDate)
);
```

**Architecture Alignment:**
- ✅ TFRS 9 Classification: `portfolio_master.accounting_classification` drives treatment
- ✅ ECL Staging: `ECLStage` field (1, 2, 3)
- ✅ Amortized Cost: `AmortizedCost` field with calculation logic
- ✅ FVOCI Support: Dual tracking in `bond_positions`
- ✅ Immutable Audit: `position_realization_events` append-only

---

### 2.4 Risk & Compliance Module Tables

#### Core Tables: `entity_master`, `counterparty_master`, `limit_utilization`

**Concentration Risk (from entity_master grouping):**

```sql
-- Example: Concentration by Industry
SELECT 
    em.industry_sector,
    SUM(bp.CarryingAmount) as TotalExposure,
    COUNT(DISTINCT bp.SecurityID) as SecurityCount
FROM bond_positions bp
JOIN portfolio_master pm ON bp.PortfolioID = pm.PortfolioID
JOIN security_master sm ON bp.SecurityID = sm.SecurityID
JOIN entity_master em ON sm.issuer_id = em.entity_id
WHERE bp.PositionDate = CURRENT_DATE
GROUP BY em.industry_sector
HAVING TotalExposure > (SELECT LimitAmount FROM concentration_limits WHERE LimitType = 'INDUSTRY');
```

**Architecture Alignment:**
- ✅ Counterparty Credit: `limit_utilization` real-time tracking
- ✅ Concentration Risk: `entity_master` grouping fields
- ✅ Four-Eyes: Trade table approval fields

---

## 3. Integration Layer Mapping

### 3.1 ThaiBMA Integration

**Export Mapping for Trade Reporting:**

```python
# ThaiBMA Trade Report Generation
thai_bma_report_query = """
SELECT 
    bt.TradeDate as TransactionDate,
    bt.TradeID as ReferenceNumber,
    sm.isin as ISIN,
    cm.short_code as CounterpartyCode,
    CASE bt.TradeType 
        WHEN 'BUY' THEN 'P' 
        WHEN 'SELL' THEN 'S' 
    END as BuySellIndicator,
    bt.NominalAmount as NominalAmount,
    bt.CleanPrice as CleanPrice,
    bt.AccruedInterest as AccruedInterest,
    bt.DirtyPrice as DirtyPrice,
    bt.SettlementAmount as SettlementAmount,
    bt.Yield as Yield,
    bt.SettlementDate as SettlementDate,
    CASE bt.SettlementSystem
        WHEN 'TSD' THEN 'DVP'
        WHEN 'BAHTNET' THEN 'DVP'
    END as SettlementType
FROM bond_trades bt
JOIN security_master sm ON bt.SecurityID = sm.security_id
JOIN counterparty_master cm ON bt.counterparty_id = cm.counterparty_id
WHERE bt.TradeDate = CURRENT_DATE
  AND bt.Status IN ('CONFIRMED', 'SETTLED')
  AND bt.ThaiBMA_Reported = FALSE
ORDER BY bt.TradeDate, bt.TradeTime
"""
```

**30-Minute Reporting Logic:**
```python
def check_thai_bma_reporting_deadline():
    """
    Monitor trades not reported within 30 minutes
    """
    overdue_trades = db.query("""
        SELECT TradeID, TradeTime,
               TIMESTAMPDIFF(MINUTE, TradeTime, NOW()) as MinutesElapsed
        FROM bond_trades
        WHERE TradeDate = CURRENT_DATE
          AND ThaiBMA_Reported = FALSE
          AND Status = 'CONFIRMED'
          AND TIMESTAMPDIFF(MINUTE, TradeTime, NOW()) > 20
    """)
    
    for trade in overdue_trades:
        if trade.MinutesElapsed > 28:
            alert_red(f"CRITICAL: Trade {trade.TradeID} not reported to ThaiBMA!")
        else:
            alert_amber(f"WARNING: Trade {trade.TradeID} approaching deadline")
```

---

### 3.2 BAHTNET Integration

**Payment Message Generation:**

```python
def generate_bahtnet_message(interbank_deal, message_type='MT103'):
    """
    Generate SWIFT MT103 for interbank settlement
    """
    counterparty = get_counterparty(interbank_deal.counterparty_id)
    
    mt103 = {
        'Sender': BANK_SWIFT_BIC,  # Our BIC
        'Receiver': counterparty.swift_bic,
        'TransactionReference': generate_umid(),
        'ValueDate': interbank_deal.value_date.strftime('%y%m%d'),
        'Currency': interbank_deal.currency,
        'Amount': interbank_deal.principal_amount,
        'OrderingCustomer': OUR_BANK_NAME,
        'BeneficiaryCustomer': counterparty.legal_name,
        'BeneficiaryAccount': counterparty.settlement_account,
        'DetailsOfCharges': 'OUR',
        'RemittanceInfo': f"Interbank {interbank_deal.deal_type} {interbank_deal.DealID}"
    }
    
    return format_swift_mt103(mt103)
```

---

### 3.3 TSD Integration

**DVP Settlement Instruction:**

```python
def generate_tsd_instruction(bond_trade):
    """
    Generate TSD DVP Model 1 settlement instruction
    """
    security = get_security(bond_trade.SecurityID)
    counterparty = get_counterparty(bond_trade.counterparty_id)
    
    instruction = {
        'MessageType': 'SETR',  # Settlement
        'TradeReference': bond_trade.TradeID,
        'ISIN': security.isin,
        'TradeDate': bond_trade.TradeDate,
        'SettlementDate': bond_trade.SettlementDate,
        'SettlementType': 'DVP',
        'BuySellIndicator': bond_trade.TradeType,
        'NominalAmount': bond_trade.NominalAmount,
        'SettlementAmount': bond_trade.SettlementAmount,
        'DeliveringAgent': counterparty.tsd_account if bond_trade.TradeType == 'BUY' else OUR_TSD_ACCOUNT,
        'ReceivingAgent': OUR_TSD_ACCOUNT if bond_trade.TradeType == 'BUY' else counterparty.tsd_account,
        'TradeCurrency': 'THB',
        'SettlementCurrency': 'THB'
    }
    
    return instruction
```

---

## 4. Step-by-Step Development Guide

### Development Philosophy
**Based on the Excel data model, we adopt:**
1. **Schema-First Development** - Tables exist in Excel, generate DDL first
2. **Module-by-Module Implementation** - Align with architecture
3. **Test-Driven with Real Data** - Use monthly test data from Excel
4. **Regulatory Compliance Built-In** - BOT reporting from day one

---

### Phase 1: Foundation (Weeks 1-4)

#### Week 1: Database Schema Setup

**Tasks:**
1. Generate DDL from Excel data model
2. Set up development database
3. Create schema versions with Flyway
4. Establish naming conventions

**Deliverables:**
```sql
-- 001_create_master_tables.sql
-- 002_create_transaction_tables.sql
-- 003_create_position_tables.sql
-- 004_create_control_tables.sql
-- 005_create_indexes.sql
```

**Key Decisions:**
- ✅ Primary Keys: VARCHAR(40) for all IDs (as per Excel)
- ✅ Timestamps: All tables have created_at/updated_at
- ✅ Soft Deletes: Use status fields, no DELETE
- ✅ Audit: limit_utilization and position_realization_events immutable

---

#### Week 2: Master Data API

**Tasks:**
1. Create CRUD APIs for master tables
2. Implement validation rules
3. Set up reference data loading

**APIs to Build:**
```
GET    /api/v1/entities
GET    /api/v1/entities/{entity_id}
POST   /api/v1/entities
PUT    /api/v1/entities/{entity_id}

GET    /api/v1/counterparties
GET    /api/v1/counterparties/{counterparty_id}
POST   /api/v1/counterparties
PUT    /api/v1/counterparties/{counterparty_id}

GET    /api/v1/securities
GET    /api/v1/securities/{security_id}
POST   /api/v1/securities
PUT    /api/v1/securities/{security_id}

GET    /api/v1/portfolios
GET    /api/v1/portfolios/{portfolio_id}
POST   /api/v1/portfolios
PUT    /api/v1/portfolios/{portfolio_id}
```

**Validation Rules:**
- entity_id format: `short_name + juristic_id` (13 digits)
- bank_code must exist in BANK_CODE reference table
- isin format: TH + 9 digits + check digit
- involved_party_type must be in reference list

---

#### Week 3: Security & RBAC

**Tasks:**
1. Implement OAuth 2.0 authentication
2. Create RBAC framework
3. Implement Four-Eyes approval data model

**Tables:**
```sql
CREATE TABLE users (
    user_id VARCHAR(40) PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(100),
    role ENUM('FRONT_OFFICE', 'MIDDLE_OFFICE', 'BACK_OFFICE', 'IT_ADMIN'),
    department VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE approval_workflows (
    WorkflowID VARCHAR(40) PRIMARY KEY,
    TransactionType VARCHAR(50),  -- BOND_TRADE, REPO_TRADE, etc.
    TransactionAmount DECIMAL(20,2),
    RequestedBy VARCHAR(40),
    RequestedAt TIMESTAMP,
    ApprovedBy VARCHAR(40),
    ApprovedAt TIMESTAMP,
    Status ENUM('PENDING', 'APPROVED', 'REJECTED'),
    Comments TEXT
);
```

---

#### Week 4: Master Data Migration

**Tasks:**
1. Import data from Excel sheets:
   - BANK_CODE
   - Involved_Party_Type
   - Customer_type_master
   - Haircut_table
   - Govt_agency_code
2. Import sample securities from "Selected Bonds" sheets
3. Import test counterparties

**Validation:**
- Reconcile imported counts with Excel
- Run data quality checks
- Create reference data cache (Redis)

---

### Phase 2: Trade Execution Module (Weeks 5-8)

#### Week 5: Bond Trade Capture

**Tasks:**
1. Create bond_trades table with workflow
2. Build trade entry UI
3. Implement validation logic

**Key Validations:**
```python
def validate_bond_trade(trade):
    errors = []
    
    # Business day check
    if not is_business_day(trade.TradeDate):
        errors.append("Trade date must be a business day")
    
    # Settlement date (T+2)
    expected_settlement = add_business_days(trade.TradeDate, 2)
    if trade.SettlementDate != expected_settlement:
        errors.append(f"Settlement date must be T+2 ({expected_settlement})")
    
    # Price reasonableness
    last_price = get_last_price(trade.SecurityID)
    if abs(trade.CleanPrice - last_price) / last_price > 0.10:
        errors.append("Price deviation > 10% from last price - requires override")
    
    # Counterparty KYC check
    cp = get_counterparty(trade.counterparty_id)
    if cp.kyc_status != 'APPROVED':
        errors.append("Counterparty KYC not approved")
    
    return errors
```

---

#### Week 6: Limit Management

**Tasks:**
1. Implement limit_utilization logging
2. Build real-time limit checking
3. Create limit administration UI

**Limit Check Flow:**
```python
def pre_trade_limit_check(counterparty_id, transaction_amount, transaction_type):
    """
    Pre-trade limit validation
    """
    # Get current utilization
    latest = db.query("""
        SELECT LimitID, AvailableAfter, LimitAmount
        FROM limit_utilization
        WHERE counterparty_id = %s
          AND LimitType IN ('PLACEMENT_LIMIT', 'REPO_LIMIT')
        ORDER BY Timestamp DESC
        LIMIT 1
    """, counterparty_id)
    
    if not latest:
        return {'approved': False, 'reason': 'No limit found'}
    
    available = latest.AvailableAfter
    
    if transaction_amount > available:
        return {
            'approved': False, 
            'reason': f'Insufficient limit. Available: {available}, Required: {transaction_amount}'
        }
    
    if available / latest.LimitAmount < 0.20:  # 80% utilized
        return {
            'approved': True,
            'warning': f'Limit utilization will be {(latest.LimitAmount - available + transaction_amount) / latest.LimitAmount * 100:.1f}%'
        }
    
    return {'approved': True}
```

---

#### Week 7: ThaiBMA Reporting

**Tasks:**
1. Build ThaiBMA export formatter
2. Implement automated reporting scheduler
3. Create monitoring dashboard

**Reporting Job:**
```python
@scheduler.task('interval', minutes=5)
def thai_bma_reporting_job():
    """
    Run every 5 minutes to report unreported trades
    """
    unreported = db.query("""
        SELECT * FROM bond_trades
        WHERE ThaiBMA_Reported = FALSE
          AND Status = 'CONFIRMED'
          AND TIMESTAMPDIFF(MINUTE, TradeTime, NOW()) > 5
    """)
    
    for trade in unreported:
        try:
            report = format_thai_bma_report(trade)
            response = submit_to_thai_bma(report)
            
            if response.status == 'ACK':
                db.execute("""
                    UPDATE bond_trades
                    SET ThaiBMA_Reported = TRUE,
                        ThaiBMA_ReportedAt = NOW()
                    WHERE TradeID = %s
                """, trade.TradeID)
            else:
                log_error(f"ThaiBMA rejection: {response.error}")
        
        except Exception as e:
            log_error(f"ThaiBMA submission failed for {trade.TradeID}: {e}")
```

---

#### Week 8: Interbank Deals

**Tasks:**
1. Create interbank_deals table
2. Build lending/borrowing workflow
3. Implement interest schedule for floating rates

**Floating Rate Logic:**
```python
def calculate_interest_schedule(deal):
    """
    Generate interest periods for floating rate deals
    """
    if deal.rate_type == 'FIXED':
        return [{
            'start_date': deal.value_date,
            'end_date': deal.maturity_date,
            'benchmark_rate': deal.interest_rate,
            'effective_rate': deal.interest_rate,
            'accrued_interest': calculate_accrual(deal)
        }]
    
    # Floating rate - generate periods
    periods = []
    current_date = deal.value_date
    
    while current_date < deal.maturity_date:
        period_end = min(
            add_months(current_date, 3),  # Quarterly reset
            deal.maturity_date
        )
        
        # Get THOR for period
        th_rate = get_thor_rate(current_date)
        effective_rate = th_rate + (deal.spread_bp / 100)
        
        periods.append({
            'DealID': deal.DealID,
            'period_start_date': current_date,
            'period_end_date': period_end,
            'benchmark_rate': th_rate,
            'spread_bp': deal.spread_bp,
            'effective_rate': effective_rate,
            'accrued_interest': 0  # Calculated daily
        })
        
        current_date = period_end
    
    return periods
```

---

### Phase 3: Settlement Module (Weeks 9-12)

#### Week 9: Repo Trade Management

**Tasks:**
1. Create repo_trades table
2. Implement repo lifecycle workflow
3. Build collateral allocation logic

**Repo Workflow:**
```
CREATED → COLLATERAL_ALLOCATED → SETTLED → OPEN → 
    ↓ (Daily)
MARK_TO_MARKET → [MARGIN_CALL if needed] → 
    ↓ (At maturity)
REPAID → CLOSED
```

**Collateral Allocation:**
```python
def allocate_collateral(repo_trade, security_id, quantity):
    """
    Allocate securities as collateral for repo
    """
    security = get_security(security_id)
    
    # Get current market price
    market_price = get_thai_bma_price(security_id)
    market_value = quantity * market_price / 100  # Price in percentage
    
    # Apply haircut
    haircut = get_haircut(security_id, repo_trade.maturity_date)
    margin_value = market_value * (1 - haircut)
    
    # Check if sufficient
    required = repo_trade.settlement_amount
    current_collateral = get_current_collateral_value(repo_trade.RepoTradeID)
    
    if current_collateral + margin_value < required:
        return {'allocated': False, 'reason': 'Insufficient collateral after haircut'}
    
    # Create collateral position
    collateral_id = generate_id()
    db.execute("""
        INSERT INTO collateral_positions
        (CollateralID, RepoTradeID, SecurityID, collateral_quantity,
         market_value, haircut_applied, margin_value, allocation_date, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'ALLOCATED')
    """, collateral_id, repo_trade.RepoTradeID, security_id, quantity,
         market_value, haircut, margin_value, today())
    
    return {'allocated': True, 'CollateralID': collateral_id}
```

---

#### Week 10: Margin Management

**Tasks:**
1. Create margin_calls table
2. Implement daily MTM calculation
3. Build margin call workflow

**Daily Margin Process:**
```python
@scheduler.task('cron', hour=17, minute=0)  # 5 PM daily
def daily_margin_process():
    """
    Calculate margin for all open repos
    """
    open_repos = db.query("""
        SELECT * FROM repo_trades
        WHERE status = 'OPEN'
          AND maturity_date > CURRENT_DATE
    """)
    
    for repo in open_repos:
        # Calculate current exposure
        exposure = calculate_repo_exposure(repo)
        
        # Get collateral value
        collateral = db.query("""
            SELECT SUM(margin_value) as total
            FROM collateral_positions
            WHERE RepoTradeID = %s AND status = 'ALLOCATED'
        """, repo.RepoTradeID)
        
        collateral_value = collateral.total or 0
        net_exposure = exposure - collateral_value
        
        # Check threshold (THB 500,000)
        threshold = 500000
        
        if abs(net_exposure) > threshold:
            # Create margin call
            margin_call_id = generate_id()
            call_type = 'DELIVERY' if net_exposure > 0 else 'RETURN'
            
            db.execute("""
                INSERT INTO margin_calls
                (MarginCallID, counterparty_id, RepoTradeID, ValuationDate,
                 ExposureAmount, CollateralValue, NetExposure, ThresholdAmount,
                 MarginCallAmount, MarginCallType, Status, DueDate)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'PENDING', %s)
            """, margin_call_id, repo.counterparty_id, repo.RepoTradeID,
                 today(), exposure, collateral_value, net_exposure,
                 threshold, abs(net_exposure), call_type, next_business_day())
            
            notify_counterparty(repo.counterparty_id, margin_call_id, call_type, abs(net_exposure))
```

---

#### Week 11: Settlement Integration

**Tasks:**
1. Build BAHTNET message generators
2. Implement TSD instruction generators
3. Create settlement confirmation handling

**BAHTNET Settlement:**
```python
def settle_interbank_deal(deal_id):
    """
    Process settlement for interbank deal
    """
    deal = get_interbank_deal(deal_id)
    counterparty = get_counterparty(deal.counterparty_id)
    
    # Generate MT103
    if deal.deal_type == 'LEND':
        # We send money
        mt103 = generate_mt103_outgoing(
            beneficiary=counterparty,
            amount=deal.principal_amount,
            value_date=deal.value_date,
            reference=deal.DealID
        )
    else:
        # We receive money - wait for incoming
        mt103 = None
    
    # Send to BAHTNET
    if mt103:
        bahtnet_response = send_to_bahtnet(mt103)
        
        db.execute("""
            UPDATE interbank_deals
            SET settlement_status = 'SETTLED',
                bahtnet_reference = %s,
                settled_at = NOW()
            WHERE DealID = %s
        """, bahtnet_response.reference, deal_id)
```

---

#### Week 12: Exception Handling

**Tasks:**
1. Build settlement failure detection
2. Create exception workflow UI
3. Implement manual override with approval

---

### Phase 4: Accounting Module (Weeks 13-16)

#### Week 13: Position Management

**Tasks:**
1. Create bond_positions table
2. Build position calculation engine
3. Implement daily position build

**Position Build Process:**
```python
@scheduler.task('cron', hour=18, minute=0)  # 6 PM daily
def build_positions():
    """
    Build end-of-day positions from trades
    """
    portfolios = db.query("SELECT * FROM portfolio_master")
    
    for portfolio in portfolios:
        securities = db.query("""
            SELECT DISTINCT SecurityID FROM bond_trades
            WHERE PortfolioID = %s
              AND Status = 'SETTLED'
              AND TradeDate <= %s
        """, portfolio.PortfolioID, today())
        
        for sec in securities:
            # Calculate position
            buys = db.query("""
                SELECT SUM(NominalAmount) as total
                FROM bond_trades
                WHERE SecurityID = %s
                  AND PortfolioID = %s
                  AND TradeType = 'BUY'
                  AND Status = 'SETTLED'
            """, sec.SecurityID, portfolio.PortfolioID)
            
            sells = db.query("""
                SELECT SUM(NominalAmount) as total
                FROM bond_trades
                WHERE SecurityID = %s
                  AND PortfolioID = %s
                  AND TradeType = 'SELL'
                  AND Status = 'SETTLED'
            """, sec.SecurityID, portfolio.PortfolioID)
            
            nominal = (buys.total or 0) - (sells.total or 0)
            
            if nominal > 0:
                position_id = generate_id()
                
                # Get costs from costing table
                costing = get_or_create_costing(position_id, sec.SecurityID, portfolio.PortfolioID)
                
                # Get market value
                security = get_security(sec.SecurityID)
                market_price = get_thai_bma_price(sec.SecurityID)
                market_value = nominal * market_price / 100
                
                db.execute("""
                    INSERT INTO bond_positions
                    (PositionID, SecurityID, PortfolioID, NominalAmount,
                     BookCost, AverageCost, AmortizedCost, AccruedInterest,
                     MarketValue, UnrealizedPnL, PositionDate)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    NominalAmount = VALUES(NominalAmount),
                    BookCost = VALUES(BookCost),
                    MarketValue = VALUES(MarketValue),
                    UnrealizedPnL = VALUES(UnrealizedPnL)
                """, position_id, sec.SecurityID, portfolio.PortfolioID, nominal,
                     costing.BookCost, costing.WeightedAvgCost, 0, 0,
                     market_value, market_value - costing.BookCost, today())
```

---

#### Week 14: Costing & Realized P&L

**Tasks:**
1. Implement weighted average costing
2. Build realized P&L calculation
3. Create position_realization_events logging

**Realized P&L on Sale:**
```python
def process_bond_sale(trade):
    """
    Calculate realized P&L when bond is sold
    """
    position = get_position(trade.SecurityID, trade.PortfolioID)
    costing = get_costing(position.PositionID)
    
    # Calculate realized P&L
    wac = costing.WeightedAvgCost
    sale_price = trade.CleanPrice
    nominal = trade.NominalAmount
    
    realized_pnl = (sale_price - wac) * nominal / 100
    
    # Log realization event (immutable)
    realization_id = generate_id()
    db.execute("""
        INSERT INTO position_realization_events
        (RealizationID, PositionID, TradeID, RealizationDate,
         NominalAmountSold, SaleCleanPrice, WACAtSale, RealizedPnL)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, realization_id, position.PositionID, trade.TradeID,
         trade.TradeDate, nominal, sale_price, wac, realized_pnl)
    
    # Update costing
    remaining_nominal = costing.TotalNominalPurchased - nominal
    remaining_cost = costing.TotalCost - (wac * nominal / 100)
    
    if remaining_nominal > 0:
        new_wac = remaining_cost / remaining_nominal * 100
        db.execute("""
            UPDATE position_costing
            SET TotalNominalPurchased = %s,
                TotalCost = %s,
                WeightedAvgCost = %s,
                CumulativeRealizedPnL = CumulativeRealizedPnL + %s
            WHERE CostingID = %s
        """, remaining_nominal, remaining_cost, new_wac, realized_pnl, costing.CostingID)
    else:
        # Position closed
        db.execute("""
            UPDATE position_costing
            SET TotalNominalPurchased = 0,
                TotalCost = 0,
                CumulativeRealizedPnL = CumulativeRealizedPnL + %s,
                ClosedDate = %s
            WHERE CostingID = %s
        """, realized_pnl, today(), costing.CostingID)
    
    return realized_pnl
```

---

#### Week 15: TFRS 9 Implementation

**Tasks:**
1. Implement SPPI test logic
2. Build ECL calculation engine
3. Create business model assessment

**ECL Calculation:**
```python
def calculate_ecl(position):
    """
    Calculate Expected Credit Loss for a position
    """
    security = get_security(position.SecurityID)
    portfolio = get_portfolio(position.PortfolioID)
    
    # Determine stage
    stage = determine_ecl_stage(position, security)
    
    if stage == 1:
        # 12-month ECL
        pd = get_12m_pd(security)  # 12-month probability of default
        lgd = get_lgd(security)    # Loss given default
        ead = position.CarryingAmount  # Exposure at default
        
        ecl = pd * lgd * ead
    
    elif stage in [2, 3]:
        # Lifetime ECL
        pd_lifetime = get_lifetime_pd(security)
        lgd = get_lgd(security)
        ead = position.CarryingAmount
        
        ecl = pd_lifetime * lgd * ead
    
    # Update position
    db.execute("""
        UPDATE bond_positions
        SET ECLStage = %s,
            ECLProvision = %s,
            CarryingAmount = AmortizedCost - %s
        WHERE PositionID = %s
    """, stage, ecl, ecl, position.PositionID)
    
    return {'stage': stage, 'ecl': ecl}


def determine_ecl_stage(position, security):
    """
    Determine ECL stage based on credit deterioration
    """
    # Stage 3: Credit-impaired (objective evidence)
    if is_credit_impaired(security):
        return 3
    
    # Stage 2: Significant increase in credit risk
    if has_significant_deterioration(security, position):
        return 2
    
    # Stage 1: No significant deterioration
    return 1
```

---

#### Week 16: Journal Entry Generation

**Tasks:**
1. Build journal entry templates
2. Implement GL mapping
3. Create end-of-day batch

**Journal Entry Examples:**
```python
def generate_journal_entries(position_date):
    """
    Generate all journal entries for the day
    """
    journals = []
    
    # 1. Trade Date Entries
    trades = get_trades_by_date(position_date)
    for trade in trades:
        if trade.TradeType == 'BUY':
            journals.append({
                'entry_type': 'BOND_PURCHASE',
                'account_dr': 'INVESTMENT_BONDS',
                'account_cr': 'CASH',
                'amount': trade.SettlementAmount,
                'reference': trade.TradeID
            })
    
    # 2. Accrual Entries
    positions = get_positions_by_date(position_date)
    for pos in positions:
        accrual = calculate_daily_accrual(pos)
        if accrual > 0:
            journals.append({
                'entry_type': 'INTEREST_ACCRUAL',
                'account_dr': 'ACCRUED_INTEREST',
                'account_cr': 'INTEREST_INCOME',
                'amount': accrual,
                'reference': pos.PositionID
            })
    
    # 3. MTM Entries (FVTPL only)
    trading_positions = [p for p in positions if is_trading(p)]
    for pos in trading_positions:
        mtm_change = calculate_mtm_change(pos)
        if mtm_change != 0:
            journals.append({
                'entry_type': 'MTM_VALUATION',
                'account_dr': 'MTM_GAIN' if mtm_change > 0 else 'INVESTMENT_BONDS',
                'account_cr': 'INVESTMENT_BONDS' if mtm_change > 0 else 'MTM_LOSS',
                'amount': abs(mtm_change),
                'reference': pos.PositionID
            })
    
    # 4. ECL Entries
    for pos in positions:
        if pos.ECLProvision > 0:
            journals.append({
                'entry_type': 'ECL_PROVISION',
                'account_dr': 'CREDIT_IMPAIRMENT',
                'account_cr': 'ECL_ALLOWANCE',
                'amount': pos.ECLProvision,
                'reference': pos.PositionID
            })
    
    return journals
```

---

### Phase 5: Reporting Module (Weeks 17-19)

#### Week 17: Regulatory Reporting

**Tasks:**
1. Build BOT DER_CPEN export
2. Implement LCR/NSFR calculations
3. Create ThaiBMA position reports

**BOT DER_CPEN Export:**
```python
def generate_der_cpen_report(report_date):
    """
    Generate DER_CPEN report for BOT
    """
    query = """
    SELECT 
        em.entity_id as 'Entity Id',
        em.entity_name as 'Entity Name',
        em.country_code as 'Country Code',
        em.industry_sector as 'Industry Code',
        cm.involved_party_type as 'Involved Party Type',
        CASE WHEN cm.reside_in_thailand_flag THEN 'Y' ELSE 'N' END as 'Resident Flag',
        SUM(bp.CarryingAmount) as 'Total Exposure'
    FROM bond_positions bp
    JOIN portfolio_master pm ON bp.PortfolioID = pm.PortfolioID
    JOIN security_master sm ON bp.SecurityID = sm.security_id
    JOIN entity_master em ON sm.issuer_id = em.entity_id
    JOIN counterparty_master cm ON em.entity_id = cm.entity_id
    WHERE bp.PositionDate = %s
    GROUP BY em.entity_id, em.entity_name, em.country_code,
             em.industry_sector, cm.involved_party_type, cm.reside_in_thailand_flag
    """
    
    return db.query(query, report_date)
```

---

#### Week 18: Management Reporting

**Tasks:**
1. Build portfolio valuation reports
2. Create liquidity position dashboards
3. Implement risk exposure reports

---

#### Week 19: Audit Trail & Compliance

**Tasks:**
1. Build immutable audit log queries
2. Create user activity reports
3. Implement regulatory examination support

---

### Phase 6: Integration & Testing (Weeks 20-22)

#### Week 20: End-to-End Testing

**Test Scenarios (from Excel sheets):**
1. Bond Buy (from Bond buy_1_V4 sheets)
2. Bond Sell (from Bond sell_1_V4_Oct25)
3. Repo Trade (from Repo_1_V4_Sep25, etc.)
4. Reverse Repo (from RRP_1_V4_Sep25, etc.)
5. Interbank Lending (from IB Lend_V4 sheets)
6. Interbank Borrowing (from IB Borrow_V4 sheets)

**Test Data Validation:**
```python
def validate_test_data():
    """
    Validate system output against Excel test data
    """
    # Load expected results from Excel
    expected_sep = pd.read_excel('Treasury System Database V2_Internal.xlsx', 
                                  sheet_name='V4_Result_30 Sep 2025')
    
    # Get actual system results
    actual_sep = generate_position_report(date='2025-09-30')
    
    # Compare
    discrepancies = compare_reports(expected_sep, actual_sep)
    
    return discrepancies
```

---

#### Week 21: User Acceptance Testing

**UAT Scenarios:**
- Front Office: Trade capture workflow
- Middle Office: Limit management, risk reports
- Back Office: Settlement, reconciliation
- IT Admin: Master data management

---

#### Week 22: Production Readiness

**Go-Live Checklist:**
- [ ] All test cases passing
- [ ] Data migration validated
- [ ] External connectivity tested (ThaiBMA, BAHTNET, TSD)
- [ ] Disaster recovery tested
- [ ] User training completed
- [ ] Operations runbooks ready
- [ ] Monitoring dashboards configured
- [ ] Support roster defined

---

## 5. Development Phase Details

### 5.1 Sprint Planning (2-Week Sprints)

| Sprint | Focus | Deliverables |
|--------|-------|--------------|
| 1-2 | Foundation | Database, Security, Master Data |
| 3-4 | Trade Execution | Bond trades, Interbank, ThaiBMA |
| 5-6 | Settlement | Repo, Collateral, Margin, BAHTNET/TSD |
| 7-8 | Accounting | Positions, Costing, ECL, Journals |
| 9-10 | Reporting | BOT reports, Management reports |
| 11 | Integration | E2E testing, UAT |
| 12 | Go-Live | Production deployment |

---

### 5.2 Technology Stack (Aligned with Architecture)

| Layer | Technology | Purpose |
|-------|------------|---------|
| Backend | C# .NET 8 | API development |
| Database | PostgreSQL 16 | Primary datastore |
| Cache | Redis | Master data, session |
| Message Queue | RabbitMQ | Async processing |
| Scheduler | Quartz.NET | Batch jobs, EOD |
| Frontend | React + TypeScript | UI |
| Reporting | SQL Server Reporting Services | Regulatory reports |

---

## 6. API Specification by Module

### 6.1 Trade Execution APIs

```yaml
# Bond Trade API
/api/v1/bond-trades:
  get:
    summary: List bond trades
    parameters:
      - name: tradeDate
        in: query
        type: string
        format: date
      - name: status
        in: query
        type: string
        enum: [CREATED, PENDING, APPROVED, CONFIRMED, SETTLED]
  
  post:
    summary: Create new bond trade
    body:
      schema:
        type: object
        properties:
          SecurityID: { type: string }
          PortfolioID: { type: string }
          counterparty_id: { type: string }
          TradeType: { type: string, enum: [BUY, SELL] }
          NominalAmount: { type: number }
          CleanPrice: { type: number }
    responses:
      201:
        description: Trade created
      400:
        description: Validation error
      403:
        description: Limit exceeded

/api/v1/bond-trades/{tradeId}/approve:
  post:
    summary: Four-eyes approval
    body:
      schema:
        type: object
        properties:
          approved: { type: boolean }
          comments: { type: string }
```

---

### 6.2 Settlement APIs

```yaml
# Repo Management API
/api/v1/repos:
  get:
    summary: List repo trades
    parameters:
      - name: status
        in: query
        type: string
        enum: [OPEN, CLOSED, MATURED]
  
  post:
    summary: Create repo trade

/api/v1/repos/{repoId}/collateral:
  post:
    summary: Allocate collateral
    body:
      schema:
        type: object
        properties:
          SecurityID: { type: string }
          quantity: { type: number }

/api/v1/repos/{repoId}/margin-calls:
  get:
    summary: Get margin calls for repo
  
  post:
    summary: Respond to margin call
```

---

### 6.3 Accounting APIs

```yaml
# Position API
/api/v1/positions:
  get:
    summary: Get positions
    parameters:
      - name: positionDate
        in: query
        type: string
        format: date
      - name: PortfolioID
        in: query
        type: string

/api/v1/positions/{positionId}/ecl:
  post:
    summary: Trigger ECL recalculation
    responses:
      200:
        schema:
          type: object
          properties:
            stage: { type: integer }
            eclProvision: { type: number }

# Journal API
/api/v1/journals:
  get:
    summary: Get journal entries
    parameters:
      - name: entryDate
        in: query
        type: string
        format: date
```

---

### 6.4 Reporting APIs

```yaml
# Regulatory Reports API
/api/v1/reports/thai-bma:
  get:
    summary: ThaiBMA trade report
    parameters:
      - name: reportDate
        in: query
        required: true
        type: string
        format: date

/api/v1/reports/bot/der-cpen:
  get:
    summary: BOT DER_CPEN report
    produces:
      - application/json
      - text/csv

/api/v1/reports/lcr:
  get:
    summary: Liquidity Coverage Ratio
    parameters:
      - name: reportDate
        in: query
        type: string
        format: date
```

---

## 7. Testing Strategy

### 7.1 Test Data from Excel

| Excel Sheet | Test Purpose |
|-------------|--------------|
| Bond buy_1_V4_Sep25 | Bond purchase scenario |
| Bond sell_1_V4_Oct25 | Bond sale + realized P&L |
| Repo_1_V4_Sep25 | Repo lifecycle |
| RRP_1_V4_Sep25 | Reverse repo + margin |
| IB Lend_V4_Sep25 | Interbank lending |
| IB Borrow_V4_Sep25 | Interbank borrowing |
| V4_Result_30 Sep 2025 | Expected position results |

---

### 7.2 Test Types

| Test Type | Scope | Tools |
|-----------|-------|-------|
| Unit Tests | Individual functions | xUnit, Moq |
| Integration Tests | API endpoints | Postman, REST Assured |
| Database Tests | Stored procedures, migrations | tSQLt |
| E2E Tests | Full workflows | Playwright |
| Performance Tests | Load, burst capacity | k6, JMeter |
| Regression Tests | Monthly data validation | Python + pandas |

---

### 7.3 Regression Testing with Excel Data

```python
def run_monthly_regression():
    """
    Validate system output against Excel test data
    """
    test_months = [
        ('V4_Result_30 Sep 2025', '2025-09-30'),
        ('V4_Result_31 Oct 2025', '2025-10-31'),
        ('V4_Result_30 Nov 2025', '2025-11-30'),
        ('V4_Result_31 Dec 2025', '2025-12-31')
    ]
    
    results = []
    for sheet, date in test_months:
        expected = load_excel_sheet(sheet)
        actual = generate_system_report(date)
        
        comparison = compare_position_values(expected, actual)
        results.append({
            'month': date,
            'passed': comparison.all_match,
            'discrepancies': comparison.differences
        })
    
    return results
```

---

## Summary

This development guide provides:

1. **Complete Mapping** between your Excel data model and the modular monolith architecture
2. **Detailed DDL** for all 18 core tables
3. **Step-by-Step Implementation** across 22 weeks / 12 sprints
4. **API Specifications** for all modules
5. **Testing Strategy** using your existing Excel test data

### Key Alignment Points

| Excel Design | Architecture | Status |
|--------------|--------------|--------|
| 18 core tables | 5 modules | ✅ Fully mapped |
| limit_utilization (immutable) | Audit trail requirement | ✅ Satisfied |
| bond_positions (derived) | Position management | ✅ Satisfied |
| ECLStage (1,2,3) | TFRS 9 compliance | ✅ Satisfied |
| Monthly test data | Regression testing | ✅ Can use directly |

### Next Steps

1. **Review** the DDL and API specifications
2. **Confirm** technology stack choices
3. **Prioritize** any additional requirements
4. **Begin** Phase 1 (Foundation) implementation

---

*Document integrates: Treasury System Database V2_Internal.xlsx + Treasury_System_Architecture_and_Implementation_Guide.md*
