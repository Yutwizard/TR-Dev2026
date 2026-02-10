# Architecture & Flow: Testing Framework

The TMS employs a multi-layered testing strategy to ensure reliability, financial accuracy, and security.

## 1. Testing Layers
The system is divided into three primary testing domains:

- **Unit Tests**: testing individual functions (e.g., `calculation_engine.py`) with zero dependencies.
- **Service Tests**: testing complex business logic in `app.services`, often using a test database.
- **API Tests**: testing full HTTP request/response cycles, including authentication and CORS.

---

## 2. Test Execution Flow
Tests are orchestrated via `pytest`, with localized `conftest.py` files managing shared fixtures.

```mermaid
graph TD
    A[Start Pytest] --> B[Load conftest.py Fixtures]
    B --> C[Create Isolated Test DB]
    C --> D[Run Test Suite]
    D --> E{Test Category}
    E -- Auth --o F[test_auth.py: Token cycles]
    E -- Service --o G[test_repo_service.py: State logic]
    E -- API --o H[test_api.py: HTTP endpoints]
    F --> I[Teardown DB]
    G --> I
    H --> I
    I --> J[Generate Coverage Report]
```

---

## 3. Database Isolation Strategy
To ensure tests are idempotent and fast, the framework uses an isolated database instance.

### Logical Interaction:
```mermaid
sequenceDiagram
    participant Suite as Test Suite
    participant Fix as DB Fixture
    participant ORM as SQLAlchemy
    participant DB as Test Database

    Suite->>Fix: Request db_session
    Fix->>DB: Begin Transaction (SAVEPOINT)
    Fix-->>Suite: Session Provider
    Suite->>ORM: perform_action()
    ORM->>DB: SQL Queries
    Suite->>Fix: Test Complete
    Fix->>DB: Rollback (Return to clean state)
    Note over Fix,DB: DB remains pristine for next test
```

---

## 4. External Service Mocking
External integrations (like ThaiBMA or Bank of Thailand APIs) are mocked during testing to avoid network latency and dependency on external uptime.

### Mocking Flow:
```mermaid
graph LR
    A[Service under Test] --> B{Env == TEST?}
    B -- Yes --> C[MockFetcher: Returns static JSON]
    B -- No --> D[RealFetcher: Calls HTTPS API]
    C --> E[Verify Logic Processing]
```

---

## 5. Security Testing
- **Role-Based Access**: Specialized tests verify that a `TRADER` cannot access `admin` endpoints.
- **Four-Eyes Verification**: Explicitly testing that self-approval attempts return `AuthorizationError (403)`.
- **JWT Integrity**: Verifying that expired or malformed tokens are rejected with `401 Unauthorized`.
