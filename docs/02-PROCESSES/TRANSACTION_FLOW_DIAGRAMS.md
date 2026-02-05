# Transaction Flow Diagrams

**Format:** Mermaid diagrams (renders automatically in GitHub/GitLab)  
**Purpose:** Visual process flows for easy understanding and communication

---

## 1. Bond Trade Flow (Buy/Sell)

### Overall Flow

```mermaid
flowchart TD
    Start([Start]) --> Entry[Step 1: Trade Entry<br/>Front Office]
    Entry --> Limit{Step 2: Limit Check<br/>System}
    Limit -->|Pass| Approve[Step 3: Four-Eyes Approval<br/>Middle Office]
    Limit -->|Fail| Reject1[Reject Trade]
    Approve -->|Approved| ThaiBMA[Step 4: ThaiBMA Reporting<br/>Within 30 min]
    Approve -->|Rejected| Reject2[Reject Trade]
    ThaiBMA --> Settlement[Step 5: Settlement<br/>Back Office T+2]
    Settlement --> Position[Step 6: Position Update<br/>System]
    Position --> EOD[Step 7: Daily EOD Batch<br/>Accrued Interest]
    EOD --> End([End])
    Reject1 --> End
    Reject2 --> End
```

### Detailed Steps

```mermaid
flowchart LR
    subgraph "Step 1: Trade Entry (FO)"
        E1[Select Portfolio]
        E2[Select Security]
        E3[Select Counterparty]
        E4[Input Nominal Amount]
        E5[Input Clean Price]
        E6[System calculates:<br/>- Settlement Date T+2<br/>- Yield to Maturity]
    end
    
    E1 --> E2 --> E3 --> E4 --> E5 --> E6
```

```mermaid
flowchart TD
    subgraph "Step 2: Limit Check (System)"
        L1[Check Counterparty Limit]
        L2{Proposed + Current<br/>> Total Credit Line?}
        L3[BLOCK:<br/>Limit Exceeded]
        L4{> 90% of Limit?}
        L5[WARNING:<br/>Approaching Limit]
        L6[PASS:<br/>Proceed to Approval]
        L7[Create Limit Utilization Record]
    end
    
    L1 --> L2
    L2 -->|Yes| L3
    L2 -->|No| L4
    L4 -->|Yes| L5 --> L6
    L4 -->|No| L6
    L6 --> L7
```

```mermaid
flowchart TD
    subgraph "Step 3: Four-Eyes Approval (MO)"
        A1[Middle Office Reviews Trade]
        A2{Decision}
        A3[APPROVE<br/>Status → APPROVED]
        A4[REJECT<br/>Status → REJECTED<br/>Reverse Limit Utilization]
        A5[Notify Front Office]
    end
    
    A1 --> A2
    A2 -->|Approve| A3
    A2 -->|Reject| A4
    A3 --> A5
    A4 --> A5
```

```mermaid
flowchart TD
    subgraph "Step 4: ThaiBMA Reporting (System/FO)"
        T1[Generate Trade Report]
        T2{Within 30 min<br/>of trade?}
        T3[Submit to ThaiBMA]
        T4[⚠️ LATE REPORT<br/>Flag for Compliance]
        T5[✅ Reported Successfully]
    end
    
    T1 --> T2
    T2 -->|Yes| T3
    T2 -->|No| T4
    T3 --> T5
```

```mermaid
flowchart TD
    subgraph "Step 5: Settlement (BO)"
        S1[T+2 Settlement Date]
        S2{Settlement System?}
        S3[TSD:<br/>SWIFT MT540/MT541]
        S4[BAHTNET:<br/>Manual Portal Upload]
        S5[Receive Confirmation]
        S6[Update Status:<br/>SETTLED]
        S7{Failed?}
        S8[Status: FAILED<br/>Exception Handling]
    end
    
    S1 --> S2
    S2 -->|Corporate Bond| S3
    S2 -->|Govt Bond| S4
    S3 --> S5
    S4 --> S5
    S5 --> S6
    S5 -->|No Confirm| S7
    S7 -->|Yes| S8
```

```mermaid
flowchart TD
    subgraph "Step 6: Position Update (System)"
        P1[Create/Update bond_positions]
        P2[Update position_costing]
        P3{Trade Type?}
        P4[BUY:<br/>- Increase Nominal<br/>- Recalculate WAC]
        P5[SELL:<br/>- Decrease Nominal<br/>- Calculate Realized P&L<br/>- Create realization_event]
    end
    
    P1 --> P2 --> P3
    P3 -->|Buy| P4
    P3 -->|Sell| P5
```

```mermaid
flowchart TD
    subgraph "Step 7: Daily EOD Batch (System 18:00)"
        D1[Calculate Accrued Interest<br/>Nominal × Coupon% × 1/365]
        D2[Update bond_positions<br/>accrued_interest]
        D3[Calculate Market Value<br/>(Price × Nominal/100) + Accrued]
        D4[Calculate Unrealized P&L<br/>Market Value - Book Value]
        D5[Generate GL Journals]
    end
    
    D1 --> D2 --> D3 --> D4 --> D5
```

---

## 2. Interbank Deal Flow (Lend/Borrow)

### Overall Flow

```mermaid
flowchart TD
    Start([Start]) --> Entry[Step 1: Deal Entry<br/>Front Office]
    Entry --> Limit{Step 2: Limit Check<br/>System}
    Limit -->|Pass| Approve[Step 3: Approval<br/>Middle Office]
    Limit -->|Fail| Reject1[Reject]
    Approve -->|Approved| Settlement[Step 4: Settlement<br/>Back Office]
    Approve -->|Rejected| Reject2[Reject]
    Settlement --> Accrual[Step 5: Daily Accrual<br/>System 18:00]
    Accrual --> Maturity{Maturity Date?}
    Maturity -->|Yes| Close[Step 6: Maturity<br/>Principal + Interest]
    Maturity -->|No| Accrual
    Close --> End([End])
    Reject1 --> End
    Reject2 --> End
```

### Detailed Steps

```mermaid
flowchart LR
    subgraph "Step 1: Deal Entry (FO)"
        IE1[Select Deal Type:<br/>LEND or BORROW]
        IE2[Select Counterparty]
        IE3[Input Principal Amount]
        IE4[Input Value Date &<br/>Maturity Date]
        IE5[Select Rate Type:<br/>FIXED or FLOATING]
        IE6[Input Interest Rate<br/>(or Reference Rate + Margin)]
        IE7[System calculates Term]
    end
    
    IE1 --> IE2 --> IE3 --> IE4 --> IE5 --> IE6 --> IE7
```

```mermaid
flowchart TD
    subgraph "Step 5: Daily Accrual & Step 6: Maturity"
        IA1[Daily at 18:00]
        IA2{Is it<br/>Reset Date?}
        IA3[Update Interest Rate<br/>Reference Rate + Margin]
        IA4[Calculate Daily Accrual<br/>Principal × Rate × 1/365]
        IA5{Maturity Date<br/>Reached?}
        IA6[Receive/Pay Principal<br/>+ Accrued Interest]
        IA7[Update Status:<br/>MATURED]
        IA8[Release Limit]
    end
    
    IA1 --> IA2
    IA2 -->|Yes| IA3 --> IA4
    IA2 -->|No| IA4
    IA4 --> IA5
    IA5 -->|Yes| IA6 --> IA7 --> IA8
    IA5 -->|No| IA1
```

---

## 3. Repo Trade Flow (Repo/Reverse Repo)

### Overall Flow

```mermaid
flowchart TD
    Start([Start]) --> Entry[Step 1: Trade Entry<br/>Front Office]
    Entry --> Limit{Step 2: Limit Check<br/>System}
    Limit -->|Pass| Approve[Step 3: Approval<br/>Middle Office]
    Limit -->|Fail| Reject1[Reject]
    Approve -->|Approved| Collateral[Step 4: Collateral Allocation<br/>Back Office]
    Approve -->|Rejected| Reject2[Reject]
    Collateral --> Settlement1[Step 5: Settlement<br/>First Leg]
    Settlement1 --> Active[Status: ACTIVE]
    Active --> MTM[Step 6: Daily MTM<br/>System 17:00]
    MTM --> Margin{Margin Check}
    Margin -->|Threshold Breached| Call[Step 7: Margin Call<br/>MO → BO]
    Margin -->|OK| Accrual[Step 8: Daily Accrual<br/>System 18:00]
    Call --> Accrual
    Accrual --> Maturity{Maturity Date?}
    Maturity -->|Yes| Settlement2[Step 9: Settlement<br/>Second Leg + Release]
    Maturity -->|No| MTM
    Settlement2 --> End([End])
    Reject1 --> End
    Reject2 --> End
```

### Detailed Steps

```mermaid
flowchart LR
    subgraph "Step 4: Collateral Allocation (BO)"
        C1[Calculate Required Collateral<br/>Nominal / (1 - Haircut)]
        C2[Select Securities<br/>from Inventory]
        C3[Apply Haircut %
by Rating/Tenor]
        C4{Collateral Value<br/>>= Repo Exposure?}
        C5[✅ Allocate Collateral]
        C6[❌ Request More<br/>or Different Securities]
    end
    
    C1 --> C2 --> C3 --> C4
    C4 -->|Yes| C5
    C4 -->|No| C6 --> C2
```

```mermaid
flowchart TD
    subgraph "Step 6: Daily MTM & Step 7: Margin Call"
        M1[Daily at 17:00]
        M2[Update Collateral Prices<br/>from ThaiBMA]
        M3[Recalculate Collateral Value<br/>After Haircut]
        M4[Compare to Repo Exposure]
        M5{Collateral < Exposure<br/>- Threshold?}
        M6[✅ No Action Required]
        M7[🚨 Create Margin Call]
        M8[Set Call Amount<br/>Set Due Time T+1 11:00]
        M9[MO Agreement]
        M10[BO Settlement]
    end
    
    M1 --> M2 --> M3 --> M4 --> M5
    M5 -->|No| M6
    M5 -->|Yes| M7 --> M8 --> M9 --> M10
```

```mermaid
flowchart TD
    subgraph "Step 9: Maturity/Second Leg"
        R1[Repurchase Date Reached]
        R2[Calculate Final Amount<br/>Principal + Accrued Interest]
        R3{Trade Type?}
        R4[REPO:<br/>Pay Cash + Interest<br/>Receive Securities]
        R5[REVERSE REPO:<br/>Receive Cash + Interest<br/>Return Securities]
        R6[Release Collateral]
        R7[Update Status:<br/>MATURED]
        R8[Release Limit]
    end
    
    R1 --> R2 --> R3
    R3 -->|Repo| R4
    R3 -->|Reverse Repo| R5
    R4 --> R6
    R5 --> R6
    R6 --> R7 --> R8
```

---

## 4. Client Onboarding Flow

### Overall Flow

```mermaid
flowchart TD
    Start([Start]) --> S1[Step 1: Entity Setup<br/>Back Office]
    S1 --> S2[Step 2: Counterparty Setup<br/>Back Office]
    S2 --> S3[Step 3: Credit Risk Assessment<br/>Credit Risk Team]
    S3 -->|Approved| S4[Step 4: Limit Configuration<br/>Middle Office]
    S3 -->|Rejected| Reject[Reject Onboarding]
    S4 --> S5[Step 5: Netting Agreement<br/>Back Office<br/>(if Repo trading)]
    S5 --> S6[Step 6: KYC Approval<br/>Compliance]
    S6 -->|Approved| End([✅ Ready to Trade])
    S6 -->|Rejected| Reject
    Reject --> End2([❌ Onboarding Failed])
```

### Timeline

```mermaid
gantt
    title Client Onboarding Timeline (3-5 Business Days)
    dateFormat  YYYY-MM-DD
    section Back Office
    Entity Setup           :a1, 2026-02-01, 1d
    Counterparty Setup     :a2, after a1, 1d
    Netting Agreement      :a5, after a4, 1d
    section Credit Risk
    Credit Assessment      :a3, after a2, 2d
    section Middle Office
    Limit Configuration    :a4, after a3, 1d
    section Compliance
    KYC Approval           :a6, after a5, 1d
```

---

## 5. New Bond Setup Flow

### Overall Flow

```mermaid
flowchart TD
    Start([Start]) --> B1[Step 1: Security Master Setup<br/>Back Office]
    B1 --> B2[Step 2: Haircut Configuration<br/>Back Office<br/>(if Repo eligible)]
    B2 --> B3[Step 3: System Configuration<br/>IT Admin]
    B3 --> B4[Step 4: Initial Price Import<br/>Back Office]
    B4 --> End([✅ Ready for Trading])
```

### Timeline

```mermaid
gantt
    title New Bond Setup Timeline (1-2 Business Days)
    dateFormat  YYYY-MM-DD
    section Back Office
    Security Master Setup      :b1, 2026-02-01, 1d
    Haircut Configuration      :b2, after b1, 4h
    Initial Price Import       :b4, after b3, 2h
    section IT Admin
    System Configuration       :b3, after b2, 4h
```

---

## 6. Daily Operations Flow

### End-to-End Daily Process

```mermaid
flowchart TD
    subgraph "Morning (08:00-09:00)"
        AM1[Pre-Market Checks]
        AM2[System Health Check]
        AM3[Previous Day Reconciliation]
    end
    
    subgraph "Market Hours (09:00-17:00)"
        MH1[Settlement Processing]
        MH2[Collateral Management]
        MH3[Trading Support]
    end
    
    subgraph "Post-Market Normal Day (17:00-19:30)"
        PM1[17:00: Download ThaiBMA]
        PM2[17:15: Validate Prices]
        PM3[17:30: Import Prices]
        PM4[18:00: Accrued Interest Calc]
        PM5[18:30: Position Build]
        PM6[19:00: MTM Valuation]
        PM7[19:30: GL Journals]
    end
    
    subgraph "Post-Market Month-End (17:30-19:50)"
        ME1[17:30-18:00: Monitor ThaiBMA]
        ME2[18:15: Import Prices]
        ME3[18:30: Batch Start]
        ME4[19:50: Complete + Notify]
    end
    
    AM1 --> AM2 --> AM3 --> MH1 --> MH2 --> MH3
    MH3 --> PM1 --> PM2 --> PM3 --> PM4 --> PM5 --> PM6 --> PM7
    MH3 -->|Month-End| ME1 --> ME2 --> ME3 --> ME4
```

### ThaiBMA Import Detail

```mermaid
flowchart TD
    subgraph "Normal Day"
        N1[17:00: Login ThaiBMA Portal] --> N2[Download EOD File]
        N2 --> N3[17:15: Validate Prices]
        N3 --> N4{Price Movement?}
        N4 -->|±5-10%| N5[⚠️ Warning - Continue]
        N4 -->|±10-20%| N6[🚨 Alert - MO Approval]
        N4 -->|>±20%| N7[🛑 STOP - Risk Manager]
        N4 -->|OK| N8[17:30: Import to System]
    end
    
    subgraph "Month-End Day"
        M1[17:30: Start Monitoring] --> M2[Wait for Release]
        M2 --> M3[18:00: Download File]
        M3 --> M4[18:15: Validate & Import]
    end
```

---

## Status Icons Legend

| Icon | Meaning |
|------|---------|
| ✅ | Success / Complete |
| ❌ | Failure / Reject |
| ⚠️ | Warning |
| 🚨 | Alert |
| 🛑 | Hard Stop |
| ⏱️ | Time-sensitive |

---

## Team Abbreviations

| Abbreviation | Team |
|--------------|------|
| FO | Front Office (Trading) |
| MO | Middle Office (Risk) |
| BO | Back Office (Operations) |
| IT | IT Admin |

---

**Document End**

*For detailed process descriptions, see [Transaction Workflows](./TRANSACTION_WORKFLOWS.md)*  
*For field definitions, see [Field Reference](../01-DESIGN/FIELD_REFERENCE.md)*
