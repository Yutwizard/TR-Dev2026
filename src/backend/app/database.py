"""
Treasury Management System - Database Connection
=================================================

Database engine, session management, and dependency injection.
"""

from typing import AsyncGenerator, Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import logging

from app.config import settings
from app.models.base import Base

logger = logging.getLogger(__name__)


# =============================================================================
# Sync Engine (for migrations and scripts)
# =============================================================================
sync_engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE,
    echo=settings.DEBUG,
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
)


# =============================================================================
# Async Engine (for API)
# =============================================================================
# Convert postgresql:// to postgresql+asyncpg://
async_database_url = settings.DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
)

async_engine = create_async_engine(
    async_database_url,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE,
    echo=settings.DEBUG,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# =============================================================================
# Dependencies
# =============================================================================
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for async database sessions.
    
    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_async_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_db() -> Generator[Session, None, None]:
    """
    Dependency for sync database sessions.
    Used mainly for background tasks and scripts.
    """
    session = SyncSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for sync database sessions.
    
    Usage:
        with get_db_session() as db:
            db.add(item)
            db.commit()
    """
    session = SyncSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# =============================================================================
# Database Initialization
# =============================================================================
def create_all_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=sync_engine)
    logger.info("All database tables created")


def drop_all_tables():
    """Drop all database tables (USE WITH CAUTION)"""
    Base.metadata.drop_all(bind=sync_engine)
    logger.warning("All database tables dropped")


async def check_database_connection() -> bool:
    """Check if database is accessible"""
    try:
        async with async_engine.begin() as conn:
            await conn.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
