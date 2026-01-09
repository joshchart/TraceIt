import os
from typing import AsyncGenerator, Optional

import dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.config import settings

dotenv.load_dotenv()

Base = declarative_base()

# Engine and session factory will be created lazily
_engine: Optional[AsyncEngine] = None
_SessionLocal: Optional[sessionmaker] = None


def get_engine() -> AsyncEngine:
    """Get or create the async engine (lazy initialization)."""
    global _engine
    if _engine is None:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        _engine = create_async_engine(
            database_url,
            echo=settings.echo_sql,
            future=True,
        )
    return _engine


def get_session_local() -> sessionmaker:
    """Get or create the session factory (lazy initialization)."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            bind=get_engine(),
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
            class_=AsyncSession,
        )
    return _SessionLocal


# Backwards compatibility - expose engine as a function call
engine = property(lambda self: get_engine())


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that yields database sessions."""
    session_factory = get_session_local()
    async with session_factory() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


def reset_engine() -> None:
    """Reset the engine and session factory. Useful for testing."""
    global _engine, _SessionLocal
    _engine = None
    _SessionLocal = None
