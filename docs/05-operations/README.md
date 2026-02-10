# Operations & Procedures

This section contains operational procedures and guides for running the TMS in production.

## 📋 Operational Guides

### [Daily Operations](./daily-ops/DAILY_OPERATIONS.md)
**Day-to-day tasks** including:
- Morning checklist
- End-of-day processing
- Settlement monitoring
- Position reconciliation
- Exception handling

### [Manual Calculation Guide](./daily-ops/MANUAL_CALCULATION_GUIDE.md)
**Financial formulas** for:
- Bond pricing (clean/dirty price)
- Accrued interest calculation
- Repo interest calculation
- Day count conventions (ACT/365, ACT/360)
- Yield calculations

### [Stakeholder Checklist](./daily-ops/STAKEHOLDER_CHECKLIST.md)
**Review checklist** for:
- System readiness verification
- Compliance requirements
- Risk management controls
- Audit trail completeness

---

## 👥 User Roles

### For Treasury Operators
→ Follow [Daily Operations](./daily-ops/DAILY_OPERATIONS.md) for routine tasks

### For Middle Office
→ Use [Manual Calculation Guide](./daily-ops/MANUAL_CALCULATION_GUIDE.md) to verify system calculations

### For Compliance/Audit
→ Reference [Stakeholder Checklist](./daily-ops/STAKEHOLDER_CHECKLIST.md) for controls review

---

## 🔄 Critical Processes

1. **Morning Start**: System health checks
2. **Trade Day**: Monitor deals and limits
3. **EOD Processing**: Run batch calculations
4. **Settlement Day**: Confirm BAHTNET/TSD transfers
5. **Month-End**: Position and P&L reconciliation

---

## 🔗 Related Documentation

- **Business Workflows** → [Transaction Workflows](../04-business-processes/workflows/TRANSACTION_WORKFLOWS.md)
- **Technical Operations** → [DevOps Guide](../02-architecture/technical-details/07_operations_devops.md)
- **Setup** → [Getting Started](../01-getting-started/)

---

**Important**: All operations must comply with Bank of Thailand (BOT) and ThaiBMA regulations.
