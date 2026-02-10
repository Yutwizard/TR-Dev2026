# Architecture & Flow: Core Module

This document details the core infrastructure of the Treasury Management System (TMS) backend.

## 1. Enums (`app/core/enums.py`)
**Purpose**: Centralized source of truth for all system constants, ensuring consistency across models, schemas, and services.

### Key Components:
- `TradeStatus`: Defines the lifecycle of all deals (DRAFT, PENDING_APPROVAL, etc.).
- `TradeSide`: BUY, SELL, LEND, BORROW.
- `Permission`: Granular action-based permissions.
- `AuditAction`: Types of actions captured in the audit trail.

---

## 2. State Machine (`app/core/state_machine.py`)
**Purpose**: Enforces valid state transitions for complex financial instruments.

### Transition Logic Flow:
```mermaid
graph TD
    subgraph Bond Trade Lifecycle
        B1(DRAFT) --> B2(PENDING_APPROVAL)
        B2 --> B3(APPROVED)
        B2 --> B1
        B3 --> B4(PENDING_SETTLEMENT)
        B4 --> B5(SETTLED)
        B2 -- Rejected --> B1
        B3 -- Cancelled --> B6(CANCELLED)
    end

    subgraph Repo Lifecycle
        R1(DRAFT) --> R2(PENDING_APPROVAL)
        R2 --> R3(APPROVED)
        R3 --> R4(ACTIVE)
        R4 --> R5(NEAR_LEG_SETTLED)
        R5 --> R6(MATURED)
        R4 -- Margin Alert --> R7(MARGIN_CALL)
        R7 --> R4
    end
```

---

## 3. Authentication & Security (`app/core/auth.py`, `app/core/security.py`)
**Purpose**: Handles JWT token generation, password hashing, and user identity verification.

### Authentication Flow:
```mermaid
sequenceDiagram
    participant User
    participant Router
    participant Auth
    participant DB

    User->>Router: POST /auth/token (Credentials)
    Router->>Auth: authenticate_user()
    Auth->>DB: get_user_by_username()
    DB-->>Auth: User Record (Hashed Pwd)
    Auth->>Auth: verify_password()
    alt Success
        Auth-->>Router: JWT Access & Refresh Tokens
        Router-->>User: 200 OK + Tokens
    else Failure
        Auth-->>Router: AuthenticationError
        Router-->>User: 401 Unauthorized
    end
```

---

## 4. Permissions & RBAC (`app/core/permissions.py`)
**Purpose**: Role-Based Access Control (RBAC) ensuring only authorized users can perform specific actions (e.g., Four-Eyes Principle).

### Permission Check Flow:
```mermaid
graph LR
    A[Dependency: require_permission] --> B{User Active?}
    B -- No --> C[401 Unauthorized]
    B -- Yes --> D{Has Permission?}
    D -- No --> E[403 Forbidden]
    D -- Yes --> F[Proceed to Router]
    
    subgraph Four-Eyes Principle
        G[Action: Approve] --> H{Approver == Creator?}
        H -- Yes --> I[ValidationError: Self-Approval Blocked]
        H -- No --> J[Allow Approval]
    end
```

---

## 5. Global Exception Handling (`app/core/exceptions.py`)
**Purpose**: Unified error reporting across the API.

### Flow:
```mermaid
graph TD
    A[Service Error] --> B{Is TreasuryException?}
    B -- Yes --> C[Map to Custom HTTP Response]
    B -- No --> D[Internal Server Error 500]
    C --> E[JSON Response: {code, message, details}]
```
