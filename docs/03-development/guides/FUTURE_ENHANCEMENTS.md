# Future Enhancements & Roadmap

**Last Updated**: February 10, 2026  
**Version**: 0.3.0

---

## 📊 Current Implementation Status

### ✅ Completed Modules

| Module | Status | Coverage |
|--------|--------|----------|
| **Bond Trading** | ✅ Complete | 100% - Full service, router, and DB integration |
| **Interbank Deals** | ✅ Complete | 100% - Full service, router, and DB integration |
| **Repo Trades** | ✅ Complete | 100% - Full service, router, and DB integration |
| **Settlement** | ✅ Complete | BAHTNET/TSD integration ready |
| **Position Tracking** | ✅ Complete | Real-time bond/cash/collateral positions |
| **Market Data** | ✅ Complete | ThaiBMA import and pricing |
| **Calendar** | ✅ Complete | Thai business day handling |
| **Authentication** | ✅ Complete | JWT + RBAC |
| **Audit Trail** | ✅ Complete | Comprehensive logging |

### 🚀 Batch Jobs Implemented

- ✅ **Daily Accrual** - `scripts/run_eod_batch.py`
- ✅ **Maturity Processing** - Integrated in EOD batch
- ⏳ **Margin Call Job** - Planned (see below)

---

## 🎯 Planned Enhancements

### High Priority

#### 1. Automated Margin Call Detection (Repo)
**Priority**: High  
**Effort**: 1-2 days  
**Description**: Daily MTM job to monitor collateral values and trigger margin calls automatically.

**Key Features**:
- Daily collateral revaluation using ThaiBMA prices
- Automatic margin percentage calculation
- Threshold-based margin call triggers (e.g., <105%)
- Notification to Middle Office
- Integration with existing `repo_service.py`

**Implementation Path**:
```python
# File: app/jobs/margin_call_job.py
- Update collateral market values
- Calculate current margin percentages
- Identify trades below threshold
- Create margin call records
- Send alerts/notifications
```

---

### Medium Priority

#### 2. Enhanced Reporting Module
**Priority**: Medium  
**Effort**: 3-4 days  
**Description**: Pre-built reports for regulatory and management needs.

**Planned Reports**:
- Daily Position Summary (by security, counterparty, portfolio)
- Limit Utilization Report
- Settlement Forecast (T+0 to T+7)
- P&L Analysis (realized vs unrealized)
- ThaiBMA Trade Reporting Export

#### 3. Limit Management Enhancements
**Priority**: Medium  
**Effort**: 2-3 days  
**Description**: Advanced limit features beyond current implementation.

**Features**:
- Multi-tier limits (entity, counterparty, product)
- Time-based limit resets (daily, monthly)
- Pre-trade limit checking API
- Limit breach workflow and approvals

---

### Low Priority

#### 4. Integration APIs
**Priority**: Low  
**Effort**: 1-2 weeks  
**Description**: External system integrations for production deployment.

**Potential Integrations**:
- **Core Banking System** - Real-time cash balance updates
- **Risk Management** - VAR calculation data feeds
- **GL System** - Automated journal entry posting
- **Email/SMS** - Approval and alert notifications

#### 5. Advanced Analytics
**Priority**: Low  
**Effort**: 1-2 weeks  
**Description**: Data analytics and visualization features.

**Features**:
- Historical trade analysis
- Yield curve tracking
- Portfolio stress testing
- Counterparty exposure analysis

---

## 📝 Technical Debt Items

### Code Quality
- ⚠️ Increase test coverage to 85%+ (currently ~70%)
- ⚠️ Add OpenAPI schema examples for all endpoints
- ⚠️ Implement rate limiting on public endpoints

### Performance
- ⚠️ Add Redis caching for market data queries
- ⚠️ Optimize position calculation queries
- ⚠️ Implement database connection pooling

### Security
- ⚠️ Add API request signing for external integrations
- ⚠️ Implement audit log retention policy
- ⚠️ Add security headers (HSTS, CSP, etc.)

---

## 🗺️ Roadmap Overview

### Q1 2026 (Current)
- ✅ Core modules complete (Bond, Interbank, Repo)
- ✅ Settlement integration (BAHTNET/TSD)
- ✅ Basic EOD batch processing

### Q2 2026 (Planned)
- 🎯 Margin call automation
- 🎯 Enhanced reporting module
- 🎯 Limit management enhancements
- 🎯 Test coverage improvement

### Q3 2026 (Future)
- 🔮 External system integrations
- 🔮 Advanced analytics
- 🔮 Mobile app for approvals
- 🔮 API v2 with GraphQL support

---

## 💡 Feature Requests

To request a new feature or enhancement:

1. **Check the roadmap** above to see if it's already planned
2. **Create an issue** in the project management system
3. **Provide details**:
   - Business justification
   - Expected impact
   - User stories
   - Priority assessment

---

## 📊 Effort Estimation Guide

| Size | Effort | Examples |
|------|--------|----------|
| **XS** | 1-2 hours | Minor bug fixes, text changes |
| **S** | 4-8 hours | New endpoint, simple report |
| **M** | 1-3 days | New service module, complex report |
| **L** | 1-2 weeks | New product type, major integration |
| **XL** | 1+ month | Complete system redesign |

---

## 🔍 Notes

- All **core treasury functions** are production-ready
- The system follows **Bank of Thailand** and **ThaiBMA** standards
- Current focus is on **operational enhancements** rather than new features
- Architecture is **extensible** - new modules can be added easily

---

**Questions?** Contact the development team or check the [Development Guide](./DEVELOPMENT_GUIDE.md).
