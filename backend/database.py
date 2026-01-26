"""
Database connection and session management.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from config import settings
import logging

logger = logging.getLogger(__name__)

import uuid

# Workaround for Supabase Transaction Pooler:
# Force unique prepared statement names even if cache is disabled (double safety)
def _get_start_name(*args): 
    return f"stmt_{uuid.uuid4().hex}"

# Create async engine
# using NullPool to avoid "prepared statement already exists" errors with Supabase Transaction Mode
engine = create_async_engine(
    settings.database_url,
    echo=settings.app_debug,
    poolclass=NullPool,
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_name_func": _get_start_name
    }
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Base class for models
Base = declarative_base()


from typing import AsyncGenerator


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session.
    Use with FastAPI Depends.
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


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")


async def close_db():
    """Close database connections."""
    await engine.dispose()
    logger.info("Database connections closed")
