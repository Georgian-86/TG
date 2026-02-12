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

# Validate database configuration
if settings.ENVIRONMENT == "production" and "sqlite" in settings.DATABASE_URL:
    logger.critical("FATAL: SQLite cannot be used in production! Set DATABASE_URL to PostgreSQL.")
    raise ValueError("SQLite is not supported in production environment")

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
    # PostgreSQL with connection pooling (tuned for AWS RDS + 25 concurrent users)
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,       # Detect stale RDS connections
        pool_size=10,             # Base pool size
        max_overflow=20,          # Allow burst up to 30 total connections
        pool_recycle=1800,        # Recycle connections every 30 min (RDS compatibility)
        pool_timeout=30,          # Wait up to 30s for a connection from pool
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
    """Initialize database - create tables if they don't exist (safe for production)"""
    # Import all models to register them with Base.metadata
    from app.models import user, lesson, email_otp, lesson_history, feedback, admin_log, file_upload
    
    try:
        async with engine.begin() as conn:
            # create_all is safe: only creates tables that don't already exist
            logger.info("Ensuring all database tables exist...")
            await conn.run_sync(Base.metadata.create_all)
            
        logger.info("✅ Database tables verified/created successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        # Don't crash the app, just log the error
        logger.warning("App will continue but database operations may fail")


async def close_db():
    """Close database connections"""
    await engine.dispose()
    logger.info("Database connections closed")
