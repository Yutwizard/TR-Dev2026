# Stakeholder Review Checklist - Treasury System Documentation

**Review Date:** February 3, 2026  
**Documents for Review:**
- [Treasury System Detailed Design Input](./Treasury_System_Detailed_Design_Input.md)
- [Field Update Matrix](./Field_Update_Matrix.md)

**Purpose:** Validate design documentation before implementation proceeds to Sprint 3 (Interbank + Repo)

---

## 📋 Review Instructions

### For Business Teams (Front/Middle/Back Office)
1. Focus on **Section 1-5** (Team Responsibilities) in Detailed Design
2. Review **Section 6** (Transaction Lifecycles) for your product area
3. Check Field Update Matrix for your team's fields

### For IT/Technical Team
1. Review **Appendix A** (Table Structures) in Detailed Design
2. Check data types and relationships
3. Validate batch job schedules in Section 8
4. Confirm Security Master is Back Office owned (IT provides infrastructure support only)

### For Management/Risk/Compliance
1. Review approval workflows and limit management
2. Check regulatory reporting mappings
3. Validate audit trail requirements

---

## ✅ Team Responsibilities Review

### Front Office (Trading Team)

| Item | Description | Status | Comments |
|------|-------------|--------|----------|
| Trade Capture | Bond trades, interbank deals, repo trades input | [ ] Approved | |
| Portfolio Selection | Assignment to correct portfolio (AMC/FVOCI/FVTPL) | [ ] Approved | |
| Price Input | Clean price entry with ±10% warning threshold | [ ] Approved | |
| Real-time Validation | Business day, KYC status, limit pre-check | [ ] Approved | |
| ThaiBMA Reporting | 30-minute reporting deadline awareness | [ ] Approved | |

**Questions for Front Office:**
- [ ] Is the ±10% price warning threshold appropriate?
- [ ] Do you need price/yield conversion calculator in UI?
- [ ] Should settlement date be auto T+2 or always editable?

---

### Middle Office (Risk & Compliance)

| Item | Description | Status | Comments |
|------|-------------|--------|----------|
| Four-Eyes Approval | ALL transactions require second approval (no threshold) | [ ] Approved | ⚠️ Confirm this is correct |
| Limit Types | SINGLE_TXN, AGGREGATE, TENOR, CONCENTRATION, REPO_LIMIT, PLACEMENT_LIMIT | [ ] Approved | |
| Alert Thresholds | 80% warning, 90% high warning, 100% hard block | [ ] Approved | |
| Margin Call Workflow | Pending → Agreed → Settled (with due_time T+1 11:00) | [ ] Approved | |
| Limit Utilization Log | Immutable audit trail (append-only) | [ ] Approved | |

**CRITICAL DECISION - Requires Confirmation:**
> **Four-Eyes Approval for ALL Transactions**
> 
> Current design: Every single trade (regardless of amount) requires approval by a second person.
> 
> [ ] **CONFIRMED** - Yes, all transactions require four-eyes approval  
> [ ] **MODIFY** - Set amount threshold (e.g., > 10M THB requires approval)  
> [ ] Comment: ___________________________

---

### Back Office (Settlement, Operations & Accounting)

| Item | Description | Status | Comments |
|------|-------------|--------|----------|
| **Daily ThaiBMA Price Import** | Download at 17:00, import by 18:00 | [ ] Approved | ⚠️ Critical daily task |
| Settlement Confirmation | TSD (SWIFT MT) + BAHTNET (manual portal upload) | [ ] Approved | |
| Collateral Allocation | Allocate securities to repo trades with haircut | [ ] Approved | |
| Margin Call Settlement | Cash margin posting, status updates | [ ] Approved | |
| Counterparty Master | Rating updates, KYC status management | [ ] Approved | |
| **Security Master** | **New security setup, rating updates, daily price imports** | [ ] Approved | |
| Daily Batch Monitoring | Verify accrued interest calc at 18:00 | [ ] Approved | |

**CRITICAL PROCESS - Requires Confirmation:**
> **BAHTNET Manual Settlement Process**
> 
> Current design: System generates MT103 file → Back Office downloads → Manual upload to BAHTNET portal → Confirm → Update system status
> 
> [ ] **CONFIRMED** - Manual process is acceptable  
> [ ] **REQUIREMENT** - Need automated BAHTNET integration  
> [ ] **TIMELINE** - Manual for MVP, automate in Phase 2  
> [ ] Comment: ___________________________

---

### IT Admin Team

| Item | Description | Status | Comments |
|------|-------------|--------|----------|
| ~~Security Master Setup~~ | ~~Moved to Back Office~~ | N/A | See Back Office section |
| Portfolio Configuration | Create portfolios with Treasury/Accounting approval | [ ] Approved | |
| User Management | Create users, assign roles, password policy | [ ] Approved | |
| Reference Data | BANK_CODE, Haircut Table, Holiday Calendar | [ ] Approved | |
| Emergency Access | Super user access for emergency fixes (with approval) | [ ] Approved | |
| System Configuration | ThaiBMA API settings, technical infrastructure | [ ] Approved | |

**Open Decision:**
> **Password Policy**
> 
> Current status: Deferred to security policy document
> 
| Requirement | Proposed Value | Approved |
|-------------|----------------|----------|
| Minimum length | 12 characters | [ ] |
| Complexity | Upper, lower, number, special | [ ] |
| Expiry | 90 days | [ ] |
| History | Last 5 cannot reuse | [ ] |
| Lockout | 5 failed = 30 min lockout | [ ] |
| Session timeout | 30 minutes idle | [ ] |

---

## 📊 Data Update Frequency Review

### Daily Batch Schedule (Working Days 17:00-19:30)

| Time | Process | System/Team | Back Office Confirm |
|------|---------|-------------|---------------------|
| 17:00 | Download ThaiBMA EOD prices | Back Office | [ ] |
| 17:15 | Validate price file | Back Office | [ ] |
| 17:30 | Import prices to security_master | Back Office | [ ] |
| 18:00 | **Calculate accrued interest** | System (Batch) | Monitor |
| 18:30 | Update bond_positions | System (Batch) | Verify |
| 19:00 | MTM valuation | System (Batch) | Verify |
| 19:30 | GL journal generation | System (Batch) | Verify |

**Questions:**
- [ ] Are the timings realistic for your operations?
- [ ] Who is the backup if primary Back Office staff is unavailable?
- [ ] What happens if ThaiBMA file is delayed/missing?

---

### Weekend/Holiday Handling

| Scenario | Current Design | Approved |
|----------|----------------|----------|
| Weekend | Use last ThaiBMA price + 2 days accrued interest | [ ] |
| Holiday | Use last ThaiBMA price + N days accrued interest | [ ] |
| First working day after long holiday | Import accumulated accrued interest | [ ] |

---

## 🔄 Special Scenarios Review

### 1. Margin Call Scenario (REPO)

**Process:** Daily MTM → Compare collateral vs exposure → Generate call → Settlement

| Step | Detail | Approved |
|------|--------|----------|
| Daily MTM at 17:00 | Update collateral market values from ThaiBMA | [ ] |
| Threshold breach | If collateral < exposure - threshold, generate call | [ ] |
| Due time | T+1 11:00 per GMRA terms | [ ] |
| Workflow | Pending → Agreed (Middle Office) → Settled (Back Office) | [ ] |

**Questions:**
- [ ] What is the threshold amount for margin calls? (GMRA Minimum Transfer Amount)
- [ ] Who in Middle Office approves margin calls?
- [ ] What if counterparty disputes the call?

---

### 2. Coupon Payment Scenario

**Process:** Auto-detect coupon date → Reset accrued_interest → Create transaction → GL entries

| Step | Detail | Approved |
|------|--------|----------|
| Auto-detection | System identifies positions with coupon payment date = today | [ ] |
| Accrued interest reset | Set to 0 for new accrual period | [ ] |
| Transaction creation | Create bond_transactions record with type='Coupon' | [ ] |
| GL entries | Generate journal entries for coupon received/paid | [ ] |

**Questions:**
- [ ] Are coupon dates automatically known from security_master?
- [ ] How are partial period coupons handled (if bond bought/sold between coupon dates)?

---

### 3. Bond Maturity Scenario

**Process:** Auto-detect maturity → Set status='Matured' → Archive position → Final redemption

| Step | Detail | Approved |
|------|--------|----------|
| Auto-detection | CURRENT_DATE > maturity_date | [ ] |
| Position status | Set to 'Matured' | [ ] |
| Transaction status | Set to 'Matured' | [ ] |
| Security status | Set to 'Matured' | [ ] |
| Archive | Remove from active positions view | [ ] |
| Final redemption | Generate GL entries | [ ] |

**Questions:**
- [ ] How many days after maturity should position be archived?
- [ ] Do you need maturity reminders (e.g., 1 week before)?

---

### 4. Collateral Substitution Scenario

| Step | Detail | Approved |
|------|--------|----------|
| Request | Initiate substitution request | [ ] |
| Validate | New collateral meets margin requirements | [ ] |
| Allocate | Create new collateral_positions record | [ ] |
| Release | Mark old collateral as released | [ ] |
| Recalculate | Update margin calculations | [ ] |

**Questions:**
- [ ] Who can initiate substitution? (Middle Office or Back Office?)
- [ ] Is substitution allowed during margin call period?

---

### 5. Limit Breach Scenario

| Step | Detail | Approved |
|------|--------|----------|
| Pre-trade check | Proposed utilization vs total credit line | [ ] |
| Hard block | Reject if > 100% of limit | [ ] |
| Warning | Alert if > 90% of limit (but allow) | [ ] |
| Utilization log | Append-only record created | [ ] |
| Maturity release | Negative utilization record on maturity | [ ] |

**Questions:**
- [ ] Should there be different limits for different products (bond vs interbank vs repo)?
- [ ] How often are credit limits reviewed/renewed?

---

## 📈 Regulatory Compliance Review

### BOT Reporting

| Report | Source Data | Status |
|--------|-------------|--------|
| DER_CPEN | entity_master, counterparty_master, bond_positions | [ ] Confirmed |
| ThaiBMA Trade Reporting | bond_trades (within 30 min) | [ ] Confirmed |
| LCR HQLA | security_master (is_eligible_crm_collateral) | [ ] Confirmed |

### ECL/TFRS 9 Scope

> **CONFIRMED OUT OF SCOPE**
> 
> ECL calculation is handled by existing Risk/Finance system. This treasury system only provides raw data feeds.

| Data Provided | Destination |
|---------------|-------------|
| bond_positions | Risk system |
| interbank_deals | Risk system |
| repo_trades | Risk system |
| counterparty_master | Risk system |

[ ] **CONFIRMED** - ECL out of scope is correct

---

## 📝 Open Items Requiring Decision

### High Priority (Block Sprint 3 if not resolved)

| # | Item | Current Status | Decision Needed By |
|---|------|----------------|-------------------|
| 1 | Four-eyes approval threshold | All transactions | Before Sprint 3 |
| 2 | BAHTNET integration approach | Manual upload | Before Sprint 3 |
| 3 | Margin call threshold amount | Not defined | Before Sprint 3 |

### Medium Priority (Can be decided during Sprint 3)

| # | Item | Current Status | Decision Needed By |
|---|------|----------------|-------------------|
| 4 | Password policy specifications | Deferred | Before UAT |
| 5 | Data retention period | Not defined | Before production |
| 6 | IT Admin emergency procedure | Not defined | Before production |
| 7 | Position archive timing (post-maturity) | Not defined | Before Sprint 4 |

---

## 👥 Sign-Off

### Front Office (Trading)
| Role | Name | Signature | Date |
|------|------|-----------|------|
| Head of Trading | | | |
| Senior Trader | | | |

### Middle Office (Risk)
| Role | Name | Signature | Date |
|------|------|-----------|------|
| Head of Risk | | | |
| Risk Manager | | | |

### Back Office (Operations)
| Role | Name | Signature | Date |
|------|------|-----------|------|
| Head of Operations | | | |
| Settlement Officer | | | |
| Accounting Manager | | | |

### IT
| Role | Name | Signature | Date |
|------|------|-----------|------|
| IT Manager | | | |
| System Architect | | | |
| DBA | | | |

### Management
| Role | Name | Signature | Date |
|------|------|-----------|------|
| Treasury Head | | | |
| Project Sponsor | | | |

---

## 🚀 Post-Review Actions

### If Approved
1. [ ] Update documentation with any feedback
2. [ ] Proceed to Sprint 3: Interbank + Repo implementation
3. [ ] Schedule daily standups for Sprint 3
4. [ ] Assign sprint tasks to developers

### If Changes Required
1. [ ] Document all required changes in comments
2. [ ] Prioritize changes (Must Have vs Nice to Have)
3. [ ] Update Field Update Matrix if field changes needed
4. [ ] Schedule follow-up review meeting
5. [ ] Delay Sprint 3 start until documentation approved

---

## 📧 Feedback Collection

Please provide feedback via:
1. **Email:** Reply to project team with completed checklist
2. **Comments:** Add comments directly in this document
3. **Meeting:** Schedule 1-hour review meeting with all stakeholders

**Feedback Deadline:** _______________

**Next Steps Meeting:** _______________

---

*This checklist ensures all stakeholders validate the design before implementation proceeds.*
