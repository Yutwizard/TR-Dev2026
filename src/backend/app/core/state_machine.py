"""
Treasury Management System - State Machine
============================================

Explicit, auditable state transition rules for all deal lifecycles.

Each product defines its valid state transitions. Any transition not
listed is REJECTED. This makes lifecycle rules:
- Explicit: All allowed transitions are documented
- Testable: Easy to unit test each transition
- Auditable: Transition validation is centralized

Usage:
    from app.core.state_machine import (
        validate_transition, get_allowed_transitions,
        BOND_TRADE_TRANSITIONS, INTERBANK_DEAL_TRANSITIONS, REPO_TRADE_TRANSITIONS
    )
    
    # Check if transition is valid
    if not validate_transition("PENDING_APPROVAL", "APPROVED", BOND_TRADE_TRANSITIONS):
        raise BusinessRuleError("Invalid status transition")
    
    # Get all valid next states
    next_states = get_allowed_transitions("APPROVED", BOND_TRADE_TRANSITIONS)
    # Returns: ["PENDING_SETTLEMENT", "CANCELLED"]
"""

from typing import Dict, List, Optional, Set
import logging

from app.core.enums import TradeStatus

logger = logging.getLogger(__name__)


# =============================================================================
# Bond Trade Lifecycle
# =============================================================================
# 
# DRAFT → PENDING_APPROVAL → APPROVED → PENDING_SETTLEMENT → SETTLED
#   ↓        ↓                  ↓                               
# CANCELLED REJECTED         CANCELLED                       
#            ↓
#          DRAFT (re-submission after rejection)
#
BOND_TRADE_TRANSITIONS: Dict[str, List[str]] = {
    TradeStatus.DRAFT: [
        TradeStatus.PENDING_APPROVAL,
        TradeStatus.CANCELLED,
    ],
    TradeStatus.PENDING_APPROVAL: [
        TradeStatus.APPROVED,
        TradeStatus.REJECTED,
        TradeStatus.CANCELLED,
    ],
    TradeStatus.APPROVED: [
        TradeStatus.PENDING_SETTLEMENT,
        TradeStatus.CANCELLED,
    ],
    TradeStatus.REJECTED: [
        TradeStatus.DRAFT,              # Allow re-submission
    ],
    TradeStatus.PENDING_SETTLEMENT: [
        TradeStatus.SETTLED,
        TradeStatus.PARTIALLY_SETTLED,
    ],
    TradeStatus.PARTIALLY_SETTLED: [
        TradeStatus.SETTLED,
    ],
    TradeStatus.SETTLED: [],            # Terminal state
    TradeStatus.CANCELLED: [],          # Terminal state
}


# =============================================================================
# Interbank Deal Lifecycle
# =============================================================================
#
# DRAFT → PENDING_APPROVAL → APPROVED → ACTIVE → [Daily Accrual] → MATURED
#   ↓        ↓                  ↓          ↓
# CANCELLED REJECTED         CANCELLED  CANCELLED (early termination only)
#            ↓
#          DRAFT (re-submission)
#
INTERBANK_DEAL_TRANSITIONS: Dict[str, List[str]] = {
    TradeStatus.DRAFT: [
        TradeStatus.PENDING_APPROVAL,
        TradeStatus.CANCELLED,
    ],
    TradeStatus.PENDING_APPROVAL: [
        TradeStatus.APPROVED,
        TradeStatus.REJECTED,
        TradeStatus.CANCELLED,
    ],
    TradeStatus.APPROVED: [
        TradeStatus.ACTIVE,             # Settlement done, deal starts
        TradeStatus.CANCELLED,
    ],
    TradeStatus.REJECTED: [
        TradeStatus.DRAFT,              # Re-submission
    ],
    TradeStatus.ACTIVE: [
        TradeStatus.MATURED,            # Normal maturity
        TradeStatus.CANCELLED,          # Early termination
    ],
    TradeStatus.MATURED: [],            # Terminal state
    TradeStatus.CANCELLED: [],          # Terminal state
}


# =============================================================================
# Repo Trade Lifecycle
# =============================================================================
#
# DRAFT → PENDING_APPROVAL → APPROVED → PENDING_SETTLEMENT → ACTIVE 
#   ↓        ↓                  ↓                                ↓
# CANCELLED REJECTED         CANCELLED                     [Daily MTM]
#            ↓                                                   ↓
#          DRAFT                                         MARGIN_CALL (if needed)
#                                                              ↓
#                                                            ACTIVE (after margin settled)
#                                                              ↓
#                                                           MATURED
#
REPO_TRADE_TRANSITIONS: Dict[str, List[str]] = {
    TradeStatus.DRAFT: [
        TradeStatus.PENDING_APPROVAL,
        TradeStatus.CANCELLED,
    ],
    TradeStatus.PENDING_APPROVAL: [
        TradeStatus.APPROVED,
        TradeStatus.REJECTED,
        TradeStatus.CANCELLED,
    ],
    TradeStatus.APPROVED: [
        TradeStatus.PENDING_SETTLEMENT,  # Collateral allocation
        TradeStatus.CANCELLED,
    ],
    TradeStatus.REJECTED: [
        TradeStatus.DRAFT,
    ],
    TradeStatus.PENDING_SETTLEMENT: [
        TradeStatus.ACTIVE,              # Near leg settled
        TradeStatus.CANCELLED,
    ],
    TradeStatus.ACTIVE: [
        TradeStatus.MARGIN_CALL,         # Margin threshold breached
        TradeStatus.MATURED,             # Far leg settlement
        TradeStatus.CANCELLED,           # Early termination
    ],
    TradeStatus.MARGIN_CALL: [
        TradeStatus.ACTIVE,              # Margin call resolved
    ],
    TradeStatus.MATURED: [],             # Terminal state
    TradeStatus.CANCELLED: [],           # Terminal state
}


# =============================================================================
# Product-to-Transitions Map
# =============================================================================
PRODUCT_TRANSITIONS: Dict[str, Dict[str, List[str]]] = {
    "BOND_TRADE": BOND_TRADE_TRANSITIONS,
    "INTERBANK_DEAL": INTERBANK_DEAL_TRANSITIONS,
    "REPO_TRADE": REPO_TRADE_TRANSITIONS,
}


# =============================================================================
# Validation Functions
# =============================================================================

def validate_transition(
    current_status: str,
    target_status: str,
    transitions: Dict[str, List[str]]
) -> bool:
    """
    Check if a state transition is allowed.
    
    Args:
        current_status: Current status value
        target_status: Desired new status value
        transitions: The transition map for this product
    
    Returns:
        True if transition is allowed, False otherwise
    """
    allowed = transitions.get(current_status, [])
    return target_status in allowed


def get_allowed_transitions(
    current_status: str,
    transitions: Dict[str, List[str]]
) -> List[str]:
    """
    Get all valid next states from the current state.
    
    Args:
        current_status: Current status value
        transitions: The transition map for this product
    
    Returns:
        List of allowed target states (may be empty for terminal states)
    """
    return list(transitions.get(current_status, []))


def is_terminal_state(
    status: str,
    transitions: Dict[str, List[str]]
) -> bool:
    """
    Check if a status is a terminal (final) state.
    
    Terminal states have no outgoing transitions.
    
    Returns:
        True if the status is terminal
    """
    return len(transitions.get(status, [])) == 0


def get_terminal_states(
    transitions: Dict[str, List[str]]
) -> Set[str]:
    """
    Get all terminal states for a product.
    
    Returns:
        Set of terminal status values
    """
    return {
        status for status, targets in transitions.items()
        if len(targets) == 0
    }


def get_cancellable_states(
    transitions: Dict[str, List[str]]
) -> List[str]:
    """
    Get all states from which cancellation is possible.
    
    Returns:
        List of states that allow transition to CANCELLED
    """
    return [
        status for status, targets in transitions.items()
        if TradeStatus.CANCELLED in targets
    ]


def assert_transition(
    current_status: str,
    target_status: str,
    transitions: Dict[str, List[str]],
    entity_type: str = "Deal",
    entity_ref: str = ""
) -> None:
    """
    Assert that a state transition is valid, raising an error if not.
    
    Use this in services to enforce transitions with clear error messages.
    
    Args:
        current_status: Current status
        target_status: Target status
        transitions: Transition map
        entity_type: Type name for error message (e.g., "Bond Trade")
        entity_ref: Reference for error message (e.g., "BND20260210001")
    
    Raises:
        ValueError: If transition is not allowed
    """
    if not validate_transition(current_status, target_status, transitions):
        allowed = get_allowed_transitions(current_status, transitions)
        allowed_str = ", ".join(allowed) if allowed else "none (terminal state)"
        
        ref_str = f" ({entity_ref})" if entity_ref else ""
        raise ValueError(
            f"{entity_type}{ref_str}: Cannot transition from "
            f"'{current_status}' to '{target_status}'. "
            f"Allowed transitions: [{allowed_str}]"
        )
    
    logger.debug(
        f"State transition: {entity_type} {entity_ref} "
        f"{current_status} → {target_status}"
    )
