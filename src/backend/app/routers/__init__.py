# API Routers package
"""
FastAPI routers for Treasury Management System
"""

from app.routers.auth import router as auth_router
from app.routers.health import router as health_router
from app.routers.securities import router as securities_router
from app.routers.bond_trades import router as bond_trades_router
from app.routers.positions import router as positions_router
from app.routers.calendar import router as calendar_router
from app.routers.interbank import router as interbank_router
from app.routers.repo import router as repo_router
from app.routers.settlement import router as settlement_router

__all__ = [
    "auth_router",
    "health_router",
    "securities_router",
    "bond_trades_router",
    "positions_router",
    "calendar_router",
    "interbank_router",
    "repo_router",
    "settlement_router",
]
