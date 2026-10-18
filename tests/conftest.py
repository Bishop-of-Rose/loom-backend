import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.models import Base
from src.core.database import get_session
from src.core.config import settings

engine = create_engine(settings.TEST_DATABASE_URL)
testing_session = sessionmaker(bind=engine)

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
        'email': registered_user['email'],
        'password': registered_user['password']
    }

    res = client.post('/auth/login', json=data)
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