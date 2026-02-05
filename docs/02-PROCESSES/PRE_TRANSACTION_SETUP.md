# Pre-Transaction Setup Guide

**For:** Operations, Credit Risk, Compliance, and IT Teams  
**Purpose:** Step-by-step guide for onboarding new clients and setting up new bonds before trading

**Related Documents:**
- [Transaction Process Guide](./TRANSACTION_PROCESS_GUIDE.md) - Complete trading workflows
- [Field Update Matrix](./Field_Update_Matrix.md) - Field-level details
- [Treasury System Detailed Design Input](./Treasury_System_Detailed_Design_Input.md) - Team responsibilities

---

## Quick Overview

| Setup Type | Duration | Teams Involved | Blocking Factor |
|------------|----------|----------------|-----------------|
| **New Client** | 3-5 business days | BO → Risk → MO → Compliance | Cannot trade without KYC approval |
| **New Bond** | 1-2 business days | BO → IT | Cannot trade without price data |

---

## PART A: New Client/Counterparty Onboarding

### Why This Matters
**No counterparty can trade without completing this process.** The KYC approval is a hard gate.

---

### Step 1: Entity Master Setup (Back Office)

**Who:** Back Office Onboarding Team  
**Time:** 30 minutes  
**System:** Treasury Management System → Master Data → Entity

#### Actions:
1. Check if entity already exists in `entity_master` (avoid duplicates)
2. Click "Create New Entity"
3. Fill in required fields:

| Field | Description | Example | Required |
|-------|-------------|---------|----------|
| `entity_name` | Full legal name | Bangkok Bank Public Company Limited | ✅ |
| `entity_short_name` | Trading abbreviation | BBL | ✅ |
| `entity_type` | Basel classification | BANK | ✅ |
| `juristic_registration_number` | 13-digit Thai registration | 0107536000374 | ✅ |
| `country_code` | ISO country code | TH | ✅ |
| `registered_capital_amount` | Registered capital | 40000000000 | |
| `financials_currency` | Capital currency | THB | |

4. System auto-generates: `entity_id` = BBL0107536000374

#### Output:
- Entity record created
- Ready for counterparty setup

---

### Step 2: Counterparty Master Setup (Back Office)

**Who:** Back Office Onboarding Team  
**Time:** 30 minutes  
**System:** Treasury Management System → Master Data → Counterparty

#### Actions:
1. Select entity from Step 1
2. Click "Create Counterparty"
3. Fill in required fields:

| Field | Description | Example | Source |
|-------|-------------|---------|--------|
| `legal_name` | Full legal name | Bangkok Bank PCL | Legal docs |
| `short_code` | Trading code | BBL | Internal convention |
| `counterparty_type` | Type | Commercial Bank | Classification |
| `bank_code` | BOT bank code | 001 | BANK_CODE table |
| `swift_bic` | SWIFT code | BKKBTHBK | SWIFT directory |
| `primary_credit_rating` | Rating | AA+ | Latest rating |
| `primary_rating_agency` | Agency | TRIS Rating | Rating source |
| `primary_rating_date` | Rating date | 2025-07-15 | Rating date |
| `involved_party_type` | BOT code | 176039 | BOT reference |
| `customer_code` | Internal code | 2008 | Internal policy |
| `reside_in_thailand_flag` | Residency | TRUE | MFSMCG rule |

#### BOT Involved Party Type Reference:
| Code | Description |
|------|-------------|
| 176039 | Commercial Bank (Thai) |
| 176040 | Commercial Bank (Foreign) |
| 176015 | Government Agency |
| (Others) | See reference data table |

#### Output:
- Counterparty record created
- Status: PENDING (awaiting KYC)

---

### Step 3: Credit Risk Assessment (Credit Risk Team)

**Who:** Credit Risk Department  
**Time:** 1-2 business days  
**Input:** Entity documents, financial statements

#### Actions:
1. Review entity type and classification
2. Verify credit ratings (TRIS, Fitch, Moody's)
3. Conduct internal risk assessment
4. Prepare credit approval memo
5. Obtain signed approval from authorized person

#### Approval Levels:
| Exposure Amount | Approver |
|-----------------|----------|
| < 500M THB | Credit Manager |
| 500M - 2B THB | Head of Credit Risk |
| > 2B THB | Credit Committee |

#### Output:
- Credit approval document
- Approved `entity_type` and risk classification
- Go/no-go decision for trading

---

### Step 4: Limit Configuration (Middle Office)

**Who:** Middle Office Risk Manager  
**Time:** 30 minutes  
**System:** Treasury Management System → Limits → Configure

#### Actions:
1. Navigate to Limit Management
2. Select counterparty
3. Configure limits by type:

| Limit Type | Purpose | Typical Limit |
|------------|---------|---------------|
| PLACEMENT_LIMIT | Interbank lending/borrowing | 2,000,000,000 THB |
| REPO_LIMIT | Repo/Reverse Repo trading | 1,000,000,000 THB |
| SINGLE_TXN | Maximum single transaction | 500,000,000 THB |
| TENOR | Maximum maturity allowed | 365 days |

> **Note:** Limits are controlled at product level (PLACEMENT_LIMIT for interbank, REPO_LIMIT for repo). There is no aggregate cross-product limit.

4. Input fields:
   - `total_credit_line`: Approved amount
   - `currency`: THB
   - `credit_line_approve_date`: Committee approval date

5. System automatically:
   - Sets `available_line` = `total_credit_line`
   - Creates immutable `limit_utilization` record

#### Alert Thresholds:
| Utilization | Action |
|-------------|--------|
| 80% | Warning (Amber) |
| 90% | High Warning + Email/SMS |
| 100% | Hard Block - Trade Rejected |

#### Output:
- Limit configured and active
- Counterparty can trade (within limits)

---

### Step 5: Netting Agreement Setup (Back Office - If Repo Trading)

**Who:** Back Office Legal/Operations  
**Time:** 1-2 business days  
**Applies to:** Repo/Reverse Repo trading only

#### Actions:
1. Verify signed GMRA/CSA agreement exists
2. Navigate to Treasury Management System → Agreements → Netting
3. Create new agreement:

| Field | Description | Example |
|-------|-------------|---------|
| `netting_agreement_id` | Agreement ID | GMRA_2023_BBL |
| `counterparty_id` | Counterparty | BBL |
| `agreement_type` | Type | GMRA |
| `netting_type` | Netting style | CLOSE_OUT |
| `collateral_contract_type` | Collateral | REP |
| `trade_date` | Signature date | 2023-06-15 |
| `value_date` | Effective date | 2023-07-01 |
| `maturity_date` | Expiry date | 2025-06-30 |
| `settlement_currency` | Currency | THB |
| `agreement_status` | Status | Active |

#### Output:
- Agreement record created
- Counterparty eligible for repo trading

---

### Step 6: KYC Approval (Compliance)

**Who:** Compliance Team  
**Time:** 1-2 business days  
**This is the FINAL GATE before trading**

#### Required Documents:
| Document | Purpose |
|----------|---------|
| Commercial Registration | Legal existence |
| Board Resolution | Trading authorization |
| Audited Financials | Financial health |
| Banking License | Regulatory approval |
| Authorized Signatories | Who can bind the entity |

#### Actions:
1. Collect all KYC documents
2. Verify document authenticity
3. Conduct AML/Compliance checks
4. Update `counterparty_master`:
   - KYC status = 'APPROVED'
   - Approval date
   - Expiry date (annual renewal)
5. Notify all teams:
   - 📧 Back Office: Ready for trading
   - 📧 Front Office: Can now trade with counterparty
   - 📧 Middle Office: Monitor limits

#### KYC Status Values:
| Status | Meaning | Trading Allowed? |
|--------|---------|------------------|
| PENDING | Under review | ❌ NO |
| APPROVED | Cleared for trading | ✅ YES |
| REJECTED | Cannot trade | ❌ NO |
| SUSPENDED | Temporary halt | ❌ NO |

#### Output:
- **Counterparty READY for trading**
- Can be selected in trade entry screens

---

## PART B: New Bond Symbol Setup

### Why This Matters
**A bond cannot be traded until it's in the system with a price.** This must be done for every new bond issue.

---

### Step 1: Security Master Setup (Back Office)

**Who:** Back Office Security Master Administrator  
**Time:** 30 minutes  
**System:** Treasury Management System → Master Data → Securities

#### Actions:
1. Navigate to Security Master
2. Click "Create New Security"
3. Fill in bond details:

**Identification:**
| Field | Description | Example |
|-------|-------------|---------|
| `security_id` | ThaiBMA symbol | LB28DA |
| `isin` | ISIN code | TH0623038C09 |
| `issuer_id` | Issuer type | 1 (Government) |
| `unique_id` | BOT report ID | 001 |

**Issuer ID Mapping:**
| ID | Type | Unique ID Source |
|----|------|------------------|
| 1 | Government Thailand | Govt Agency code |
| 2 | Bank of Thailand | BANK_CODE |
| 3 | SOE | BANK_CODE |
| 4 | Corporate | - |

**Terms:**
| Field | Description | Example |
|-------|-------------|---------|
| `instrument_type` | Bond type | Gov Bond |
| `issue_date` | Issue date | 2024-01-15 |
| `maturity_date` | Maturity | 2029-01-15 |
| `bond_structure` | Structure | Bullet |

**Coupon:**
| Field | Description | Example |
|-------|-------------|---------|
| `coupon_rate` | Annual rate % | 3.50 |
| `coupon_rate_type` | Fixed/Floating | Fixed |
| `coupon_frequency` | Payment freq | Semi-Annual |
| `coupon_day_count_conv` | Convention | ACT/365 |

**Floating Rate (if applicable):**
| Field | Description | Example |
|-------|-------------|---------|
| `coupon_reference_rate` | Benchmark | THBFIX6M |
| `coupon_margin` | Spread % | 0.25 |

**Day Count Conventions:**
| Convention | Calculation | Common For |
|------------|-------------|------------|
| ACT/365 | Actual/365 | Most THB bonds |
| ACT/360 | Actual/360 | Some short-term |
| 30/360 | 30-day months | Some corporate |
| ACT/ACT | Actual/Actual | Government bonds |

**Ratings & Eligibility:**
| Field | Description | Example |
|-------|-------------|---------|
| `rating_tris` | TRIS rating | AAA |
| `rating_fitch` | Fitch rating | AAA(tha) |
| `is_eligible_bot_repo_collateral` | BOT repo eligible | TRUE |
| `is_eligible_crm_collateral` | CRM eligible | TRUE |
| `status` | Status | Active |

#### Validation Rules:
- ISIN: TH + 9 digits + check digit
- Maturity > Issue date
- Coupon >= 0 (0 for zero-coupon)
- If Floating: reference rate required

#### Output:
- Security record created
- Ready for haircut config

---

### Step 2: Haircut Configuration (Back Office)

**Who:** Back Office Collateral Manager  
**Time:** 15 minutes  
**Required if:** Bond is repo-eligible

#### Standard BOT Haircut Matrix:

| Collateral Type | 0-5 Years | 5-10 Years | 10-20 Years | >20 Years |
|-----------------|-----------|------------|-------------|-----------|
| **T-Bills, Gov Bonds** | 1.0% | 1.5% | 2.5% | 3.0% |
| **SOE (Gov Guaranteed)** | 1.5% | 3.0% | 4.5% | 5.5% |
| **Corporate AAA** | 5.0% | 10.0% | 15.0% | 20.0% |
| **Corporate AA** | 10.0% | 15.0% | 20.0% | 25.0% |

#### Actions:
1. Determine bond rating and tenor
2. Look up standard haircut %
3. Configure in `haircut_matrix` table
4. Test calculation:
   ```
   Collateral Value = Market Value × (1 - Haircut%)
   ```

#### Output:
- Haircut configured
- Bond can be used as repo collateral

---

### Step 3: System Configuration (IT Admin)

**Who:** IT Admin  
**Time:** 30 minutes  
**One-time setup per security**

#### Actions:
1. Configure ThaiBMA API mapping:
   - Map `security_id` to ThaiBMA feed
   - Verify price field mapping
2. Set up price import:
   - File format: `THAIBMA_MTM_YYYYMMDD.csv`
   - Schedule: Daily 17:00
3. Test connection:
   - Verify price retrieval
   - Check data quality

#### Output:
- API configuration complete
- Ready for automated price feeds

---

### Step 4: Initial Price Import (Back Office)

**Who:** Back Office Market Data  
**Time:** 15 minutes  
**Must complete before trading**

#### Actions:
1. Obtain initial price:
   - Source: ThaiBMA or prospectus
   - Price at issue: Usually 100.00%
2. Input to system:
   - Navigate: Market Data → Prices → Manual Entry
   - Field: `clean_price`
3. System calculates:
   - `accrued_interest` from issue date
   - `dirty_price` = Clean + Accrued

#### Output:
- Initial price in system
- Bond **READY for trading**

**Note:** After this, ThaiBMA EOD prices will update automatically daily at 17:00.

---

## Summary: Who Does What

### Back Office (Primary Owner)
| Task | When | System |
|------|------|--------|
| Entity setup | Onboarding | Master Data → Entity |
| Counterparty setup | Onboarding | Master Data → Counterparty |
| Netting agreement | If repo trading | Agreements → Netting |
| Security Master | New bond issue | Master Data → Securities |
| Haircut config | If repo eligible | Haircut Matrix |
| Initial price | Before trading | Market Data → Prices |
| Daily ThaiBMA import | Every working day 17:00 | Market Data → Import |

### Credit Risk Team
| Task | When |
|------|------|
| Credit assessment | After entity setup |
| Rating verification | Ongoing |

### Middle Office
| Task | When | System |
|------|------|--------|
| Limit configuration | After credit approval | Limits → Configure |

### Compliance
| Task | When |
|------|------|
| KYC review | After counterparty setup |
| Final approval | Before trading |

### IT Admin
| Task | When |
|------|------|
| System configuration | One-time setup |
| API configuration | Per new security |
| Technical support | As needed |

---

## Checklists

### Client Onboarding Checklist
- [ ] Entity created in `entity_master`
- [ ] Counterparty created in `counterparty_master`
- [ ] Credit risk assessment completed
- [ ] Limits configured
- [ ] Netting agreement (if repo)
- [ ] KYC status = 'APPROVED'
- [ ] Front Office notified

### Bond Setup Checklist
- [ ] Security Master record created
- [ ] All terms validated (dates, rates)
- [ ] Haircut configured (if repo eligible)
- [ ] IT configuration complete
- [ ] Initial price imported
- [ ] Available for trade entry

---

## Contact & Support

| Issue | Contact |
|-------|---------|
| System access | IT Admin |
| Credit limits | Middle Office |
| KYC questions | Compliance |
| ThaiBMA prices | Back Office Market Data |
| System errors | IT Support |

---

**Document Version:** 1.0  
**Last Updated:** February 3, 2026  
**Next Review:** After first month of go-live
