from typing import Generator

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from .config import settings

class Base(DeclarativeBase):
    pass

engine = create_async_engine(settings.DATABASE_URL, echo=True)
local = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

async def get_session() -> Generator[AsyncSession, None, None]:
    async with local() as session:
        try:
            yield session
        finally:
            await session.close()