from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from .config import settings

class Base(DeclarativeBase):
    pass

engine = create_engine(settings.DATABASE_URL, echo=True)
local = sessionmaker(bind=engine)

def get_session() -> Generator[Session, None]:
    with local() as session:
        try:
            yield session
        finally:
            session.close()