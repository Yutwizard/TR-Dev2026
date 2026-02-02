-- =============================================================================
-- Treasury Management System - Database Initialization Script
-- This script runs automatically when PostgreSQL container starts
-- =============================================================================

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================================
-- MASTER DATA TABLES
-- =============================================================================

-- Entity Master (Obligor level)
CREATE TABLE IF NOT EXISTS entity_master (
    entity_id VARCHAR(40) PRIMARY KEY,
    entity_name VARCHAR(255) NOT NULL,
    entity_short_name VARCHAR(10),
    entity_type VARCHAR(50),
    industry_sector VARCHAR(50),
    country_code CHAR(3) DEFAULT 'THA',
    juristic_registration_number VARCHAR(20),
    registered_capital_amount DECIMAL(20,2),
    g_sib_type CHAR(1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Counterparty Master
CREATE TABLE IF NOT EXISTS counterparty_master (
    counterparty_id VARCHAR(40) PRIMARY KEY,
    entity_id VARCHAR(40) REFERENCES entity_master(entity_id),
    legal_name VARCHAR(255) NOT NULL,
    short_code VARCHAR(50),
    counterparty_type VARCHAR(50),
    bank_code VARCHAR(13),
    swift_bic VARCHAR(11),
    primary_credit_rating VARCHAR(10),
    primary_rating_agency VARCHAR(50),
    primary_rating_date DATE,
    involved_party_type INT,
    customer_code VARCHAR(10),
    reside_in_thailand_flag BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Security Master (ThaiBMA aligned)
CREATE TABLE IF NOT EXISTS security_master (
    security_id VARCHAR(10),
    isin VARCHAR(12),
    issuer_id VARCHAR(40),
    unique_id VARCHAR(20),
    instrument_type VARCHAR(20),
    issue_date DATE,
    maturity_date DATE,
    coupon_rate DECIMAL(5,2),
    coupon_frequency VARCHAR(20),
    coupon_day_count_conv VARCHAR(20) DEFAULT 'Actual/365',
    currency CHAR(3) DEFAULT 'THB',
    country CHAR(2) DEFAULT 'TH',
    bond_structure VARCHAR(50),
    rating_tris VARCHAR(10),
    rating_fitch VARCHAR(10),
    is_eligible_bot_repo_collateral BOOLEAN DEFAULT FALSE,
    is_eligible_crm_collateral BOOLEAN DEFAULT FALSE,
    coupon_rate_type VARCHAR(10) DEFAULT 'Fixed',
    cross_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (security_id, isin)
);

-- Portfolio Master (TFRS 9)
CREATE TABLE IF NOT EXISTS portfolio_master (
    portfolio_id VARCHAR(40) PRIMARY KEY,
    portfolio_name VARCHAR(100) NOT NULL,
    portfolio_type VARCHAR(50), -- HOLD_TO_COLLECT, HOLD_TO_COLLECT_AND_SELL, TRADING
    accounting_classification VARCHAR(50), -- AMORTIZED_COST, FVOCI, FVTPL
    business_model VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Netting Agreement
CREATE TABLE IF NOT EXISTS netting_agreement (
    netting_agreement_id VARCHAR(40) PRIMARY KEY,
    counterparty_id VARCHAR(40) REFERENCES counterparty_master(counterparty_id),
    agreement_type VARCHAR(50), -- ISDA, GMRA
    effective_date DATE,
    expiry_date DATE,
    margin_threshold DECIMAL(20,2),
    rounding_amount DECIMAL(20,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- =============================================================================
-- TRANSACTION TABLES
-- =============================================================================

-- Interbank Deals
CREATE TABLE IF NOT EXISTS interbank_deals (
    deal_id VARCHAR(40) PRIMARY KEY,
    counterparty_id VARCHAR(40) REFERENCES counterparty_master(counterparty_id),
    limit_id VARCHAR(40),
    entity_id VARCHAR(40) REFERENCES entity_master(entity_id),
    deal_type VARCHAR(10) NOT NULL, -- LEND, BORROW
    currency CHAR(3) DEFAULT 'THB',
    principal_amount DECIMAL(20,2) NOT NULL,
    interest_rate DECIMAL(7,4),
    rate_type VARCHAR(10) DEFAULT 'FIXED', -- FIXED, FLOATING
    benchmark_rate VARCHAR(10), -- THOR
    spread_bp INT,
    value_date DATE NOT NULL,
    maturity_date DATE NOT NULL,
    tenor_days INT,
    settlement_account VARCHAR(20),
    status VARCHAR(20) DEFAULT 'ACTIVE', -- ACTIVE, MATURED, CANCELLED
    created_by VARCHAR(50),
    approved_by VARCHAR(50),
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Interbank Interest Schedule
CREATE TABLE IF NOT EXISTS interbank_interest_schedule (
    schedule_id VARCHAR(40) PRIMARY KEY,
    deal_id VARCHAR(40) REFERENCES interbank_deals(deal_id),
    period_start_date DATE NOT NULL,
    period_end_date DATE NOT NULL,
    benchmark_rate DECIMAL(7,4),
    effective_rate DECIMAL(7,4),
    accrued_interest DECIMAL(20,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Repo Trades
CREATE TABLE IF NOT EXISTS repo_trades (
    repo_trade_id VARCHAR(40) PRIMARY KEY,
    counterparty_id VARCHAR(40) REFERENCES counterparty_master(counterparty_id),
    netting_agreement_id VARCHAR(40) REFERENCES netting_agreement(netting_agreement_id),
    limit_id VARCHAR(40),
    entity_id VARCHAR(40) REFERENCES entity_master(entity_id),
    trade_type VARCHAR(20) NOT NULL, -- REPO, REVERSE_REPO
    trade_date DATE NOT NULL,
    value_date DATE NOT NULL,
    maturity_date DATE,
    tenor_days INT,
    currency CHAR(3) DEFAULT 'THB',
    nominal_amount DECIMAL(20,2) NOT NULL,
    repo_rate DECIMAL(7,4),
    repo_rate_type VARCHAR(10) DEFAULT 'FIXED',
    haircut_percent DECIMAL(5,2),
    collateral_market_value DECIMAL(20,2),
    settlement_amount DECIMAL(20,2),
    open_repo_flag BOOLEAN DEFAULT FALSE,
    call_date DATE,
    settlement_system VARCHAR(20), -- BAHTNET, TSD
    status VARCHAR(20) DEFAULT 'OPEN', -- OPEN, CLOSED, MATURED
    created_by VARCHAR(50),
    approved_by VARCHAR(50),
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Collateral Positions
CREATE TABLE IF NOT EXISTS collateral_positions (
    collateral_id VARCHAR(40) PRIMARY KEY,
    repo_trade_id VARCHAR(40) REFERENCES repo_trades(repo_trade_id),
    security_id VARCHAR(10),
    isin VARCHAR(12),
    collateral_quantity DECIMAL(20,2),
    market_value DECIMAL(20,2),
    haircut_applied DECIMAL(5,2),
    margin_value DECIMAL(20,2),
    valuation_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (security_id, isin) REFERENCES security_master(security_id, isin)
);

-- Bond Trades
CREATE TABLE IF NOT EXISTS bond_trades (
    trade_id VARCHAR(40) PRIMARY KEY,
    portfolio_id VARCHAR(40) REFERENCES portfolio_master(portfolio_id),
    security_id VARCHAR(10),
    isin VARCHAR(12),
    counterparty_id VARCHAR(40) REFERENCES counterparty_master(counterparty_id),
    trade_type VARCHAR(10) NOT NULL, -- BUY, SELL
    trade_date DATE NOT NULL,
    settlement_date DATE NOT NULL,
    nominal_amount DECIMAL(20,2) NOT NULL,
    clean_price DECIMAL(10,6),
    accrued_interest DECIMAL(20,2),
    dirty_price DECIMAL(10,6),
    settlement_amount DECIMAL(20,2),
    yield_to_maturity DECIMAL(10,6),
    settlement_system VARCHAR(20), -- TSD, BAHTNET
    trader_id VARCHAR(20),
    status VARCHAR(20) DEFAULT 'CREATED', -- CREATED, CONFIRMED, SETTLED, CANCELLED
    thaibma_reported BOOLEAN DEFAULT FALSE,
    thaibma_report_timestamp TIMESTAMP,
    created_by VARCHAR(50),
    approved_by VARCHAR(50),
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (security_id, isin) REFERENCES security_master(security_id, isin)
);

-- =============================================================================
-- POSITION & ANALYTICAL TABLES
-- =============================================================================

-- Bond Positions
CREATE TABLE IF NOT EXISTS bond_positions (
    position_id VARCHAR(40) PRIMARY KEY,
    security_id VARCHAR(10),
    isin VARCHAR(12),
    portfolio_id VARCHAR(40) REFERENCES portfolio_master(portfolio_id),
    position_date DATE NOT NULL,
    nominal_amount DECIMAL(20,2),
    average_cost DECIMAL(20,6),
    book_cost DECIMAL(20,2),
    amortized_cost DECIMAL(20,2),
    accrued_interest DECIMAL(20,2),
    market_value DECIMAL(20,2),
    unrealized_pnl DECIMAL(20,2),
    ecl_stage INT DEFAULT 1, -- 1, 2, 3
    ecl_provision DECIMAL(20,2) DEFAULT 0,
    carrying_amount DECIMAL(20,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (security_id, isin) REFERENCES security_master(security_id, isin)
);

-- Position Costing
CREATE TABLE IF NOT EXISTS position_costing (
    costing_id VARCHAR(40) PRIMARY KEY,
    position_id VARCHAR(40) REFERENCES bond_positions(position_id),
    total_nominal_purchased DECIMAL(20,2),
    total_cost DECIMAL(20,2),
    weighted_avg_cost DECIMAL(20,6),
    cumulative_realized_pnl DECIMAL(20,2),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Position Realization Events (Append-only)
CREATE TABLE IF NOT EXISTS position_realization_events (
    realization_id VARCHAR(40) PRIMARY KEY,
    position_id VARCHAR(40) REFERENCES bond_positions(position_id),
    trade_id VARCHAR(40) REFERENCES bond_trades(trade_id),
    realization_date DATE NOT NULL,
    nominal_amount_sold DECIMAL(20,2),
    sale_clean_price DECIMAL(20,6),
    wac_at_sale DECIMAL(20,6),
    realized_pnl DECIMAL(20,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- CONTROL & RISK MANAGEMENT TABLES
-- =============================================================================

-- Limit Utilization (Append-only audit log)
CREATE TABLE IF NOT EXISTS limit_utilization (
    utilization_id BIGSERIAL PRIMARY KEY,
    limit_id VARCHAR(40) NOT NULL,
    counterparty_id VARCHAR(40) REFERENCES counterparty_master(counterparty_id),
    entity_id VARCHAR(40) REFERENCES entity_master(entity_id),
    limit_type VARCHAR(50), -- SINGLE_TXN, AGGREGATE, TENOR, CONCENTRATION, REPO
    limit_amount DECIMAL(20,2),
    utilized_before DECIMAL(20,2),
    utilized_after DECIMAL(20,2),
    available_before DECIMAL(20,2),
    available_after DECIMAL(20,2),
    utilization_percent DECIMAL(5,2),
    transaction_id VARCHAR(40),
    transaction_type VARCHAR(50),
    event_type VARCHAR(50), -- NEW_TRADE, MATURITY, CANCELLATION
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50)
);

-- Margin Calls
CREATE TABLE IF NOT EXISTS margin_calls (
    margin_call_id VARCHAR(40) PRIMARY KEY,
    counterparty_id VARCHAR(40) REFERENCES counterparty_master(counterparty_id),
    repo_trade_id VARCHAR(40) REFERENCES repo_trades(repo_trade_id),
    valuation_date DATE NOT NULL,
    exposure_amount DECIMAL(20,2),
    collateral_value DECIMAL(20,2),
    net_exposure DECIMAL(20,2),
    threshold_amount DECIMAL(20,2),
    margin_call_amount DECIMAL(20,2),
    margin_call_type VARCHAR(20), -- DELIVERY, RETURN
    status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, AGREED, SETTLED, DISPUTED
    due_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cash Margin Movements
CREATE TABLE IF NOT EXISTS cash_margin_movements (
    cash_margin_movement_id VARCHAR(40) PRIMARY KEY,
    margin_call_id VARCHAR(40) REFERENCES margin_calls(margin_call_id),
    counterparty_id VARCHAR(40) REFERENCES counterparty_master(counterparty_id),
    movement_type VARCHAR(20), -- POST, RECEIVE, RETURN, ADJUST
    currency CHAR(3) DEFAULT 'THB',
    amount DECIMAL(20,2),
    interest_rate DECIMAL(7,4),
    accrued_interest DECIMAL(20,2),
    outstanding_balance DECIMAL(20,2),
    settlement_date DATE,
    bahtnet_reference VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- USER & AUTHENTICATION TABLES
-- =============================================================================

-- Users
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(40) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(50) NOT NULL, -- TRADER, SUPERVISOR, RISK_OFFICER, ADMIN
    department VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit Log
CREATE TABLE IF NOT EXISTS audit_log (
    audit_id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(40),
    action VARCHAR(50) NOT NULL,
    table_name VARCHAR(50),
    record_id VARCHAR(40),
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(45),
    user_agent VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- REFERENCE DATA TABLES
-- =============================================================================

-- Thai Business Days Calendar
CREATE TABLE IF NOT EXISTS thai_calendar (
    calendar_date DATE PRIMARY KEY,
    is_business_day BOOLEAN NOT NULL,
    is_holiday BOOLEAN DEFAULT FALSE,
    holiday_name VARCHAR(100),
    day_of_week INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- THOR Rate History (for floating rate deals)
CREATE TABLE IF NOT EXISTS thor_rate_history (
    rate_date DATE PRIMARY KEY,
    thor_rate DECIMAL(7,4) NOT NULL,
    source VARCHAR(50) DEFAULT 'BOT',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Haircut Matrix
CREATE TABLE IF NOT EXISTS haircut_matrix (
    haircut_id SERIAL PRIMARY KEY,
    collateral_type VARCHAR(50) NOT NULL,
    tenor_min_years INT,
    tenor_max_years INT,
    initial_haircut DECIMAL(5,2),
    variation_margin DECIMAL(5,2),
    effective_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Counterparty lookups
CREATE INDEX IF NOT EXISTS idx_counterparty_bank_code ON counterparty_master(bank_code);
CREATE INDEX IF NOT EXISTS idx_counterparty_entity ON counterparty_master(entity_id);

-- Trade date lookups
CREATE INDEX IF NOT EXISTS idx_bond_trades_date ON bond_trades(trade_date);
CREATE INDEX IF NOT EXISTS idx_bond_trades_settlement ON bond_trades(settlement_date);
CREATE INDEX IF NOT EXISTS idx_bond_trades_status ON bond_trades(status);
CREATE INDEX IF NOT EXISTS idx_interbank_deals_date ON interbank_deals(value_date);
CREATE INDEX IF NOT EXISTS idx_interbank_deals_maturity ON interbank_deals(maturity_date);
CREATE INDEX IF NOT EXISTS idx_repo_trades_date ON repo_trades(value_date);
CREATE INDEX IF NOT EXISTS idx_repo_trades_maturity ON repo_trades(maturity_date);

-- Position lookups
CREATE INDEX IF NOT EXISTS idx_bond_positions_date ON bond_positions(position_date);
CREATE INDEX IF NOT EXISTS idx_bond_positions_security ON bond_positions(security_id, isin);

-- Limit utilization
CREATE INDEX IF NOT EXISTS idx_limit_utilization_counterparty ON limit_utilization(counterparty_id);
CREATE INDEX IF NOT EXISTS idx_limit_utilization_timestamp ON limit_utilization(event_timestamp);

-- Calendar lookups
CREATE INDEX IF NOT EXISTS idx_thai_calendar_business ON thai_calendar(is_business_day);

-- =============================================================================
-- INSERT DEFAULT DATA
-- =============================================================================

-- Default Portfolios
INSERT INTO portfolio_master (portfolio_id, portfolio_name, portfolio_type, accounting_classification, business_model)
VALUES 
    ('TRADING', 'Trading Portfolio', 'TRADING', 'FVTPL', 'Trading'),
    ('HTM', 'Hold to Maturity', 'HOLD_TO_COLLECT', 'AMORTIZED_COST', 'Hold to collect contractual cash flows'),
    ('AFS', 'Available for Sale', 'HOLD_TO_COLLECT_AND_SELL', 'FVOCI', 'Hold to collect and sell')
ON CONFLICT (portfolio_id) DO NOTHING;

-- Default Admin User (password: admin123 - CHANGE IN PRODUCTION!)
INSERT INTO users (user_id, username, email, hashed_password, full_name, role, department)
VALUES 
    ('ADMIN001', 'admin', 'admin@bank.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X.rF7fCKtJ1.JGf/O', 'System Administrator', 'ADMIN', 'IT')
ON CONFLICT (user_id) DO NOTHING;

-- Default Haircut Matrix (BOT Standard)
INSERT INTO haircut_matrix (collateral_type, tenor_min_years, tenor_max_years, initial_haircut, variation_margin, effective_date)
VALUES 
    ('GOV_BOND', 0, 5, 1.00, 0.75, '2025-01-01'),
    ('GOV_BOND', 5, 10, 1.50, 1.00, '2025-01-01'),
    ('GOV_BOND', 10, 20, 2.50, 2.00, '2025-01-01'),
    ('GOV_BOND', 20, 99, 3.00, 2.00, '2025-01-01'),
    ('SOE_BOND', 0, 5, 1.50, 1.00, '2025-01-01'),
    ('SOE_BOND', 5, 10, 3.00, 2.00, '2025-01-01'),
    ('SOE_BOND', 10, 20, 4.50, 3.00, '2025-01-01'),
    ('SOE_BOND', 20, 99, 5.50, 3.00, '2025-01-01')
ON CONFLICT DO NOTHING;

-- =============================================================================
-- Grant permissions
-- =============================================================================
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO tms_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO tms_user;

-- =============================================================================
-- Success message
-- =============================================================================
DO $$
BEGIN
    RAISE NOTICE '✅ Treasury Management System database initialized successfully!';
    RAISE NOTICE '📊 Tables created: 20+';
    RAISE NOTICE '🔑 Default admin user: admin / admin123';
    RAISE NOTICE '⚠️  Remember to change default password in production!';
END $$;
