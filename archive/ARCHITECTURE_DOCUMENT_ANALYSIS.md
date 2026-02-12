# Architecture Documents Analysis & Comparison

**Analysis Date:** February 5, 2026  
**Purpose:** Compare all architecture documents, identify relationships, and determine authoritative source

---

## 📊 Document Inventory

| # | Document | Size | Last Modified | Primary Purpose |
|---|----------|------|---------------|-----------------|
| 1 | `Treasury_System_Architecture_and_Implementation_Guide.md` | ~35KB | Feb 3 (indirect) | High-level architecture decisions |
| 2 | `Data_to_Architecture_Mapping_and_Development_Guide.md` | ~25KB | **Feb 5** | SQL schema, development phases |
| 3 | `Condensed_Development_Plan.md` | ~20KB | Feb 2 | 10-week sprint plan |
| 4 | `Development_Plan_Review_and_Concerns.md` | ~18KB | Feb 2 | Risk analysis, gaps |
| 5 | `Development_Approach_Summary.md` | ~10KB | Feb 2 | Local-first approach |
| 6 | `Local_Development_and_Testing_Guide.md` | ~12KB | Feb 2 | Setup instructions |

---

## 🔄 Document Relationships

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ARCHITECTURE DOCUMENT ECOSYSTEM                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Treasury_System_Architecture_and_Implementation_Guide.md           │    │
│  │  ├── High-level architecture (Monolith vs Microservices)            │    │
│  │  ├── Technology stack recommendation                                │    │
│  │  └── 6-month roadmap (phases)                                       │    │
│  │       ↓                                                             │    │
│  │  REFERENCES → Data_to_Architecture_Mapping (detailed SQL)           │    │
│  │  REFERENCES → Condensed_Development_Plan (10-week timeline)         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Data_to_Architecture_Mapping_and_Development_Guide.md  ◄── MOST    │    │
│  │  ├── SQL schema definitions (NOW ALIGNED with database design)      │    │
│  │  ├── Table-to-module mapping                                        │    │
│  │  ├── Development phase details (Weeks 1-10)                         │    │
│  │  └── API specifications                                             │    │
│  │       ↑                                                             │    │
│  │  REQUIRES ALIGNMENT with Treasury_System_Detailed_Design_Input.md   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Condensed_Development_Plan.md                                      │    │
│  │  ├── 10-week sprint breakdown                                       │    │
│  │  ├── Daily tasks per sprint                                         │    │
│  │  └── Deliverables per sprint                                        │    │
│  │       ⚠️ PARTIALLY OUTDATED (based on older schema)                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Development_Plan_Review_and_Concerns.md                            │    │
│  │  ├── Risk assessment                                                │    │
│  │  ├── Gap analysis                                                   │    │
│  │  └── Recommendations                                                │    │
│  │       ⚠️ STATIC REVIEW (not updated after fixes)                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Development_Approach_Summary.md                                    │    │
│  │  ├── Local-first justification                                      │    │
│  │  └── Timeline comparison                                            │    │
│  │       ✅ CONCEPTUAL (still valid)                                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Local_Development_and_Testing_Guide.md                             │    │
│  │  ├── Docker setup commands                                          │    │
│  │  ├── Environment configuration                                      │    │
│  │  └── Testing procedures                                             │    │
│  │       ⚠️ NEEDS VERIFICATION (commands may need updates)              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ✅ Most Current Document: Analysis

### Winner: `Data_to_Architecture_Mapping_and_Development_Guide.md`

**Reasons:**
1. **Most Recently Updated:** Feb 5, 2026 (yesterday)
2. **Aligned with Database:** SQL schema now matches `Treasury_System_Detailed_Design_Input.md`
3. **Contains Implementation Details:** Actual SQL, API specs, development phases
4. **Actively Maintained:** Recent commit fixed naming conventions

---

## ⚠️ Document Issues & Outdated Content

### 1. `Condensed_Development_Plan.md` - PARTIALLY OUTDATED

| Aspect | Status | Issue |
|--------|--------|-------|
| Sprint timeline | ⚠️ Check | May not reflect current schema |
| Table references | ❌ Outdated | Uses old field names (PascalCase) |
| Limit types | ✅ OK | References PLACEMENT_LIMIT, REPO_LIMIT |

**Recommendation:** Update table/field references to match current schema

---

### 2. `Development_Plan_Review_and_Concerns.md` - STATIC SNAPSHOT

| Aspect | Status | Issue |
|--------|--------|-------|
| Risk assessment | ✅ Valid | High-level risks still applicable |
| Gap analysis | ⚠️ Partial | Some gaps may have been addressed |
| Missing infrastructure | ⚠️ Check | May have been created since |

**Recommendation:** Add "Update Log" section tracking addressed concerns

---

### 3. `Local_Development_and_Testing_Guide.md` - NEEDS VERIFICATION

| Aspect | Status | Issue |
|--------|--------|-------|
| Docker commands | ⚠️ Verify | May need path updates |
| Environment setup | ⚠️ Verify | Check if `.env` format changed |
| Test procedures | ✅ Valid | General approach still correct |

**Recommendation:** Test all commands and update if needed

---

### 4. `Treasury_System_Architecture_and_Implementation_Guide.md` - HIGH-LEVEL ONLY

| Aspect | Status | Issue |
|--------|--------|-------|
| Architecture decision | ✅ Valid | Monolith choice still stands |
| Technology stack | ✅ Valid | FastAPI + PostgreSQL + React |
| Timeline | ⚠️ Superseded | Use Condensed_Development_Plan instead |

**Recommendation:** Add note referring to Data_to_Architecture_Mapping for implementation details

---

## 📋 Detailed Comparison Matrix

### SQL Schema Coverage

| Table | Data_to_Architecture | Detailed_Design_Input | Status |
|-------|---------------------|----------------------|--------|
| `bond_trades` | ✅ SQL provided | ✅ Full structure | **ALIGNED** |
| `repo_trades` | ✅ SQL provided | ✅ Full structure | **ALIGNED** |
| `limit_utilization` | ✅ SQL provided | ✅ Full structure | **ALIGNED** |
| `collateral_positions` | ✅ SQL provided | ✅ Full structure | **ALIGNED** |
| `interbank_deals` | ⚠️ Mentioned | ✅ Full structure | **NEEDS SQL** |
| `entity_counterparty` | ❌ Missing | ✅ Full structure | **NEEDS ADDITION** |

### Naming Convention

| Document | Convention | Status |
|----------|-----------|--------|
| Data_to_Architecture (AFTER Feb 5) | `snake_case` | ✅ **CURRENT** |
| Detailed_Design_Input | `snake_case` | ✅ **CURRENT** |
| Condensed_Development_Plan | `PascalCase` | ⚠️ **OUTDATED** |

### Limit Types

| Document | Limit Types | Status |
|----------|-------------|--------|
| Data_to_Architecture (AFTER Feb 5) | `PLACEMENT_LIMIT`, `REPO_LIMIT` | ✅ **CURRENT** |
| Detailed_Design_Input | `PLACEMENT_LIMIT`, `REPO_LIMIT` | ✅ **CURRENT** |
| Other docs | May have `AGGREGATE` | ⚠️ **CHECK** |

---

## 🎯 Recommended Document Hierarchy

### For Implementation
```
1. Data_to_Architecture_Mapping_and_Development_Guide.md (PRIMARY)
   ├── SQL schemas (verified current)
   ├── API specifications
   └── Development phases

2. Treasury_System_Detailed_Design_Input.md (REFERENCE)
   ├── Team responsibilities
   ├── Field definitions
   └── Process workflows

3. Condensed_Development_Plan.md (TIMELINE)
   └── Sprint schedules (verify table refs)
```

### For Understanding Context
```
1. Treasury_System_Architecture_and_Implementation_Guide.md
   └── Why we chose modular monolith

2. Development_Approach_Summary.md
   └── Why local-first approach

3. Development_Plan_Review_and_Concerns.md
   └── What risks to watch for
```

### For Setup
```
1. Local_Development_and_Testing_Guide.md (VERIFY FIRST)
   └── Docker and environment setup
```

---

## 🔄 Recommended Actions

### Immediate (This Week)
- [ ] Add disclaimer to `Condensed_Development_Plan.md` pointing to current schema
- [ ] Verify `Local_Development_and_Testing_Guide.md` commands still work
- [ ] Add "Last Updated" dates to all architecture documents

### Short Term (Next Sprint)
- [ ] Update `Condensed_Development_Plan.md` table/field references
- [ ] Add missing `entity_counterparty` to `Data_to_Architecture_Mapping`
- [ ] Create single "Architecture Quick Reference" consolidating all docs

### Long Term (Ongoing)
- [ ] Establish document ownership (who updates what)
- [ ] Create update checklist when schema changes
- [ ] Set up automated link checking between documents

---

## 📊 Summary Statistics

| Category | Count |
|----------|-------|
| **Total Architecture Docs** | 6 |
| **Currently Aligned** | 2 (Data_to_Architecture, Detailed_Design) |
| **Needs Update** | 3 (Condensed_Plan, Review, Local_Guide) |
| **Conceptual Only** | 1 (High-level Architecture) |
| **Most Authoritative for SQL** | Data_to_Architecture_Mapping |
| **Most Authoritative for Process** | Treasury_System_Detailed_Design_Input |

---

## 🔗 Cross-Reference Verification

| Reference From | Points To | Status |
|----------------|-----------|--------|
| Data_to_Architecture | Detailed_Design_Input | ✅ Valid |
| Condensed_Development_Plan | Data_to_Architecture | ⚠️ May be outdated |
| All docs | Treasury_System_Database_V2_Internal.xlsx | ✅ Source of truth |

---

**Conclusion:** 
- Use **`Data_to_Architecture_Mapping_and_Development_Guide.md`** for implementation (SQL, APIs)
- Use **`Treasury_System_Detailed_Design_Input.md`** for business process understanding
- Update **`Condensed_Development_Plan.md`** and **`Local_Development_and_Testing_Guide.md`** before use
- Treat **`Development_Plan_Review_and_Concerns.md`** as historical risk assessment

**Analysis Completed:** February 5, 2026
