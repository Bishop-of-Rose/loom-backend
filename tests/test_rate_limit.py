from fastapi.testclient import TestClient

from src.main import app
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from src.core.config import settings
from src.core.database import get_session

class Base(DeclarativeBase):
    pass

engine = create_engine(settings.DATABASE_URL, echo=True)
session = sessionmaker(bind=engine)

def test_get_session() -> Generator[Session]:
    db = session()
    try:
        yield db
    finally:
        db.close()

def test_rate_limit_exceeded_handler():
    app.dependency_overrides[get_session] = test_get_session
    client = TestClient(app)
    for _ in range(100):
        token = client.post('/auth/login', data={'username': 'user@example.com', 'password': 'string'})

    token = client.post('/auth/login', data={'username': 'user@example.com', 'password': 'string'})
    assert token.status_code == 429

test_rate_limit_exceeded_handler()