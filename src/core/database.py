from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from .config import settings

class Base(DeclarativeBase):
    pass

engine = create_engine(settings.DATABASE_URL, echo=True)
session = sessionmaker(bind=engine)

def get_session() -> Generator[Session]:
    db = session()
    try:
        yield db
    finally:
        db.close()