import asyncio

import pytest
from httpx2 import AsyncClient

@pytest.mark.anyio
async def test_rate_limit_blocks_after_threshold(client: AsyncClient):
    spam_payload = {
        'email': 'spam@example.com',
        'password': 'guessed_password'
    }
    for _ in range(10):
        await client.post('auth/jwt/login', json=spam_payload)

    res = await client.post('auth/jwt/login', json= spam_payload)
    assert res.status_code == 429

@pytest.mark.anyio
async def test_rate_limit_runs_under_window(client: AsyncClient):
    spam_payload = {
        'email': 'spam@example.com',
        'password': 'guessed_password'
    }
    for _ in range(10):
        res = await client.post('auth/jwt/login', json=spam_payload)
        assert res.status_code != 429

@pytest.mark.anyio
async def test_rate_limit_resets_after_window(client: AsyncClient, monkeypatch):
    spam_payload = {
        'email': 'spam@example.com',
        'password': 'guessed_password'
    }
    for _ in range(10):
        await client.post('auth/jwt/login', json=spam_payload)

    res = await client.post('auth/jwt/login', json=spam_payload)
    assert res.status_code == 429
    await asyncio.sleep(60)
    res = await client.post('auth/jwt/login', json= spam_payload)
    assert res.status_code != 429