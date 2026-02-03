"""
Database configuration and session management
Async SQLAlchemy setup with SQLite/PostgreSQL support
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import QueuePool, StaticPool
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Create async engine with appropriate pooling based on database type
if "sqlite" in settings.DATABASE_URL:
    # SQLite doesn't support connection pooling
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # PostgreSQL with connection pooling
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Create declarative base
Base = declarative_base()


async def get_db():
    """
    Dependency for FastAPI routes to get database session
    
    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database - create all tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")


async def close_db():
    """Close database connections"""
    await engine.dispose()
    logger.info("Database connections closed")
