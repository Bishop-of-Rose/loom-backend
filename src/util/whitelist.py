from uuid import UUID

from ..core.redis import client

def get(hashed: str) -> UUID | None:
    user_id = client.get(f'whitelist:{hashed}')
    if user_id is None:
        return None

    return UUID(bytes=user_id)

def add(hashed: str, ttl: int, user_id: UUID) -> None:
    if ttl > 0:
        client.set(f'whitelist:{hashed}', user_id.bytes, ttl)

def remove(hashed: str) -> None:
    client.delete(f'whitelist:{hashed}')