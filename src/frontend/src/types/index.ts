/**
 * Treasury Management System - TypeScript Types
 */

// =============================================================================
// User & Auth
// =============================================================================
export interface User {
    user_id: string;
    username: string;
    email: string;
    full_name: string;
    role: UserRole;
    is_active: boolean;
}

export type UserRole = 'ADMIN' | 'SUPERVISOR' | 'FRONT_OFFICE' | 'MIDDLE_OFFICE' | 'BACK_OFFICE' | 'READONLY';

export interface AuthToken {
    access_token: string;
    token_type: string;
    expires_in: number;
}

export interface LoginCredentials {
    username: string;
    password: string;
}

// =============================================================================
// Security & Master Data
// =============================================================================
export interface Security {
    security_id: string;
    isin: string;
    symbol?: string;
    security_name: string;
    security_type: SecurityType;
    issuer_id?: string;
    issuer_name?: string;
    issue_date: string;
    maturity_date: string;
    coupon_rate: number;
    coupon_frequency: number;
    face_value: number;
    currency: string;
    credit_rating?: string;
    is_tradeable: boolean;
    is_repo_eligible: boolean;
    tenor_days?: number;
    is_zero_coupon: boolean;
}

export type SecurityType = 'GOVERNMENT_BOND' | 'CORPORATE_BOND' | 'TREASURY_BILL' | 'BOT_BOND' | 'STATE_ENTERPRISE_BOND';

export interface Counterparty {
    counterparty_id: string;
    counterparty_name: string;
    short_name?: string;
    counterparty_type: string;
    bot_code?: string;
    credit_limit?: number;
    is_active: boolean;
}

export interface Entity {
    entity_id: string;
    entity_name: string;
    entity_type: string;
    bot_code?: string;
    swift_bic?: string;
}

export interface Portfolio {
    portfolio_id: string;
    portfolio_code: string;
    portfolio_name: string;
    entity_id: string;
    portfolio_type: string;
    tfrs9_classification: string;
}

// =============================================================================
// Bond Trades
// =============================================================================
export interface BondTrade {
    trade_ref: string;
    trade_type: 'BUY' | 'SELL';
    trade_side: 'BUY' | 'SELL';
    entity_id: string;
    counterparty_id: string;
    counterparty_name: string;
    portfolio_id: string;
    security_id: string;
    isin: string;
    security_name?: string;
    trade_date: string;
    settlement_date: string;
    face_value: number;
    quantity: number;
    clean_price: number;
    dirty_price?: number;
    yield_rate?: number;
    accrued_interest: number;
    principal_amount: number;
    settlement_amount: number;
    commission: number;
    broker_fee: number;
    withholding_tax: number;
    status: TradeStatus;
    settlement_status: string;
    trader_id?: string;
    approver_id?: string;
    is_thaibma_reported: boolean;
    created_at: string;
    updated_at?: string;
}

export type TradeStatus = 'DRAFT' | 'PENDING_APPROVAL' | 'APPROVED' | 'SETTLED' | 'CANCELLED';

// =============================================================================
// Interbank Deals
// =============================================================================
export interface InterbankDeal {
    deal_ref: string;
    external_ref?: string;
    deal_type: 'PLACEMENT' | 'BORROWING';
    entity_id: string;
    counterparty_id: string;
    counterparty_name: string;
    portfolio_id: string;
    currency: string;
    principal_amount: number;
    rate_type: 'FIXED' | 'FLOATING';
    interest_rate: number;
    spread: number;
    reference_rate?: string;
    day_count_convention: string;
    deal_date: string;
    start_date: string;
    maturity_date: string;
    tenor_days: number;
    interest_amount: number;
    accrued_interest: number;
    maturity_amount: number;
    status: DealStatus;
    trader_id?: string;
    approver_id?: string;
    start_settlement_status: string;
    maturity_settlement_status: string;
    created_at: string;
    updated_at?: string;
}

export type DealStatus = 'DRAFT' | 'PENDING_APPROVAL' | 'APPROVED' | 'ACTIVE' | 'MATURED' | 'CANCELLED';

// =============================================================================
// Repo Trades
// =============================================================================
export interface RepoTrade {
    trade_id: string;
    trade_ref: string;
    external_ref?: string;
    repo_type: 'REPO' | 'REVERSE_REPO';
    entity_id: string;
    counterparty_id: string;
    counterparty_name: string;
    portfolio_id: string;
    currency: string;
    near_leg_amount: number;
    far_leg_amount: number;
    repo_rate: number;
    day_count_convention: string;
    interest_amount: number;
    trade_date: string;
    start_date: string;
    end_date: string;
    tenor_days: number;
    collateral: CollateralInfo;
    haircut_pct: number;
    initial_margin: number;
    current_margin: number;
    margin_call_threshold: number;
    margin_call_amount: number;
    status: RepoStatus;
    near_leg_cash_status: string;
    near_leg_collateral_status: string;
    far_leg_cash_status: string;
    far_leg_collateral_status: string;
    trader_id?: string;
    approver_id?: string;
    is_early_terminated: boolean;
    early_termination_date?: string;
    created_at: string;
    updated_at?: string;
}

export type RepoStatus = 'DRAFT' | 'PENDING_APPROVAL' | 'APPROVED' | 'NEAR_LEG_SETTLED' | 'ACTIVE' | 'FAR_LEG_SETTLED' | 'MATURED' | 'EARLY_TERMINATED' | 'CANCELLED';

export interface CollateralInfo {
    security_id: string;
    isin: string;
    security_name: string;
    face_value: number;
    market_price: number;
    market_value: number;
    haircut_pct: number;
    collateral_value: number;
}

// =============================================================================
// Positions
// =============================================================================
export interface BondPosition {
    id: number;
    position_date: string;
    entity_id: string;
    portfolio_id: string;
    security_id: string;
    isin: string;
    security_name?: string;
    face_value: number;
    quantity: number;
    cost_price: number;
    cost_amount: number;
    market_price?: number;
    market_value: number;
    accrued_interest: number;
    unrealized_pnl: number;
    tfrs9_classification: string;
    pledged_quantity: number;
    available_quantity: number;
}

export interface CashPosition {
    id: number;
    position_date: string;
    entity_id: string;
    currency: string;
    account_type: string;
    opening_balance: number;
    closing_balance: number;
    inflows: number;
    outflows: number;
    projected_t1_inflow: number;
    projected_t1_outflow: number;
}

// =============================================================================
// Settlement
// =============================================================================
export interface PendingSettlement {
    settlement_id: string;
    trade_ref: string;
    trade_type: string;
    settlement_system: 'BAHTNET' | 'TSD';
    settlement_type: 'CASH' | 'SECURITIES' | 'DVP';
    direction: 'INCOMING' | 'OUTGOING';
    currency: string;
    amount: number;
    security_isin?: string;
    security_quantity?: number;
    counterparty_id: string;
    counterparty_name: string;
    value_date: string;
    status: SettlementStatus;
    message_generated: boolean;
    message_ref?: string;
    created_at: string;
}

export type SettlementStatus = 'PENDING' | 'PROCESSING' | 'SENT' | 'CONFIRMED' | 'SETTLED' | 'FAILED' | 'REJECTED';

export interface SettlementSummary {
    settlement_date: string;
    total_bahtnet_outgoing: number;
    total_bahtnet_incoming: number;
    net_bahtnet: number;
    total_securities_delivered: number;
    total_securities_received: number;
    pending_count: number;
    settled_count: number;
    failed_count: number;
}

// =============================================================================
// Calendar
// =============================================================================
export interface BusinessDayCheck {
    date: string;
    is_business_day: boolean;
    is_holiday: boolean;
    holiday_name?: string;
    day_of_week: string;
}

export interface SettlementDateResult {
    start_date: string;
    settlement_date: string;
    business_days: number;
    calendar_days: number;
    holidays_skipped: string[];
}

// =============================================================================
// API Response Wrappers
// =============================================================================
export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    size: number;
}

export interface ApiError {
    detail: string | { msg: string; type: string }[];
}

// =============================================================================
// Form Types
// =============================================================================
export interface BondTradeForm {
    trade_type: 'BUY' | 'SELL';
    counterparty_id: string;
    portfolio_id: string;
    security_id: string;
    trade_date: string;
    settlement_date: string;
    face_value: number;
    clean_price: number;
}

export interface InterbankDealForm {
    deal_type: 'PLACEMENT' | 'BORROWING';
    counterparty_id: string;
    portfolio_id: string;
    currency: string;
    principal_amount: number;
    rate_type: 'FIXED' | 'FLOATING';
    interest_rate: number;
    spread: number;
    reference_rate?: string;
    day_count_convention: string;
    start_date: string;
    maturity_date: string;
}

export interface RepoTradeForm {
    repo_type: 'REPO' | 'REVERSE_REPO';
    counterparty_id: string;
    portfolio_id: string;
    currency: string;
    near_leg_amount: number;
    repo_rate: number;
    start_date: string;
    end_date: string;
    collateral_security_id: string;
    collateral_isin: string;
    collateral_face_value: number;
    haircut_pct: number;
}
