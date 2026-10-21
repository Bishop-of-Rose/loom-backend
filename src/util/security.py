from uuid import UUID, uuid4
from datetime import datetime, UTC, timedelta

import jwt
from pydantic import BaseModel
from fastapi import status, HTTPException

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

    token = jwt.encode(payload, settings.SECRET_KEY, settings.ALGORITHM)
    return token

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
        payload = Payload.model_validate(payload).model_dump()
        if payload['exp'] - payload['iat'] != settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60:
            raise ValueError

    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f'Expected access token form unadhered')

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f'Access token expired')

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f'Access token invalid')

    return payload