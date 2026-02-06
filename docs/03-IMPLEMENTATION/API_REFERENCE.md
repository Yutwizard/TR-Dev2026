# API Reference

**Version:** 1.0  
**Date:** February 6, 2026  
**Base URL:** `http://localhost:8000/api/v1`

---

## Quick Reference

| Category | Base Path | Endpoints |
|----------|-----------|-----------|
| Authentication | `/auth` | 3 |
| Master Data | `/master` | 19 |
| Bond Trading | `/bond-trades` | 9 |
| Interbank | `/interbank` | 6 |
| Repo | `/repo` | 8 |
| Positions | `/positions` | 4 |
| Market Data | `/market-data` | 3 |
| Settlement | `/settlement` | 2 |
| **Total** | | **54** |

---

## 1. API Conventions

| Convention | Standard |
|------------|----------|
| Protocol | REST over HTTPS |
| Data Format | JSON |
| Date Format | `YYYY-MM-DD` (ISO 8601) |
| Timestamp | `YYYY-MM-DDTHH:MM:SS+07:00` |
| Decimal | Amount: 2 dp, Price: 6 dp |

### Request Headers
```http
Content-Type: application/json
Authorization: Bearer <access_token>
```

---

## 2. Authentication

### POST /auth/login
```json
// Request
{"username": "trader001", "password": "********"}

// Response
{"access_token": "eyJ...", "token_type": "bearer", "expires_in": 1800}
```

### POST /auth/refresh
```json
{"refresh_token": "eyJ..."}
```

---

## 3. Master Data APIs

### Entities
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/master/entities` | List entities |
| GET | `/master/entities/{id}` | Get entity |
| POST | `/master/entities` | Create entity |
| PUT | `/master/entities/{id}` | Update entity |

### Counterparties
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/master/counterparties` | List counterparties |
| GET | `/master/counterparties/{id}` | Get counterparty |
| POST | `/master/counterparties` | Create counterparty |
| PUT | `/master/counterparties/{id}` | Update counterparty |

### Securities
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/master/securities` | List securities |
| GET | `/master/securities/{id}` | Get security |
| GET | `/master/securities/isin/{isin}` | Get by ISIN |
| POST | `/master/securities` | Create security |
| PUT | `/master/securities/{id}` | Update security |

### Portfolios
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/master/portfolios` | List portfolios |
| GET | `/master/portfolios/{id}` | Get portfolio |
| POST | `/master/portfolios` | Create portfolio |
| PUT | `/master/portfolios/{id}` | Update portfolio |

### Haircuts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/master/haircuts` | List haircut matrix |
| GET | `/master/haircuts/lookup` | Lookup by security |

---

## 4. Bond Trading APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/bond-trades` | List trades |
| GET | `/bond-trades/{id}` | Get trade |
| POST | `/bond-trades` | Create trade |
| POST | `/bond-trades/{id}/approve` | Approve trade |
| POST | `/bond-trades/{id}/cancel` | Cancel trade |
| POST | `/bond-trades/{id}/settle` | Settle trade |
| POST | `/bond-trades/{id}/thaibma-report` | Report to ThaiBMA |
| GET | `/bond-trades/pending-approval` | Pending approvals |
| GET | `/bond-trades/settlement/today` | Today's settlements |

### Create Trade Request
```json
{
    "portfolio_id": "TRADING",
    "security_id": "LB28DA",
    "counterparty_id": "CP001",
    "trade_type": "BUY",
    "trade_date": "2026-02-06",
    "settlement_date": "2026-02-08",
    "nominal_amount": 10000000.00,
    "clean_price_trade": 102.450000
}
```

### Validation Rules
- `trade_date`: Must be Thai business day
- `settlement_date`: Must be T+2
- `clean_price_trade`: Within ±20% of last price
- Counterparty KYC must be APPROVED

---

## 5. Interbank APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/interbank/deals` | List deals |
| GET | `/interbank/deals/{id}` | Get deal |
| POST | `/interbank/deals` | Create deal |
| POST | `/interbank/deals/{id}/approve` | Approve deal |
| GET | `/interbank/deals/{id}/schedule` | Interest schedule |
| GET | `/interbank/deals/maturing` | Maturing deals |

### Create Deal Request (Fixed Rate)
```json
{
    "counterparty_id": "CP002",
    "deal_type": "LEND",
    "principal_amount": 100000000.00,
    "interest_rate": 2.50,
    "rate_type": "FIXED",
    "value_date": "2026-02-06",
    "maturity_date": "2026-02-13"
}
```

### Create Deal Request (Floating Rate)
```json
{
    "counterparty_id": "CP002",
    "deal_type": "LEND",
    "principal_amount": 100000000.00,
    "rate_type": "FLOATING",
    "benchmark_rate": "THOR",
    "spread_bp": 25,
    "value_date": "2026-02-06",
    "maturity_date": "2026-05-06"
}
```

---

## 6. Repo APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/repo/trades` | List trades |
| GET | `/repo/trades/{id}` | Get trade |
| POST | `/repo/trades` | Create trade |
| POST | `/repo/trades/{id}/approve` | Approve trade |
| POST | `/repo/trades/{id}/collateral` | Allocate collateral |
| POST | `/repo/trades/{id}/collateral/substitute` | Substitute |
| POST | `/repo/trades/{id}/margin-process` | Process margin |
| GET | `/repo/margin-calls` | List margin calls |

### Create Repo Request
```json
{
    "counterparty_id": "CP001",
    "trade_type": "REPO",
    "purchase_date": "2026-02-06",
    "repurchase_date": "2026-02-07",
    "nominal_amount": 100000000.00,
    "repo_rate": 2.50
}
```

---

## 7. Position APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/positions/bonds` | Bond positions |
| GET | `/positions/bonds/{id}` | Position details |
| GET | `/positions/collateral` | Collateral positions |
| GET | `/positions/cash` | Cash positions |

---

## 8. Market Data APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/market-data/import` | Import ThaiBMA prices |
| GET | `/market-data/prices` | Get current prices |
| GET | `/market-data/prices/{id}/history` | Price history |

---

## 9. Settlement APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/settlement/today` | Today's settlements |
| POST | `/settlement/generate-instructions` | Generate SWIFT |

---

## 10. Error Codes

### HTTP Status Codes
| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Validation error |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Business rule violation |

### Business Error Codes
| Code | Description |
|------|-------------|
| `TRADE_001` | Settlement date must be T+2 |
| `TRADE_002` | Counterparty KYC not approved |
| `TRADE_003` | Price deviation exceeds threshold |
| `TRADE_005` | Cannot approve own trade |
| `LIMIT_001` | Insufficient credit limit |
| `COLL_001` | Insufficient collateral |
| `PRICE_001` | Price exceeds ±20% threshold |

---

## 11. Interactive Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

---

**Document End**

*For system design, see [System Design](../01-DESIGN/SYSTEM_DESIGN.md)*
