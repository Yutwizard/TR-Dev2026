# Treasury Management System (TMS) - Thailand

**Thai Commercial Bank Treasury System: Local Bond and Money Market Operations**

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Status](https://img.shields.io/badge/status-development-orange)
![Last Updated](https://img.shields.io/badge/updated-February%202026-green)

---

## 📋 Project Overview

A comprehensive Treasury Management System designed for Thai Commercial Banks, covering:

| Product | Description |
|---------|-------------|
| **Interbank Lending/Borrowing** | THB placements and takings with Thai banks |
| **Repo/Reverse Repo** | Bilateral repos with BOT and private market repos |
| **Bond Trading** | T-Bills, T-Bonds, BOT Bonds, SOE Bonds, Corporate Bonds |

### Key Features

- ✅ **Real-time cash position monitoring** across BAHTNET settlement accounts
- ✅ **OTC trade capture** (~99% of market volume)
- ✅ **ThaiBMA 30-minute trade reporting** obligation
- ✅ **T+2 settlement cycle** compliance
- ✅ **Multi-layer segregation**: Front/Middle/Back Office + IT Admin
- ✅ **Four-eyes principle** for approvals
- ✅ **TFRS 9 / IFRS 9** accounting compliance
- ✅ **BOT regulatory reporting** ready

---

## 📁 Project Structure

```
TR Dev2026/
│
├── 📁 docs/                          # Documentation
│   ├── 📁 analysis/                  # Data & system analysis
│   ├── 📁 architecture/              # Architecture & design guides
│   ├── 📁 requirements/              # Original requirements documents
│   └── 📁 reference/                 # Reference materials
│
├── 📁 data/                          # Data files
│   ├── 📁 source/                    # Original source data (Excel, etc.)
│   ├── 📁 extracted/                 # Extracted/processed data
│   └── 📁 reference/                 # Reference lookup data
│
├── 📁 scripts/                       # Utility scripts
│
├── 📁 src/                           # Application source code
│   ├── 📁 backend/                   # Backend API (FastAPI)
│   ├── 📁 frontend/                  # Frontend UI (Next.js)
│   └── 📁 shared/                    # Shared utilities
│
├── 📁 tests/                         # Test files
│
├── 📁 output/                        # Generated outputs
│   ├── 📁 csv/                       # CSV exports
│   └── 📁 json/                      # JSON exports
│
├── README.md                         # This file
├── CHANGELOG.md                      # Version history
└── .gitignore                        # Git ignore rules
```

---

## 📖 Documentation Quick Links

### 🚀 Getting Started
**New to this project?** Start here:
1. [📍 **START_HERE.md**](START_HERE.md) - Navigation guide for all documents
2. [🎯 **Development Approach Summary**](docs/architecture/Development_Approach_Summary.md) - How we develop (local-first)
3. [🛠️ **Local Development Guide**](docs/architecture/Local_Development_and_Testing_Guide.md) - Set up your local environment
4. [⚠️ **Development Plan Review & Concerns**](docs/architecture/Development_Plan_Review_and_Concerns.md) - **MUST READ** Critical issues and recommendations

### Analysis Documents
- [Data Structure Analysis](docs/analysis/Data_Structure_Analysis.md) - Database schema analysis from Treasury System Database V2

### Architecture Documents
- [Architecture & Implementation Guide](docs/architecture/Treasury_System_Architecture_and_Implementation_Guide.md) - System architecture, module design, and implementation roadmap
- [Data to Architecture Mapping](docs/architecture/Data_to_Architecture_Mapping_and_Development_Guide.md) - Mapping data structures to system modules
- [Condensed Development Plan](docs/architecture/Condensed_Development_Plan.md) - 10-week sprint plan (local-first)

### Requirements
- [Treasury System Structure (PDF)](docs/requirements/Treasury_System_Structure.pdf) - Original requirements document

---

## 🏗️ Architecture Overview

The system follows a **Modular Monolith Architecture** for optimal balance between simplicity and scalability:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                                │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│   │Front Office │  │Middle Office│  │ Back Office │  │  IT Admin   │   │
│   │  (Trader)   │  │ (Risk/Com)  │  │(Settlement) │  │  (Config)   │   │
│   └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
├─────────────────────────────────────────────────────────────────────────┤
│                        APPLICATION LAYER                                 │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │  TRADE EXECUTION  │  SETTLEMENT  │  ACCOUNTING  │  REPORTING   │   │
│   └─────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────┤
│                           DATA LAYER                                     │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│   │   Master    │  │ Transaction │  │  Position   │  │   Audit     │   │
│   │    Data     │  │    Data     │  │    Data     │  │   Trail     │   │
│   └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js + TypeScript |
| **Backend** | FastAPI (Python) |
| **Database** | PostgreSQL / SQLite (dev) |
| **Deployment** | Docker |
| **Authentication** | JWT / OAuth2 |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11.x (recommended)
- Node.js 18+ (LTS)
- Docker Desktop (**REQUIRED** for database)
- Git

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd "TR Dev2026"

# Backend setup
cd src/backend
pip install -r requirements.txt
python main.py

# Frontend setup (in another terminal)
cd src/frontend
npm install
npm run dev
```

---

## 📊 Data Sources

| Source | Description | Location |
|--------|-------------|----------|
| Treasury System Database V2 | Master data model (76 sheets) | `data/source/` |
| Bank Codes | BOT official bank codes | `data/extracted/bank_code.txt` |
| Haircut Table | BOT standard haircut matrix | `data/extracted/haircut_table.txt` |

---

## 🔗 External Integrations

| System | Purpose | Integration Method |
|--------|---------|-------------------|
| **ThaiBMA** | Market data, trade reporting | API |
| **BAHTNET** | THB settlement | **Manual input** - ISO20022 pacs.008/pacs.009 messages |
| **TSD** | Bond settlement (DVP) | **Manual input** - Settlement instructions |
| **BOT Reporting** | Regulatory compliance | Batch/API |

---

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

## 👥 Team

| Role | Responsibility |
|------|----------------|
| **Business Analyst** | Requirements, BOT compliance |
| **System Architect** | Technical design |
| **Backend Developer** | API, business logic |
| **Frontend Developer** | UI/UX implementation |
| **QA Engineer** | Testing, validation |

---

## 📄 License

Internal use only - Thai Commercial Bank Treasury Operations

---

*Last Updated: February 2026*
