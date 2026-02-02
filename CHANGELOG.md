# Changelog

All notable changes to the Treasury Management System project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Frontend UI implementation (Next.js)
- Database models implementation
- Full API implementation

---

## [0.2.0] - 2026-02-02

### Added

- **Backend Foundation**
  - `src/backend/app/main.py` - FastAPI application entry point with CORS, lifespan
  - `src/backend/app/config.py` - Pydantic settings configuration
  - `src/backend/README.md` - Backend structure documentation

- **Authentication & Security**
  - `src/backend/app/core/auth.py` - JWT authentication with access/refresh tokens
  - `src/backend/app/core/security.py` - Password hashing, validation utilities
  - `src/backend/app/core/permissions.py` - Role-Based Access Control (RBAC)
  - `src/backend/app/core/exceptions.py` - Custom exception handlers

- **Business Services**
  - `src/backend/app/services/calendar_service.py` - Thai business day calendar (2025-2026 holidays)
  - `src/backend/app/services/settlement_service.py` - BAHTNET ISO20022 & TSD message generators

- **API Routers**
  - `src/backend/app/routers/auth.py` - Authentication endpoints (login, refresh, me)
  - `src/backend/app/routers/health.py` - Health check endpoints

- **Infrastructure**
  - `docker-compose.local.yml` - Local Docker setup (PostgreSQL, Redis, Adminer)
  - `scripts/init_db.sql` - Database initialization with 20+ tables
  - `src/backend/requirements.txt` - Python dependencies
  - `.env.example` - Environment variables template

- **Documentation Updates**
  - `docs/architecture/Development_Plan_Review_and_Concerns.md` - Phase review with risks
  - Updated `docs/architecture/Local_Development_and_Testing_Guide.md` - Docker Desktop, WSL2, Windows setup
  - Updated `docs/architecture/Condensed_Development_Plan.md` - BAHTNET as ISO20022 manual
  - Updated `README.md` and `docs/index.md` with new documents

- **Settlement Output Directories**
  - `output/bahtnet/README.md` - BAHTNET message output (manual upload)
  - `output/tsd/README.md` - TSD instruction output (manual entry)

### Changed
- BAHTNET integration clarified as manual ISO20022 message generation (no API)
- TSD integration clarified as manual settlement instruction (no API)

---

## [0.1.0] - 2026-02-02

### Added
- **Project Structure Reorganization**
  - Created `docs/` folder with subfolders: `analysis/`, `architecture/`, `requirements/`, `reference/`
  - Created `data/` folder with subfolders: `source/`, `extracted/`, `reference/`
  - Created `scripts/` folder for utility scripts
  - Created `src/` folder with subfolders: `backend/`, `frontend/`, `shared/`
  - Created `tests/` folder for test files
  - Created `output/` folder with subfolders: `csv/`, `json/`

- **Documentation**
  - `README.md` - Project overview and quick start guide
  - `CHANGELOG.md` - Version history tracking
  - `docs/index.md` - Documentation navigation index
  - `.gitignore` - Git ignore rules

- **Core Documents** (migrated and renamed)
  - `docs/analysis/Data_Structure_Analysis.md` - Database structure analysis
  - `docs/architecture/Treasury_System_Architecture_and_Implementation_Guide.md` - System architecture
  - `docs/architecture/Data_to_Architecture_Mapping_and_Development_Guide.md` - Data mapping guide
  - `docs/requirements/Treasury_System_Structure.docx` - Original requirements
  - `docs/requirements/Treasury_System_Structure.pdf` - Original requirements (PDF)

- **Data Files** (migrated)
  - `data/source/Treasury_System_Database_V2_Internal.xlsx` - Master data model
  - `data/extracted/` - All extracted text files (tables, bank codes, haircuts, etc.)

- **Scripts** (migrated)
  - `scripts/extract_excel.py` - Excel data extraction utility

### Changed
- Renamed files from space-separated to underscore-separated naming convention
- Reorganized flat file structure into logical folder hierarchy

### Removed
- Old `document/` folder (content migrated to `docs/`)

---

## Version History Summary

| Version | Date | Description |
|---------|------|-------------|
| 0.1.0 | 2026-02-02 | Project structure reorganization |

---

*For questions or contributions, contact the project team.*
