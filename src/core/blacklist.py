from uuid import UUID

from .redis import client

def ban(jti: UUID, remaining_ttl: int) -> None:
    client.set(f'{jti}', 'revoked', ex=remaining_ttl)

def check(jti: UUID) -> bool:
    return client.get(f'{jti}') is not None