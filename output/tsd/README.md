# TSD Output Directory

This directory contains settlement instructions for TSD (Thailand Securities Depository) for **manual submission**.

## Generated Files

| File Pattern | Instruction Type | Usage |
|--------------|------------------|-------|
| `TSD_DVP_*.json` | DVP Settlement | Bond buy/sell settlement |
| `TSD_FOP_*.json` | Free of Payment | Collateral transfer/return |

## Workflow

1. **System generates** settlement instructions based on confirmed trades
2. **Back Office reviews** the instruction details
3. **Back Office enters** into TSD system manually
4. **Back Office updates** settlement status after TSD confirmation

## Instruction Types

### DVP (Delivery vs Payment)
- Used for bond purchase/sale settlement
- Securities move against cash payment
- Counterparty DVP matching required

### FoP (Free of Payment)
- Used for collateral transfer
- Securities move without cash
- Used for repo collateral allocation/return

## Important Notes

⚠️ **No API Integration** - Instructions are for manual TSD entry.

⚠️ **Matching Required** - DVP requires counterparty to enter matching instruction.

⚠️ **Cutoff Times** - Be aware of TSD settlement cutoff times (14:00, 16:00).
