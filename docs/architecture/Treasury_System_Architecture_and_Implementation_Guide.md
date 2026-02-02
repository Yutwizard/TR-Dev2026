# Treasury System Architecture and Implementation Guide

**Thai Commercial Bank Treasury System: Local Bond and Money Market Operations**

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architecture Approaches Comparison](#2-architecture-approaches-comparison)
3. [Recommended Architecture: Modular Monolith](#3-recommended-architecture-modular-monolith)
4. [Technology Stack](#4-technology-stack)
5. [Implementation Roadmap](#5-implementation-roadmap)
6. [Critical Success Factors](#6-critical-success-factors)
7. [Team Structure and Timeline](#7-team-structure-and-timeline)

---

## 1. Executive Summary

This document provides a comprehensive architecture analysis and step-by-step implementation guide for building a Treasury System for Thai Commercial Banks focusing on Local Bond and Money Market Operations.

### System Characteristics

| Attribute | Specification |
|-----------|---------------|
| **Transaction Volume** | ≤25 transactions/day (normal), burst capacity ~100 T/day |
| **Currency** | Thai Baht (THB) exclusively |
| **Market Focus** | Local bond and money market |
| **Regulatory Environment** | BOT, SEC, ThaiBMA compliance |
| **Accounting Standards** | TFRS 9 / IFRS 9 |

### Key Requirements

- **Real-time cash position monitoring** across BAHTNET settlement accounts
- **OTC trade capture** (~99% of market volume)
- **ThaiBMA 30-minute trade reporting** obligation
- **T+2 settlement cycle** compliance
- **Multi-layer segregation**: Front/Middle/Back Office + IT Admin
- **Four-eyes principle** for approvals

---

## 2. Architecture Approaches Comparison

### 2.1 Option A: Monolithic Architecture

**Structure:** Single unified application with modular internal components

**Best for:** Low-volume (≤25 T/day), tight regulatory compliance needs

#### Pros

| # | Advantage | Business Impact |
|---|-----------|-----------------|
| 1 | **Simpler data consistency** | Critical for financial transactions requiring ACID compliance |
| 2 | **Easier regulatory auditing** | Single codebase simplifies BOT/SEC examination |
| 3 | **Lower integration overhead** | All modules share the same database and security model |
| 4 | **Faster development** | No distributed system complexity for a small team |
| 5 | **Simpler testing** | End-to-end testing is straightforward |

#### Cons

| # | Disadvantage | Mitigation |
|---|--------------|------------|
| 1 | **Limited horizontal scaling** | Acceptable given fixed low-volume ceiling |
| 2 | **Technology lock-in** | Choose mature, proven stack |
| 3 | **Deployment risk** | Thorough regression testing required |
| 4 | **Team coordination** | Clear code ownership and module boundaries |

---

### 2.2 Option B: Microservices Architecture

**Structure:** Separate services: Trade Execution, Settlement, Accounting, Reporting

**Best for:** High-volume, rapid scaling, multiple teams

#### Pros

| # | Advantage | Context |
|---|-----------|---------|
| 1 | **Independent scaling** | Scale only busy services (unnecessary for ≤25 T/day) |
| 2 | **Technology flexibility** | Best tool for each service |
| 3 | **Team autonomy** | Separate teams can own separate services |
| 4 | **Fault isolation** | One service failure doesn't cascade |

#### Cons

| # | Disadvantage | Severity |
|---|--------------|----------|
| 1 | **Over-engineering** | Too complex for 6,250 annual transactions |
| 2 | **Distributed transaction complexity** | ACID compliance harder across services |
| 3 | **Integration overhead** | Need API gateways, service discovery, message queues |
| 4 | **Operational burden** | Multiple deployments, monitoring points |
| 5 | **Data consistency challenges** | Eventual consistency problematic for financial records |

**Verdict:** NOT RECOMMENDED for this use case

---

### 2.3 Option C: Modular Monolith (Hybrid - RECOMMENDED)

**Structure:** Single deployable unit with clearly separated internal modules

**Best for:** Balance of simplicity and future flexibility

#### Pros

| # | Advantage | Detail |
|---|-----------|--------|
| 1 | **Future-proof** | Can extract services later if volume grows |
| 2 | **Clear boundaries** | Each module (Trade, Settlement, Accounting) has defined interfaces |
| 3 | **Simpler than microservices** | No network calls between modules |
| 4 | **Database per module possible** | Within same instance for separation |
| 5 | **Easier testing** | Can test modules in isolation or together |

#### Cons

| # | Disadvantage | Mitigation |
|---|--------------|------------|
| 1 | **Requires discipline** | Enforce module boundaries through code reviews |
| 2 | **Shared database risks** | Use schema separation or strict API enforcement |

---

## 3. Recommended Architecture: Modular Monolith

### 3.1 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Front Office│  │Middle Office│  │  Back Office│  │  IT Admin   │         │
│  │   (Trader)  │  │  (Risk/Com) │  │(Settlement) │  │  (Config)   │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
└─────────┼────────────────┼────────────────┼────────────────┼────────────────┘
          │                │                │                │
          └────────────────┴────────────────┴────────────────┘
                                   │
                          ┌────────▼────────┐
                          │   API Gateway   │  ← Auth, RBAC, Rate Limiting
                          │   (RBAC Enforced)│
                          └────────┬────────┘
                                   │
┌──────────────────────────────────┼──────────────────────────────────────────┐
│                         APPLICATION LAYER                                    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     MODULE: TRADE EXECUTION                          │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │    │
│  │  │   OTC Trade │  │   Order     │  │ Counterparty│  │ Price      │ │    │
│  │  │   Capture   │  │ Management  │  │ Limit Check │  │ Discovery  │ │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │    │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │    │
│  │  │           ThaiBMA Trade Reporting Interface                     │ │    │
│  │  └─────────────────────────────────────────────────────────────────┘ │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      MODULE: SETTLEMENT                              │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │    │
│  │  │    TSD      │  │   BAHTNET   │  │    Repo     │  │ Settlement │ │    │
│  │  │Integration  │  │ Integration │  │  Lifecycle  │  │  Failure   │ │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      MODULE: ACCOUNTING                              │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │    │
│  │  │ TFRS9/IFRS9 │  │    ECL      │  │    Repo     │  │   Journal  │ │    │
│  │  │Classification│  │Impairment   │  │ Accounting  │  │   Entry    │ │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      MODULE: REPORTING                               │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │    │
│  │  │  Regulatory │  │  Management │  │  Liquidity  │  │  Audit     │ │    │
│  │  │  Reporting  │  │  Reporting  │  │  Forecast   │  │  Trail     │ │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    MODULE: RISK & COMPLIANCE                         │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │    │
│  │  │Concentration│  │ Market Risk │  │    AML/KYC  │  │ Four-Eyes  │ │    │
│  │  │    Risk     │  │  (VaR/DV01) │  │  Screening  │  │  Approval  │ │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────────┘
                                   │
                          ┌────────▼────────┐
                          │  EVENT BUS      │  ← Internal module communication
                          │ (for decoupling)│
                          └────────┬────────┘
                                   │
┌──────────────────────────────────┼──────────────────────────────────────────┐
│                           DATA LAYER                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Primary    │  │   Market    │  │   Document  │  │   Audit     │         │
│  │  Database   │  │    Data     │  │   Store     │  │   Log       │         │
│  │ (PostgreSQL)│  │   Cache     │  │  (Files)    │  │ (Immutable) │         │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘         │
└──────────────────────────────────────────────────────────────────────────────┘
                                   │
                          ┌────────▼────────┐
                          │  INTEGRATION    │
                          │    LAYER        │
┌──────────────────────────────────────────────────────────────────────────────┐
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │    TSD      │  │  BAHTNET    │  │  ThaiBMA    │  │ Bloomberg/  │         │
│  │ (Corporate) │  │ (Govt Sec)  │  │(Reporting)  │  │  Reuters    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                          │
│  │Core Banking │  │    Risk     │  │   Data      │                          │
│  │   System    │  │ Management  │  │ Warehouse   │                          │
│  └─────────────┘  └─────────────┘  └─────────────┘                          │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

### 3.2 Module Specifications

#### 3.2.1 Trade Execution Module

**Purpose:** Handle OTC trade capture, validation, and ThaiBMA reporting

**Key Components:**

| Component | Function |
|-----------|----------|
| OTC Trade Capture | Voice-brokered transaction entry with validation |
| Order Management | Workflow routing (Created → Approved → Executed → Confirmed) |
| Counterparty Limit | Real-time limit checking (single txn, aggregate, tenor-based) |
| Price Discovery | Market data integration (ThaiBMA, Bloomberg, Reuters) |
| ThaiBMA Reporting | Automated 30-minute trade reporting obligation |

**Key Business Rules:**
- Settlement date: T+2 standard with holiday adjustment
- Price validation: Reasonableness range checks
- Limit enforcement: Warning at 80%, hard block at 100%
- Reporting: Must submit within 30 minutes of execution

---

#### 3.2.2 Settlement Module

**Purpose:** Manage DVP settlement through TSD and BAHTNET

**Key Components:**

| Component | Function |
|-----------|----------|
| TSD Integration | Corporate bond DVP Model 1 settlement |
| BAHTNET Integration | Government securities RTGS settlement |
| Repo Lifecycle | Initial trade, mark-to-market, margin, maturity |
| PSMS Interface | Pre-Settlement Matching System |
| Exception Management | Failure handling and resolution |

**Key Business Rules:**
- TSD: No debit balances allowed (since Nov 2017)
- BAHTNET: Immediate finality for high-value payments
- T+2 settlement cycle compliance
- Margin call threshold: THB 500,000

**Haircut Matrix (BOT Operations):**

| Collateral Type | 0-5 Years | 5-10 Years | 10-20 Years | >20 Years |
|-----------------|-----------|------------|-------------|-----------|
| Government bonds | 1% | 3% | 4% | 5% |
| BOT bonds/bills | 1% | 3% | 4% | 5% |
| SOE bonds (guaranteed) | 1% | 3% | 4% | 5% |
| Corporate bonds (AAA) | 5% | 10% | 15% | 20% |
| Corporate bonds (AA) | 10% | 15% | 20% | 25% |
| Corporate bonds (A) | 15% | 20% | 25% | 30% |
| Corporate bonds (BBB) | 20% | 25% | 30% | 35% |

---

#### 3.2.3 Accounting Module

**Purpose:** TFRS 9 / IFRS 9 financial instrument accounting

**Key Components:**

| Component | Function |
|-----------|----------|
| Classification Engine | Business model assessment, SPPI test |
| Amortized Cost | EIR calculation, premium/discount amortization |
| FVOCI | Fair value tracking, OCI recycling |
| FVTPL | Trading position accounting |
| ECL Engine | Expected credit loss calculation (Stage 1/2/3) |
| Repo Accounting | Secured financing treatment |
| Journal Entry | GL posting and reconciliation |

**TFRS 9 Classification Categories:**

| Category | Business Model | Accounting Treatment |
|----------|----------------|---------------------|
| Amortized Cost | Hold-to-Collect | EIR, 12-month ECL |
| FVOCI | Hold-to-Collect-and-Sell | Amortized cost + FV in OCI |
| FVTPL | Trading or SPPI fail | Fair value through P&L |

**ECL Stages:**

| Stage | Trigger | ECL Measurement |
|-------|---------|-----------------|
| Stage 1 | No significant deterioration | 12-month ECL |
| Stage 2 | Significant credit deterioration | Lifetime ECL |
| Stage 3 | Credit-impaired (objective evidence) | Lifetime ECL, net carrying amount |

---

#### 3.2.4 Reporting Module

**Purpose:** Regulatory and management reporting

**Key Components:**

| Component | Output |
|-----------|--------|
| Regulatory Reporting | ThaiBMA reports, BOT liquidity returns, SEC disclosures |
| Management Reporting | Portfolio valuation, performance attribution, risk dashboards |
| Liquidity Forecast | Cash flow projections, maturity ladder |
| Audit Trail | Immutable 5-year transaction history |

---

#### 3.2.5 Risk & Compliance Module

**Purpose:** Risk monitoring and regulatory compliance

**Key Components:**

| Component | Function |
|-----------|----------|
| Concentration Risk | Single issuer, sector, rating limits |
| Market Risk | Duration, DV01, VaR calculations |
| AML/KYC | Suspicious transaction monitoring |
| Four-Eyes Approval | Mandatory secondary approval workflow |
| Capital Adequacy | BOT regulatory capital reporting |

---

### 3.3 Data Layer Design

#### 3.3.1 Primary Database Schema (Simplified)

```
┌─────────────────────────────────────────────────────────────────┐
│                    SECURITY MASTER                              │
├─────────────────────────────────────────────────────────────────┤
│ security_id (PK)       │ ISIN, internal code                    │
│ security_type          │ T-BILL, T-BOND, BOT_BOND, SOE, CORP    │
│ issuer_id (FK)         │ Reference to issuer                    │
│ currency               │ THB                                    │
│ maturity_date          │ Final maturity                         │
│ coupon_rate            │ Annual coupon (null for discount)      │
│ coupon_frequency       │ Semi-annual, annual, etc.              │
│ day_count_convention   │ Actual/365, Actual/Actual              │
│ issue_date             │ Original issue date                    │
│ outstanding_amount     │ Total outstanding                      │
│ rating_fitch           │ External rating                        │
│ rating_moodys          │ External rating                        │
│ rating_sp              │ External rating                        │
│ rating_tris            │ Thai rating                            │
│ eligible_collateral    │ BOT repo eligibility flag              │
│ created_at             │ Timestamp                              │
│ updated_at             │ Timestamp                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  COUNTERPARTY MASTER                            │
├─────────────────────────────────────────────────────────────────┤
│ counterparty_id (PK)   │ Internal identifier                    │
│ counterparty_name      │ Legal name                             │
│ counterparty_type      │ BANK, SOE, CORPORATE, etc.             │
│ tax_id                 │ Thai tax ID                            │
│ kyc_status             │ APPROVED, PENDING, SUSPENDED           │
│ kyc_expiry_date        │ Review date                            │
│ tsd_account            │ TSD settlement account                 │
│ bahtnet_account        │ BAHTNET account                        │
│ single_txn_limit       │ Maximum single transaction             │
│ aggregate_limit        │ Maximum total exposure                 │
│ tenor_limit_days       │ Maximum tenor allowed                  │
│ created_at             │ Timestamp                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     TRADE HEADER                                │
├─────────────────────────────────────────────────────────────────┤
│ trade_id (PK)          │ Unique trade identifier                │
│ trade_reference        │ External reference number              │
│ trade_date             │ Transaction date                       │
│ trade_time             │ Execution timestamp                    │
│ trade_type             │ BUY, SELL, REPO, REVERSE_REPO          │
│ security_id (FK)       │ Reference to security                  │
│ counterparty_id (FK)   │ Reference to counterparty              │
│ trader_id (FK)         │ User who executed                      │
│ status                 │ CREATED, PENDING, APPROVED, CONFIRMED  │
│ settlement_date        │ Settlement date (T+2)                  │
│ settlement_type        │ DVP, FOP                               │
│ created_at             │ Timestamp                              │
│ approved_by (FK)       │ Four-eyes approver                     │
│ approved_at            │ Approval timestamp                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   TRADE DETAIL (REPO)                           │
├─────────────────────────────────────────────────────────────────┤
│ trade_detail_id (PK)   │                                        │
│ trade_id (FK)          │ Reference to header                    │
│ start_date             │ Repo start date                        │
│ end_date               │ Repo maturity date                     │
│ repo_rate              │ Agreed repo rate                       │
│ repo_rate_type         │ FIXED, FLOATING (THOR)                 │
│ haircut_percent        │ Collateral haircut                     │
│ collateral_security_id │ Collateral ISIN                        │
│ collateral_amount      │ Nominal collateral amount              │
│ collateral_market_value│ Current market value                   │
│ margin_call_threshold  │ Usually THB 500,000                    │
│ margin_frequency       │ Daily, intraday                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     POSITION                                    │
├─────────────────────────────────────────────────────────────────┤
│ position_id (PK)       │                                        │
│ security_id (FK)       │                                        │
│ book_id (FK)           │ Trading book / portfolio               │
│ position_date          │ As-of date                             │
│ nominal_amount         │ Face value                             │
│ amortized_cost         │ Carrying amount                        │
│ fair_value             │ Mark-to-market                         │
│ accrued_interest       │ Accrued since last coupon              │
│ classification         │ AMORTIZED_COST, FVOCI, FVTPL           │
│ ecl_stage              │ 1, 2, or 3                             │
│ ecl_provision          │ Impairment allowance                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  SETTLEMENT INSTRUCTION                         │
├─────────────────────────────────────────────────────────────────┤
│ instruction_id (PK)    │                                        │
│ trade_id (FK)          │ Reference to trade                     │
│ instruction_type       │ DELIVERY, RECEIPT                      │
│ settlement_system      │ TSD, BAHTNET                           │
│ settlement_date        │ Target settlement date                 │
│ status                 │ PENDING, MATCHED, SETTLED, FAILED      │
│ message_reference      │ External message ID                    │
│ psms_match_status      │ Pre-settlement matching                │
│ settlement_amount      │ Cash amount                            │
│ securities_nominal     │ Nominal amount                         │
│ created_at             │ Timestamp                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   JOURNAL ENTRY                                 │
├─────────────────────────────────────────────────────────────────┤
│ entry_id (PK)          │                                        │
│ entry_date             │ Accounting date                        │
│ trade_id (FK)          │ Reference (optional)                   │
│ journal_type           │ TRADE, ACCRUAL, MTM, ECL, REPO         │
│ account_code           │ GL account                             │
│ debit_amount           │ Debit (THB)                            │
│ credit_amount          │ Credit (THB)                           │
│ description            │ Narrative                              │
│ posted_by (FK)         │ User/system                            │
│ posted_at              │ Timestamp                              │
│ gl_batch_id            │ Batch reference                        │
└─────────────────────────────────────────────────────────────────┘
```

---

### 3.4 External System Integration Specifications

#### 3.4.1 Thailand Securities Depository (TSD)

**Integration Method:** SWIFT MT messages + Proprietary API

**Key Messages:**

| Message Type | Purpose | Direction |
|--------------|---------|-----------|
| MT540 | Receive Free (corporate action) | Outbound |
| MT541 | Receive Against Payment | Outbound |
| MT542 | Deliver Free | Outbound |
| MT543 | Deliver Against Payment | Outbound |
| MT544-547 | Confirmation messages | Inbound |
| MT548 | Settlement Status | Inbound |

**Settlement Cycle:** T+2 DVP Model 1 (gross, trade-by-trade)

**Critical Constraint:** No debit balances allowed (since Nov 2017)

---

#### 3.4.2 BAHTNET RTGS

**Integration Method:** SWIFT MT103/MT202 + Proprietary interface

**Key Functions:**

| Function | Description |
|----------|-------------|
| Payment Initiation | Real-time high-value payment |
| Liquidity Monitoring | Real-time central bank reserve balance |
| Settlement Finality | Irrevocable settlement confirmation |
| Queue Management | Time-critical payment prioritization |

---

#### 3.4.3 ThaiBMA

**Integration Method:** REST API + SFTP for bulk data

**Key Interfaces:**

| Interface | Purpose | Frequency |
|-----------|---------|-----------|
| Trade Reporting API | Submit transactions within 30 minutes | Real-time |
| Reference Price Feed | End-of-day prices for MTM | Daily |
| THOR Rate | Overnight repo benchmark | Daily |
| Market Statistics | Volume, outstanding data | Daily |

**Trade Reporting Workflow:**

```
Trade Execution → Immediate Capture → Validation → Formatting → 
Transmission → Acknowledgment Receipt → Exception Handling (if needed)
```

**Monitoring Thresholds:**

| Element | Threshold | Action |
|---------|-----------|--------|
| Time to report | 20 minutes | Amber alert |
| Time to report | 28 minutes | Red alert, escalation |
| Acknowledgment pending | 5 minutes | Retry, backup transmission |
| Rejection received | Immediate | Investigation, resubmission |

---

## 4. Technology Stack

### 4.1 Recommended Stack

| Layer | Technology | Alternative | Selection Criteria |
|-------|------------|-------------|-------------------|
| **Backend Framework** | C# .NET 8 | Java Spring Boot | Type safety, performance, enterprise support |
| **Database** | PostgreSQL 16 | SQL Server 2022 | ACID compliance, JSON support, cost |
| **Cache** | Redis 7 | - | Performance, pub/sub for events |
| **Message Queue** | RabbitMQ | Azure Service Bus | Reliability, guaranteed delivery |
| **API Gateway** | YARP / Ocelot | Kong | .NET native integration |
| **Frontend** | React 18 + TypeScript | Angular 17 | Component reusability, ecosystem |
| **UI Component Library** | Ant Design / Material-UI | - | Professional financial UI patterns |
| **Reporting** | SQL Server Reporting Services | JasperReports | Native integration, Thai font support |
| **Authentication** | IdentityServer / Auth0 | Keycloak | OAuth 2.0 + OIDC compliance |
| **Logging** | Serilog + ELK Stack | - | Structured logging, audit trail |
| **Monitoring** | Prometheus + Grafana | Datadog | Cost-effective, customizable |
| **Testing** | xUnit + Playwright | Jest + Cypress | Comprehensive test coverage |
| **Documentation** | Swagger/OpenAPI | - | API documentation |
| **Version Control** | Git + Azure DevOps | GitHub | CI/CD integration |

### 4.2 Development Tools

| Tool | Purpose |
|------|---------|
| Visual Studio 2022 / VS Code | IDE |
| SQL Server Management Studio / pgAdmin | Database management |
| Postman / Insomnia | API testing |
| Docker Desktop | Containerization |
| SonarQube | Code quality |
| Fortify / Checkmarx | Security scanning |

---

## 5. Implementation Roadmap

### Phase 1: Foundation (Months 1-3)

#### Week 1-2: Project Setup & Infrastructure

**Deliverables:**
- [ ] Development environment setup (Git repository, CI/CD pipeline)
- [ ] Coding standards document
- [ ] Branch strategy (GitFlow or trunk-based)
- [ ] Development and test database instances
- [ ] Static code analysis configuration (SonarQube)
- [ ] Modular monolith project structure
- [ ] Logging infrastructure (ELK stack)
- [ ] Monitoring foundation (Prometheus + Grafana)

**Key Decisions:**
- Code review process (minimum 1 approval)
- Branch protection rules
- Deployment environments (DEV, SIT, UAT, PROD)

---

#### Week 3-4: Security & Access Control Framework

**Deliverables:**
- [ ] RBAC data model implementation
  - Users table
  - Roles table (Front Office, Middle Office, Back Office, IT Admin)
  - Permissions table (granular actions)
  - Role-Permission mapping
  - User-Role assignment
- [ ] Authentication service (OAuth 2.0 flow)
- [ ] JWT token implementation with refresh tokens
- [ ] Four-Eyes approval data model
  - Approval workflows configuration
  - Approval history tracking
  - Escalation rules
- [ ] Audit logging mechanism
  - Immutable audit log table
  - Change data capture (CDC) triggers
  - Tamper-evident logging
- [ ] User management screens (IT Admin module)
  - User CRUD
  - Role assignment
  - Password policy enforcement
- [ ] Initial security testing

**Key Business Rules:**
- Password complexity: min 12 chars, mixed case, number, special char
- Session timeout: 30 minutes idle
- Failed login lockout: 5 attempts, 30-minute lockout
- Four-Eyes: Mandatory for transactions > THB 10 million

---

#### Week 5-8: Master Data & Static Data

**Deliverables:**

**Security Master:**
- [ ] Instrument types: T-Bills, T-Bonds, BOT Bonds/Bills, SOE Bonds, Corporate Bonds
- [ ] ISIN code validation and mapping
- [ ] Coupon schedule management
- [ ] Maturity date tracking
- [ ] Day count convention (Actual/365, Actual/Actual)
- [ ] Rating information (Fitch, Moody's, S&P, TRIS)
- [ ] BOT collateral eligibility flag
- [ ] Haircut matrix configuration

**Counterparty Master:**
- [ ] Counterparty type classification
- [ ] KYC data storage
- [ ] Settlement account details (TSD, BAHTNET)
- [ ] Limit structure definition
  - Single transaction limits
  - Aggregate exposure limits
  - Tenor limits
  - Concentration limits

**Reference Data:**
- [ ] Thai business day calendar
- [ ] Official holiday calendar (Bank of Thailand)
- [ ] Haircut matrices (by collateral type and maturity)
- [ ] FX rates (if multi-currency support needed in future)
- [ ] ThaiBMA reference price history

**Data Migration:**
- [ ] Data import templates (Excel/CSV)
- [ ] Validation rules for import
- [ ] Reconciliation reports

---

#### Week 9-10: External Connectivity Foundation

**Deliverables:**
- [ ] TSD message format library (SWIFT MT message builders)
- [ ] BAHTNET RTGS message templates
- [ ] ThaiBMA API client with authentication
- [ ] Market data feed connectors (Bloomberg API, Reuters RFA)
- [ ] Connection pooling configuration
- [ ] Retry logic with exponential backoff
- [ ] Circuit breaker pattern for external calls
- [ ] Timeout configuration
- [ ] Message queuing for async processing

**Testing:**
- [ ] Mock servers for external systems
- [ ] Connectivity testing
- [ ] Message format validation

---

#### Week 11-12: Core Transaction Data Model

**Deliverables:**
- [ ] Trade entity design and implementation
  - Trade header (common fields)
  - Trade detail (instrument-specific)
  - Trade history/audit
- [ ] Position entity
  - Daily position snapshots
  - Position movements
- [ ] Settlement instruction entity
- [ ] Accounting journal entry entity
- [ ] Database migration scripts (Flyway or EF Migrations)
- [ ] Unit testing framework with 80%+ coverage target
- [ ] Integration test foundation

**Documentation:**
- [ ] Entity relationship diagrams
- [ ] Data dictionary
- [ ] API contracts (OpenAPI)

---

### Phase 2: Trade Execution Module (Months 4-5)

#### Week 1-3: OTC Trade Capture

**Deliverables:**

**Front Office Screens:**
- [ ] Trade entry form
  - Instrument search with autocomplete
  - Price/yield input with real-time conversion
  - Accrued interest calculation
  - Clean/dirty price display
  - Settlement date calculation (auto T+2, holiday-aware)
  - Counterparty selection with KYC status check
- [ ] Trade blotter (list view with filters)
- [ ] Trade detail view
- [ ] Trade amendment workflow
- [ ] Trade cancellation with approval

**Validation Engine:**
- [ ] Business day validation
- [ ] Market hours check (Thai market hours)
- [ ] Price reasonableness checks (±10% from last price)
- [ ] Settlement date validation
- [ ] Instrument eligibility check

**Workflow States:**
```
CREATED → PENDING_APPROVAL → APPROVED → EXECUTED → CONFIRMED → SETTLED
   ↓            ↓               ↓
CANCELLED   REJECTED       REJECTED
```

**Notifications:**
- [ ] Email alerts for pending approvals
- [ ] Dashboard notifications
- [ ] SMS for critical breaches (optional)

---

#### Week 4-5: Counterparty Limit Management

**Deliverables:**

**Limit Engine:**
- [ ] Real-time exposure calculation
  - Settled positions
  - Pending settlements
  - Pending approvals
  - Repo exposures (collateral-adjusted)
- [ ] Limit types implementation
  - Single transaction limit
  - Counterparty aggregate exposure limit
  - Tenor-based limits (by maturity bucket)
  - Concentration limits (issuer, sector, rating)
  - Repo-specific limits (cash vs collateral)

**Pre-Trade Controls:**
- [ ] Hard block at 100% limit utilization
- [ ] Warning at 80% threshold
- [ ] Limit override workflow with approval chain
- [ ] Limit utilization dashboard

**Limit Administration:**
- [ ] Limit configuration screens (Middle Office)
- [ ] Limit history tracking
- [ ] Temporary limit increases with expiry

---

#### Week 6-6: ThaiBMA Trade Reporting

**Deliverables:**

**Reporting Engine:**
- [ ] Trade capture timestamp logging (execution time)
- [ ] Automatic report generation
- [ ] Message formatting to ThaiBMA specifications
- [ ] Validation before submission (completeness check)
- [ ] Retry mechanism (3 attempts with backoff)
- [ ] Acknowledgment tracking
- [ ] Exception handling dashboard

**Monitoring:**
- [ ] Countdown timer display (time remaining to report)
- [ ] Amber alert at 20 minutes
- [ ] Red alert at 28 minutes
- [ ] Auto-escalation to operations manager

**Audit:**
- [ ] Submission log with timestamps
- [ ] Response log (success/failure)
- [ ] Manual intervention tracking

---

#### Week 7-8: Price Discovery Integration

**Deliverables:**

**Market Data Integration:**
- [ ] ThaiBMA reference price daily ingestion
- [ ] THOR rate integration (overnight benchmark)
- [ ] BOT policy rate feed
- [ ] Yield curve data (if available)

**Internal Price Storage:**
- [ ] Historical trade price database
- [ ] Counterparty quote logging
- [ ] Best execution documentation

**Price Validation:**
- [ ] Price movement threshold alerts (±5% from previous day)
- [ ] Stale price detection (>1 day old)
- [ ] Fallback price sources

---

### Phase 3: Settlement Module (Months 6-7)

#### Week 1-3: TSD Integration (Corporate Bonds)

**Deliverables:**

**DVP Model 1 Settlement:**
- [ ] Settlement instruction generation (MT541/MT543)
- [ ] Instruction validation
- [ ] Cutoff time management (TSD: typically 14:00 for same-day)
- [ ] Settlement confirmation processing (MT544-547)
- [ ] Settlement status tracking

**PSMS (Pre-Settlement Matching System):**
- [ ] PSMS message submission
- [ ] Matching status monitoring
- [ ] Mismatch resolution workflow
- [ ] Mandatory matching fields validation

**Position Management:**
- [ ] Position inquiry integration
- [ ] Available balance check before trade
- [ ] Pending settlement position tracking
- [ ] Corporate action processing (coupons, redemptions, maturities)

**Constraints:**
- [ ] No debit balance enforcement (TSD rule since Nov 2017)
- [ ] T+2 compliance validation

---

#### Week 4-5: BAHTNET Integration (Government Securities)

**Deliverables:**

**RTGS Settlement:**
- [ ] Payment message generation (SWIFT MT103)
- [ ] Unique reference generation (UMID)
- [ ] Liquidity monitoring dashboard
  - Current BAHTNET balance
  - Projected incoming/outgoing
  - Net position
- [ ] Settlement prioritization logic
- [ ] Finality confirmation processing
- [ ] End-of-day reconciliation
  - BAHTNET statement retrieval
  - Internal records matching
  - Exception reporting

**Liquidity Management:**
- [ ] Real-time cash position monitoring
- [ ] Early warning alerts for potential shortfalls
- [ ] Intraday liquidity forecasting

---

#### Week 6-7: Repo Lifecycle Management

**Deliverables:**

**Repo Trade Support:**
- [ ] Initial trade recording (first leg)
- [ ] Collateral selection and allocation
- [ ] Haircut application
- [ ] Cash amount calculation

**Daily Operations:**
- [ ] Mark-to-market valuation
- [ ] Margin calculation
- [ ] Variation margin processing (cash with interest)
- [ ] Collateral substitution workflow

**Coupon Processing:**
- [ ] Coupon pass-through to collateral provider
- [ ] Coupon reinvestment (if applicable)
- [ ] Tax treatment (withholding tax)

**Maturity/Rollover:**
- [ ] Maturity notification (T-1, T-3)
- [ ] Final settlement amount calculation
- [ ] Collateral return processing
- [ ] Rollover workflow (terminate + new trade)

**Margin Call Formula:**
```
Margin Call = Market Value - (Purchase Price + Accrued Interest) / (1 - Initial Margin)
```

---

#### Week 8-8: Exception Management

**Deliverables:**

**Failure Detection:**
- [ ] Real-time settlement status monitoring
- [ ] Automatic failure identification
- [ ] Alert generation

**Resolution Workflows:**

| Failure Type | Resolution Options |
|--------------|-------------------|
| Securities Fail | Securities borrowing, market purchase, settlement date extension |
| Cash Fail | Intraday liquidity mobilization, overdraft arrangement |
| Technical Fail | IT escalation, manual processing contingency |
| Mismatch Fail | Counterparty coordination, correction, resubmission |

**Manual Override:**
- [ ] Override request workflow
- [ ] Approval chain based on amount/risk
- [ ] Audit trail for all overrides

---

### Phase 4: Accounting Module (Months 8-9)

#### Week 1-2: TFRS 9 / IFRS 9 Classification

**Deliverables:**

**Classification Engine:**
- [ ] Business model assessment questionnaire
- [ ] Hold-to-Collect classification rules
- [ ] Hold-to-Collect-and-Sell classification rules
- [ ] Trading classification rules

**SPPI Test:**
- [ ] SPPI (Solely Payments of Principal and Interest) test implementation
- [ ] SPPI failure indicator detection
  - Leverage features
  - Non-recourse arrangements
  - Interest rate caps/floors
  - Prepayment options with significant prepayment compensation
- [ ] Manual assessment workflow for complex instruments

**Classification Override:**
- [ ] FVTPL elective designation (to eliminate accounting mismatch)
- [ ] Override approval workflow
- [ ] Documentation requirements

---

#### Week 3-4: Amortized Cost Engine

**Deliverables:**

**EIR Calculation:**
- [ ] Effective interest rate computation at initial recognition
- [ ] Cash flow projection engine
- [ ] Day count convention handling (Actual/365, Actual/Actual)

**Amortization:**
- [ ] Premium/discount amortization (systematic over instrument life)
- [ ] Daily accrual calculation
- [ ] Coupon accrual tracking
- [ ] Amortization schedule generation

**Impairment:**
- [ ] 12-month ECL for Stage 1
- [ ] Lifetime ECL for Stage 2/3
- [ ] Low credit risk exemption (for government bonds)

---

#### Week 5-6: FVOCI & FVTPL Support

**Deliverables:**

**FVOCI Mechanics:**
- [ ] Dual tracking implementation
  - Amortized cost basis for interest income
  - Fair value for balance sheet
- [ ] OCI recycling on derecognition
  - Cumulative FV gains/losses transfer to P&L
- [ ] Impairment in P&L (not OCI)
- [ ] OCI balance adjustment for impairment

**FVTPL Mechanics:**
- [ ] Transaction cost expensing (immediate, not capitalized)
- [ ] No impairment (all credit risk in fair value)
- [ ] P&L volatility tracking
- [ ] Trading performance reporting

---

#### Week 7-8: ECL Impairment Calculation

**Deliverables:**

**ECL Models:**
- [ ] PD (Probability of Default) estimation
- [ ] LGD (Loss Given Default) estimation
- [ ] EAD (Exposure at Default) calculation

**Macroeconomic Integration:**
- [ ] Thai GDP growth forecasts
- [ ] Unemployment rate scenarios
- [ ] Industry-specific indicators
- [ ] Forward-looking forecast engine (reasonable and supportable period)

**Stage Determination:**

| Stage | Trigger | System Implementation |
|-------|---------|----------------------|
| Stage 1 | No significant deterioration | 12-month ECL |
| Stage 2 | Significant credit deterioration | Lifetime ECL |
| Stage 3 | Credit-impaired (objective evidence) | Lifetime ECL, net carrying amount |

**Deterioration Indicators:**
- [ ] Rating downgrade tracking
- [ ] Delinquency monitoring
- [ ] Watchlist flagging
- [ ] Significant increase in credit risk (SICR) assessment

---

#### Week 9-10: Repo Accounting

**Deliverables:**

**Secured Financing Treatment:**
- [ ] Securities remain on balance sheet (not derecognized)
- [ ] Cash borrowing/lending recognition
- [ ] Repo fee accrual (interest expense/income)
- [ ] Collateral tracking (off-balance sheet disclosure)

**Journal Entries:**

**Repo (Cash Borrower):**
```
Dr Cash
    Cr Repo Liability

Dr Interest Expense (accrual)
    Cr Repo Liability
```

**Reverse Repo (Cash Lender):**
```
Dr Reverse Repo Asset
    Cr Cash

Dr Reverse Repo Asset (accrual)
    Cr Interest Income
```

---

#### Week 11-12: Journal Entry & GL Integration

**Deliverables:**

**Journal Entry Generation:**
- [ ] Trade date accounting entries
- [ ] Settlement date entries
- [ ] Accrual entries (daily batch)
- [ ] Mark-to-market entries (daily)
- [ ] ECL provision entries
- [ ] Coupon entries
- [ ] Maturity entries

**GL Mapping:**
- [ ] Account code mapping configuration
- [ ] Cost center allocation
- [ ] Profit center tagging

**Core Banking Integration:**
- [ ] GL interface specification
- [ ] Batch file generation (daily)
- [ ] Real-time API integration (if available)
- [ ] Reconciliation reports

**End-of-Day Batch:**
- [ ] Accrual calculation batch
- [ ] MTM valuation batch
- [ ] ECL calculation batch
- [ ] Journal entry posting batch
- [ ] GL transmission batch

---

### Phase 5: Reporting & Risk Module (Months 10-11)

#### Week 1-2: Regulatory Reporting

**Deliverables:**

**ThaiBMA Reports:**
- [ ] Transaction reports (daily)
- [ ] Position reports (daily)
- [ ] Outstanding reports (monthly)

**BOT Reports:**
- [ ] Liquidity Coverage Ratio (LCR) returns
- [ ] Net Stable Funding Ratio (NSFR) returns
- [ ] Statistical returns
- [ ] Liquidity monitoring tools

**HQLA Classification:**

| Asset Class | LCR Level | Haircut | System Tracking |
|-------------|-----------|---------|-----------------|
| Government bonds (THB) | Level 1 | 0% | Automatic |
| BOT bonds/bills (THB) | Level 1 | 0% | Automatic |
| SOE bonds (guaranteed, AA-) | Level 1 | 0% | Guarantee verification |
| Corporate bonds (AA-) | Level 2A | 15% | Rating monitoring |

**SEC Reports:**
- [ ] Corporate bond holding disclosures
- [ ] Large exposure reports

---

#### Week 3-4: Management Reporting

**Deliverables:**

**Portfolio Valuation:**
- [ ] Daily portfolio MTM
- [ ] Unrealized P&L calculation
- [ ] Realized P&L calculation

**Performance Attribution:**
- [ ] Carry return
- [ ] Price return
- [ ] Currency return (if applicable)
- [ ] Benchmark comparison

**Liquidity Dashboard:**
- [ ] Cash flow forecasting (1 day, 1 week, 1 month)
- [ ] Maturity ladder
- [ ] Available liquidity buffer
- [ ] Stress scenario modeling

**Risk Exposure Dashboards:**
- [ ] Counterparty exposure
- [ ] Issuer concentration
- [ ] Sector distribution
- [ ] Rating distribution
- [ ] Maturity profile

---

#### Week 5-6: Risk Management

**Deliverables:**

**Market Risk:**
- [ ] Duration calculation (Macaulay, Modified)
- [ ] DV01 (Dollar Value of 01bp) calculation
- [ ] Convexity calculation
- [ ] VaR calculation (if required by risk policy)
- [ ] Sensitivity analysis

**Credit Risk:**
- [ ] Counterparty credit exposure monitoring
- [ ] Wrong-way risk identification
- [ ] Credit migration tracking

**Concentration Risk:**
- [ ] Single issuer limit monitoring
- [ ] Sector concentration alerts
- [ ] Rating concentration analysis
- [ ] Geographic concentration (if applicable)

---

#### Week 7-8: Audit & Compliance

**Deliverables:**

**Audit Trail:**
- [ ] 5-year transaction retention (per Thai regulations)
- [ ] Immutable audit log
- [ ] User activity tracking
- [ ] Data lineage tracking
- [ ] Change history for all master data

**Regulatory Examination Support:**
- [ ] Report templates for BOT examinations
- [ ] Report templates for SEC examinations
- [ ] Data export functionality
- [ ] Query tools for auditors

---

### Phase 6: Integration & Testing (Month 12)

#### Week 1-2: End-to-End Integration

**Deliverables:**
- [ ] Full trade lifecycle testing
  - Trade capture → Approval → Execution → Confirmation → Settlement → Accounting
- [ ] External system integration testing
  - TSD test environment
  - BAHTNET test environment
  - ThaiBMA test environment
- [ ] Core banking system integration testing
- [ ] Disaster recovery testing
  - Failover procedures
  - Backup restoration
  - RPO/RTO validation

---

#### Week 3-4: User Acceptance Testing (UAT)

**Deliverables:**

**UAT Execution:**
- [ ] Front Office UAT (traders)
- [ ] Middle Office UAT (risk managers, compliance)
- [ ] Back Office UAT (settlement officers)
- [ ] IT Admin UAT (system administrators)

**Test Scenarios:**
- Normal day operations
- Month-end/quarter-end burst volume
- Settlement failure scenarios
- System exception handling
- Reporting accuracy verification

**Performance Testing:**
- Normal load (25 T/day)
- Burst capacity (100 T/day)
- End-of-day batch processing time
- Concurrent user testing

---

#### Week 5-6: Security & Compliance Testing

**Deliverables:**
- [ ] Penetration testing (external vendor)
- [ ] RBAC testing (role boundary verification)
- [ ] Data encryption validation (at rest and in transit)
- [ ] Audit trail completeness check
- [ ] Regulatory compliance verification (BOT, SEC, ThaiBMA)
- [ ] Vulnerability assessment

---

#### Week 7-8: Production Preparation

**Deliverables:**
- [ ] Production environment setup
  - Server provisioning
  - Database setup
  - Security configuration
  - Monitoring configuration
- [ ] Data migration (if from legacy system)
  - Data mapping
  - Migration scripts
  - Reconciliation
  - Rollback plan
- [ ] User training
  - Front Office training
  - Middle Office training
  - Back Office training
  - IT Admin training
- [ ] Documentation finalization
  - User manuals
  - Operations runbooks
  - Technical documentation
  - Troubleshooting guides
- [ ] Go-live planning
  - Cutover plan
  - Parallel running period (if applicable)
  - Support roster
  - Escalation procedures

---

## 6. Critical Success Factors

### 6.1 Regulatory Compliance

| Factor | Implementation |
|--------|----------------|
| Early Involvement | Include compliance team from Week 1 |
| Pre-Review | Schedule BOT/SEC pre-review before go-live |
| Documentation | Maintain comprehensive compliance documentation |
| Audit Trail | Immutable logging of all compliance-relevant actions |

### 6.2 Data Quality

| Factor | Implementation |
|--------|----------------|
| Validation at Entry | Strict validation rules; never allow bad data to propagate |
| Master Data Governance | Clear ownership of Security Master, Counterparty Master |
| Reconciliation | Daily reconciliation with external systems |
| Exception Management | Clear procedures for data quality issues |

### 6.3 Audit Trail

| Requirement | Implementation |
|-------------|----------------|
| Completeness | Every transaction change logged |
| Immutability | Append-only logs with checksums |
| Attribution | User, timestamp, before/after values |
| Retention | 5-year minimum (Thai regulation) |

### 6.4 Settlement Reliability

| Requirement | Implementation |
|-------------|----------------|
| T+2 Compliance | Non-negotiable; automatic monitoring |
| Failure Recovery | Multiple recovery paths per failure type |
| Liquidity Management | Real-time monitoring with early warnings |
| Communication | Automated alerts to operations team |

### 6.5 Performance

| Scenario | Target |
|----------|--------|
| Normal Load | ≤25 T/day with sub-second response |
| Burst Capacity | 100 T/day (month-end) without degradation |
| End-of-Day Batch | Complete within 2 hours of market close |
| Report Generation | < 5 minutes for standard reports |

### 6.6 Security

| Layer | Implementation |
|-------|----------------|
| Network | Firewall, VPN, intrusion detection |
| Application | OAuth 2.0, RBAC, input validation |
| Database | Encryption at rest, parameterized queries |
| Audit | Immutable logs, access monitoring |

---

## 7. Team Structure and Timeline

### 7.1 Team Composition by Phase

#### Phase 1: Foundation (Months 1-3)

| Role | Count | Responsibilities |
|------|-------|------------------|
| Project Manager | 1 | Planning, coordination, stakeholder management |
| Solution Architect | 1 | Technical design, standards |
| Senior Backend Developer | 2 | Core framework, security, master data |
| Backend Developer | 2 | API development, integration |
| Frontend Developer | 1 | UI foundation |
| Database Administrator | 1 | Schema design, performance |
| DevOps Engineer | 1 | CI/CD, infrastructure |
| QA Engineer | 1 | Test strategy, automation |
| Business Analyst | 1 | Requirements, documentation |
| **Total** | **11** | |

#### Phase 2-5: Core Development (Months 4-9)

| Role | Count | Responsibilities |
|------|-------|------------------|
| Project Manager | 1 | Planning, coordination |
| Solution Architect | 1 | Technical oversight |
| Senior Backend Developer | 3 | Module leads (Trade, Settlement, Accounting) |
| Backend Developer | 4 | Feature development |
| Frontend Developer | 2 | UI development |
| Integration Specialist | 1 | TSD, BAHTNET, ThaiBMA |
| Database Administrator | 1 | Optimization, tuning |
| DevOps Engineer | 1 | Infrastructure, monitoring |
| QA Engineer | 2 | Testing, UAT support |
| Business Analyst | 1 | Requirements, UAT coordination |
| Compliance Analyst | 1 | Regulatory validation |
| **Total** | **18** | |

#### Phase 6: Integration & Go-Live (Month 12)

| Role | Count | Responsibilities |
|------|-------|------------------|
| Project Manager | 1 | Go-live coordination |
| Solution Architect | 1 | Production support |
| Senior Backend Developer | 2 | Critical issue resolution |
| Backend Developer | 2 | Support |
| Frontend Developer | 1 | UI support |
| DevOps Engineer | 1 | Production deployment |
| QA Engineer | 1 | Final validation |
| Business Analyst | 1 | User training |
| **Total** | **10** | |

### 7.2 Timeline Summary

```
Month:  1   2   3   4   5   6   7   8   9  10  11  12
        ├───────┤
        │Phase 1│
        │Foundation
                ├───────┤
                │Phase 2│
                │Trade Execution
                        ├───────┤
                        │Phase 3│
                        │Settlement
                                ├───────┤
                                │Phase 4│
                                │Accounting
                                        ├───────┤
                                        │Phase 5│
                                        │Reporting
                                                ├───┤
                                                │P6 │
                                                │Integration
```

### 7.3 Milestones

| Milestone | Target Date | Success Criteria |
|-----------|-------------|------------------|
| M1: Foundation Complete | End Month 3 | Security framework, master data, external connectivity ready |
| M2: Trade Execution Live | End Month 5 | OTC capture, limits, ThaiBMA reporting operational |
| M3: Settlement Live | End Month 7 | TSD, BAHTNET, repo lifecycle operational |
| M4: Accounting Live | End Month 9 | TFRS 9 classification, ECL, GL integration operational |
| M5: Reporting Complete | End Month 11 | All regulatory and management reports operational |
| M6: Go-Live | End Month 12 | Production deployment, parallel running complete |

### 7.4 Budget Estimate

| Category | Estimate (THB) | Notes |
|----------|----------------|-------|
| Personnel (12 months) | 24,000,000 | 18-person peak team |
| Infrastructure (cloud/on-premise) | 2,000,000 | Servers, databases, monitoring |
| Software Licenses | 1,500,000 | Database, reporting, security tools |
| External Connectivity | 500,000 | TSD, BAHTNET, ThaiBMA, Bloomberg |
| Security Testing | 800,000 | Penetration testing, audit |
| Training | 300,000 | User training materials, sessions |
| Contingency (10%) | 2,910,000 | |
| **Total** | **32,010,000** | Approximate estimate |

---

## Appendix A: External System Contact Information

| System | Organization | Contact | Purpose |
|--------|--------------|---------|---------|
| TSD | Thailand Securities Depository | API Support | Corporate bond settlement |
| BAHTNET | Bank of Thailand | Operations | Government securities settlement |
| ThaiBMA | Thai Bond Market Association | IT Department | Trade reporting, market data |
| Bloomberg | Bloomberg LP | Account Manager | Market data feeds |
| Reuters | LSEG (Refinitiv) | Account Manager | Market data feeds |

---

## Appendix B: Regulatory Reference Documents

| Document | Issuer | Purpose |
|----------|--------|---------|
| ThaiBMA Reporting Guidelines | ThaiBMA | Trade reporting requirements |
| BOT Notification on Liquidity Coverage Ratio | Bank of Thailand | LCR reporting |
| SEC Notification on Corporate Bond Disclosure | SEC | Disclosure requirements |
| TFRS 9 Standard | Federation of Accounting Professions | Accounting standards |

---

## Appendix C: Glossary

| Term | Definition |
|------|------------|
| BAHTNET | Bank of Thailand Automated High-value Transfer Network (RTGS) |
| DVP | Delivery Versus Payment |
| EAD | Exposure at Default |
| ECL | Expected Credit Loss |
| EIR | Effective Interest Rate |
| FVTPL | Fair Value Through Profit or Loss |
| FVOCI | Fair Value Through Other Comprehensive Income |
| GMRA | Global Master Repurchase Agreement |
| HQLA | High Quality Liquid Assets |
| LCR | Liquidity Coverage Ratio |
| LGD | Loss Given Default |
| MTM | Mark-to-Market |
| NSFR | Net Stable Funding Ratio |
| OTC | Over-the-Counter |
| PD | Probability of Default |
| PSMS | Pre-Settlement Matching System |
| Repo | Repurchase Agreement |
| RTGS | Real-Time Gross Settlement |
| SBT | Specific Business Tax |
| SOE | State-Owned Enterprise |
| SPPI | Solely Payments of Principal and Interest |
| TFRS | Thai Financial Reporting Standards |
| THOR | Thai Overnight Repurchase Rate |
| TSD | Thailand Securities Depository |
| UAT | User Acceptance Testing |
| VaR | Value at Risk |

---

*Document Version: 1.0*
*Last Updated: February 2026*
*Author: System Architecture Team*
