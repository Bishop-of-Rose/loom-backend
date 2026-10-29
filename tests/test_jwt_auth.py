from typing import Any

from httpx2 import AsyncClient

from src.schemas import UserResponse

async def test_jwt_register_success(client: AsyncClient):
    payload = {'email': 'user@example.com', 'password': 'random_password'}
    res = await client.post('/auth/jwt/register', json=payload)
    UserResponse.model_validate(res.json())
    assert res.status_code == 201

async def test_jwt_login_success(client: AsyncClient, registered_user: dict[str, Any]):
    res = await client.post('/auth/jwt/login', json=registered_user)
    assert res.status_code == 200
    assert res.json().get('access_token')
    assert res.cookies.get('refresh_token')

async def test_jwt_logout_success(client: AsyncClient, logged_in: tuple[str, str]):
    refresh_token = logged_in[0]
    res = await client.post(
        '/auth/jwt/logout',
        cookies={'refresh_token': refresh_token},
    )
    assert res.status_code == 200
    assert not res.cookies.get('refresh_token')

async def test_jwt_refresh_success(client: AsyncClient, logged_in: tuple[str, str]):
    refresh_token = logged_in[1]
    res = await client.post(
        '/auth/jwt/refresh',
        cookies={'refresh_token': refresh_token},
    )
    assert res.status_code == 200
    assert res.cookies.get('refresh_token')