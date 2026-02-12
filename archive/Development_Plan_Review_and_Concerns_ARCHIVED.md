# Development Plan Review, Suggestions & Concerns

**Comprehensive Review of All Phases**  
**Date:** February 2026  
**Document Purpose:** Critical analysis of the 10-week development plan with actionable recommendations

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Phase 1 Review: Foundation Setup](#2-phase-1-review-foundation-setup-week-1)
3. [Phase 2 Review: Backend Development](#3-phase-2-review-backend-development-week-1-2)
4. [Phase 3 Review: Frontend Development](#4-phase-3-review-frontend-development-week-4)
5. [Phase 4 Review: Product Development](#5-phase-4-review-product-development-weeks-2-5)
6. [Phase 5 Review: Accounting & Compliance](#6-phase-5-review-accounting--compliance-week-6-7)
7. [Phase 6 Review: Testing & Validation](#7-phase-6-review-testing--validation-week-8)
8. [Phase 7 Review: UAT & Deployment](#8-phase-7-review-uat--deployment-weeks-9-10)
9. [Cross-Cutting Concerns](#9-cross-cutting-concerns)
10. [Risk Assessment Summary](#10-risk-assessment-summary)
11. [Recommendations Priority Matrix](#11-recommendations-priority-matrix)

---

## 1. Executive Summary

### Overall Assessment

| Aspect | Rating | Comment |
|--------|--------|---------|
| **Documentation Quality** | ⭐⭐⭐⭐⭐ | Excellent, comprehensive, well-structured |
| **Technical Approach** | ⭐⭐⭐⭐ | Sound "local-first" strategy |
| **Timeline Feasibility** | ⭐⭐⭐ | Aggressive but achievable with experienced team |
| **Risk Management** | ⭐⭐⭐ | Good identification, needs more mitigation details |
| **Implementation Readiness** | ⭐⭐ | Missing prerequisite files and configs |

### Key Strengths ✅

1. **Local-first approach** eliminates deployment risks during development
2. **Excel test data strategy** provides real-world validation
3. **Clear sprint boundaries** with defined deliverables
4. **Comprehensive product coverage** (Bond, IB Lend/Borrow, Repo/RRP)

### Critical Gaps ⚠️

1. **Missing infrastructure files** (docker-compose, requirements.txt, .env)
2. **No authentication implementation details**
3. **External integration complexity underestimated** (ThaiBMA, BAHTNET, TSD)
4. **Database migration strategy not defined**
5. **Holiday/business day calendar logic missing**

---

## 2. Phase 1 Review: Foundation Setup (Week 1)

### What's Planned

```
Day 1: PostgreSQL + Docker setup
Day 2: FastAPI project scaffold
Day 3: Auto-generate models from Excel
Day 4: Auto-generate CRUD APIs
Day 5: Import master data
```

### 🟢 Strengths

| Item | Why It's Good |
|------|---------------|
| Docker for database | Consistent environment across developers |
| Auto-generation from Excel | Significant time savings |
| Redis for caching | Good architecture foresight |
| Adminer for DB GUI | Easy inspection during development |

### 🟡 Concerns

| Concern | Impact | Severity |
|---------|--------|----------|
| **Missing `docker-compose.local.yml`** | Can't start infrastructure | 🔴 HIGH |
| **Missing `requirements.txt`** | Dependency confusion | 🔴 HIGH |
| **Missing `init_db.sql`** | Database won't initialize properly | 🟡 MEDIUM |
| **Windows path issues** | Docker volumes may fail | 🟡 MEDIUM |
| **No `.env.example`** | Team won't know required variables | 🟡 MEDIUM |

### 🔧 Recommendations

1. **Create prerequisite files BEFORE Week 1 starts:**
   ```
   - docker-compose.local.yml (with correct Windows paths)
   - src/backend/requirements.txt
   - scripts/init_db.sql
   - .env.example
   ```

2. **Add Docker Desktop verification step:**
   ```bash
   # Verify Docker is running
   docker --version
   docker-compose --version
   docker ps  # Should not error
   ```

3. **Add WSL2 setup for Windows:**
   - Docker Desktop requires WSL2 on Windows
   - Add instructions to install WSL2 if not present

4. **Python version pinning:**
   - Recommend Python 3.11.x specifically
   - 3.12 has some library compatibility issues

### 📋 Missing Files to Create

```yaml
# docker-compose.local.yml - CRITICAL
version: '3.8'
services:
  postgres:
    image: postgres:15-alpine
    container_name: tms_postgres_local
    environment:
      POSTGRES_USER: tms_user
      POSTGRES_PASSWORD: tms_password
      POSTGRES_DB: treasury_local
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      # Windows path fix:
      - ./scripts/init_db.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U tms_user -d treasury_local"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: tms_redis_local
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  adminer:
    image: adminer
    container_name: tms_adminer
    ports:
      - "8080:8080"
    depends_on:
      postgres:
        condition: service_healthy

volumes:
  postgres_data:
```

---

## 3. Phase 2 Review: Backend Development (Week 1-2)

### What's Planned

- FastAPI project structure with modular design
- SQLAlchemy models for all 18+ tables
- CRUD endpoints for master data
- Bond trading core logic

### 🟢 Strengths

| Item | Why It's Good |
|------|---------------|
| Clean folder structure | Maintainable codebase |
| Separation of concerns | Models, schemas, routers, services |
| FastAPI choice | Modern, fast, auto-documentation |
| Dependency injection | Testable code |

### 🟡 Concerns

| Concern | Impact | Severity | Explanation |
|---------|--------|----------|-------------|
| **No authentication code** | Security gap | 🔴 HIGH | JWT/OAuth2 mentioned but not implemented |
| **No database migrations** | Schema changes break DB | 🔴 HIGH | Alembic mentioned but not set up |
| **`pydantic-settings` missing** | Config won't work | 🟡 MEDIUM | Separate package from pydantic v2 |
| **No CORS configuration** | Frontend can't call API | 🟡 MEDIUM | Will block frontend development |
| **No error handling pattern** | Inconsistent API responses | 🟡 MEDIUM | Need global exception handler |

### 🔧 Recommendations

1. **Add authentication boilerplate in Week 1:**
   ```python
   # app/core/auth.py - MUST HAVE
   from fastapi import Depends, HTTPException, status
   from fastapi.security import OAuth2PasswordBearer
   from jose import JWTError, jwt
   
   oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
   
   async def get_current_user(token: str = Depends(oauth2_scheme)):
       # Decode and validate JWT
       pass
   ```

2. **Set up Alembic immediately:**
   ```bash
   cd src/backend
   alembic init alembic
   alembic revision --autogenerate -m "initial"
   alembic upgrade head
   ```

3. **Add CORS middleware:**
   ```python
   # app/main.py
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],  # Frontend URL
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

4. **Create global exception handler:**
   ```python
   # app/core/exceptions.py
   class TreasuryException(Exception):
       def __init__(self, code: str, message: str, status_code: int = 400):
           self.code = code
           self.message = message
           self.status_code = status_code
   
   @app.exception_handler(TreasuryException)
   async def treasury_exception_handler(request, exc):
       return JSONResponse(
           status_code=exc.status_code,
           content={"code": exc.code, "message": exc.message}
       )
   ```

### 📋 Required `requirements.txt`

```txt
# Core
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.6.0
pydantic-settings==2.1.0

# Database
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
alembic==1.13.1

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Caching
redis==5.0.1
celery==5.3.6

# Data Processing
pandas==2.2.0
openpyxl==3.1.2

# Testing
pytest==8.0.0
pytest-asyncio==0.23.4
httpx==0.26.0

# Utilities
python-dateutil==2.8.2
pytz==2024.1
```

---

## 4. Phase 3 Review: Frontend Development (Week 4)

### What's Planned

- Next.js + TypeScript setup
- Trade entry forms
- Trade blotter with approval workflow
- Position view dashboard

### 🟢 Strengths

| Item | Why It's Good |
|------|---------------|
| Next.js choice | Server-side rendering, good DX |
| TypeScript | Type safety, fewer bugs |
| Ant Design | Comprehensive component library |
| React Query | Efficient data fetching |

### 🟡 Concerns

| Concern | Impact | Severity | Explanation |
|---------|--------|----------|-------------|
| **TailwindCSS in setup command** | Conflicts with project conventions | 🟡 MEDIUM | Your project uses vanilla CSS |
| **One week for full UI** | Very aggressive | 🟡 MEDIUM | May need 1.5-2 weeks realistically |
| **No state management detail** | Complex state handling | 🟡 MEDIUM | Zustand mentioned but not designed |
| **No responsive design** | Poor mobile experience | 🟢 LOW | Traders use desktop mainly |
| **No offline capability** | Can't trade offline | 🟢 LOW | Desktop with stable connection |

### 🔧 Recommendations

1. **Use Vite instead of Next.js if no SSR needed:**
   ```bash
   # Simpler, faster for admin dashboards
   npm create vite@latest . -- --template react-ts
   ```

2. **If keeping Next.js, avoid Tailwind conflict:**
   ```bash
   # Remove --tailwind from setup command
   npx create-next-app@latest . --typescript --eslint --app --src-dir
   ```

3. **Prioritize UI components by importance:**
   ```
   Day 1: Trade entry form (CRITICAL)
   Day 2: Trade blotter (CRITICAL)
   Day 3: Approval workflow (CRITICAL)
   Day 4: Position view (HIGH)
   Day 5: Dashboard + polish (MEDIUM)
   ```

4. **Create reusable form components early:**
   - TradeForm (shared by Bond, IB, Repo)
   - DataTable (shared by all blotters)
   - ApprovalActions (shared workflow)

---

## 5. Phase 4 Review: Product Development (Weeks 2-5)

### What's Planned

| Week | Products | Complexity |
|------|----------|------------|
| 2 | Bond Trading | High |
| 3 | Settlement + Accounting | High |
| 5 | Interbank + Repo/RRP | Very High |

### 🟢 Strengths

| Item | Why It's Good |
|------|---------------|
| MVP-first approach | Bond trading is highest volume |
| All products in scope | Complete coverage by Week 5 |
| Settlement integration | Core to any TMS |

### 🔴 Critical Concerns

| Concern | Impact | Severity | Explanation |
|---------|--------|----------|-------------|
| **Week 5 is overloaded** | 4 products in 1 week | 🔴 HIGH | IB Lend + IB Borrow + Repo + RRP is too much |
| **No holiday calendar logic** | Wrong settlement dates | 🔴 HIGH | T+2 fails on holidays |
| **ThaiBMA integration complexity** | Can't report trades | 🔴 HIGH | API integration takes time |
| **THOR rate source missing** | Floating rate fails | 🟡 MEDIUM | Need BOT THOR API integration |
| **Margin call workflow complex** | Incomplete margin management | 🟡 MEDIUM | Needs detailed state machine |

### 🔧 Recommendations

1. **Split Week 5 into Week 5 and 6:**
   ```
   Week 5: Interbank Lending + Borrowing
   Week 6: Repo + Reverse Repo + Margin
   Week 7: TFRS 9 + Reporting (shifted)
   Week 8: Risk + Controls (shifted)
   Week 9: Testing (shifted)
   Week 10: UAT + Deployment (compressed)
   ```

2. **Implement Thai business day calendar:**
   ```python
   # services/calendar_service.py - CRITICAL
   from datetime import date, timedelta
   
   THAI_HOLIDAYS_2025 = [
       date(2025, 1, 1),   # New Year
       date(2025, 2, 12),  # Makha Bucha
       date(2025, 4, 6),   # Chakri Day
       date(2025, 4, 13),  # Songkran
       date(2025, 4, 14),  # Songkran
       date(2025, 4, 15),  # Songkran
       date(2025, 5, 1),   # Labor Day
       date(2025, 5, 4),   # Coronation Day
       date(2025, 5, 22),  # Visakha Bucha
       date(2025, 6, 3),   # Queen's Birthday
       date(2025, 7, 28),  # King's Birthday
       date(2025, 8, 12),  # Mother's Day
       date(2025, 10, 13), # King Rama IX Memorial
       date(2025, 10, 23), # Chulalongkorn Day
       date(2025, 12, 5),  # Father's Day
       date(2025, 12, 10), # Constitution Day
       date(2025, 12, 31), # New Year's Eve
   ]
   
   def is_thai_business_day(d: date) -> bool:
       if d.weekday() >= 5:  # Saturday or Sunday
           return False
       if d in THAI_HOLIDAYS_2025:
           return False
       return True
   
   def add_business_days(start: date, days: int) -> date:
       current = start
       added = 0
       while added < days:
           current += timedelta(days=1)
           if is_thai_business_day(current):
               added += 1
       return current
   
   def calculate_t_plus_2(trade_date: date) -> date:
       return add_business_days(trade_date, 2)
   ```

3. **Create external integration stubs first:**
   ```python
   # services/external/thaibma.py
   class ThaiBMAClient:
       def __init__(self, mode='mock'):  # Start with mock
           self.mode = mode
       
       async def report_trade(self, trade: dict) -> dict:
           if self.mode == 'mock':
               return {"status": "REPORTED", "confirmation_id": "MOCK-001"}
           # Real implementation in Phase 2
   ```

4. **Define margin call state machine:**
   ```
   PENDING → AGREED → SETTLED
       │        │
       └→ DISPUTED → ESCALATED → SETTLED
   ```

---

## 6. Phase 5 Review: Accounting & Compliance (Week 6-7)

### What's Planned

- TFRS 9 classification (FVOCI, Amortized Cost, FVTPL)
- ECL calculation (Stage 1/2/3)
- BOT DER_CPEN export
- LCR calculation

### 🟢 Strengths

| Item | Why It's Good |
|------|---------------|
| TFRS 9 compliance | Regulatory requirement |
| ECL staging | Credit risk visibility |
| BOT reporting | Regulatory compliance |

### 🟡 Concerns

| Concern | Impact | Severity | Explanation |
|---------|--------|----------|-------------|
| **ECL calculation is complex** | Incorrect provisions | 🔴 HIGH | Requires probability models |
| **TFRS 9 rules are intricate** | Misclassification risk | 🟡 MEDIUM | SPPI test implementation needed |
| **LCR calculation detailed** | Wrong liquidity ratios | 🟡 MEDIUM | Many asset categories |
| **BOT report format unknown** | Can't export correctly | 🟡 MEDIUM | Need exact XML/CSV specs |

### 🔧 Recommendations

1. **Simplify ECL for MVP:**
   ```python
   # Use simplified approach
   ECL_RATES = {
       1: 0.001,  # Stage 1: 0.1% (12-month)
       2: 0.030,  # Stage 2: 3.0% (lifetime)
       3: 0.500,  # Stage 3: 50% (credit-impaired)
   }
   
   def calculate_ecl(position):
       return position.carrying_amount * ECL_RATES[position.ecl_stage]
   ```

2. **Get BOT report templates first:**
   - Request sample DER_CPEN file from BOT
   - Validate output format before Week 7

3. **TFRS 9 classification should be configurable:**
   - Portfolio-level setting (not trade-level)
   - Admin can configure classification rules

---

## 7. Phase 6 Review: Testing & Validation (Week 8)

### What's Planned

- Import all Excel test data
- Run automated tests for all products
- Validate against expected results
- Performance testing

### 🟢 Strengths

| Item | Why It's Good |
|------|---------------|
| Excel validation | Real-world test cases |
| Comprehensive coverage | All products tested |
| Local testing | No deployment risks |
| Clear success criteria | Measurable outcomes |

### 🟡 Concerns

| Concern | Impact | Severity | Explanation |
|---------|--------|----------|-------------|
| **Excel sheet names may differ** | Import fails | 🟡 MEDIUM | Verify exact sheet names |
| **Excel data format varies** | Parsing errors | 🟡 MEDIUM | Some sheets have headers at different rows |
| **One week may not be enough** | Incomplete testing | 🟡 MEDIUM | Bug fixes take time |
| **No negative testing** | Edge cases missed | 🟡 MEDIUM | Only happy path tested |

### 🔧 Recommendations

1. **Create Excel sheet verification script:**
   ```python
   # Verify all expected sheets exist
   import pandas as pd
   
   excel_file = 'data/source/Treasury_System_Database_V2_Internal.xlsx'
   xl = pd.ExcelFile(excel_file)
   
   expected_sheets = [
       'Bond buy_1_V4_Sep25',
       'Bond sell_1_V4_Oct25',
       'IB Lend_V4_Sep25',
       # ... all others
   ]
   
   for sheet in expected_sheets:
       if sheet not in xl.sheet_names:
           print(f"❌ Missing: {sheet}")
       else:
           print(f"✅ Found: {sheet}")
   ```

2. **Add negative test cases:**
   - Trade exceeds limit → Should reject
   - Settlement date on holiday → Should recalculate
   - Invalid counterparty → Should error
   - Missing collateral for repo → Should block

3. **Allocate 1-2 buffer days for bug fixes:**
   ```
   Day 1-2: Import + initial test run
   Day 3-4: Fix failures + retest
   Day 5: Final validation + performance
   Day 6-7: Buffer for remaining issues (if needed, extends into Week 9)
   ```

---

## 8. Phase 7 Review: UAT & Deployment (Weeks 9-10)

### What's Planned

- Week 9: Local UAT with business users
- Week 10: Staging → Production deployment

### 🟢 Strengths

| Item | Why It's Good |
|------|---------------|
| Local UAT first | No cloud costs during UAT |
| Staged deployment | Risk mitigation |
| Sign-off requirements | Clear accountability |

### 🔴 Critical Concerns

| Concern | Impact | Severity | Explanation |
|---------|--------|----------|-------------|
| **No production environment defined** | Can't deploy | 🔴 HIGH | Cloud provider not chosen |
| **No data migration plan** | Incomplete production data | 🔴 HIGH | How to load production master data? |
| **No rollback strategy** | Stuck if issues | 🟡 MEDIUM | Need backout plan |
| **Parallel run period too short** | Risky cutover | 🟡 MEDIUM | Only 1-2 days parallel |
| **No monitoring setup** | Can't detect issues | 🟡 MEDIUM | No observability tools defined |

### 🔧 Recommendations

1. **Define cloud environment early (Week 1):**
   ```
   Option A: AWS (RDS PostgreSQL + ECS + CloudFront)
   Option B: Azure (Azure Database + App Service)
   Option C: GCP (Cloud SQL + Cloud Run)
   Option D: On-premise (if bank requires)
   ```

2. **Create production deployment checklist:**
   ```
   Pre-deployment:
   [ ] All tests pass in staging
   [ ] Security scan complete
   [ ] Backup strategy verified
   [ ] Rollback script tested
   [ ] Monitoring alerts configured
   
   Deployment:
   [ ] Database migrations run
   [ ] Master data loaded
   [ ] Smoke tests pass
   [ ] Performance baseline captured
   
   Post-deployment:
   [ ] Monitor for 24 hours
   [ ] Compare with old system
   [ ] User feedback collected
   ```

3. **Extend parallel run to 1 week:**
   - Week 10 Day 1-3: Deploy + parallel run
   - Week 10 Day 4-5: Monitor + stabilize
   - Week 11 (if needed): Continue parallel run

4. **Set up basic monitoring:**
   - Application logs → CloudWatch/Azure Monitor
   - API metrics → Prometheus + Grafana
   - Error tracking → Sentry
   - Uptime monitoring → Pingdom/UptimeRobot

---

## 9. Cross-Cutting Concerns

### 9.1 Security

| Gap | Risk | Recommendation |
|-----|------|----------------|
| No authentication implementation | Unauthorized access | Implement JWT auth in Week 1 |
| No role-based access control | Permission violations | Define roles: Trader, Supervisor, Admin |
| No encryption at rest | Data breach | Use PostgreSQL encryption |
| No audit logging | Compliance failure | Log all state changes |

### 9.2 Performance

| Gap | Risk | Recommendation |
|-----|------|----------------|
| No database indexing strategy | Slow queries | Add indexes in Week 2 |
| No connection pooling config | DB overload | Configure SQLAlchemy pool |
| No caching strategy | Repeated queries | Cache master data in Redis |
| No pagination | Large result sets | Add limit/offset to all list APIs |

### 9.3 Data Integrity

| Gap | Risk | Recommendation |
|-----|------|----------------|
| No database constraints | Invalid data | Add FK constraints, CHECK constraints |
| No transaction boundaries | Partial updates | Use explicit transactions |
| No idempotency keys | Duplicate trades | Add unique trade ID generation |
| No soft delete strategy | Accidental deletion | Add `is_deleted` flag |

### 9.4 External Integrations

| System | Status | Integration Type | Notes |
|--------|--------|------------------|-------|
| **ThaiBMA** | Not started | API | Trade reporting API, need credentials |
| **BAHTNET** | Manual input | ISO20022 messages | System generates pacs.008/pacs.009 files, manual upload to BAHTNET portal |
| **TSD** | Manual input | Settlement instruction | System generates DVP instructions, manual submission |
| **BOT THOR rates** | Not started | API/Batch | Need data source for floating rate (BOT API or FRED fallback) |

---

## 10. Risk Assessment Summary

### Risk Matrix

```
                    IMPACT
           Low    Medium    High
         ┌──────┬──────┬──────┐
    High │  3   │  2   │  1   │  ← PRIORITY
  L      ├──────┼──────┼──────┤
  I Med  │  5   │  4   │  3   │
  K      ├──────┼──────┼──────┤
  E Low  │  -   │  5   │  4   │
         └──────┴──────┴──────┘
```

### Top Risks by Priority

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|------------|--------|------------|
| 1 | **Week 5 overload** (4 products) | High | High | Split into 2 weeks |
| 2 | **Missing prerequisite files** | High | High | Create before Week 1 |
| 3 | **No authentication** | Medium | High | Add in Week 1 |
| 4 | **External integration delays** | High | Medium | Use mocks, defer to Phase 2 |
| 5 | **Holiday calendar missing** | Medium | High | Implement in Week 2 |
| 6 | **ECL complexity** | Medium | Medium | Simplify for MVP |
| 7 | **Production environment undefined** | Medium | High | Decide in Week 1 |
| 8 | **Short parallel run period** | Low | High | Extend to 1 week |

---

## 11. Recommendations Priority Matrix

### 🔴 MUST DO Before Starting (Week 0)

| # | Action | Effort | Owner |
|---|--------|--------|-------|
| 1 | Create `docker-compose.local.yml` | 2 hours | DevOps |
| 2 | Create `requirements.txt` | 1 hour | Backend Lead |
| 3 | Create `init_db.sql` | 1 hour | Database Dev |
| 4 | Create `.env.example` | 30 min | Backend Lead |
| 5 | Verify Docker Desktop installed | 30 min | All Devs |
| 6 | Verify Excel sheet names | 1 hour | QA |

### 🟡 SHOULD DO During Week 1

| # | Action | Sprint | Owner |
|---|--------|--------|-------|
| 1 | Implement JWT authentication | Sprint 1 | Backend |
| 2 | Set up Alembic migrations | Sprint 1 | Backend |
| 3 | Add CORS middleware | Sprint 1 | Backend |
| 4 | Implement Thai holiday calendar | Sprint 1 | Backend |
| 5 | Create external integration stubs | Sprint 1 | Backend |
| 6 | Decide production cloud provider | Sprint 1 | Tech Lead |

### 🟢 NICE TO HAVE (Add If Time Permits)

| # | Action | Sprint | Benefit |
|---|--------|--------|---------|
| 1 | GitHub Actions CI/CD | Sprint 2 | Automated testing |
| 2 | Swagger customization | Sprint 3 | Better API docs |
| 3 | Error tracking (Sentry) | Sprint 4 | Production visibility |
| 4 | Rate limiting | Sprint 7 | API protection |

---

## 12. Revised Timeline Recommendation

Based on this review, I recommend a **12-week timeline** instead of 10 weeks:

```
Week 0:  Preparation (create missing files)
Week 1:  Foundation + Auth + Calendar
Week 2:  Bond Trading Core
Week 3:  Settlement + Accounting
Week 4:  Frontend MVP
Week 5:  Interbank Lending + Borrowing
Week 6:  Repo + Reverse Repo + Margin
Week 7:  TFRS 9 + Risk Controls
Week 8:  Integration Testing
Week 9:  Bug Fixes + Performance
Week 10: UAT (Local)
Week 11: Staging Deployment + Testing
Week 12: Production + Hypercare
```

**Benefits:**
- 🟢 More realistic for 4 products
- 🟢 Proper testing time
- 🟢 Safer production deployment
- 🟢 Buffer for unforeseen issues

---

## Next Steps

1. **Review this document with the team**
2. **Decide on 10-week vs 12-week timeline**
3. **Create missing prerequisite files**
4. **Assign owners to Week 1 tasks**
5. **Begin Sprint 1**

---

*Document Version: 1.0*  
*Last Updated: February 2026*
