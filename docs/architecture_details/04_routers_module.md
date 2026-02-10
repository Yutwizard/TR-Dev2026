# Architecture & Request Flow: API Routers

The Routers module serves as the entry point (FastAPI controllers), handling HTTP requests, validation through Pydantic schemas, and delegation to backend services.

## 1. Request Lifecycle Overview
Every request to the TMS API follows this standard path:

```mermaid
graph TD
    A[Client Request] --> B[FastAPI Middleware: CORS/Logging]
    B --> C{Auth: JWT Middleware}
    C -- Valid Token --> D{Permissions: Dependency Check}
    D -- Authorized --> E[Router Implementation]
    E --> F[Pydantic Schema Validation]
    F -- Valid --> G[Service Method Call]
    G --> H[Response Serialization]
    H --> I[Client Response]
    
    subgraph Error Handling
        F -- Invalid --> J[422 Unprocessable Entity]
        G -- Business Error --> K[TreasuryException Mapper]
        K --> L[Custom Error JSON]
    end
```

---

## 2. Key Routers and Their Roles

| Router | Purpose | Key Endpoints | Dependencies |
| :--- | :--- | :--- | :--- |
| `auth_router` | Identity Management | `/login`, `/refresh`, `/me` | User Service, Auth Utility |
| `bond_trades_router` | Trade Capture | `POST /` (Capture), `PATCH /{id}/approve` | Bond Service, Four-Eyes Check |
| `repo_router` | Collateralized Trading | `POST /create`, `GET /active` | Repo Service, Position Service |
| `settlement_router` | Ops Management | `GET /pending`, `POST /execute` | Settlement Service |
| `market_data_router` | Pricing Feeds | `POST /upload`, `GET /price/{symbol}` | ThaiBMA Service |

---

## 3. Data Flow Example: Trade Approval
This flow ensures the "Four-Eyes Principle" where the person who entered the trade cannot be the one who approves it.

```mermaid
sequenceDiagram
    participant UI as Frontend
    participant R as Bond Router
    participant P as Permission Check
    participant S as Bond Service
    participant DB as Database

    UI->>R: PATCH /api/v1/bond-trades/{id}/approve
    R->>P: require_permission(APPROVE_TRADE)
    P-->>R: Authorized (Role: SUPERVISOR)
    R->>S: approve_trade(trade_id, user_id)
    S->>S: validate_four_eyes(creator_id, current_user_id)
    alt Same User
        S-->>R: AuthorizationError (403)
        R-->>UI: "Cannot approve own trade"
    else Different User
        S->>DB: Update Status -> APPROVED
        S->>DB: Create Audit Log Entry
        S-->>R: Success
        R-->>UI: 200 OK (Trade Approved)
    end
```

---

## 4. Middleware and Security Headers
- **CORS**: Restricted to allowed origins specified in `.env`.
- **Logging**: Captures request metadata (method, path, user_id) for every transaction.
- **Exception Handlers**: Located in `app.core.exceptions`, they catch business-specific errors and return standardized JSON status codes.
