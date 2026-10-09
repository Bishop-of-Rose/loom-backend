from uuid import uuid4, uuid7
from datetime import datetime, UTC, timedelta

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.models import Base
from src.core.database import get_session
from src.core.config import settings

engine = create_engine(settings.TEST_DATABASE_URL)
testing_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope='session', autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

@pytest.fixture(scope='function')
def session():
    connection = engine.connect()
    transaction = connection.begin()
    session = testing_session(bind=connection)

    nested = connection.begin_nested()

    def restart_savepoint():
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    event.listen(session, 'after_transaction_end', lambda s, t: restart_savepoint)

    try:
        yield session

    finally:
        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture(scope='function')
def client(session):
    def override_get_session():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def registered_user(client):
    data = {
        'email': 'registeredemail123@gmail.com',
        'password': 'password'
    }

    res = client.post('/auth/register', json=data)
    data.update(res.json())
    return data

@pytest.fixture
def logged_in(client, registered_user):
    data = {
        'username': registered_user['email'],
        'password': registered_user['password']
    }

    res = client.post('/auth/login', data=data)
    access_token = res.json()['access_token']
    refresh_token = res.cookies.get('refresh_token')

    return access_token, refresh_token

@pytest.fixture
def logged_out(client, logged_in):
    access_token, refresh_token = logged_in

    res = client.post(
        '/auth/logout',
        headers={'Authorization': 'Bearer ' + access_token},
        cookies={'refresh_token': refresh_token}
    )

    return logged_in

@pytest.fixture
def random_expired_tokens():
    sub = str(uuid7())
    current_time = datetime.now(UTC)

    access_payload = {
        'sub': sub,
        'jti': str(uuid4()),
        'exp': current_time,
        'type': 'access'
    }

    refresh_payload = {
        'sub': sub,
        'jti': str(uuid4()),
        'exp': current_time,
        'type': 'refresh'
    }

    access_token = jwt.encode(access_payload, settings.SECRET_KEY, settings.ALGORITHM)
    refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, settings.ALGORITHM)

    return access_token, refresh_token

@pytest.fixture
def random_unmatched_tokens():
    sub = str(uuid7())
    current_time = datetime.now(UTC)
    access_exp = current_time + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_exp = current_time + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    access_payload = {
        'sub': sub,
        'jti': str(uuid4()),
        'exp': access_exp,
        'type': 'access'
    }

    refresh_payload = {
        'sub': sub,
        'jti': str(uuid4()),
        'exp': refresh_exp,
        'type': 'refresh'
    }

    access_token = jwt.encode(access_payload, settings.SECRET_KEY, settings.ALGORITHM)
    refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, settings.ALGORITHM)

    return access_token, refresh_token

@pytest.fixture
def random_matched_tokens():
    sub = str(uuid7())
    jti = str(uuid4())
    current_time = datetime.now(UTC)
    access_exp = current_time + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_exp = current_time + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    access_payload = {
        'sub': sub,
        'jti': jti,
        'exp': access_exp,
        'type': 'access'
    }

    refresh_payload = {
        'sub': sub,
        'jti': jti,
        'exp': refresh_exp,
        'type': 'refresh'
    }

    access_token = jwt.encode(access_payload, settings.SECRET_KEY, settings.ALGORITHM)
    refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, settings.ALGORITHM)

    return access_token, refresh_token