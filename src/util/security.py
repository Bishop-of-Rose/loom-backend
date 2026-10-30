from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import jwt
from fastapi import HTTPException, status
from pydantic import BaseModel

from ..core.config import settings

class Payload(BaseModel):
    sub: str
    jti: str
    iat: int
    exp: int

def create_access_token(user_id: UUID) -> str:
    iat = datetime.now(UTC)
    exp = iat + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        'sub': str(user_id),
        'jti': str(uuid4()),
        'iat': iat,
        'exp': exp,
    }

    token = jwt.encode(payload, settings.ACCESS_JWT_SECRET, settings.JWT_ALGORITHM)
    return token

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.ACCESS_JWT_SECRET, settings.JWT_ALGORITHM)
        payload = Payload.model_validate(payload).model_dump()

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Expected access token form unadhered',
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Access token expired'
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Access token invalid'
        )

    return payload