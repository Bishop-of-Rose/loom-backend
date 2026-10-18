from typing import Dict, Any

from ..core.redis import client

def match(real_ip: str, unique_id: str):
    for key in client.scan_iter(match=f'session:{real_ip}:{unique_id}*'):
        if key:
            return True

    return False

def get(session_id: str) -> Dict | None:
    for key in client.scan_iter(match=f'session*{session_id}'):
        if key:
            raw_data = client.hgetall(key)
            session_data = {}
            client.expire(key, 3600)
            for i, value in raw_data.items():
                session_data[str(i.decode())] = str(value.decode())

            return session_data

    return None

def add(real_ip: str, unique_id: str, session_id: str, session_data: Dict) -> None:
    client.hset(f'session:{real_ip}:{unique_id}:{session_id}', mapping=session_data)
    client.expire(f'session:{real_ip}:{unique_id}:{session_id}', 3600)

def remove(session_id: str) -> None:
    client.delete(f'session:{session_id}')
