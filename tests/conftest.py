import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base, get_session
from src.app import models  # noqa: F401 - needed to register models


# Create a test-specific engine
_test_engine = None
_test_session_factory = None


def get_test_engine():
    """Get or create the test engine."""
    global _test_engine
    if _test_engine is None:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL not set")
        _test_engine = create_async_engine(
            database_url,
            echo=False,
            future=True,
        )
    return _test_engine


def get_test_session_factory():
    """Get or create the test session factory."""
    global _test_session_factory
    if _test_session_factory is None:
        _test_session_factory = sessionmaker(
            bind=get_test_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _test_session_factory


@pytest_asyncio.fixture(scope="module")
async def setup_database():
    """Set up the test database once per module."""
    engine = get_test_engine()
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Cleanup at end of module
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(setup_database) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client with overridden database dependency."""
    from src.main import app
    
    async def override_get_session():
        session_factory = get_test_session_factory()
        async with session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
    
    app.dependency_overrides[get_session] = override_get_session
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()
