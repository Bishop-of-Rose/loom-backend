from uuid import UUID

from ..core.redis import client

def check(jti: UUID) -> bool:
    return client.exists(f'blacklist:{jti}')

def ban(jti: UUID, ttl: int) -> None:
    if ttl > 0:
        client.set(f'blacklist:{jti}', 'revoked', ex=ttl)