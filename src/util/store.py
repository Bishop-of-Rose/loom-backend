from typing import Dict

from ..core.redis import client

def get(session_id: str) -> Dict | None:
    session_data = client.hgetall(f'session:{session_id}')
    client.expire(f'session:{session_id}', 3600)
    return session_data

def add(session_id: str, session_data: Dict) -> None:
    client.hset(f'session:{session_id}', mapping=session_data)
    client.expire(f'session:{session_id}', 3600)

def remove(session_id: str) -> None:
    client.delete(f'session:{session_id}')
