"""
Treasury Management System - Unified Enums
============================================

Single source of truth for all enum types used across the system.

IMPORTANT: Do NOT define duplicate enums in routers, schemas, or models.
           Always import from this module.

Usage:
    from app.core.enums import TradeStatus, TradeSide, DayCountConvention
"""

from enum import Enum


# =============================================================================
# Trade Status (Shared across all products)
# =============================================================================
class TradeStatus(str, Enum):
    """Universal trade lifecycle status"""
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PENDING_SETTLEMENT = "PENDING_SETTLEMENT"
    PARTIALLY_SETTLED = "PARTIALLY_SETTLED"
    SETTLED = "SETTLED"
    ACTIVE = "ACTIVE"           # For interbank/repo: deal is live
    NEAR_LEG_SETTLED = "NEAR_LEG_SETTLED"  # Repo: near leg done, awaiting far leg
    MATURED = "MATURED"         # For interbank/repo: reached maturity
    EARLY_TERMINATED = "EARLY_TERMINATED"  # Repo/interbank: terminated before maturity
    CANCELLED = "CANCELLED"
    MARGIN_CALL = "MARGIN_CALL" # Repo: margin event triggered


# =============================================================================
# Trade Direction
# =============================================================================
class TradeSide(str, Enum):
    """Trade direction"""
    BUY = "BUY"
    SELL = "SELL"
    LEND = "LEND"
    BORROW = "BORROW"


# =============================================================================
# Product-Specific Deal Types
# =============================================================================
class BondTradeType(str, Enum):
    """Bond trade types"""
    OUTRIGHT = "OUTRIGHT"
    WHEN_ISSUED = "WHEN_ISSUED"


class InterbankDealType(str, Enum):
    """Interbank deal types"""
    PLACEMENT = "PLACEMENT"     # We lend (place)
    BORROWING = "BORROWING"     # We borrow (take)


class RepoTradeType(str, Enum):
    """Repo trade types"""
    REPO = "REPO"               # We borrow cash, post collateral
    REVERSE_REPO = "REVERSE_REPO"  # We lend cash, receive collateral


class RepoSubType(str, Enum):
    """Repo sub-types"""
    BILATERAL = "BILATERAL"
    BOT_BRP = "BOT_BRP"        # BOT Bilateral Repo Program


# =============================================================================
# Rate & Convention Types
# =============================================================================
class RateType(str, Enum):
    """Interest rate type"""
    FIXED = "FIXED"
    FLOATING = "FLOATING"


class DayCountConvention(str, Enum):
    """Day count convention for interest calculation"""
    ACT_365 = "ACT/365"
    ACT_360 = "ACT/360"
    THIRTY_360 = "30/360"
    ACT_ACT = "ACT/ACT"


class ReferenceRate(str, Enum):
    """Reference rates for floating rate deals"""
    THOR = "THOR"               # Thai Overnight Repurchase rate
    THBFIX = "THBFIX"           # THB FIX
    BIBOR = "BIBOR"             # Bangkok Interbank Offered Rate


# =============================================================================
# Settlement Status
# =============================================================================
class SettlementStatus(str, Enum):
    """Settlement status"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SETTLED = "SETTLED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"


class SettlementChannel(str, Enum):
    """Settlement channels"""
    BAHTNET = "BAHTNET"         # BOT's RTGS system
    TSD = "TSD"                 # Thailand Securities Depository
    MANUAL = "MANUAL"


# =============================================================================
# Master Data Status
# =============================================================================
class EntityStatus(str, Enum):
    """Entity/counterparty status"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    PENDING_KYC = "PENDING_KYC"


class SecurityStatus(str, Enum):
    """Security status"""
    ACTIVE = "ACTIVE"
    MATURED = "MATURED"
    DEFAULTED = "DEFAULTED"
    SUSPENDED = "SUSPENDED"


# =============================================================================
# Limit Types
# =============================================================================
class LimitType(str, Enum):
    """Counterparty limit types (product-specific, no aggregate)"""
    PLACEMENT_LIMIT = "PLACEMENT_LIMIT"
    REPO_LIMIT = "REPO_LIMIT"
    SINGLE_TXN = "SINGLE_TXN"
    TENOR = "TENOR"
    CONCENTRATION = "CONCENTRATION"


# =============================================================================
# TFRS 9 / Accounting
# =============================================================================
class AccountingClassification(str, Enum):
    """TFRS 9 portfolio classification"""
    AMORTIZED_COST = "AMC"
    FVOCI = "FVOCI"             # Fair Value through Other Comprehensive Income
    FVTPL = "FVTPL"             # Fair Value through Profit and Loss


# =============================================================================
# Audit Action Types
# =============================================================================
class AuditAction(str, Enum):
    """Audit log action types"""
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    SETTLED = "SETTLED"
    STATUS_CHANGE = "STATUS_CHANGE"
    LIMIT_CHECK = "LIMIT_CHECK"
    THAIBMA_REPORTED = "THAIBMA_REPORTED"
    MARGIN_CALL = "MARGIN_CALL"
    COLLATERAL_UPDATE = "COLLATERAL_UPDATE"
    BATCH_PROCESS = "BATCH_PROCESS"


# =============================================================================
# Entity Types (for audit log)
# =============================================================================
class EntityType(str, Enum):
    """Entity types for audit trail"""
    BOND_TRADE = "BondTrade"
    INTERBANK_DEAL = "InterbankDeal"
    REPO_TRADE = "RepoTrade"
    SECURITY = "Security"
    COUNTERPARTY = "Counterparty"
    LIMIT = "Limit"
    POSITION = "Position"
    MARGIN_CALL = "MarginCall"
