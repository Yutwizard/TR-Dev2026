# 📚 Treasury Management System - Documentation Index

**Navigation hub for all project documentation**

---

## 🗂️ Document Categories

### 📊 Analysis Documents
*System and data analysis documentation*

| Document | Description | Last Updated |
|----------|-------------|--------------|
| [Data Structure Analysis](analysis/Data_Structure_Analysis.md) | Comprehensive analysis of the 76-sheet Treasury System Database V2, including table relationships, field mappings, and regulatory compliance requirements | Feb 2026 |

---

### 🏗️ Architecture Documents
*System design and implementation guides*

| Document | Description | Last Updated |
|----------|-------------|--------------|
| [Development Approach Summary](architecture/Development_Approach_Summary.md) | **START HERE** - Overview of local-first development approach, timeline summary, and quick reference | Feb 2026 |
| [Local Development & Testing Guide](architecture/Local_Development_and_Testing_Guide.md) | **FOR DEVELOPERS** - Complete local environment setup, testing strategy, and step-by-step development guide | Feb 2026 |
| [Condensed Development Plan](architecture/Condensed_Development_Plan.md) | 10-week sprint plan with detailed week-by-week deliverables (local-first approach) | Feb 2026 |
| [**Development Plan Review & Concerns**](architecture/Development_Plan_Review_and_Concerns.md) | **CRITICAL READ** - Risk assessment, concerns, and recommendations for all phases | Feb 2026 |
| [Architecture & Implementation Guide](architecture/Treasury_System_Architecture_and_Implementation_Guide.md) | Complete system architecture including modular monolith design, module specifications, technology stack | Feb 2026 |
| [Data to Architecture Mapping](architecture/Data_to_Architecture_Mapping_and_Development_Guide.md) | Detailed mapping of database tables to system modules, SQL schemas, and API specifications | Feb 2026 |

---

### 📋 Requirements Documents
*Original business requirements and specifications*

| Document | Description | Format |
|----------|-------------|--------|
| [Treasury System Structure](requirements/Treasury_System_Structure.pdf) | Original requirements document for Thai Commercial Bank Treasury System covering Local Bond and Money Market Operations | PDF |
| [Treasury System Structure](requirements/Treasury_System_Structure.docx) | Editable version of requirements | DOCX |

---

### 📖 Reference Documents
*Reference materials and lookup data*

| Resource | Description | Location |
|----------|-------------|----------|
| Bank Codes | BOT official bank code list | `data/extracted/bank_code.txt` |
| Haircut Table | BOT standard haircut matrix | `data/extracted/haircut_table.txt` |
| Stage Master | TFRS 9 staging definitions | `data/extracted/stage_master.txt` |
| Table Master | Table definitions | `data/extracted/table_master.txt` |

---

## 📁 Quick Reference: Folder Structure

```
docs/
├── index.md                 # This file - documentation index
├── analysis/                # Data & system analysis
│   └── Data_Structure_Analysis.md
├── architecture/            # Architecture & design
│   ├── Treasury_System_Architecture_and_Implementation_Guide.md
│   └── Data_to_Architecture_Mapping_and_Development_Guide.md
├── requirements/            # Original requirements
│   ├── Treasury_System_Structure.docx
│   └── Treasury_System_Structure.pdf
└── reference/               # Reference materials
    └── (future reference docs)
```

---

## 🔍 Document Search Guide

### By Goal (What do you want to do?)

| Goal | Document to Read |
|------|------------------|
| **Understand the project** | [Development Approach Summary](architecture/Development_Approach_Summary.md) |
| **Set up local environment** | [Local Development & Testing Guide](architecture/Local_Development_and_Testing_Guide.md) |
| **Start coding (Week 1)** | [Local Development & Testing Guide](architecture/Local_Development_and_Testing_Guide.md) Phase 1-2 |
| **Understand the timeline** | [Condensed Development Plan](architecture/Condensed_Development_Plan.md) |
| **See database design** | [Data Structure Analysis](analysis/Data_Structure_Analysis.md) |
| **See API specifications** | [Data to Architecture Mapping](architecture/Data_to_Architecture_Mapping_and_Development_Guide.md) Section 6 |
| **Understand testing** | [Local Development & Testing Guide](architecture/Local_Development_and_Testing_Guide.md) Section 4 |

### By Development Stage

| Stage | Documents |
|-------|-----------|
| **Week 1: Setup** | [Local Development & Testing Guide](architecture/Local_Development_and_Testing_Guide.md) Phase 1 |
| **Week 2-3: Core Features** | [Condensed Development Plan](architecture/Condensed_Development_Plan.md) Sprint 2-3 |
| **Week 4: Frontend** | [Local Development & Testing Guide](architecture/Local_Development_and_Testing_Guide.md) Phase 4 |
| **Week 5: All Products** | [Condensed Development Plan](architecture/Condensed_Development_Plan.md) Sprint 5 |
| **Week 8: Testing** | [Local Development & Testing Guide](architecture/Local_Development_and_Testing_Guide.md) Phase 4 |
| **Week 10: Deployment** | [Condensed Development Plan](architecture/Condensed_Development_Plan.md) Sprint 10 |

### By Topic

| Topic | Relevant Documents |
|-------|-------------------|
| **Database Schema** | Data Structure Analysis |
| **System Architecture** | Architecture & Implementation Guide |
| **Module Design** | Data to Architecture Mapping |
| **BOT Compliance** | Data Structure Analysis (Section 7-8) |
| **TFRS 9 Implementation** | Data Structure Analysis (Section 8.1) |
| **API Design** | Data to Architecture Mapping (Section 6) |
| **Settlement Flow** | Architecture Guide (Settlement Module) |
| **Local Testing** | Local Development & Testing Guide |

### By Product

| Product | Relevant Sections |
|---------|------------------|
| **Interbank Lending/Borrowing** | Data Structure (3.1), Architecture (Trade Execution), Condensed Plan (Sprint 5) |
| **Repo/Reverse Repo** | Data Structure (3.2), Architecture (Settlement), Condensed Plan (Sprint 5) |
| **Bond Trading** | Data Structure (3.3), Architecture (Trade Execution), Condensed Plan (Sprint 2) |

### By Role

| Role | Start Here |
|------|-----------|
| **Project Manager** | [Development Approach Summary](architecture/Development_Approach_Summary.md) → [Condensed Development Plan](architecture/Condensed_Development_Plan.md) |
| **Business Analyst** | Requirements → Data Structure Analysis |
| **System Architect** | [Development Approach Summary](architecture/Development_Approach_Summary.md) → [Architecture & Implementation Guide](architecture/Treasury_System_Architecture_and_Implementation_Guide.md) |
| **Backend Developer** | **[Local Development & Testing Guide](architecture/Local_Development_and_Testing_Guide.md)** → [Data to Architecture Mapping](architecture/Data_to_Architecture_Mapping_and_Development_Guide.md) |
| **Frontend Developer** | [Local Development & Testing Guide](architecture/Local_Development_and_Testing_Guide.md) Phase 4 → [Data to Architecture Mapping](architecture/Data_to_Architecture_Mapping_and_Development_Guide.md) (API Specs) |
| **QA Engineer** | [Local Development & Testing Guide](architecture/Local_Development_and_Testing_Guide.md) Section 4 → [Condensed Plan - Sprint 8](architecture/Condensed_Development_Plan.md) |

---

## 📝 Document Conventions

### Version Numbering
- Documents use semantic versioning: `MAJOR.MINOR.PATCH`
- Major = significant structural changes
- Minor = new sections or significant updates
- Patch = corrections and minor updates

### Status Indicators
| Status | Meaning |
|--------|---------|
| 🟢 **Final** | Approved and complete |
| 🟡 **Draft** | Under development |
| 🔴 **Deprecated** | Superseded by newer version |

### Current Document Status
| Document | Status |
|----------|--------|
| Development Approach Summary | 🟢 Final |
| Local Development & Testing Guide | 🟢 Final |
| Condensed Development Plan | 🟢 Final |
| **Development Plan Review & Concerns** | 🟢 Final |
| Data Structure Analysis | 🟢 Final |
| Architecture & Implementation Guide | 🟢 Final |
| Data to Architecture Mapping | 🟢 Final |
| Requirements (PDF/DOCX) | 🟢 Final |

---

## 🔄 Recent Updates

| Date | Document | Change |
|------|----------|--------|
| 2026-02-02 | **Development Plan Review & Concerns** | Created - comprehensive review with risks and recommendations |
| 2026-02-02 | docker-compose.local.yml | Created - local Docker infrastructure |
| 2026-02-02 | requirements.txt | Created - Python dependencies |
| 2026-02-02 | init_db.sql | Created - database initialization script |
| 2026-02-02 | .env.example | Created - environment template with BAHTNET manual mode |
| 2026-02-02 | Local Development & Testing Guide | Updated - Docker Desktop, WSL2, Windows setup |
| 2026-02-02 | Condensed Development Plan | Updated - BAHTNET as ISO20022 manual input |
| 2026-02-02 | Development Approach Summary | Created - local-first approach overview |
| 2026-02-02 | START_HERE.md | Created - navigation guide for new team members |
| 2026-02-02 | All | Project restructuring - migrated to new folder structure |

---

## 📞 Document Owners

| Area | Owner | Responsibility |
|------|-------|----------------|
| Requirements | Business Analyst | Business requirements accuracy |
| Architecture | System Architect | Technical design decisions |
| Data Model | Database Architect | Schema and data integrity |
| API Design | Backend Lead | API specifications |

---

*Last Updated: February 2026*
