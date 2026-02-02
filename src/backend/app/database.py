"""
Treasury Management System - Database Connection
=================================================

Database engine, session management, and dependency injection.

Uses lazy initialization to avoid import errors when 
database drivers are not installed.
"""

from typing import AsyncGenerator, Generator, Optional
from contextlib import contextmanager
import logging

from app.config import settings
from app.models.base import Base

logger = logging.getLogger(__name__)


# =============================================================================
# Lazy Database Engine Initialization
# =============================================================================
_sync_engine = None
_async_engine = None
_SyncSessionLocal = None
_AsyncSessionLocal = None


def get_sync_engine():
    """Get or create sync database engine"""
    global _sync_engine
    if _sync_engine is None:
        from sqlalchemy import create_engine
        _sync_engine = create_engine(
            settings.DATABASE_URL,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_recycle=settings.DB_POOL_RECYCLE,
            echo=settings.DEBUG,
        )
    return _sync_engine


def get_async_engine():
    """Get or create async database engine"""
    global _async_engine
    if _async_engine is None:
        from sqlalchemy.ext.asyncio import create_async_engine
        async_database_url = settings.DATABASE_URL.replace(
            "postgresql://", "postgresql+asyncpg://"
        )
        _async_engine = create_async_engine(
            async_database_url,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_recycle=settings.DB_POOL_RECYCLE,
            echo=settings.DEBUG,
        )
    return _async_engine


def get_sync_session_local():
    """Get or create sync session factory"""
    global _SyncSessionLocal
    if _SyncSessionLocal is None:
        from sqlalchemy.orm import sessionmaker
        _SyncSessionLocal = sessionmaker(
            bind=get_sync_engine(),
            autocommit=False,
            autoflush=False,
        )
    return _SyncSessionLocal


def get_async_session_local():
    """Get or create async session factory"""
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
        _AsyncSessionLocal = async_sessionmaker(
            bind=get_async_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _AsyncSessionLocal


# =============================================================================
# Dependencies
# =============================================================================
async def get_async_db() -> AsyncGenerator:
    """
    FastAPI dependency for async database sessions.
    
    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_async_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    session_factory = get_async_session_local()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_db() -> Generator:
    """
    Dependency for sync database sessions.
    Used mainly for background tasks and scripts.
    """
    session_factory = get_sync_session_local()
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# Alias for common usage
get_db = get_sync_db


@contextmanager
def get_db_session() -> Generator:
    """
    Context manager for sync database sessions.
    
    Usage:
        with get_db_session() as db:
            db.add(item)
            db.commit()
    """
    session_factory = get_sync_session_local()
    session = session_factory()
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
    engine = get_sync_engine()
    Base.metadata.create_all(bind=engine)
    logger.info("All database tables created")


def drop_all_tables():
    """Drop all database tables (USE WITH CAUTION)"""
    engine = get_sync_engine()
    Base.metadata.drop_all(bind=engine)
    logger.warning("All database tables dropped")


async def check_database_connection() -> bool:
    """Check if database is accessible"""
    try:
        engine = get_async_engine()
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

