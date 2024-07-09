import os

import dotenv
from geoalchemy2 import Geometry
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base, sessionmaker

from src.config import settings

dotenv.load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


echo_sql = settings.echo_sql
if isinstance(echo_sql, str):
    echo_sql = echo_sql.lower() == "true"


engine = create_async_engine(
    DATABASE_URL,
    echo=echo_sql,
    future=True,
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
