# System Landscape & Architecture Canvas

This document provides a high-level visual map of the entire Treasury Management System (TMS), connecting all modules into a single cohesive view.

## 1. C4 System Context Diagram
Shows how the TMS fits into the external banking ecosystem.

```mermaid
C4Context
    title System Context Diagram - Treasury Management System

    Person(trader, "Front Office Trader", "Executes Bond, Repo, and Interbank deals")
    Person(mo, "Middle Office", "Risk control, Limit monitoring, and P&L verification")
    Person(bo, "Back Office", "Settlement, Confirmation, and Accounting")
    
    System(tms, "Treasury Management System", "Core platform for trade capture, position management, and settlement")
    
    System_Ext(thaibma, "ThaiBMA API", "Bond market data, pricing, and yield curves")
    System_Ext(bot, "Bank of Thailand (BOT)", "Policy rates, holidays, and regulatory reporting")
    System_Ext(bahtnet, "BAHTNET", "High-value payment system for THB settlement")
    System_Ext(tsd, "TSD (Depository)", "Securities settlement and custody")

    Rel(trader, tms, "Enters trades, views positions")
    Rel(mo, tms, "Approves limits, verifies prices")
    Rel(bo, tms, "Confirms payments, generates settlement instructions")
    
    Rel(tms, thaibma, "Fetches market data (Daily)")
    Rel(tms, bot, "Fetches holidays, reports transactions")
    Rel(tms, bahtnet, "Sends payment instructions (MT202)")
    Rel(tms, tsd, "Sends settlement instructions (MT540/541/542/543)")
```

---

## 2. Container Diagram (High-Level Architecture)
Shows the internal software containers and their interactions.

```mermaid
C4Container
    title Container Diagram - TMS Application Stack

    Container(spa, "Single Page Application", "Next.js / TypeScript", "Web interface for all users")
    Container(api, "API Gateway", "FastAPI / Python", "REST API handling requests, auth, and validation")
    
    Container_Boundary(services, "Backend Services") {
        Component(trade_svc, "Trade Service", "Module", "Handles Bond, Repo, Interbank logic")
        Component(pos_svc, "Position Service", "Module", "Manages balances and holdings")
        Component(limit_svc, "Limit Engine", "Module", "Checks credit and counterparty limits")
        Component(calc_svc, "Calculation Engine", "Module", "Financial math (Yield, Accrual, Pricing)")
        Component(stl_svc, "Settlement Service", "Module", "Orchestrates T+n workflows")
    }

    ContainerDb(db, "Primary Database", "PostgreSQL", "Stores transactions, master data, and audit logs")
    ContainerDb(cache, "Cache / Session Store", "Redis", "Stores user sessions and market data cache")

    Rel(spa, api, "Uses", "JSON/HTTPS")
    Rel(api, trade_svc, "Delegates to")
    Rel(api, pos_svc, "Delegates to")
    Rel(api, limit_svc, "Delegates to")
    
    Rel(trade_svc, calc_svc, "Uses", "Function Call")
    Rel(trade_svc, limit_svc, "Uses", "Function Call")
    
    Rel(trade_svc, db, "Reads/Writes")
    Rel(pos_svc, db, "Reads/Writes")
    Rel(api, cache, "Reads/Writes")
```

---

## 3. Dynamic Data Flow (End-to-End)
Visualizes how data moves through the system during a typical trade lifecycle.

```mermaid
flowchart TD
    subgraph Frontend ["Frontend Logic"]
        UI[User Interface] -->|1. Submit Trade| VAL[Validation Layer]
        VAL -->|2. Valid Request| API[API Client]
    end

    subgraph Backend ["Backend API"]
        API -->|3. POST /trades| ROUTER[FastAPI Router]
        ROUTER -->|4. Check Auth| AUTH[Auth Middleware]
        AUTH -->|5. Verify Perms| RBAC[RBAC Service]
    end

    subgraph Business ["Business Logic"]
        RBAC -->|6. Authorized| SERVICE[Trade Service]
        SERVICE -->|7. Check Limit - Limit Service| LIMIT{Limit OK?}
        LIMIT -- No --> REJECT[Reject Trade]
        LIMIT -- Yes --> CALC[Calc Engine: Price/Yield]
        CALC -->|8. Enriched Data| DB_TX[DB Transaction]
    end

    subgraph Data ["Data Persistence"]
        DB_TX -->|9. Insert Trade| TABLE_A[(Trades Table)]
        DB_TX -->|10. Update utilization| TABLE_B[(Limits Table)]
        DB_TX -->|11. Create Audit| TABLE_C[(Audit Log)]
    end

    subgraph Post ["Post-Process"]
        DB_TX -->|12. Commit Success| EVENT[Event Bus / Queue]
        EVENT -->|13. Async| POSITION[Position Service: Update]
    end
```

---

## 4. Infrastructure & Deployment Map
Shows how the system is deployed in a production-like environment (Docker).

```mermaid
flowchart TB
    subgraph Docker ["Docker Host"]
        subgraph FrontendNet ["Frontend Network"]
            NextJS["Next.js Container :3000"]
        end

        subgraph BackendNet ["Backend Network"]
            FastAPI["FastAPI Container :8000"]
            Worker["Celery Worker (Future)"]
        end

        subgraph DataLayer ["Data Persistence Layer"]
            Postgres[("PostgreSQL 15 :5432")]
            Redis[("Redis 7 :6379")]
        end

        subgraph Mgmt ["Management & Observability"]
            Adminer["Adminer GUI :8080"]
            Commander["Redis Commander :8081"]
        end
    end

    NextJS --> FastAPI
    FastAPI --> Postgres
    FastAPI --> Redis
    Worker --> Redis
    Worker --> Postgres
    Adminer --> Postgres
    Commander --> Redis
```
