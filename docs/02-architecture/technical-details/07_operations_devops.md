# Architecture & Operations: DevOps & Deployment

This document details the operational architecture, local development environment, and production lifecycle of the TMS.

## 1. Local Development Stack (Docker)
The system uses `docker-compose.local.yml` to orchestrate essential back-end infrastructure.

### Container Architecture:
```mermaid
graph TD
    subgraph Host Machine
        A[FastAPI App: Port 8000]
        B[Next.js App: Port 3000]
    end
    
    subgraph Docker Network
        C[(PostgreSQL 15)]
        D[(Redis 7)]
        E[Adminer: DB GUI]
        F[Redis Commander]
    end
    
    A --> C
    A --> D
    B --> A
    E --> C
    F --> D
```

---

## 2. Startup & Initialization Flow
When the system starts, it undergoes a multi-stage initialization to ensure data integrity.

```mermaid
sequenceDiagram
    participant OS as Docker/Shell
    participant DB as Postgres
    participant Ini as init_db.sql
    participant App as FastAPI Backend

    OS->>DB: docker-compose up
    DB->>Ini: Execute Schema & Master Data
    OS->>App: uvicorn app.main:app
    App->>DB: check_database_connection()
    App->>App: Lifespan Startup: Logging & Config
    Note over App: Ready for requests
```

---

## 3. Persistent Storage Strategy
- **Volumes**: Databases use Docker Volumes (`tms_postgres_data`) for persistence across container restarts.
- **Backups**: The `scripts/init_db.sql` provides a baseline state for the Money Market, Bond, and Repo environments.

---

## 4. Operational Workflows (Batch Jobs)
Treasury systems rely on End-of-Day (EOD) processing for valuation and interest accrual.

### EOD Batch Process Flow:
```mermaid
graph TD
    A[Cron / Trigger: run_eod_batch.py] --> B[Fetch Today MTM Prices]
    B --> C[Calculate Realized/Unrealized P&L]
    C --> D[Accrue Interest for Interbank/Repo]
    D --> E[Update Positions: Current Face]
    E --> F[Generate EOD Reports]
    F --> G[Close Business Day]
```

---

## 5. Environment Configuration
The system uses Pydantic Settings to load variables from `.env`.

- **Security**: `SECRET_KEY` and `JWT_ALGORITHM` are non-negotiable for production.
- **Integrations**: `THAIBMA_API_URL` and `BOT_API_KEY` control external data flows.
- **Modes**: `TSD_MODE` and `BAHTNET_MODE` allow switching between `manual` (CSV-based) and `api` workflows.
