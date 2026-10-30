import time

from httpx2 import AsyncClient
from _pytest.monkeypatch import MonkeyPatch

async def test_rate_limit_blocks_after_threshold(client: AsyncClient):
    spam_payload = {'email': 'spam@example.com', 'password': 'spam_password'}
    for _ in range(10):
        await client.post('auth/jwt/login', json=spam_payload)

    res = await client.post('auth/jwt/login', json=spam_payload)
    assert res.status_code == 429

async def test_rate_limit_runs_under_window(client: AsyncClient):
    spam_payload = {'email': 'spam@example.com', 'password': 'spam_password'}
    for _ in range(10):
        res = await client.post('auth/jwt/login', json=spam_payload)
        assert res.status_code != 429

async def test_rate_limit_resets_after_window(client: AsyncClient, monkeypatch: MonkeyPatch):
    spam_payload = {'email': 'spam@example.com', 'password': 'spam_password'}
    for _ in range(10):
        await client.post('auth/jwt/login', json=spam_payload)

    res = await client.post('auth/jwt/login', json=spam_payload)
    assert res.status_code == 429

    current = time.time() + 61
    monkeypatch.setattr(time, 'time', lambda: current)

    res = await client.post('auth/jwt/login', json=spam_payload)
    assert res.status_code != 429