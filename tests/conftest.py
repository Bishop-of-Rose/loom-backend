from collections.abc import AsyncGenerator
from typing import Any

import pytest
from httpx2 import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from src.core.config import settings
from src.core.database import get_session
from src.main import app
from src.models import Base

@pytest.fixture(scope='session', autouse=True)
async def setup_test_database():
    engine = create_async_engine(settings.TEST_DATABASE_URL)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def test_session() -> AsyncGenerator[AsyncSession]:
    engine = create_async_engine(settings.TEST_DATABASE_URL)
    connection = await engine.connect()
    transaction = await connection.begin()
    session = AsyncSession(bind=connection)

    nested = await connection.begin_nested()
    @event.listens_for(session.sync_session, 'after_transaction_end', once=True)
    async def restart_savepoint(s, t):
        nonlocal nested
        if not nested.is_active:
            nested = await connection.begin_nested()

    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()
    await engine.dispose()

@pytest.fixture
async def client(test_session: AsyncGenerator[AsyncSession]) -> AsyncGenerator[AsyncClient]:
    async def override_get_session():
        yield test_session

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture
async def registered_user(client: AsyncClient) -> dict[str, Any]:
    payload = {
        'email': 'user@example.com',
        'password': 'random_password',
    }
    res = await client.post('/auth/jwt/register', json=payload)
    payload.update(res.json())
    return payload

@pytest.fixture
async def auth_header(
    client: AsyncClient, registered_user: dict[str, Any]
) -> dict[str, str]:
    res = await client.post('/auth/jwt/login', json=registered_user)
    access_token = res.json().get('access_token')
    authorization_header = {'Authorization': 'Bearer ' + access_token}
    return authorization_header

@pytest.fixture
async def init_auth_header(
    client: AsyncClient, auth_header: dict[str, str],
) -> dict[str, str]:
    payload = {'username': 'random_username'}
    await client.post('/profiles', headers=auth_header, json=payload)
    return auth_header

@pytest.fixture
async def logged_in(
    client: AsyncClient, registered_user: dict[str, Any]
) -> tuple[str, str]:
    res = await client.post('/auth/jwt/login', json=registered_user)
    access_token = res.json().get('access_token')
    refresh_token = res.cookies.get('refresh_token')
    return access_token, refresh_token

@pytest.fixture
async def logged_out():
    pass

@pytest.fixture
async def created_post(
    client: AsyncClient, init_auth_header: dict[str, str]
) -> dict[str, Any]:
    payload = {'title': 'random title', 'content': 'random content'}
    res = await client.post('/posts', headers=init_auth_header, json=payload)
    post = res.json()
    return post

@pytest.fixture
async def created_root_comment(
    client: AsyncClient, init_auth_header: dict[str, str], created_post: dict[str, Any]
) -> dict[str, Any]:
    payload = {'commented': created_post['id'], 'content': 'random content'}
    res = await client.post('/comments', headers=init_auth_header, json=payload)
    comment = res.json()
    return comment

@pytest.fixture
async def created_branch_comment(
    client: AsyncClient, init_auth_header: dict[str, str], created_root_comment: dict[str, Any]
) -> dict[str, Any]:
    payload = {'replied': created_root_comment['id'], 'content': 'random content'}
    res = await client.post('/comments', headers=init_auth_header, json=payload)
    comment = res.json()
    return comment

@pytest.fixture(autouse=True)
async def reset_rate_limiter():
    yield
    if hasattr(app.state, 'limiter'):
        app.state.limiter._storage.reset()