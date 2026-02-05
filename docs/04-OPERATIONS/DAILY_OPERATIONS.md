# Daily Operations Manual

**For:** Back Office Operations Team  
**Frequency:** Every Working Day  
**Critical Path:** ThaiBMA import must complete before 18:00 batch

---

## 📋 Daily Schedule Overview

### Normal Working Day

| Time | Activity | Duration | Critical |
|------|----------|----------|----------|
| **08:00-09:00** | Pre-market checks | 1 hour | ⚠️ |
| **09:00-17:00** | Market hours support | 8 hours | |
| **17:00-17:30** | ThaiBMA price download | 30 min | 🔴 |
| **17:30-18:00** | Import & validation | 30 min | 🔴 |
| **18:00-19:30** | EOD batch processing | 1.5 hours | 🔴 |

### Month-End Day (Extended)

| Time | Activity | Note |
|------|----------|------|
| **17:30-18:00** | Monitor ThaiBMA portal | Later release |
| **18:00-18:30** | Download & validate | Delayed start |
| **18:30-19:50** | EOD batch processing | +20 min delay |

---

## 🌅 Pre-Market (08:00 - 09:00)

### System Health Check
- [ ] Database connectivity check
- [ ] Application server status
- [ ] Previous day batch completion verified
- [ ] No overnight errors in logs

### Reconciliation
- [ ] Previous day settlements confirmed
- [ ] Exception items reviewed
- [ ] Pending items followed up

---

## 🏢 Market Hours (09:00 - 17:00)

### Primary Responsibilities
1. **Settlement Processing**
   - Monitor TSD/BAHTNET confirmations
   - Update settlement_status in system
   - Handle failed settlements

2. **Collateral Management**
   - Allocate collateral for new repos
   - Process substitution requests
   - Monitor margin call notifications

3. **Support Trading Operations**
   - Answer settlement queries
   - Provide trade confirmations
   - Handle counterparty inquiries

---

## 📥 ThaiBMA Price Import (17:00 - 18:00)

### Step 1: Download (17:00 Normal / 17:30-18:00 Month-End)

**Normal Day:**
```
1. Login to ThaiBMA portal: https://www.thaibma.or.th
2. Navigate: Market Data → EOD Prices
3. Download: THAIBMA_MTM_YYYYMMDD.csv
4. Save to: [designated folder]
```

**Month-End Day:**
```
1. Start monitoring from 17:30
2. ThaiBMA typically releases later due to:
   - Higher trading volume processing
   - Month-end reconciliation
   - Additional validation
3. Download as soon as available
4. Notify team of potential delay
```

### Step 2: Validate (17:15 Normal / 18:00-18:15 Month-End)

**Validation Checklist:**
- [ ] All active securities have prices
- [ ] No zero or null prices
- [ ] Price movements within thresholds:
  - ±5%: Warning (log and continue)
  - ±10%: Alert (notify Middle Office)
  - ±20%: Hard stop (investigate)
- [ ] File date matches trading date
- [ ] File format correct (CSV)

**Exception Handling:**
| Issue | Action |
|-------|--------|
| Missing price | Use last available + alert |
| Zero price | Manual lookup required |
| >±20% movement | Escalate to Risk Manager |
| Corrupt file | Contact ThaiBMA support |

### Step 3: Import (17:30 Normal / 18:15-18:30 Month-End)

**Procedure:**
```
1. Login to Treasury System
2. Navigate: Market Data → Import
3. Select file: THAIBMA_MTM_YYYYMMDD.csv
4. Click "Validate & Import"
5. Review import log
6. Confirm success
```

**Tables Updated:**
- `bond_positions.clean_price`
- `bond_positions.market_rate`
- `collateral_positions.valuation_price`

---

## ⚙️ EOD Batch Processing (18:00 - 19:30)

### Batch Schedule

| Time | Process | System Action | Verify |
|------|---------|---------------|--------|
| **18:00** | Accrued Interest Calc | Calculate for all positions | ⏱️ |
| **18:30** | Position Build | Update quantities, WAC | ⏱️ |
| **19:00** | MTM Valuation | Update market values | ⏱️ |
| **19:30** | GL Generation | Create journal entries | ⏱️ |

**Month-End Times:**
- Start: 18:30 (30 min delay)
- Complete: ~19:50

### Verification Checklist

**After Accrued Interest (18:30 / 18:50 Month-End):**
- [ ] `bond_positions.accrued_interest` updated
- [ ] `interbank_deals.accrued_interest` updated
- [ ] `repo_trades.accrued_interest` updated
- [ ] No calculation errors in log

**After Position Build:**
- [ ] `bond_positions.book_value` updated
- [ ] `bond_positions.dirty_price` calculated

**After MTM Valuation:**
- [ ] `bond_positions.market_value` updated
- [ ] `bond_positions.unrealized_gain_loss` calculated
- [ ] `collateral_positions.market_value` updated
- [ ] Margin calls generated (if any)

**After GL Generation:**
- [ ] Journal entries created
- [ ] Accounting team notified
- [ ] Month-end: Notify of completion time

---

## 🚨 Exception Handling

### Stale Prices
```
Condition: Price not updated for >1 day
Action:
  1. Check ThaiBMA portal for missing security
  2. If ThaiBMA has price: Re-import
  3. If ThaiBMA missing: Use last price + flag
  4. Notify Risk Manager
```

### Batch Failure
```
Condition: EOD batch stops or errors
Action:
  1. Check error log
  2. Identify failing step
  3. Fix data issue if applicable
  4. Restart batch from failed step
  5. Notify IT if system error
  6. Document in incident log
```

### Missing ThaiBMA File
```
Condition: File not available by cutoff time
Action:
  1. Contact ThaiBMA support
  2. If delay confirmed:
     a. Notify Accounting of GL delay
     b. Use last available prices
     c. Run batch with stale prices
     d. Re-run with new prices when available
```

---

## 📊 End of Day Sign-Off

**Before Leaving:**
- [ ] All batches completed successfully
- [ ] Exception report reviewed
- [ ] No pending critical items
- [ ] Handover notes for next shift (if applicable)
- [ ] Incident log updated (if any)

**Sign-Off Format:**
```
Date: [YYYY-MM-DD]
ThaiBMA Import: ✅ Completed / ⚠️ Exceptions
Batch Status: ✅ All Complete / ❌ Issues
Exceptions: [List any]
Handover: [Notes for next shift]
Signed: [Name]
```

---

## 📞 Escalation Contacts

| Issue | Primary Contact | Escalation |
|-------|-----------------|------------|
| ThaiBMA portal issues | ThaiBMA Support | - |
| Price validation | Middle Office | Risk Manager |
| Batch failures | IT Support | IT Manager |
| Settlement issues | Settlement Lead | Operations Manager |
| System errors | IT Support | IT Manager |

---

## 🔄 Monthly Tasks

### Month-End Day
- Extended schedule (see above)
- Additional reconciliation checks
- Notify Accounting of potential delay
- Complete GL by 19:50

### First Working Day of Month
- Verify all month-end processes completed
- Check for any carry-forward issues
- Review month-end reports

---

## 📚 Related Documents

- [Transaction Workflows](../02-PROCESSES/TRANSACTION_WORKFLOWS.md) - Detailed transaction steps
- [Pre-Transaction Setup](../02-PROCESSES/PRE_TRANSACTION_SETUP.md) - New client/bond setup
- [System Design](../01-DESIGN/SYSTEM_DESIGN.md) - Technical reference

---

**Document End**

*For technical details, see [System Design](../01-DESIGN/SYSTEM_DESIGN.md)*  
*For process workflows, see [Transaction Workflows](../02-PROCESSES/TRANSACTION_WORKFLOWS.md)*
