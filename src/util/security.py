from typing import Dict, Literal
from uuid import UUID, uuid4
from datetime import datetime, UTC, timedelta

import jwt
from pydantic import BaseModel
from fastapi import status, HTTPException

from ..core.config import settings

class Payload(BaseModel):
    sub: str
    jti: str
    exp: int
    type: Literal['access', 'refresh']

def encode_jwt_token(user_id: UUID, expected: Literal['access', 'refresh']) -> str:
    diff = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES) if expected == 'access' else timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    exp = datetime.now(UTC) + diff
    payload = {
        'sub': str(user_id),
        'jti': str(uuid4()),
        'exp': exp,
        'type': expected
    }

    token = jwt.encode(payload, settings.SECRET_KEY, settings.ALGORITHM)
    return token

def decode_jwt_token(token: str, expected: Literal['access', 'refresh']) -> Dict:
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail=f'{expected.capitalize()} token missing')

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
        payload = Payload.model_validate(payload).model_dump()
        if payload['type'] != expected:
            raise ValueError

    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f'{expected.capitalize()} token form unadhered')

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f'{expected.capitalize()} token expired')

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f'Invalid {expected} token')

    return payload
