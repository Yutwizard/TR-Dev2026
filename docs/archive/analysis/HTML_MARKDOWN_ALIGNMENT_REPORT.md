# Transaction Flow Documentation Alignment Report

**Generated:** February 5, 2026  
**Files Analyzed:**
- `docs/02-PROCESSES/transaction_flow.html` (HTML Portal)
- `docs/02-PROCESSES/TRANSACTION_WORKFLOWS.md`
- `docs/02-PROCESSES/PRE_TRANSACTION_SETUP.md`

---

## Executive Summary

This report identifies discrepancies between the HTML Transaction Flow Portal and the two Markdown workflow documents. The HTML portal provides a simplified visual interface with 7 main categories, while the Markdown documents contain more detailed step-by-step instructions with field-level specifications.

### Key Finding
**The HTML portal is missing 2 entire workflow categories** that exist in the Markdown documentation and contains several step number and team responsibility inconsistencies.

---

## 1. Missing from HTML Portal (Critical Gaps)

### 1.1 Portfolio Setup Flow ❌ MISSING

| Attribute | Details |
|-----------|---------|
| **Location in Markdown** | TRANSACTION_WORKFLOWS.md Section 0.5 / PRE_TRANSACTION_SETUP.md PART C |
| **Teams Involved** | IT Admin → Treasury Approval |
| **Duration** | 1 business day |
| **Purpose** | Create new trading portfolios with accounting classification (AMC/FVOCI/FVTPL) before trading |

**Key Steps in Markdown (NOT in HTML):**
1. Portfolio Creation (IT Admin)
   - Input `portfolio_name`, `portfolio_manager`, `accounting_treatment`
   - Verify treasury approval
   - System generates `portfolio_id`

**Impact:** Front Office cannot assign trades to portfolios without this setup.

---

### 1.2 Entity-Counterparty Mapping Setup ❌ MISSING

| Attribute | Details |
|-----------|---------|
| **Location in Markdown** | TRANSACTION_WORKFLOWS.md Section 0.6 / PRE_TRANSACTION_SETUP.md PART D |
| **Teams Involved** | Back Office → Middle Office |
| **Duration** | Part of onboarding process |
| **Purpose** | Required for consolidated limit management and BOT DER_CPEN regulatory reporting |

**Key Steps in Markdown (NOT in HTML):**
1. Create Entity-Counterparty Link (Back Office)
   - Select `entity_id` and `counterparty_id`
   - Set `parent_limit_id`, effective dates, status
   - System generates `entity_counterparty_id`

**HTML Gap:** HTML "Client Onboarding" only shows Steps 1-6 but completely omits this mapping step between Entity Setup (Step 1) and Counterparty Setup (Step 2).

---

### 1.3 Scheduled Events Section ❌ MISSING

| Attribute | Details |
|-----------|---------|
| **Location in Markdown** | TRANSACTION_WORKFLOWS.md Section 4 |
| **Events Covered** | Coupon Payment, Bond Maturity, Bond Transactions Lifecycle |
| **Trigger** | System-driven (date-based) |

**Missing Processes:**
- **4.1 Coupon Payment Process:** System auto-calculates coupon, creates transaction, resets accrued interest
- **4.2 Bond Maturity Process:** System identifies maturities, updates status across multiple tables
- **4.3 Bond Transactions Lifecycle:** Tracks all bond-related transactions with daily updates

---

## 2. Flow/Step Number Discrepancies

### 2.1 Client Onboarding Flow

| Step | HTML Portal | TRANSACTION_WORKFLOWS.md | PRE_TRANSACTION_SETUP.md | Status |
|------|-------------|--------------------------|--------------------------|--------|
| 1 | Entity Setup (BO) | Step 1: Initial Data Collection | Step 1: Entity Master Setup | ✅ Aligned |
| 2 | Counterparty Setup (BO) | Step 2: Counterparty Setup | Step 2: Counterparty Master Setup | ✅ Aligned |
| - | **MISSING** | Step 3: Credit Risk Assessment | Step 3: Credit Risk Assessment | ⚠️ HTML skips credit assessment as separate step |
| 3 | Credit Assessment (Risk) | (combined in flow) | (detailed in PART A) | ⚠️ HTML labels as "Step 3" but shows "Credit Risk Team" |
| 4 | Limit Configuration (MO) | Step 4: Limit Configuration | Step 4: Limit Configuration | ✅ Aligned |
| 5 | Netting Agreement (BO) | Step 5: Netting Agreement Setup | Step 5: Netting Agreement Setup | ✅ Aligned |
| 6 | KYC Completion (Compliance) | Step 6: KYC Completion | Step 6: KYC Approval | ✅ Aligned |

**Discrepancy:** HTML labels "Credit Assessment" as "Step 3" but TRANSACTION_WORKFLOWS.md shows it as a separate Step 3 with 5 detailed actions (3.1-3.5).

---

### 2.2 Bond Trade Flow

| Step | HTML Portal | TRANSACTION_WORKFLOWS.md | Status |
|------|-------------|--------------------------|--------|
| 1 | Trade Entry (FO) | Step 1: Trade Entry (FO) | ✅ Aligned |
| 2 | Limit Check (System) | Step 2: Pre-Trade Limit Check (System) | ✅ Aligned |
| 3 | Four-Eyes Approval (MO) | Step 3: Four-Eyes Approval (MO) | ✅ Aligned |
| 4 | ThaiBMA Reporting (System/FO) | Step 4: ThaiBMA Reporting (System/FO) | ✅ Aligned |
| 5 | Settlement (BO) | Step 5: Settlement Preparation + Step 6: Settlement Confirmation | ⚠️ **HTML merges 2 steps into 1** |
| 6 | Position Update (System) | Step 7: Position Update (System) | ✅ Aligned |
| 7 | Daily EOD Batch (System) | Step 8: Daily EOD Batch (System) | ⚠️ **Step number off by 1** |

**Key Discrepancy:** TRANSACTION_WORKFLOWS.md splits settlement into **two separate steps** (Step 5: Preparation, Step 6: Confirmation) with different responsible teams, while HTML combines them as a single "Step 5."

---

### 2.3 Interbank Deal Flow

| Step | HTML Portal | TRANSACTION_WORKFLOWS.md | Status |
|------|-------------|--------------------------|--------|
| 1 | Deal Entry (FO) | Step 1: Deal Entry (FO) | ✅ Aligned |
| 2 | Limit Check (System) | Step 2: Limit Check & Approval (MO) | ⚠️ **HTML splits; Markdown combines** |
| 3 | Approval (MO) | (combined in Step 2) | ⚠️ HTML has separate Step 3 |
| 4 | Settlement (BO) | Step 3: Settlement (BO) | ⚠️ **Step number mismatch** |
| 5 | Daily Accrual (System) | Step 4: Daily Accrual (System) | ⚠️ **Step number off by 1** |
| 6 | Maturity (System+BO) | Step 5: Maturity (System+BO) | ⚠️ **Step number off by 1** |

**Key Discrepancy:**
- HTML separates Limit Check (Step 2) and Approval (Step 3)
- TRANSACTION_WORKFLOWS.md combines them as "Step 2: Limit Check & Approval"
- This causes a **cascade step number offset** (HTML Steps 4-6 = Markdown Steps 3-5)

---

### 2.4 Repo Trade Flow

| Step | HTML Portal | TRANSACTION_WORKFLOWS.md | Status |
|------|-------------|--------------------------|--------|
| 1 | Trade Entry (FO) | Step 1: Trade Entry (FO) | ✅ Aligned |
| 2 | Limit Check (System) | Step 2: Limit Check & Approval (MO) | ⚠️ **Different step names** |
| 3 | Approval (MO) | (combined in Step 2) | ⚠️ HTML splits; Markdown combines |
| 4 | Collateral Allocation (BO) | Step 3: Collateral Allocation (BO) | ⚠️ **Step number mismatch** |
| 5 | Settlement 1st Leg (BO) | Step 4: Settlement - First Leg (BO) | ⚠️ **Step number off by 1** |
| 6 | Daily MTM (System) | Step 5: Daily Margin Management (System) | ⚠️ **Step number off by 1** |
| 7 | Margin Call (System/MO/BO) | Step 6: Margin Call Workflow (MO+BO) | ⚠️ **Step number off by 1** |
| 8 | Daily Accrual (System) | Step 8: Daily Accrual (System) | ⚠️ **Step number off by 2** |
| 9 | Settlement 2nd Leg (BO) | Step 9: Maturity/Repurchase (BO) | ⚠️ **Step number off by 1** |

**Major Discrepancy:** TRANSACTION_WORKFLOWS.md includes **Step 7: Collateral Substitution** (Optional) that HTML completely omits from its flow.

---

### 2.5 New Bond Setup Flow

| Step | HTML Portal | TRANSACTION_WORKFLOWS.md | PRE_TRANSACTION_SETUP.md | Status |
|------|-------------|--------------------------|--------------------------|--------|
| 1 | Security Master Setup (BO) | Step 1: Security Master Setup | PART B Step 1 | ✅ Aligned |
| 2 | Haircut Configuration (BO) | Step 2: Haircut Configuration | PART B Step 2 | ✅ Aligned |
| 3 | System Configuration (IT) | Step 3: System Configuration | PART B Step 3 | ✅ Aligned |
| 4 | Initial Price Import (BO) | Step 4: Initial Price Import | PART B Step 4 | ✅ Aligned |

**Status:** ✅ Fully aligned across all documents.

---

## 3. Team Responsibility Differences

### 3.1 Bond Trade Settlement

| Process | HTML Responsibility | Markdown Responsibility | Discrepancy |
|---------|---------------------|------------------------|-------------|
| Settlement | "Back Office T+2" | Step 5: Settlement Preparation (BO) + Step 6: Settlement Confirmation (BO) | HTML oversimplifies as single step |
| Settlement System | "TSD: SWIFT MT540/MT541" "BAHTNET: Manual Portal Upload" | Detailed MT103 process for BAHTNET | Markdown provides detailed file upload process |

### 3.2 Repo Trade Margin Management

| Process | HTML | TRANSACTION_WORKFLOWS.md | Discrepancy |
|---------|------|--------------------------|-------------|
| Daily MTM | "Step 6: Daily MTM" | "Step 5: Daily Margin Management (System)" | Step number different; Markdown specifies time (17:00) |
| Margin Call | Simple diagram node | Steps 6a (MO) + 6b (BO) with 11 sub-steps | HTML significantly oversimplifies |
| Cash Margin Interest | Not mentioned | Detailed accrual calculation | Missing in HTML |

### 3.3 Daily Operations

| Process | HTML | TRANSACTION_WORKFLOWS.md | Discrepancy |
|---------|------|--------------------------|-------------|
| ThaiBMA Download | "17:00: Download ThaiBMA" | Step 1: 17:00 (Normal) / 17:30-18:00 (Month-end) | HTML misses month-end timing |
| Price Validation | "17:15: Validate Prices" | Step 2: ±5%, ±10%, >±20% thresholds with approval levels | HTML lacks detail |
| Import Prices | "17:30: Import Prices" | Step 3: Import with field mappings | HTML lacks field-level detail |
| Batch Schedule | Listed as 18:00-19:30 | Detailed 18:00, 18:30, 19:00, 19:30 with durations | HTML lacks granularity |

---

## 4. Content Detail Discrepancies

### 4.1 Field-Level Specifications

| Document | Detail Level | Example |
|----------|--------------|---------|
| **HTML** | High-level actions only | "Input Nominal Amount" |
| **TRANSACTION_WORKFLOWS.md** | Field-level with validation | "`nominal_amount` > 0, multiple of 1,000" |
| **PRE_TRANSACTION_SETUP.md** | Field-level with examples | "`juristic_registration_number`: 0107536000374" |

### 4.2 Validation Rules

| Flow | HTML | TRANSACTION_WORKFLOWS.md |
|------|------|--------------------------|
| Bond Trade Entry | "System calculates: Settlement Date T+2" | Business day check, KYC status, ±10% price warning |
| Interbank Deal | "Input Term" | System calculates from value/maturity dates |
| Repo Collateral | "Apply Haircut %" | Detailed formula: Nominal / (1 - Haircut) |

### 4.3 System vs Manual Actions

**TRANSACTION_WORKFLOWS.md** uses emoji legend:
- 👤 Manual Action
- ⚙️ System Action
- ✅ Validation
- 📧 Notification

**HTML** does not distinguish between manual and system actions in the flow diagrams.

---

## 5. Structural/Organization Issues

### 5.1 Section Ordering

**PRE_TRANSACTION_SETUP.md has unusual ordering:**
- PART A: New Client/Counterparty Onboarding
- PART C: Portfolio Setup (should be B)
- PART D: Entity-Counterparty Mapping (should be C)
- PART E: Market Data Management (should be D)
- PART B: New Bond Symbol Setup (should be E)

**Recommendation:** Reorder PRE_TRANSACTION_SETUP.md sections to match logical sequence (A, B, C, D, E).

### 5.2 Pre-Transaction Checklist

- **TRANSACTION_WORKFLOWS.md Section 0.4:** Comprehensive checklist with 14 items (6 client + 4 bond + 4 market data)
- **HTML:** No equivalent checklist exists

---

## 6. Detailed Alignment Matrix

### Pre-Transaction Setup

| Component | HTML | T-WORKFLOWS | PRE-SETUP | Priority |
|-----------|------|-------------|-----------|----------|
| Client Onboarding (0.1) | ✅ 6 steps | ✅ 6 steps | ✅ PART A | Medium |
| New Bond Setup (0.2) | ✅ 4 steps | ✅ 4 steps | ✅ PART B | Low |
| Market Data - Index Rate (0.3.1) | ⚠️ Mentioned | ✅ Detailed | ✅ PART E.1 | Medium |
| Market Data - Bond MTM (0.3.2) | ⚠️ High-level | ✅ Detailed | ✅ PART E.2 | Medium |
| Pre-Transaction Checklist (0.4) | ❌ Missing | ✅ Present | ❌ Missing | **High** |
| Portfolio Setup (0.5) | ❌ Missing | ✅ Detailed | ✅ PART C | **High** |
| Entity-Counterparty Mapping (0.6) | ❌ Missing | ✅ Detailed | ✅ PART D | **High** |

### Transaction Flows

| Component | HTML | T-WORKFLOWS | Step Match | Priority |
|-----------|------|-------------|------------|----------|
| Bond Trade (1) | 7 steps | 8 steps | ⚠️ Partial | Medium |
| Interbank Deal (2) | 6 steps | 5 steps | ❌ Mismatch | Medium |
| Repo Trade (3) | 9 steps | 9 steps | ⚠️ Partial | Medium |
| Scheduled Events (4) | ❌ Missing | ✅ Detailed | N/A | **High** |

---

## 7. Recommendations

### 7.1 High Priority (Add to HTML)

1. **Add Portfolio Setup Flow** as new category #8
   - Step 1: Portfolio Creation (IT Admin)
   - Include accounting treatment options (AMC/FVOCI/FVTPL)

2. **Add Entity-Counterparty Mapping** to Client Onboarding
   - Insert between Step 2 and Step 3
   - Show link creation for consolidated limit management

3. **Add Scheduled Events Section**
   - Coupon Payment Process
   - Bond Maturity Process
   - Bond Transactions Lifecycle

4. **Add Pre-Transaction Checklist** as reference material

### 7.2 Medium Priority (Align Step Numbers)

1. **Bond Trade:** Split HTML Step 5 (Settlement) into Step 5 (Preparation) and Step 6 (Confirmation) to match Markdown
2. **Interbank:** Align step numbering (HTML Step 2-3 → Markdown Step 2)
3. **Repo:** Add missing Step 7 (Collateral Substitution) to HTML

### 7.3 Low Priority (Enhance Detail)

1. Add field-level validation rules to HTML diagrams
2. Distinguish manual vs system actions with icons/colors
3. Add month-end timing note to Daily Operations
4. Include approval threshold details (±5%, ±10%, >±20%)

---

## 8. Quick Reference: What's Where

| Feature | HTML | T-WORKFLOWS | PRE-SETUP |
|---------|------|-------------|-----------|
| Visual Flow Diagrams | ✅ | ⚠️ ASCII only | ❌ |
| Field-Level Details | ❌ | ✅ | ✅ |
| Step-by-Step Actions | ⚠️ High-level | ✅ Detailed | ✅ Detailed |
| System Automation Notes | ⚠️ Minimal | ✅ Detailed | ⚠️ Partial |
| Team Responsibilities | ✅ | ✅ | ✅ |
| Validation Rules | ❌ | ✅ | ⚠️ Partial |
| Checklists | ❌ | ✅ | ✅ |
| Gantt Charts | ✅ | ❌ | ❌ |
| Legend/Status Icons | ✅ | ✅ | ❌ |

---

## Conclusion

The HTML Transaction Flow Portal provides an excellent **visual overview** for quick reference but is missing critical setup workflows and contains step numbering inconsistencies. The Markdown documents serve as the **authoritative detailed reference** with field-level specifications.

**Immediate Action Required:**
1. Add Portfolio Setup and Entity-Counterparty Mapping to HTML
2. Add Scheduled Events section to HTML
3. Align step numbering across all documents

**End of Report**
