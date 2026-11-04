import secrets

from ..core.config import settings
from ..core.redis import client

def add(session_data: dict)-> str:
    session_id = secrets.token_urlsafe(64)
    client.hset(f'session:{session_id}', mapping=session_data)
    client.expire(f'session:{session_id}', settings.SESSION_EXPIRE_MINUTES * 60)
    return session_id

def get(session_id: str) -> dict:
    raw_data = client.hgetall(f'session:{session_id}')
    session_data = dict(map(lambda _: (str(_[0].decode()), str(_[1].decode())), raw_data.items()))
    client.expire(f'session:{session_id}', settings.SESSION_EXPIRE_MINUTES * 60)
    return session_data

def remove(session_id: str) -> dict:
    raw_data = client.hgetall(f'session:{session_id}')
    session_data = dict(map(lambda _: (str(_[0].decode()), str(_[1].decode())), raw_data.items()))
    client.delete(f'session:{session_id}')
    return session_data