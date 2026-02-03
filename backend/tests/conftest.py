"""
Pytest Configuration
Fixtures for testing the API
"""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.database import Base, get_db
from app.config import settings

# Test database URL (use in-memory SQLite for fast tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False
)

# Create test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Override get_db dependency
async def override_get_db() -> AsyncGenerator:
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Pytest fixtures
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator:
    """Create database tables and provide session"""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Provide session
    async with TestSessionLocal() as session:
        yield session
    
    # Drop tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session) -> AsyncGenerator:
    """Create test client"""
    # Override database dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # Clear overrides
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session):
    """Create a test user"""
    from app.models.user import User
    from app.core.security import hash_password
    
    user = User(
        email="test@example.com",
        password_hash=hash_password("Test123!@#"),
        full_name="Test User",
        is_active=True,
        is_verified=True
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return user


@pytest.fixture
async def auth_headers(test_user):
    """Get authentication headers for test user"""
    from app.core.security import create_access_token
    
    access_token = create_access_token(data={"sub": str(test_user.id)})
    
    return {
        "Authorization": f"Bearer {access_token}"
    }
