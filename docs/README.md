# Treasury Management System Documentation

**Last Updated:** February 5, 2026

---

## 📋 Quick Links

### For Management / Project Overview
| Document | Purpose |
|----------|---------|
| [Project Summary](./PROJECT_SUMMARY.md) | Complete work summary (Feb 2-5, 2026) |
| [Stakeholder Checklist](./04-OPERATIONS/STAKEHOLDER_CHECKLIST.md) | Review and sign-off |

### For Design Understanding
| Document | Purpose |
|----------|---------|
| [System Design](./01-DESIGN/SYSTEM_DESIGN.md) | Architecture, database, team responsibilities |
| [Field Reference](./01-DESIGN/FIELD_REFERENCE.md) | Field definitions and update rules |

### For Operations
| Document | Purpose |
|----------|---------|
| [Transaction Workflows](./02-PROCESSES/TRANSACTION_WORKFLOWS.md) | Step-by-step transaction processes |
| [Field Workflow Mapping](./02-PROCESSES/FIELD_WORKFLOW_MAPPING.md) | Database fields mapped to workflow steps |
| [Transaction Flow Diagrams](./02-PROCESSES/TRANSACTION_FLOW_DIAGRAMS.md) | Visual process flow diagrams |
| [📊 Transaction Flow Portal](./02-PROCESSES/transaction_flow.html) | **Interactive** visual portal (open in browser) |
| [Pre-Transaction Setup](./02-PROCESSES/PRE_TRANSACTION_SETUP.md) | Client onboarding, bond setup |
| [Daily Operations](./04-OPERATIONS/DAILY_OPERATIONS.md) | Daily batch procedures |

### For Development
| Document | Purpose |
|----------|---------|
| [Development Guide](./03-IMPLEMENTATION/DEVELOPMENT_GUIDE.md) | Build the system (10-week plan) |
| [Setup Instructions](./03-IMPLEMENTATION/SETUP_INSTRUCTIONS.md) | Local environment setup |

---

## 📁 Document Structure

```
docs/
├── README.md                    ← You are here
├── PROJECT_SUMMARY.md           ← Combined project summary
│
├── 01-DESIGN/                   ← System design documents
│   ├── SYSTEM_DESIGN.md         ← Architecture & database
│   └── FIELD_REFERENCE.md       ← Field definitions
│
├── 02-PROCESSES/                ← Business process docs
│   ├── TRANSACTION_WORKFLOWS.md ← Transaction steps
│   ├── FIELD_WORKFLOW_MAPPING.md ← Field-to-workflow mapping
│   ├── TRANSACTION_FLOW_DIAGRAMS.md ← Visual flow diagrams
│   ├── transaction_flow.html      ← Interactive portal
│   └── PRE_TRANSACTION_SETUP.md ← Setup procedures
│
├── 03-IMPLEMENTATION/           ← Developer docs
│   ├── DEVELOPMENT_GUIDE.md     ← Build guide
│   └── SETUP_INSTRUCTIONS.md    ← Environment setup
│
├── 04-OPERATIONS/               ← Operations docs
│   ├── DAILY_OPERATIONS.md      ← Daily procedures
│   └── STAKEHOLDER_CHECKLIST.md ← Review checklist
│
└── archive/                     ← Archived documents
```

---

## 📊 Document Status

| Document | Status | Last Updated |
|----------|--------|--------------|
| System Design | ✅ Current | Feb 5, 2026 |
| Field Reference | ✅ Current | Feb 5, 2026 |
| Transaction Workflows | ✅ Current | Feb 5, 2026 |
| Field Workflow Mapping | ✅ Current | Feb 5, 2026 |
| Pre-Transaction Setup | ✅ Current | Feb 5, 2026 |
| Development Guide | ✅ Current | Feb 5, 2026 |
| Setup Instructions | ⚠️ Verify | Feb 5, 2026 |
| Daily Operations | ✅ Current | Feb 5, 2026 |
| Stakeholder Checklist | ✅ Current | Feb 5, 2026 |

---

## 🚀 Quick Start

### For Developers
```bash
# 1. Read Development Guide
cat 03-IMPLEMENTATION/DEVELOPMENT_GUIDE.md

# 2. Follow Setup Instructions
cat 03-IMPLEMENTATION/SETUP_INSTRUCTIONS.md

# 3. Start coding!
```

### For Operations
```bash
# 1. Read Daily Operations
cat 04-OPERATIONS/DAILY_OPERATIONS.md

# 2. Review Transaction Workflows
cat 02-PROCESSES/TRANSACTION_WORKFLOWS.md
```

### For Management
```bash
# Read Project Summary
cat PROJECT_SUMMARY.md
```

---

## 📞 Support

| Question Type | Contact |
|---------------|---------|
| System Design | Architecture Team |
| Process Questions | Business Analyst |
| Technical Issues | Development Team |
| Operations | Back Office Lead |

---

## 📝 Notes

- All documents use `snake_case` naming convention
- Database design is authoritative source (from Treasury_System_Database_V2_Internal.xlsx)
- Limits: `PLACEMENT_LIMIT`, `REPO_LIMIT` (no aggregate limit)
- Security Master: Back Office ownership
- ThaiBMA import: 17:00 (normal), 17:30-18:00 (month-end)

---

**Document End**
