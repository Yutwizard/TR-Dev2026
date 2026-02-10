# Business Processes & Workflows

This section documents the treasury business processes and transaction workflows that the system implements.

## 📊 Core Documents

### [Transaction Workflows](./workflows/TRANSACTION_WORKFLOWS.md)
**Comprehensive guide** covering:
- Bond trade lifecycle (capture → approval → settlement)
- Interbank deal workflow
- Repo trade process
- State transitions and validations
- Four-eyes approval principles

### [Transaction Flow Diagrams](./workflows/TRANSACTION_FLOW_DIAGRAMS.md)
**Visual representations** of:
- Deal capture workflows
- Approval workflows
- Settlement workflows
- Position update flows

### [Pre-Transaction Setup](./workflows/PRE_TRANSACTION_SETUP.md)
**Required configuration** for:
- Master data setup (securities, counterparties)
- Portfolio configuration
- Limit definitions
- User roles and permissions
- Calendar and holidays

### [Field-Workflow Mapping](./workflows/FIELD_WORKFLOW_MAPPING.md)
**Data mappings** showing:
- How fields flow through the system
- Field transformations
- Required vs optional fields
- Validation rules

---

## 🎯 Use Cases

### For Product Managers
→ Start with [Transaction Workflows](./workflows/TRANSACTION_WORKFLOWS.md) to understand business logic

### For Business Analysts
→ Review [Field-Workflow Mapping](./workflows/FIELD_WORKFLOW_MAPPING.md) for data requirements

### For Treasury Operations
→ Check [Pre-Transaction Setup](./workflows/PRE_TRANSACTION_SETUP.md) for system configuration

### For Developers
→ Use [Transaction Flow Diagrams](./workflows/TRANSACTION_FLOW_DIAGRAMS.md) to understand implementation

---

## 🔗 Related Documentation

- **Daily Operations** → [Operations Guide](../05-operations/daily-ops/DAILY_OPERATIONS.md)
- **Technical Implementation** → [Services Module](../02-architecture/technical-details/03_services_module.md)
- **Setup** → [Getting Started](../01-getting-started/)

---

**Key Insight**: These workflows reflect Thai banking regulations and ThaiBMA requirements.
