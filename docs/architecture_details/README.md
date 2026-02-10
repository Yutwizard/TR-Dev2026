# System Architecture Documentation Index

Welcome to the detailed architectural documentation for the Treasury Management System (TMS). This folder contains technical breakdowns and flow charts for each major layer of the application.

## 📁 Folder Structure
All documentation is located in `docs/architecture_details/`.

### 1. [Core Module (Infrastructure)](./01_core_module.md)
Contains the foundation of the app:
- **Enums**: Single source of truth.
- **State Machine**: Critical lifecycle transition logic.
- **Security**: JWT Auth and Password management.
- **Permissions**: RBAC and Four-Eyes principle implementation.

### 2. [Database Models (Data Layer)](./02_models_module.md)
Maps the physical storage and entity relationships:
- **ER Diagrams**: Relationships between Entities, Users, and Trades.
- **Transactions**: Schema for Bond, Repo, and Interbank deals.
- **Audit Trails**: JSON-based change tracking.

### 3. [Services (Business Logic)](./03_services_module.md)
The "Brain" of the system:
- **Trade Services**: Lifecycle management for specific products.
- **Calculation Engine**: Financial math and conventions.
- **Settlement**: The orchestration of T+2 workflows.
- **External Integration**: ThaiBMA and BOT API handlers.

### 4. [API Routers (Interface Layer)](./04_routers_module.md)
The entry points:
- **Request Lifecycle**: How a packet travels from UI to DB.
- **Middlewares**: CORS, Authentication, and Exception mapping.
- **Sequence Diagrams**: Interaction between UI, Routers, and Services.

### 5. [Frontend Module (User Interface)](./05_frontend_module.md)
The modern web portal:
- **Next.js Architecture**: Component hierarchy and App Router.
- **API Communication**: The `ApiClient` request lifecycle.

### 6. [Testing Framework (QA)](./06_testing_framework.md)
Ensuring financial reliability:
- **Test Layers**: Unit, Service, and API testing domains.
- **Isolation**: Database transaction rollback strategy.
- **Mocking**: Handling external financial data providers.

### 7. [Operations & DevOps (Deployment)](./07_operations_devops.md)
Project lifecycle and environment:
- **Docker Stack**: Local orchestration for DB and Cache.
- **Initialization**: Startup sequences and SQL seeding.
- **EOD Processing**: The End-of-Day batch flow logic.

---

## 🛠 Tech Stack
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (SQLAlchemy ORM)
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Cache**: Redis
- **Infra**: Docker Compose
- **Testing**: Pytest
- **Diagrams**: MermaidJS
