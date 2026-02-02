# START HERE - Treasury Management System

**New to this project? Start with this guide.**

---

## Quick Navigation

### For Beginners: Follow This Order

```
1. START_HERE.md (this file) - Overview
        ↓
2. README.md - Project overview
        ↓
3. docs/architecture/Development_Approach_Summary.md
        ↓
4. docs/architecture/Local_Development_and_Testing_Guide.md
        ↓
5. Start coding!
```

---

## Which Document Should I Read?

### I want to understand the project...

| If you want to... | Read this document | Location |
|-------------------|-------------------|----------|
| **Get a quick overview** | `README.md` | Root folder |
| **Understand the approach** | `Development_Approach_Summary.md` | `docs/architecture/` |
| **See the timeline** | `Condensed_Development_Plan.md` | `docs/architecture/` |
| **Understand data model** | `Data_Structure_Analysis.md` | `docs/analysis/` |
| **See architecture details** | `Treasury_System_Architecture_and_Implementation_Guide.md` | `docs/architecture/` |

### I want to start developing...

| If you want to... | Read this document | Location |
|-------------------|-------------------|----------|
| **Set up local environment** | `Local_Development_and_Testing_Guide.md` | `docs/architecture/` |
| **Understand the mapping** | `Data_to_Architecture_Mapping_and_Development_Guide.md` | `docs/architecture/` |
| **See all documents** | `docs/index.md` | `docs/` |

---

## Recommended Reading Order by Role

### For Project Manager / Business Analyst

```
1. README.md
2. CHANGELOG.md
3. docs/requirements/Treasury_System_Structure.pdf
4. docs/analysis/Data_Structure_Analysis.md
```

### For System Architect

```
1. README.md
2. docs/analysis/Data_Structure_Analysis.md
3. docs/architecture/Treasury_System_Architecture_and_Implementation_Guide.md
4. docs/architecture/Data_to_Architecture_Mapping_and_Development_Guide.md
```

### For Backend Developer

```
1. README.md
2. docs/architecture/Development_Approach_Summary.md
3. docs/architecture/Local_Development_and_Testing_Guide.md ← START HERE
4. docs/architecture/Data_to_Architecture_Mapping_and_Development_Guide.md
5. data/extracted/all_tables_v4.txt (for schema reference)
```

### For Frontend Developer

```
1. README.md
2. docs/architecture/Development_Approach_Summary.md
3. docs/architecture/Local_Development_and_Testing_Guide.md
4. Review API specs in docs/architecture/Data_to_Architecture_Mapping_and_Development_Guide.md
```

### For QA Engineer

```
1. README.md
2. docs/architecture/Development_Approach_Summary.md
3. docs/architecture/Local_Development_and_Testing_Guide.md ← Testing focus
4. data/source/Treasury_System_Database_V2_Internal.xlsx (test data)
```

---

## Quick Start (For Developers)

### Step 1: Read the Approach (5 minutes)

→ Open `docs/architecture/Development_Approach_Summary.md`

This explains:
- **Local-first development** (test everything locally before deployment)
- **10-week timeline**
- **What to build first**

### Step 2: Set Up Local Environment (30 minutes)

→ Open `docs/architecture/Local_Development_and_Testing_Guide.md`

Follow:
- Phase 1: Install prerequisites
- Phase 2: Set up backend
- Phase 3: Set up frontend
- Phase 4: Import test data

### Step 3: Start Coding

→ Refer to `docs/architecture/Data_to_Architecture_Mapping_and_Development_Guide.md` for:
- Database schemas
- API specifications
- Code examples

---

## Document Index (All Documents)

### Root Level
| File | Purpose |
|------|---------|
| `README.md` | Project overview, quick start |
| `CHANGELOG.md` | Version history |
| `START_HERE.md` | This file - navigation guide |
| `.gitignore` | Git ignore rules |

### docs/ Folder
| Folder | Contents |
|--------|----------|
| `docs/analysis/` | Data structure analysis |
| `docs/architecture/` | System design, development guides |
| `docs/requirements/` | Original business requirements |
| `docs/reference/` | Reference materials |
| `docs/index.md` | Documentation navigation |

### data/ Folder
| Folder | Contents |
|--------|----------|
| `data/source/` | Excel data model (source of truth) |
| `data/extracted/` | Extracted text files from Excel |
| `data/reference/` | Reference lookup data |

### src/ Folder (Code will go here)
| Folder | Purpose |
|--------|---------|
| `src/backend/` | FastAPI backend code |
| `src/frontend/` | Next.js frontend code |
| `src/shared/` | Shared utilities |

---

## Important Files by Priority

### 🔴 Critical (Must Read)

1. **`README.md`** - Project overview
2. **`docs/architecture/Development_Approach_Summary.md`** - How we develop
3. **`docs/architecture/Local_Development_and_Testing_Guide.md`** - Local setup

### 🟡 Important (Should Read)

4. **`docs/architecture/Condensed_Development_Plan.md`** - 10-week plan
5. **`docs/analysis/Data_Structure_Analysis.md`** - Database design
6. **`docs/architecture/Data_to_Architecture_Mapping_and_Development_Guide.md`** - Technical details

### 🟢 Reference (Read as Needed)

7. **`docs/requirements/Treasury_System_Structure.pdf`** - Original requirements
8. **`data/extracted/`** - Extracted data for reference

---

## What Should I Do Right Now?

### Option A: I'm a Developer Starting Today

```bash
1. Read this file (START_HERE.md) ← You are here
2. Read docs/architecture/Development_Approach_Summary.md
3. Read docs/architecture/Local_Development_and_Testing_Guide.md
4. Follow the setup instructions in Phase 1
5. Start coding Week 1 deliverables
```

### Option B: I Want to Understand the Project First

```bash
1. Read README.md
2. Read docs/architecture/Development_Approach_Summary.md
3. Review docs/analysis/Data_Structure_Analysis.md
4. Ask questions to the team
```

### Option C: I'm Looking for Something Specific

| Looking for... | Go to... |
|---------------|----------|
| Database schema | `docs/analysis/Data_Structure_Analysis.md` Section 2-3 |
| API design | `docs/architecture/Data_to_Architecture_Mapping_and_Development_Guide.md` Section 6 |
| Test data | `data/source/Treasury_System_Database_V2_Internal.xlsx` |
| Development timeline | `docs/architecture/Condensed_Development_Plan.md` |
| How to test locally | `docs/architecture/Local_Development_and_Testing_Guide.md` |

---

## Next Steps

Choose your path:

### Path 1: Quick Start (Recommended for developers)
→ Go to `docs/architecture/Local_Development_and_Testing_Guide.md`

### Path 2: Understand First (Recommended for managers/analysts)
→ Go to `README.md` then `docs/architecture/Development_Approach_Summary.md`

### Path 3: Deep Dive (Recommended for architects)
→ Go to `docs/architecture/Data_to_Architecture_Mapping_and_Development_Guide.md`

---

## Need Help?

- **Project questions**: Check `docs/index.md` for document navigation
- **Technical questions**: Check `docs/architecture/Local_Development_and_Testing_Guide.md` Troubleshooting section
- **Data questions**: Check `docs/analysis/Data_Structure_Analysis.md`

---

*Last Updated: February 2026*
*Version: 0.1.0*
