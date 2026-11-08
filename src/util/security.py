from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from pydantic import BaseModel
from fastapi import HTTPException, status

from ..core.config import settings

class AccessPayload(BaseModel):
    sub: UUID
    iat: int
    exp: int

def create_access_token(user_id: UUID) -> str:
    iat = datetime.now(UTC)
    exp = iat + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        'sub': str(user_id),
        'iat': iat,
        'exp': exp,
    }

    token = jwt.encode(payload, settings.JWT_SECRET, settings.JWT_ALGORITHM)
    return token

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, settings.JWT_ALGORITHM)
        payload = AccessPayload.model_validate(payload).model_dump()
        if payload['exp'] - payload['iat'] != settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60:
            raise ValueError

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