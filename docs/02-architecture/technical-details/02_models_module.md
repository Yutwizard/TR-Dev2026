# Architecture & Data Schema: Models Module

This document outlines the data architecture and Entity-Relationship logic of the TMS.

## 1. Core Data Hierarchy
The system uses a hierarchical master data structure to support multi-entity bank operations.

### Entity Relationship Diagram (Conceptual):
```mermaid
erDiagram
    ENTITY-MASTER ||--o{ USER : "has"
    ENTITY-MASTER ||--o{ COUNTERPARTY-MASTER : "contains"
    ENTITY-MASTER ||--o{ PORTFOLIO-MASTER : "owns"
    
    SECURITY-MASTER ||--o{ THAIBMA-MARKET-DATA : "priced by"
    SECURITY-MASTER ||--o{ BOND-TRADE : "traded in"
    
    BOND-TRADE }o--|| COUNTERPARTY-MASTER : "engaged with"
    BOND-TRADE }o--|| PORTFOLIO-MASTER : "booked in"
    
    REPO-TRADE }o--|| SECURITY-MASTER : "collateral"
    REPO-TRADE }o--|| COUNTERPARTY-MASTER : "counterparty"
```

---

## 2. Transaction Models (`app/models/transactions.py`)
**Purpose**: Persistent storage for all trade types.

### Bond Trade Flow to DB:
```mermaid
graph TD
    A[Raw Trade Input] --> B[BondTrade ORM Object]
    B --> C{Validation}
    C -- Success --> D[Save to bond_trades table]
    D --> E[Update Position Engine]
```

### Repo Trade Complexity:
- `RepoTrade` tracks both legs: Near Leg (Cash Out/In) and Far Leg (Maturity).
- Linkage to `CollateralPosition` ensures collateral is blocked.

---

## 3. Position Tracking (`app/models/positions.py`)
**Purpose**: Real-time balance and holding tracking.

### Balance Update Flow:
```mermaid
graph TD
    A[Trade Settled] --> B{Trade Type?}
    B -- Bond --o C[BondPosition]
    B -- IB/Repo --o D[CashPosition]
    C --> E[Update dirty_price & face_value]
    D --> F[Update balance & projected_flow]
```

---

## 4. Audit Trail (`app/models/audit.py`, `app/models/users.py`)
**Purpose**: Regulatory compliance (SEC/BOT) for all financial actions.

### Audit Logging Logic:
- **Immutable**: Records are append-only.
- **Detailed**: Stores `old_values` and `new_values` as JSON to track specific field changes.
- **Traceable**: Includes `correlation_id` to link multiple actions in one workflow.

---

## 5. Risk & Limits (`app/models/limits.py`)
**Purpose**: Pre-trade and post-trade risk control.

### Limit Check Sequence:
```mermaid
sequenceDiagram
    participant Trader
    participant Service
    participant LimitEngine
    participant DB

    Trader->>Service: Create Trade
    Service->>LimitEngine: check_limit(counterparty, amount)
    LimitEngine->>DB: Get current utilization
    DB-->>LimitEngine: 85,000,000 (Limit: 100M)
    alt Within Limit
        LimitEngine-->>Service: OK
        Service->>DB: Save Trade + Update Utilization
    else Threshold Warning
        LimitEngine-->>Service: Warning (80%+)
        Service->>DB: Log Warning + Save Trade
    else Breach
        LimitEngine-->>Service: REJECT (100%+)
        Service->>DB: Log Breach
    end
```
