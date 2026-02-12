# Treasury Management System - Documentation Hub

Welcome to the comprehensive documentation for the Treasury Management System (TMS). This documentation covers everything from getting started to advanced operations.

## 📚 Documentation Structure

### 01 - Getting Started
**Start here if you're new to the project**
- [Project Summary](./01-getting-started/project-summary.md) - High-level overview of the TMS
- [Session Starter](./01-getting-started/session-starter.md) - Quick start guide for new developers
- [Setup Instructions](./01-getting-started/setup.md) - Complete environment setup guide

### 02 - Architecture
**System design and technical architecture**
- [Architecture Canvas](./02-architecture/design/ARCHITECTURE_CANVAS.md) - **High-Level Visual Map**
  - C4 System Context
  - Container Architecture
  - Deployment Topology
- [Technical Details](./02-architecture/technical-details/) - Detailed module-by-module architecture
  - Core Module (Enums, State Machines, Security)
  - Models & Database Schema
  - Services & Business Logic
  - API Routers & Endpoints
  - Frontend Architecture
  - Testing Framework
  - Operations & DevOps
- [System Design](./02-architecture/design/SYSTEM_DESIGN.md) - Overall system architecture
- [Field Reference](./02-architecture/design/FIELD_REFERENCE.md) - Complete field definitions

### 03 - Development
**Guides for developers building features**
- [API Reference](./03-development/guides/API_REFERENCE.md) - API endpoint documentation
- [Development Guide](./03-development/guides/DEVELOPMENT_GUIDE.md) - Coding standards and practices
- [Testing Guide](./03-development/guides/TESTING_GUIDE.md) - How to write and run tests
- [Missing Services Backlog](./03-development/guides/MISSING_SERVICES_BACKLOG.md) - Planned features

### 04 - Business Processes
**Treasury workflows and transaction flows**
- [Transaction Workflows](./04-business-processes/workflows/TRANSACTION_WORKFLOWS.md) - Complete transaction lifecycle
- [Transaction Flow Diagrams](./04-business-processes/workflows/TRANSACTION_FLOW_DIAGRAMS.md) - Visual process flows
- [Pre-Transaction Setup](./04-business-processes/workflows/PRE_TRANSACTION_SETUP.md) - Required setup before trading
- [Field-Workflow Mapping](./04-business-processes/workflows/FIELD_WORKFLOW_MAPPING.md) - Data field mappings

### 05 - Operations
**Day-to-day operational procedures**
- [Daily Operations](./05-operations/daily-ops/DAILY_OPERATIONS.md) - Daily tasks and procedures
- [Manual Calculation Guide](./05-operations/daily-ops/MANUAL_CALCULATION_GUIDE.md) - Financial formulas
- [Stakeholder Checklist](./05-operations/daily-ops/STAKEHOLDER_CHECKLIST.md) - Review checklist

---

## 🚀 Quick Navigation

### For New Team Members
1. Start with [Project Summary](./01-getting-started/project-summary.md)
2. Follow [Setup Instructions](./01-getting-started/setup.md)
3. Read [Development Guide](./03-development/guides/DEVELOPMENT_GUIDE.md)

### For Product Managers
1. Review [System Design](./02-architecture/design/SYSTEM_DESIGN.md)
2. Study [Transaction Workflows](./04-business-processes/workflows/TRANSACTION_WORKFLOWS.md)
3. Check [Stakeholder Checklist](./05-operations/daily-ops/STAKEHOLDER_CHECKLIST.md)

### For Treasury Operations
1. Start with [Daily Operations](./05-operations/daily-ops/DAILY_OPERATIONS.md)
2. Reference [Manual Calculation Guide](./05-operations/daily-ops/MANUAL_CALCULATION_GUIDE.md)
3. Follow [Transaction Workflows](./04-business-processes/workflows/TRANSACTION_WORKFLOWS.md)

### For Architects & Technical Leads
1. Review [Technical Details](./02-architecture/technical-details/)
2. Check [API Reference](./03-development/guides/API_REFERENCE.md)
3. Study [Testing Framework](./02-architecture/technical-details/06_testing_framework.md)

---

## 📁 Additional Resources

- **[Archive](../archive/)** - Historical documents and deprecated guides (moved to project root)
- **[Requirements](../archive/requirements/)** - Original requirements and specifications
- **[Analysis](../archive/analysis/)** - Analysis reports and reviews
- **[Reference](../archive/reference/)** - Quick reference materials

---

## 🔍 Finding What You Need

- **System Architecture?** → See Section 02 - Architecture
- **How to build features?** → See Section 03 - Development  
- **Business rules?** → See Section 04 - Business Processes
- **Daily tasks?** → See Section 05 - Operations
- **Setup help?** → See Section 01 - Getting Started

---

## 📝 Document Conventions

- **README.md** - Always the entry point for each section
- **Diagrams** - MermaidJS format for version control
- **Links** - Relative paths for portability
- **Updates** - Keep docs in sync with code changes

---

## 🤝 Contributing to Docs

When adding new documentation:
1. Place it in the appropriate numbered section
2. Update this index if adding a major document
3. Use MermaidJS for diagrams
4. Keep language clear and concise
5. Include examples where helpful

---

**Last Updated**: 2026-02-11  
**Version**: 0.3.1
