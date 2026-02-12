# Documentation Directory Structure

```
docs/
│
├── README.md                          # Main documentation hub (START HERE)
│
├── 01-getting-started/               # 🚀 New user onboarding
│   ├── README.md                     # Section overview
│   ├── project-summary.md            # System overview and scope
│   ├── session-starter.md            # Quick reference guide
│   └── setup.md                      # Complete setup instructions
│
├── 02-architecture/                  # 🏗️ System design
│   ├── design/                       # High-level architecture
│   │   ├── SYSTEM_DESIGN.md         # Overall system architecture
│   │   └── FIELD_REFERENCE.md       # Complete field definitions
│   │
│   └── technical-details/            # Module-by-module details
│       ├── README.md                 # Architecture index
│       ├── 01_core_module.md        # Enums, state machines, security
│       ├── 02_models_module.md      # Database schema & ERDs
│       ├── 03_services_module.md    # Business logic
│       ├── 04_routers_module.md     # API endpoints
│       ├── 05_frontend_module.md    # Next.js architecture
│       ├── 06_testing_framework.md  # Testing strategy
│       └── 07_operations_devops.md  # DevOps & deployment
│
├── 03-development/                   # 💻 Developer guides
│   ├── README.md                     # Development section overview
│   └── guides/
│       ├── API_REFERENCE.md         # API documentation
│       ├── DEVELOPMENT_GUIDE.md     # Coding standards
│       ├── TESTING_GUIDE.md         # Testing practices
│       └── MISSING_SERVICES_BACKLOG.md  # Feature roadmap
│
├── 04-business-processes/            # 📊 Treasury workflows
│   ├── README.md                     # Business process overview
│   └── workflows/
│       ├── TRANSACTION_WORKFLOWS.md  # Complete trade lifecycle
│       ├── TRANSACTION_FLOW_DIAGRAMS.md  # Visual flows
│       ├── PRE_TRANSACTION_SETUP.md  # Required setup
│       └── FIELD_WORKFLOW_MAPPING.md  # Data mappings
│
└── 05-operations/                    # 🔧 Daily operations
    ├── README.md                     # Operations overview
    └── daily-ops/
        ├── DAILY_OPERATIONS.md      # Day-to-day tasks
        ├── MANUAL_CALCULATION_GUIDE.md  # Financial formulas
        └── STAKEHOLDER_CHECKLIST.md  # Review checklist
```

> **Note:** The `archive/` folder has been moved to the **project root** (`/archive/`) and is no longer inside `docs/`. It contains historical documents, old analysis reports, original requirements, and deprecated guides.

## Quick Navigation

| I want to... | Go to... |
|---|---|
| **Get started** | `01-getting-started/` |
| **Understand architecture** | `02-architecture/technical-details/` |
| **Build features** | `03-development/guides/` |
| **Learn business rules** | `04-business-processes/workflows/` |
| **Run daily operations** | `05-operations/daily-ops/` |
| **Find old docs** | `../../archive/` (project root) |

## Document Naming Convention

- **README.md** - Always the entry point for each directory
- **Hyphens** - Separate words in filenames (e.g., `project-summary.md`)
- **Uppercase** - Legacy doc names preserved (e.g., `TRANSACTION_WORKFLOWS.md`)
- **Numbers** - Used for ordered sections (e.g., `01-getting-started/`)

## Maintenance

When adding documentation:
1. Place in the appropriate numbered section
2. Update the section's README.md
3. Link from main docs/README.md if it's a major addition
4. Keep this STRUCTURE.md updated if changing directory layout
