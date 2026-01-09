import os
from typing import AsyncGenerator, Optional

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine, async_sessionmaker
from sqlalchemy.pool import NullPool

from src.database import Base, get_session
from src.app import models  # noqa: F401 - needed to register models


# Session-scoped engine and session factory - created once per test session
# within the session-scoped event loop
_test_engine: Optional[AsyncEngine] = None
_test_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


@pytest.fixture(scope="session")
def test_engine() -> AsyncEngine:
    """Create a test engine once per session.
    
    Uses NullPool to avoid connection pooling issues across event loops.
    Each connection is created fresh and closed immediately after use.
    """
    global _test_engine
    if _test_engine is None:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL not set")
        _test_engine = create_async_engine(
            database_url,
            echo=False,
            future=True,
            poolclass=NullPool,  # Disable pooling to avoid event loop issues
        )
    return _test_engine


@pytest.fixture(scope="session")
def test_session_factory(test_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create a test session factory once per session."""
    global _test_session_factory
    if _test_session_factory is None:
        _test_session_factory = async_sessionmaker(
            bind=test_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _test_session_factory


@pytest_asyncio.fixture(scope="session")
async def setup_database(test_engine: AsyncEngine):
    """Set up the test database once per session."""
    async with test_engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Cleanup at end of session
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(
    setup_database, test_session_factory: async_sessionmaker[AsyncSession]
) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client with overridden database dependency."""
    from src.main import app

    async def override_get_session():
        async with test_session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
