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
| [Architecture & Implementation Guide](architecture/Treasury_System_Architecture_and_Implementation_Guide.md) | Complete system architecture including modular monolith design, module specifications, technology stack, and implementation roadmap | Feb 2026 |
| [Data to Architecture Mapping](architecture/Data_to_Architecture_Mapping_and_Development_Guide.md) | Detailed mapping of database tables to system modules, SQL schemas, and development guide | Feb 2026 |

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

### By Topic

| Topic | Relevant Documents |
|-------|-------------------|
| **Database Schema** | Data Structure Analysis |
| **System Architecture** | Architecture & Implementation Guide |
| **Module Design** | Data to Architecture Mapping |
| **BOT Compliance** | Data Structure Analysis (Section 7-8) |
| **TFRS 9 Implementation** | Data Structure Analysis (Section 8.1) |
| **API Design** | Architecture Guide (API Specifications) |
| **Settlement Flow** | Architecture Guide (Settlement Module) |

### By Product

| Product | Relevant Sections |
|---------|------------------|
| **Interbank Lending/Borrowing** | Data Structure (3.1), Architecture (Trade Execution) |
| **Repo/Reverse Repo** | Data Structure (3.2), Architecture (Settlement) |
| **Bond Trading** | Data Structure (3.3), Architecture (Trade Execution) |

### By Role

| Role | Start Here |
|------|-----------|
| **Business Analyst** | Requirements → Data Structure Analysis |
| **System Architect** | Architecture & Implementation Guide |
| **Backend Developer** | Data to Architecture Mapping |
| **Frontend Developer** | Architecture Guide (UI Specifications) |
| **QA Engineer** | Data Structure (Validation Rules) |

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
| Data Structure Analysis | 🟢 Final |
| Architecture & Implementation Guide | 🟢 Final |
| Data to Architecture Mapping | 🟢 Final |
| Requirements (PDF/DOCX) | 🟢 Final |

---

## 🔄 Recent Updates

| Date | Document | Change |
|------|----------|--------|
| 2026-02-02 | All | Project restructuring - migrated to new folder structure |
| 2026-02-02 | index.md | Created documentation index |

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
