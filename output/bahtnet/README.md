# BAHTNET Output Directory

This directory contains ISO20022 BAHTNET payment messages for **manual upload** to the BAHTNET portal.

## Generated Files

| File Pattern | Message Type | Usage |
|--------------|--------------|-------|
| `BAHTNET_*_CT.xml` | pacs.008 Credit Transfer | Interbank lending, repo payments |
| `BAHTNET_*_DD.xml` | pacs.009 Direct Debit | Interbank borrowing receipts |

## Workflow

1. **System generates** XML files based on trade settlement instructions
2. **User downloads** the files from this directory
3. **User uploads** to BAHTNET portal manually
4. **User updates** settlement status in system after confirmation

## Message Format

- Standard: ISO20022
- Messages: pacs.008.001.08, pacs.009.001.08
- Currency: THB only

## Important Notes

⚠️ **No API Integration** - BAHTNET does not provide API access for standard banks.

⚠️ **Manual Verification** - Always verify message content before uploading.

⚠️ **File Retention** - Files should be archived for audit purposes.
