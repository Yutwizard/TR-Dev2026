"""
Treasury Management System - Health Check Router
=================================================

Endpoints for system health monitoring.
"""

from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
import platform
import sys

from app.config import settings


router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str
    environment: str
    database: str = "unknown"
    redis: str = "unknown"


class DetailedHealthResponse(BaseModel):
    """Detailed health check response"""
    status: str
    timestamp: str
    version: str
    environment: str
    services: Dict[str, Any]
    system: Dict[str, Any]


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Basic health check endpoint.
    
    Returns:
        Health status of the application
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat() + "Z",
        version="0.1.0",
        environment=settings.APP_ENV,
        database="configured",  # TODO: Add actual DB check
        redis="configured"      # TODO: Add actual Redis check
    )


@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check():
    """
    Detailed health check with all service statuses.
    
    Returns:
        Detailed health status of all services
    """
    # TODO: Add actual service checks
    services = {
        "database": {
            "status": "healthy",
            "url": settings.DATABASE_URL[:40] + "...",
            "pool_size": settings.DB_POOL_SIZE
        },
        "redis": {
            "status": "healthy",
            "url": settings.REDIS_URL
        },
        "thaibma": {
            "status": "configured" if settings.THAIBMA_ENABLED else "disabled",
            "enabled": settings.THAIBMA_ENABLED
        },
        "bahtnet": {
            "status": "manual_mode",
            "mode": settings.BAHTNET_MODE
        },
        "tsd": {
            "status": "manual_mode",
            "mode": settings.TSD_MODE
        }
    }
    
    system = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "hostname": platform.node()
    }
    
    return DetailedHealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat() + "Z",
        version="0.1.0",
        environment=settings.APP_ENV,
        services=services,
        system=system
    )


@router.get("/ready")
async def readiness_check():
    """
    Kubernetes-style readiness probe.
    
    Returns 200 if application is ready to serve requests.
    """
    # TODO: Add checks for database connectivity, etc.
    return {"ready": True}


@router.get("/live")
async def liveness_check():
    """
    Kubernetes-style liveness probe.
    
    Returns 200 if application is alive.
    """
    return {"alive": True}
