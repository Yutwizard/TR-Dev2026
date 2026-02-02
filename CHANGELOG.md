# Changelog

All notable changes to the Treasury Management System project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Backend API implementation (FastAPI)
- Frontend UI implementation (Next.js)
- Database schema implementation
- ThaiBMA integration
- BAHTNET integration

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
