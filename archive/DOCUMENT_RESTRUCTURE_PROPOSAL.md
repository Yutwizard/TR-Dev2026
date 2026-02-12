# Documentation Restructure Proposal

**Date:** February 5, 2026  
**Purpose:** Streamline documentation, eliminate redundancy, and establish clear hierarchy

---

## 📊 Current State Analysis

### Current Document Count: 14+ documents

| Category | Documents | Issues |
|----------|-----------|--------|
| **Session Summaries** | 3 files | Combined but individual still exist (deleted now) |
| **Architecture** | 6 files | Overlapping content, some outdated |
| **Design/Process** | 5 files | Good but could be better organized |
| **Analysis/Review** | 2 files | Temporary/analysis docs |

### Problems Identified

1. **Redundancy:** Multiple documents describe same processes
2. **Outdated Content:** Condensed_Development_Plan uses old naming conventions
3. **Unclear Hierarchy:** Hard to know which document to read first
4. **Maintenance Overhead:** Too many files to keep synchronized

---

## 🎯 Proposed New Structure

### Goal: Reduce to 6-8 core documents

```
docs/
├── README.md                              # Entry point - quick links
├── PROJECT_SUMMARY.md                     # Combined Feb 2-3 work (CONSOLIDATED)
│
├── 01-DESIGN/
│   ├── SYSTEM_DESIGN.md                   # MERGE: Detailed_Design_Input + Architecture
│   └── FIELD_REFERENCE.md                 # Field Update Matrix (RENAME)
│
├── 02-PROCESSES/
│   ├── TRANSACTION_WORKFLOWS.md           # Transaction Process Guide (RENAME)
│   └── PRE_TRANSACTION_SETUP.md           # Pre-Transaction Setup Guide (RENAME)
│
├── 03-IMPLEMENTATION/
│   ├── DEVELOPMENT_GUIDE.md               # MERGE: Data_to_Architecture + Condensed_Plan
│   └── SETUP_INSTRUCTIONS.md              # Local Dev Guide (UPDATE)
│
├── 04-OPERATIONS/
│   ├── DAILY_OPERATIONS.md                # Daily batch procedures
│   └── STAKEHOLDER_CHECKLIST.md           # Review checklist
│
└── archive/                               # MOVE: Old/outdated documents
    ├── Treasury_System_Architecture_and_Implementation_Guide.md
    ├── Development_Approach_Summary.md
    ├── Development_Plan_Review_and_Concerns.md
    └── analysis/
```

---

## 📋 Detailed Restructure Plan

### 1. MERGE: Create `SYSTEM_DESIGN.md`

**Merge These:**
- `Treasury_System_Detailed_Design_Input.md` (65KB) - Main content
- `Treasury_System_Architecture_and_Implementation_Guide.md` (35KB) - High-level context
- `ARCHITECTURE_ALIGNMENT_REVIEW.md` (8KB) - Alignment notes

**Structure:**
```markdown
# System Design

## 1. Executive Summary (from Architecture)
## 2. Architecture Decisions (from Architecture)
## 3. Team Responsibilities (from Detailed_Design)
## 4. Database Design (from Detailed_Design)
## 5. Transaction Lifecycles (from Detailed_Design)
## 6. Market Data Management (from Detailed_Design)
## Appendix A: Table Structures
## Appendix B: Regulatory Mapping
```

**Benefits:**
- Single authoritative design document
- Eliminates cross-referencing between design docs
- Easier to maintain

---

### 2. MERGE: Create `DEVELOPMENT_GUIDE.md`

**Merge These:**
- `Data_to_Architecture_Mapping_and_Development_Guide.md` (25KB) - SQL schemas, phases
- `Condensed_Development_Plan.md` (20KB) - 10-week timeline

**Structure:**
```markdown
# Development Guide

## 1. Technology Stack
## 2. Database Schema (aligned with SYSTEM_DESIGN)
## 3. API Specifications
## 4. Development Phases
### Phase 1: Foundation (Week 1)
### Phase 2: Bond Trading (Week 2)
### Phase 3: Interbank (Week 3-4)
### Phase 4: Repo (Week 5-6)
### Phase 5: Testing (Week 7-8)
### Phase 6: Deployment (Week 9-10)
## 5. Testing Strategy
## Appendix: SQL DDL Scripts
```

**Benefits:**
- Single implementation reference
- Timeline + technical details together
- Consistent naming throughout

---

### 3. UPDATE: `SETUP_INSTRUCTIONS.md`

**Source:** `Local_Development_and_Testing_Guide.md`

**Updates Required:**
- [ ] Verify all Docker commands work
- [ ] Update paths to match current structure
- [ ] Add troubleshooting section
- [ ] Test on clean machine

**Structure:**
```markdown
# Setup Instructions

## 1. Prerequisites
## 2. Quick Start (5 minutes)
## 3. Full Setup
### Database
### Backend
### Frontend
## 4. Verification
## 5. Troubleshooting
```

---

### 4. RENAME (Keep Content, Better Names)

| Current Name | New Name | Reason |
|--------------|----------|--------|
| `Field_Update_Matrix.md` | `FIELD_REFERENCE.md` | Clearer purpose |
| `TRANSACTION_PROCESS_GUIDE.md` | `TRANSACTION_WORKFLOWS.md` | Better describes content |
| `PRE_TRANSACTION_SETUP_GUIDE.md` | `PRE_TRANSACTION_SETUP.md` | Shorter, clear |
| `STAKEHOLDER_REVIEW_CHECKLIST.md` | `STAKEHOLDER_CHECKLIST.md` | Shorter |

---

### 5. MOVE TO ARCHIVE

**Documents to Archive:**

| Document | Reason | Status |
|----------|--------|--------|
| `Treasury_System_Architecture_and_Implementation_Guide.md` | Merged into SYSTEM_DESIGN | Archive |
| `Development_Approach_Summary.md` | Conceptual only, not actionable | Archive |
| `Development_Plan_Review_and_Concerns.md` | Static review, risks tracked elsewhere | Archive |
| `ARCHITECTURE_DOCUMENT_ANALYSIS.md` | Temporary analysis complete | Archive |
| `ARCHITECTURE_ALIGNMENT_REVIEW.md` | Issues resolved | Archive |
| `analysis/Data_Structure_Analysis.md` | Source data extracted | Archive |

---

### 6. CREATE: `README.md` (Entry Point)

**Purpose:** Single entry point for all documentation

**Content:**
```markdown
# Treasury Management System Documentation

## Quick Links

### For Management/Overview
- [Project Summary](PROJECT_SUMMARY.md) - All work completed (Feb 2-3)

### For Design Understanding
- [System Design](01-DESIGN/SYSTEM_DESIGN.md) - Architecture & database
- [Field Reference](01-DESIGN/FIELD_REFERENCE.md) - Field definitions

### For Operations
- [Transaction Workflows](02-PROCESSES/TRANSACTION_WORKFLOWS.md) - Step-by-step
- [Pre-Transaction Setup](02-PROCESSES/PRE_TRANSACTION_SETUP.md) - Onboarding
- [Daily Operations](04-OPERATIONS/DAILY_OPERATIONS.md) - Batch procedures

### For Development
- [Development Guide](03-IMPLEMENTATION/DEVELOPMENT_GUIDE.md) - Build the system
- [Setup Instructions](03-IMPLEMENTATION/SETUP_INSTRUCTIONS.md) - Local setup

### For Review
- [Stakeholder Checklist](04-OPERATIONS/STAKEHOLDER_CHECKLIST.md) - Sign-off

---

## Document Status

| Document | Status | Last Updated |
|----------|--------|--------------|
| Project Summary | ✅ Current | Feb 5, 2026 |
| System Design | ✅ Current | Feb 5, 2026 |
| ... | ... | ... |
```

---

### 7. CREATE: `DAILY_OPERATIONS.md`

**Extract From:** `TRANSACTION_WORKFLOWS.md` (Section 0.3)

**Purpose:** Dedicated operations manual for Back Office

**Content:**
```markdown
# Daily Operations Manual

## Pre-Market (08:00 - 09:00)
- [ ] System health check
- [ ] Previous day reconciliation

## Market Hours (09:00 - 17:00)
- Support trading operations

## Post-Market (17:00 - 19:30)
### Normal Day
- [ ] 17:00: Download ThaiBMA
- [ ] 17:15: Validate prices
- [ ] 17:30: Import prices
- [ ] 18:00: Batch starts
- [ ] 19:30: Complete

### Month-End Day
- [ ] 17:30-18:00: Monitor ThaiBMA
- [ ] 18:15: Import prices
- [ ] 19:50: Complete

## Exception Handling
- Stale prices
- Missing data
- Batch failures
```

---

## 📊 Before vs After Comparison

### Before (Current)
```
docs/
├── SESSION_SUMMARY_2026-02-02.md          ❌ DELETE (combined)
├── SESSION_SUMMARY_2026-02-03.md          ❌ DELETE (combined)
├── PROJECT_SESSION_SUMMARY.md             → RENAME to PROJECT_SUMMARY.md
├── Treasury_System_Detailed_Design_Input.md  → MERGE into SYSTEM_DESIGN
├── Field_Update_Matrix.md                 → RENAME to FIELD_REFERENCE.md
├── TRANSACTION_PROCESS_GUIDE.md           → RENAME to TRANSACTION_WORKFLOWS.md
├── PRE_TRANSACTION_SETUP_GUIDE.md         → RENAME to PRE_TRANSACTION_SETUP.md
├── STAKEHOLDER_REVIEW_CHECKLIST.md        → RENAME to STAKEHOLDER_CHECKLIST.md
├── ARCHITECTURE_ALIGNMENT_REVIEW.md       ❌ ARCHIVE
├── ARCHITECTURE_DOCUMENT_ANALYSIS.md      ❌ ARCHIVE
├── architecture/
│   ├── Treasury_System_Architecture_and_Implementation_Guide.md  ❌ MERGE
│   ├── Data_to_Architecture_Mapping_and_Development_Guide.md     → MERGE into DEVELOPMENT_GUIDE
│   ├── Condensed_Development_Plan.md      → MERGE into DEVELOPMENT_GUIDE
│   ├── Development_Approach_Summary.md    ❌ ARCHIVE
│   ├── Development_Plan_Review_and_Concerns.md  ❌ ARCHIVE
│   └── Local_Development_and_Testing_Guide.md   → UPDATE to SETUP_INSTRUCTIONS
└── analysis/
    └── Data_Structure_Analysis.md         ❌ ARCHIVE (source used)
```

### After (Proposed)
```
docs/
├── README.md                              ✅ NEW - Entry point
├── PROJECT_SUMMARY.md                     ✅ KEEP (renamed)
│
├── 01-DESIGN/
│   ├── SYSTEM_DESIGN.md                   ✅ MERGED
│   └── FIELD_REFERENCE.md                 ✅ RENAMED
│
├── 02-PROCESSES/
│   ├── TRANSACTION_WORKFLOWS.md           ✅ RENAMED
│   └── PRE_TRANSACTION_SETUP.md           ✅ RENAMED
│
├── 03-IMPLEMENTATION/
│   ├── DEVELOPMENT_GUIDE.md               ✅ MERGED
│   └── SETUP_INSTRUCTIONS.md              ✅ UPDATED
│
├── 04-OPERATIONS/
│   ├── DAILY_OPERATIONS.md                ✅ NEW (extracted)
│   └── STAKEHOLDER_CHECKLIST.md           ✅ RENAMED
│
└── archive/                               ✅ NEW FOLDER
    ├── [All old documents with _ARCHIVED suffix]
```

**Result:** 14+ documents → 8 core documents

---

## ✅ Benefits of New Structure

### 1. Clear Hierarchy
- Numbered folders (01-, 02-) show reading order
- README.md provides navigation
- No confusion about where to start

### 2. Reduced Maintenance
- Fewer documents to update
- Merged content eliminates duplication
- Archive folder preserves history without clutter

### 3. Better Naming
- Consistent naming convention
- Clear purpose from filename
- Shorter names (easier to reference)

### 4. Role-Based Access
| Role | Primary Documents |
|------|-------------------|
| Management | README, PROJECT_SUMMARY, STAKEHOLDER_CHECKLIST |
| Developers | DEVELOPMENT_GUIDE, SETUP_INSTRUCTIONS |
| Operations | DAILY_OPERATIONS, TRANSACTION_WORKFLOWS |
| Analysts | SYSTEM_DESIGN, FIELD_REFERENCE |

---

## 🚀 Implementation Steps

### Phase 1: Create New Documents (Week 1)
- [ ] Create folder structure
- [ ] MERGE: SYSTEM_DESIGN.md
- [ ] MERGE: DEVELOPMENT_GUIDE.md
- [ ] UPDATE: SETUP_INSTRUCTIONS.md
- [ ] CREATE: README.md
- [ ] CREATE: DAILY_OPERATIONS.md

### Phase 2: Rename & Move (Week 1)
- [ ] RENAME: Field_Update_Matrix → FIELD_REFERENCE
- [ ] RENAME: TRANSACTION_PROCESS_GUIDE → TRANSACTION_WORKFLOWS
- [ ] RENAME: PRE_TRANSACTION_SETUP_GUIDE → PRE_TRANSACTION_SETUP
- [ ] RENAME: STAKEHOLDER_REVIEW_CHECKLIST → STAKEHOLDER_CHECKLIST
- [ ] RENAME: PROJECT_SESSION_SUMMARY → PROJECT_SUMMARY

### Phase 3: Archive Old Documents (Week 1)
- [ ] Create archive/ folder
- [ ] Move old docs with _ARCHIVED suffix
- [ ] Add note in each: "ARCHIVED - See [replacement]"

### Phase 4: Update Cross-References (Week 2)
- [ ] Update all internal links
- [ ] Update git references
- [ ] Test all document links

### Phase 5: Verify & Cleanup (Week 2)
- [ ] Verify no broken links
- [ ] Verify all content preserved
- [ ] Delete archived documents from root
- [ ] Update .gitignore if needed

---

## 🔄 Migration Checklist

### Content Preservation
- [ ] All table structures preserved
- [ ] All process workflows preserved
- [ ] All field definitions preserved
- [ ] All SQL schemas preserved
- [ ] All team responsibilities preserved

### Quality Checks
- [ ] Naming convention consistent (snake_case)
- [ ] Limit types consistent (PLACEMENT_LIMIT, REPO_LIMIT)
- [ ] No references to AGGREGATE limit
- [ ] ThaiBMA timing correct (normal vs month-end)
- [ ] Security Master ownership = Back Office

### Cross-References
- [ ] All links updated
- [ ] No broken references
- [ ] README points to correct locations

---

## 📋 Document Lifecycle Going Forward

### When to Update
| Trigger | Action |
|---------|--------|
| Schema change | Update SYSTEM_DESIGN.md + DEVELOPMENT_GUIDE.md |
| Process change | Update TRANSACTION_WORKFLOWS.md |
| Team change | Update SYSTEM_DESIGN.md (team section) |
| New feature | Update DEVELOPMENT_GUIDE.md (new phase) |
| Bug found in docs | Update relevant doc immediately |

### Review Schedule
| Document | Review Frequency |
|----------|-----------------|
| SYSTEM_DESIGN.md | Monthly or on schema change |
| DEVELOPMENT_GUIDE.md | Bi-weekly during active development |
| DAILY_OPERATIONS.md | Monthly with Back Office |
| TRANSACTION_WORKFLOWS.md | Quarterly |

---

**Proposal Created:** February 5, 2026  
**Proposed Implementation:** Week of Feb 8-12, 2026  
**Expected Result:** 50% reduction in document count, clearer hierarchy

---

## 🤔 Questions to Resolve

1. **Should we keep old documents in git history or move to archive folder?**
   - Recommendation: Move to archive folder (easier to find)

2. **Should we update Condensed_Development_Plan or merge it?**
   - Recommendation: Merge into DEVELOPMENT_GUIDE.md

3. **Should Setup Instructions be in docs/ or src/backend/?**
   - Recommendation: docs/03-IMPLEMENTATION/ (with code)

4. **How do we handle ongoing updates during restructure?**
   - Recommendation: Freeze docs during restructure, or implement in branch

---

*Ready for review and approval to proceed*
