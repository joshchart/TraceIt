import os

import dotenv
from geoalchemy2 import Geometry
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base, sessionmaker

from src.config import settings

# from sqlalchemy import NullPool


dotenv.load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
# DATABASE_URL = os.getenv("TEST_DATABASE_URL") # NOTE: Uncomment for testing db

echo_sql = settings.echo_sql

engine = create_async_engine(
    DATABASE_URL,
    echo=echo_sql,
    future=True,
    # poolclass=NullPool,  # NOTE: for testing only (allows multiple pytests to run)
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)

Base = declarative_base()


async def get_session():
    async with SessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
