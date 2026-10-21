from typing import AsyncGenerator, Dict, Tuple, Any

import pytest
from httpx2 import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.main import app
from src.models import Base
from src.core.database import get_session
from src.core.config import settings

engine = create_async_engine(settings.TEST_DATABASE_URL)
testing_local = async_sessionmaker(bind=engine)

@pytest.fixture(scope='session')
def anyio_backend() -> str:
    return 'asyncio'

@pytest.fixture(scope='session', autouse=True)
async def setup_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def get_test_session() -> AsyncGenerator[AsyncSession, None]:
    connection = await engine.connect()
    transaction = await connection.begin()
    session = testing_local(bind=connection)

    nested = await connection.begin_nested()

    async def restart_savepoint():
        nonlocal nested
        if not nested.is_active:
            nested = await connection.begin_nested()

    event.listen(session.sync_session, 'after_transaction_end', lambda s, t: restart_savepoint)
    try:
        yield session

    finally:
        await session.close()
        await transaction.rollback()
        await connection.close()

@pytest.fixture
async def client(get_test_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_session():
        try:
            yield get_test_session
        finally:
            await get_test_session.close()

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture
async def registered_user(client: AsyncClient) -> Dict[str, Any]:
    payload = {
        'email': 'user@example.com',
        'password': 'random_password',
    }
    res = await client.post('/auth/jwt/register', json=payload)
    payload.update(res.json())
    return payload

@pytest.fixture
async def auth_header(client: AsyncClient, registered_user: Dict[str, Any]) -> Dict[str, str]:
    res = await client.post('/auth/jwt/login', json=registered_user)
    access_token = res.json().get('access_token')
    authorization_header = {'Authorization': 'Bearer ' + access_token}
    return authorization_header

@pytest.fixture
async def initiated_profile(client: AsyncClient, registered_user: Dict[str, Any], auth_header: Dict[str, str]) -> Dict[str, Any]:
    payload = {
        'username': 'random_username'
    }
    res = await client.post(
        '/profiles',
        headers=auth_header,
        json=payload
    )
    registered_user['profile'] = res.json()
    return registered_user

@pytest.fixture
async def init_auth_header(client: AsyncClient, initiated_profile: Dict[str, Any]) -> Dict[str, str]:
    res = await client.post('/auth/jwt/login', json=initiated_profile)
    access_token = res.json().get('access_token')
    authorization_header = {'Authorization': 'Bearer ' + access_token}
    return authorization_header

@pytest.fixture
async def logged_in(client: AsyncClient, registered_user: Dict[str, Any]) -> Tuple[str, str]:
    res = await client.post('/auth/jwt/login', json=registered_user)
    access_token = res.json().get('access_token')
    refresh_token = res.cookies.get('refresh_token')
    return access_token, refresh_token

@pytest.fixture
async def logged_out():
    pass

@pytest.fixture(autouse=True)
async def reset_rate_limiter():
    yield
    if hasattr(app.state, "limiter"):
        app.state.limiter._storage.reset()