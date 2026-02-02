"""
Treasury Management System - FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.core.exceptions import setup_exception_handlers
from app.routers import auth_router, health_router

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Starting Treasury Management System...")
    logger.info(f"📦 Environment: {settings.APP_ENV}")
    logger.info(f"🔗 Database: {settings.DATABASE_URL[:50]}...")
    yield
    # Shutdown
    logger.info("👋 Shutting down Treasury Management System...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## Treasury Management System API
    
    Thai Commercial Bank Treasury Operations covering:
    - **Bond Trading** (Buy/Sell)
    - **Interbank Lending/Borrowing**
    - **Repo/Reverse Repo**
    
    ### Features
    - Real-time position monitoring
    - ThaiBMA trade reporting
    - T+2 settlement tracking
    - TFRS 9 compliance
    """,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup exception handlers
setup_exception_handlers(app)

# Include routers
app.include_router(health_router, tags=["Health"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])

# Future routers (uncomment as implemented)
# app.include_router(securities_router, prefix="/api/v1/securities", tags=["Securities"])
# app.include_router(counterparties_router, prefix="/api/v1/counterparties", tags=["Counterparties"])
# app.include_router(bond_trades_router, prefix="/api/v1/bond-trades", tags=["Bond Trades"])
# app.include_router(interbank_router, prefix="/api/v1/interbank", tags=["Interbank"])
# app.include_router(repos_router, prefix="/api/v1/repos", tags=["Repo/RRP"])
# app.include_router(positions_router, prefix="/api/v1/positions", tags=["Positions"])
# app.include_router(settlement_router, prefix="/api/v1/settlement", tags=["Settlement"])


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint - redirects to docs"""
    return {
        "message": "Treasury Management System API",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
