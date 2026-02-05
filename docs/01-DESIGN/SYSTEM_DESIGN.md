# Treasury Management System - Design Document

**Version:** 1.0  
**Date:** February 5, 2026  
**Status:** Complete

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architecture Overview](#2-architecture-overview)
3. [Team Responsibilities](#3-team-responsibilities)
4. [Database Design](#4-database-design)
5. [Transaction Lifecycles](#5-transaction-lifecycles)
6. [Market Data Management](#6-market-data-management)
7. [Data Update Frequency](#7-data-update-frequency)
8. [Reference Data](#8-reference-data)
9. [Appendix A: Table Structures](#appendix-a-table-structures)
10. [Appendix B: Regulatory Mapping](#appendix-b-regulatory-mapping)

---

## 1. Executive Summary

### 1.1 System Characteristics

| Attribute | Specification |
|-----------|---------------|
| **Transaction Volume** | ≤25 transactions/day (normal), burst ~100 T/day |
| **Currency** | Thai Baht (THB) exclusively |
| **Market Focus** | Local bond and money market |
| **Regulatory Environment** | BOT, SEC, ThaiBMA compliance |
| **Accounting Standards** | TFRS 9 / IFRS 9 (ECL handled externally) |

### 1.2 Key Requirements

- **Real-time cash position monitoring** across BAHTNET settlement accounts
- **OTC trade capture** (~99% of market volume)
- **ThaiBMA 30-minute trade reporting** obligation
- **T+2 settlement cycle** compliance
- **Multi-layer segregation**: Front/Middle/Back Office + IT Admin
- **Four-eyes principle** for ALL transaction approvals

### 1.3 Architecture Decision: Modular Monolith

**Chosen Approach:** Modular Monolith with FastAPI + PostgreSQL + React

**Rationale:**
| Factor | Assessment |
|--------|------------|
| Volume | Low (≤25 T/day) - monolith sufficient |
| Compliance | ACID transactions required |
| Team Size | Small team - simpler coordination |
| Deployment | Single deploy unit reduces risk |

---

## 2. Architecture Overview

### 2.1 High-Level Architecture

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
│  │  ├─ TSD Integration            ←→  bond_trades.settlement_status    │    │
│  │  ├─ BAHTNET Integration        ←→  interbank_deals, cash_margin     │    │
│  │  ├─ Repo Lifecycle             ←→  repo_trades + collateral_pos     │    │
│  │  └─ Exception Management       ←→  margin_calls                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  ACCOUNTING MODULE             ←→  Position + Analytical Tables     │    │
│  │  ├─ TFRS9 Classification       ←→  portfolio_master                 │    │
│  │  ├─ Amortized Cost             ←→  bond_positions.book_value        │    │
│  │  ├─ Repo Accounting            ←→  repo_trades accounting fields    │    │
│  │  └─ Journal Entry              ←→  position_realization_events      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  RISK & COMPLIANCE MODULE      ←→  Master + Limit Tables            │    │
│  │  ├─ Counterparty Credit        ←→  limit_utilization               │    │
│  │  ├─ Concentration Risk         ←→  entity_master grouping           │    │
│  │  └─ Four-Eyes Approval         ←→  Status workflow + audit log      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI (Python) |
| Database | PostgreSQL 14+ |
| Frontend | React 18+ |
| ORM | SQLAlchemy 2.0 |
| Migration | Alembic |
| Container | Docker + Docker Compose |

---

## 3. Team Responsibilities

### 3.1 Responsibility Matrix

| Team | Primary Responsibilities | Key Tables/Data |
|------|-------------------------|-----------------|
| **Front Office** | Trade capture, pricing, execution | `bond_trades`, `interbank_deals`, `repo_trades` |
| **Middle Office** | Limit management, risk monitoring, approval | `limit_utilization`, `margin_calls` |
| **Back Office** | Settlement, collateral, master data, **daily ThaiBMA import** | `security_master`, `collateral_positions`, `cash_margin_movements` |
| **IT Admin** | User management, reference data, system config | `users`, `roles`, technical support |
| **Credit Risk** | Credit assessment, rating verification | Credit approvals |
| **Compliance** | KYC review, final approval | KYC status management |

### 3.2 Critical Decisions

| Decision | Detail | Impact |
|----------|--------|--------|
| **Four-Eyes Approval** | ALL transactions require approval (no threshold) | Every trade must be approved by second person |
| **BAHTNET Settlement** | Manual file upload to BOT portal | Back Office generates MT103, uploads manually |
| **TSD Settlement** | SWIFT MT format | MT540/MT541 instructions |
| **ECL Calculation** | **NOT included** - handled by Risk/Finance system | Raw data feeds only |
| **Security Master** | **Back Office ownership** | Complete lifecycle management |

---

## 4. Database Design

### 4.1 Table Categories

| Category | Tables | Purpose |
|----------|--------|---------|
| **Master Data** | entity_master, counterparty_master, security_master, portfolio_master, netting_agreement | Static reference data |
| **Transaction** | bond_trades, bond_transactions, interbank_deals, interbank_interest_schedule, repo_trades | Event-driven deal capture |
| **Position/Collateral** | collateral_positions, bond_positions, position_costing, position_realization_events | Derived holding information |
| **Control/Risk** | margin_calls, cash_margin_movements, limit_utilization, entity_counterparty | Limits, margin, audit |

### 4.2 Key Relationships

```
entity_master (1)
    ↓ entity_id
counterparty_master (N)
    ↓ counterparty_id
    ├── limit_utilization (N per limit type)
    ├── bond_trades
    ├── interbank_deals
    ├── repo_trades
    └── netting_agreement

security_master
    ↓ security_id
    ├── bond_trades
    ├── bond_positions
    └── collateral_positions

portfolio_master
    ↓ portfolio_id
    └── bond_trades
```

---

## 5. Transaction Lifecycles

### 5.1 Bond Trade Lifecycle

```
CREATED → PENDING_APPROVAL → APPROVED → CONFIRMED → SETTLED
   ↓           ↓              ↓           ↓
CANCELLED   REJECTED       REJECTED    FAILED
```

**Stages:**
1. **Trade Entry** (Front Office) - Input trade details
2. **Limit Check** (System) - Pre-trade validation
3. **Four-Eyes Approval** (Middle Office) - Second person approval
4. **ThaiBMA Reporting** (System/FO) - Within 30 minutes
5. **Settlement** (Back Office) - T+2 confirmation
6. **Daily Batch** (System) - Accrued interest update

### 5.2 Repo Trade Lifecycle

```
CREATED → COLLATERAL_ALLOCATED → SETTLED → ACTIVE → [Daily MTM] → REPAID → CLOSED
   ↓                              ↓          ↓
CANCELLED                      FAILED    MARGIN_CALL (if needed)
```

**Stages:**
1. **Trade Entry** (Front Office)
2. **Approval** (Middle Office)
3. **Collateral Allocation** (Back Office)
4. **Settlement** - First leg (cash vs securities)
5. **Daily Margin Management** (System) - MTM at 17:00
6. **Margin Call Workflow** (if threshold breached)
7. **Maturity** - Second leg settlement

### 5.3 Interbank Deal Lifecycle

```
CREATED → APPROVED → SETTLED → ACTIVE → [Daily Accrual] → MATURED
   ↓         ↓          ↓
CANCELLED REJECTED   FAILED
```

---

## 6. Market Data Management

### 6.1 Daily ThaiBMA Price Import (Critical Process)

#### Normal Working Day

| Time | Process | Duration | Responsible |
|------|---------|----------|-------------|
| **17:00** | Download ThaiBMA EOD | 15 min | Back Office |
| **17:15** | Validate prices | 10 min | Back Office |
| **17:30** | Import prices | 10 min | Back Office |
| **18:00** | Accrued interest calc | 20 min | System |
| **18:30** | Position build | 30 min | System |
| **19:00** | MTM valuation | 15 min | System |
| **19:30** | GL journals | 15 min | System |

#### Month-End Day (Adjusted)

| Time | Process | Note |
|------|---------|------|
| **17:30-18:00** | Download ThaiBMA | Later release by ThaiBMA |
| **18:00-18:15** | Validate prices | - |
| **18:15-18:30** | Import prices | - |
| **18:30** | Batch start | 30 min delay |
| **19:50** | Complete | Notify accounting |

### 6.2 Accrued Interest Formula

```
Daily Accrued = Nominal × Coupon% × (1/DayCountBase)

Day Count Base (from security_master.coupon_day_count_conv):
- ACT/365: 365
- ACT/360: 360
- 30/360: 360
- ACT/ACT: Actual days in year
```

### 6.3 Price Validation Rules

| Movement | Action | Approval |
|----------|--------|----------|
| ±5% to ±10% | Warning flag | None |
| ±10% to ±20% | Alert + confirmation | Middle Office |
| > ±20% | Hard stop | Risk Manager |

---

## 7. Data Update Frequency

### 7.1 Real-Time Updates
| Table/Event | Trigger | Performance Target |
|-------------|---------|-------------------|
| `bond_trades` | Trade capture | < 500ms |
| `limit_utilization` | Pre-trade check | < 100ms |

### 7.2 Daily Batch Updates (Working Days)
| Time | Process | Tables Updated |
|------|---------|----------------|
| 17:00 | Import ThaiBMA Prices | `security_master` |
| 17:30 | Margin Calculation | `margin_calls` |
| 18:00 | Accrued Interest Calc | `bond_positions`, `interbank_deals`, `repo_trades` |
| 18:30 | Position Build | `bond_positions` |
| 19:00 | MTM Valuation | `bond_positions.market_value` |

### 7.3 Scheduled Events
| Event | Trigger | Action |
|-------|---------|--------|
| Coupon Payment | `CURRENT_DATE = coupon_date` | Reset `accrued_interest`, create transaction |
| Bond Maturity | `CURRENT_DATE > maturity_date` | Set `status='Matured'`, archive position |
| Repo Maturity | `CURRENT_DATE > repurchase_date` | Set `status='Matured'`, release collateral |

---

## 8. Reference Data

### 8.1 Limit Types

| Type | Purpose | Applies To |
|------|---------|------------|
| `PLACEMENT_LIMIT` | Interbank lending/borrowing limit | Interbank deals |
| `REPO_LIMIT` | Repo/Reverse Repo trading limit | Repo trades |
| `SINGLE_TXN` | Maximum single transaction | All trades |
| `TENOR` | Maximum maturity | All trades |
| `CONCENTRATION` | Sector/issuer concentration | Portfolio monitoring |

> **Note:** Limits are controlled at product level. No cross-product aggregate limit.

### 8.2 Day Count Conventions

| Convention | Calculation | Common Use |
|------------|-------------|------------|
| ACT/365 | Actual days / 365 | Most THB bonds |
| ACT/360 | Actual days / 360 | Some short-term |
| 30/360 | 30-day months / 360 | Some corporate |
| ACT/ACT | Actual / Actual year days | Government bonds |

---

## Appendix A: Table Structures

See [Field Reference](../01-DESIGN/FIELD_REFERENCE.md) for complete field-level documentation.

### Key Tables Summary

| Table | Records | Purpose |
|-------|---------|---------|
| entity_master | 50-100 | Enterprise obligor registry |
| counterparty_master | 100-200 | Trading counterparties |
| security_master | 500-1000 | Tradable instruments |
| bond_trades | 6,250/year | Bond transactions |
| limit_utilization | Append-only | Credit limit audit |

---

## Appendix B: Regulatory Mapping

### ThaiBMA Trade Reporting

| ThaiBMA Field | Source Table | Source Column |
|---------------|--------------|---------------|
| Transaction Date | `bond_trades` | `trade_date` |
| ISIN | `security_master` | `isin` |
| Nominal Amount | `bond_trades` | `nominal_amount` |
| Clean Price | `bond_trades` | `clean_price_trade` |

### BOT DER_CPEN Reporting

| DER_CPEN Field | Source Table | Source Column |
|----------------|--------------|---------------|
| Entity Id | `entity_master` | `entity_id` |
| Involved Party Type | `counterparty_master` | `involved_party_type` |
| Total Exposure | `bond_positions` | `book_value` |

---

**Document End**

*For detailed field definitions, see [Field Reference](../01-DESIGN/FIELD_REFERENCE.md)*  
*For process workflows, see [Transaction Workflows](../02-PROCESSES/TRANSACTION_WORKFLOWS.md)*  
*For implementation details, see [Development Guide](../03-IMPLEMENTATION/DEVELOPMENT_GUIDE.md)*
