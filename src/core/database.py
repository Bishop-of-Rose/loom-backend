from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import settings

class Base(DeclarativeBase):
    pass

engine = create_async_engine(settings.DATABASE_URL, echo=True)
local = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

async def get_session() -> AsyncGenerator[AsyncSession]:
    async with local() as session:
        try:
            yield session
        finally:
            await session.close()
