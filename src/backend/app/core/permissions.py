"""
Treasury Management System - Role-Based Access Control (RBAC)
==============================================================

Defines roles, permissions, and access control for the TMS.

Roles:
- TRADER: Front Office - Can create trades
- SUPERVISOR: Front Office - Can approve trades, view reports
- RISK_OFFICER: Middle Office - Limit management, risk reports
- BACK_OFFICE: Back Office - Settlement, reconciliation
- ADMIN: IT Admin - Full system access

Usage:
    from app.core.permissions import require_permission, Permission
    
    @router.post("/trades")
    @require_permission(Permission.CREATE_TRADE)
    async def create_trade():
        ...
"""

from enum import Enum
from functools import wraps
from typing import List, Set, Callable
from fastapi import Depends, HTTPException, status

from app.core.auth import get_current_active_user, UserInToken


# =============================================================================
# Permissions Enum
# =============================================================================
class Permission(str, Enum):
    """All permissions in the system"""
    
    # Trade Permissions
    CREATE_TRADE = "create_trade"
    VIEW_TRADE = "view_trade"
    APPROVE_TRADE = "approve_trade"
    CANCEL_TRADE = "cancel_trade"
    AMEND_TRADE = "amend_trade"
    
    # Settlement Permissions
    VIEW_SETTLEMENT = "view_settlement"
    CONFIRM_SETTLEMENT = "confirm_settlement"
    FAIL_SETTLEMENT = "fail_settlement"
    
    # Position Permissions
    VIEW_POSITION = "view_position"
    VIEW_POSITION_DETAIL = "view_position_detail"
    EXPORT_POSITION = "export_position"
    
    # Limit Permissions
    VIEW_LIMIT = "view_limit"
    CREATE_LIMIT = "create_limit"
    MODIFY_LIMIT = "modify_limit"
    APPROVE_LIMIT = "approve_limit"
    
    # Report Permissions
    VIEW_REPORT = "view_report"
    EXPORT_REPORT = "export_report"
    CREATE_REGULATORY_REPORT = "create_regulatory_report"
    
    # Master Data Permissions
    VIEW_MASTER_DATA = "view_master_data"
    CREATE_MASTER_DATA = "create_master_data"
    MODIFY_MASTER_DATA = "modify_master_data"
    
    # User Management
    VIEW_USERS = "view_users"
    CREATE_USER = "create_user"
    MODIFY_USER = "modify_user"
    DELETE_USER = "delete_user"
    
    # System Administration
    VIEW_AUDIT_LOG = "view_audit_log"
    SYSTEM_CONFIG = "system_config"
    MANAGE_ROLES = "manage_roles"


# =============================================================================
# Roles Enum
# =============================================================================
class Role(str, Enum):
    """User roles in the system"""
    
    TRADER = "TRADER"
    SUPERVISOR = "SUPERVISOR"
    RISK_OFFICER = "RISK_OFFICER"
    BACK_OFFICE = "BACK_OFFICE"
    ADMIN = "ADMIN"
    VIEWER = "VIEWER"  # Read-only access


# =============================================================================
# Role-Permission Mapping
# =============================================================================
ROLE_PERMISSIONS: dict[Role, Set[Permission]] = {
    
    Role.TRADER: {
        Permission.CREATE_TRADE,
        Permission.VIEW_TRADE,
        Permission.CANCEL_TRADE,
        Permission.VIEW_POSITION,
        Permission.VIEW_LIMIT,
        Permission.VIEW_MASTER_DATA,
    },
    
    Role.SUPERVISOR: {
        Permission.CREATE_TRADE,
        Permission.VIEW_TRADE,
        Permission.APPROVE_TRADE,
        Permission.CANCEL_TRADE,
        Permission.AMEND_TRADE,
        Permission.VIEW_POSITION,
        Permission.VIEW_POSITION_DETAIL,
        Permission.VIEW_LIMIT,
        Permission.VIEW_REPORT,
        Permission.VIEW_MASTER_DATA,
    },
    
    Role.RISK_OFFICER: {
        Permission.VIEW_TRADE,
        Permission.VIEW_POSITION,
        Permission.VIEW_POSITION_DETAIL,
        Permission.EXPORT_POSITION,
        Permission.VIEW_LIMIT,
        Permission.CREATE_LIMIT,
        Permission.MODIFY_LIMIT,
        Permission.APPROVE_LIMIT,
        Permission.VIEW_REPORT,
        Permission.EXPORT_REPORT,
        Permission.VIEW_MASTER_DATA,
    },
    
    Role.BACK_OFFICE: {
        Permission.VIEW_TRADE,
        Permission.VIEW_SETTLEMENT,
        Permission.CONFIRM_SETTLEMENT,
        Permission.FAIL_SETTLEMENT,
        Permission.VIEW_POSITION,
        Permission.VIEW_POSITION_DETAIL,
        Permission.EXPORT_POSITION,
        Permission.VIEW_REPORT,
        Permission.EXPORT_REPORT,
        Permission.CREATE_REGULATORY_REPORT,
        Permission.VIEW_MASTER_DATA,
    },
    
    Role.ADMIN: {
        # Admin has all permissions
        Permission.CREATE_TRADE,
        Permission.VIEW_TRADE,
        Permission.APPROVE_TRADE,
        Permission.CANCEL_TRADE,
        Permission.AMEND_TRADE,
        Permission.VIEW_SETTLEMENT,
        Permission.CONFIRM_SETTLEMENT,
        Permission.FAIL_SETTLEMENT,
        Permission.VIEW_POSITION,
        Permission.VIEW_POSITION_DETAIL,
        Permission.EXPORT_POSITION,
        Permission.VIEW_LIMIT,
        Permission.CREATE_LIMIT,
        Permission.MODIFY_LIMIT,
        Permission.APPROVE_LIMIT,
        Permission.VIEW_REPORT,
        Permission.EXPORT_REPORT,
        Permission.CREATE_REGULATORY_REPORT,
        Permission.VIEW_MASTER_DATA,
        Permission.CREATE_MASTER_DATA,
        Permission.MODIFY_MASTER_DATA,
        Permission.VIEW_USERS,
        Permission.CREATE_USER,
        Permission.MODIFY_USER,
        Permission.DELETE_USER,
        Permission.VIEW_AUDIT_LOG,
        Permission.SYSTEM_CONFIG,
        Permission.MANAGE_ROLES,
    },
    
    Role.VIEWER: {
        Permission.VIEW_TRADE,
        Permission.VIEW_POSITION,
        Permission.VIEW_LIMIT,
        Permission.VIEW_REPORT,
        Permission.VIEW_MASTER_DATA,
    },
}


# =============================================================================
# Permission Checking Functions
# =============================================================================
def get_user_permissions(role: str) -> Set[Permission]:
    """
    Get all permissions for a given role.
    
    Args:
        role: User role string
        
    Returns:
        Set of Permission enums
    """
    try:
        role_enum = Role(role)
        return ROLE_PERMISSIONS.get(role_enum, set())
    except ValueError:
        return set()


def has_permission(user_role: str, permission: Permission) -> bool:
    """
    Check if a role has a specific permission.
    
    Args:
        user_role: User's role
        permission: Permission to check
        
    Returns:
        True if role has permission
    """
    permissions = get_user_permissions(user_role)
    return permission in permissions


def has_any_permission(user_role: str, permissions: List[Permission]) -> bool:
    """
    Check if role has any of the specified permissions.
    
    Args:
        user_role: User's role
        permissions: List of permissions to check
        
    Returns:
        True if role has at least one permission
    """
    user_permissions = get_user_permissions(user_role)
    return any(p in user_permissions for p in permissions)


def has_all_permissions(user_role: str, permissions: List[Permission]) -> bool:
    """
    Check if role has all of the specified permissions.
    
    Args:
        user_role: User's role
        permissions: List of permissions to check
        
    Returns:
        True if role has all permissions
    """
    user_permissions = get_user_permissions(user_role)
    return all(p in user_permissions for p in permissions)


# =============================================================================
# FastAPI Dependencies
# =============================================================================
def require_permission(*required_permissions: Permission):
    """
    Dependency factory for permission-based access control.
    
    Usage:
        @router.post("/trades")
        async def create_trade(
            user = Depends(require_permission(Permission.CREATE_TRADE))
        ):
            ...
    
    Args:
        required_permissions: Permissions required to access endpoint
        
    Returns:
        FastAPI dependency function
    """
    async def permission_checker(
        current_user: UserInToken = Depends(get_current_active_user)
    ) -> UserInToken:
        user_permissions = get_user_permissions(current_user.role)
        
        missing = [p for p in required_permissions if p not in user_permissions]
        
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": "Permission denied",
                    "missing_permissions": [p.value for p in missing],
                    "user_role": current_user.role
                }
            )
        
        return current_user
    
    return permission_checker


def require_any_permission(*permissions: Permission):
    """
    Require at least one of the specified permissions.
    
    Usage:
        @router.get("/data")
        async def get_data(
            user = Depends(require_any_permission(
                Permission.VIEW_TRADE, 
                Permission.VIEW_POSITION
            ))
        ):
            ...
    """
    async def permission_checker(
        current_user: UserInToken = Depends(get_current_active_user)
    ) -> UserInToken:
        user_permissions = get_user_permissions(current_user.role)
        
        if not any(p in user_permissions for p in permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": "Permission denied",
                    "required_any": [p.value for p in permissions],
                    "user_role": current_user.role
                }
            )
        
        return current_user
    
    return permission_checker


# =============================================================================
# Four-Eyes Principle Validation
# =============================================================================
def validate_four_eyes(creator_id: str, approver_id: str) -> bool:
    """
    Validate four-eyes principle: creator cannot approve their own action.
    
    Args:
        creator_id: User ID who created the item
        approver_id: User ID attempting to approve
        
    Returns:
        True if four-eyes is satisfied (different users)
        
    Raises:
        HTTPException if same user
    """
    if creator_id == approver_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Four-eyes principle violation: You cannot approve your own action"
        )
    return True


# =============================================================================
# Role Display Helpers
# =============================================================================
def get_role_display_name(role: str) -> str:
    """Get human-readable role name"""
    names = {
        "TRADER": "Trader (Front Office)",
        "SUPERVISOR": "Supervisor (Front Office)",
        "RISK_OFFICER": "Risk Officer (Middle Office)",
        "BACK_OFFICE": "Settlement Officer (Back Office)",
        "ADMIN": "System Administrator",
        "VIEWER": "Read-Only Viewer",
    }
    return names.get(role, role)


def get_all_roles() -> List[dict]:
    """Get list of all roles with descriptions"""
    return [
        {"role": Role.TRADER.value, "name": "Trader", "office": "Front Office"},
        {"role": Role.SUPERVISOR.value, "name": "Supervisor", "office": "Front Office"},
        {"role": Role.RISK_OFFICER.value, "name": "Risk Officer", "office": "Middle Office"},
        {"role": Role.BACK_OFFICE.value, "name": "Settlement Officer", "office": "Back Office"},
        {"role": Role.ADMIN.value, "name": "Administrator", "office": "IT"},
        {"role": Role.VIEWER.value, "name": "Viewer", "office": "N/A"},
    ]
