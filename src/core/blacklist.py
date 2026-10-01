from uuid import UUID

from .redis import client

def check(jti: UUID) -> bool:
    return client.get(f'blacklist:{jti}') is not None

def ban(jti: UUID, ttl: int) -> None:
    if ttl > 0:
        client.set(f'blacklist:{jti}', 'revoked', ex=ttl)