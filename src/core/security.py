from typing import Tuple, Dict, Literal
from uuid import UUID, uuid4
from datetime import datetime, UTC, timedelta

from pydantic import BaseModel
from jwt import encode, decode, ExpiredSignatureError, InvalidTokenError
from fastapi import status, HTTPException

from .config import settings

class Payload(BaseModel):
    sub: str
    jti: str
    exp: int
    type: Literal['access', 'refresh']

def create_tokens(user_id: UUID, current_time: datetime = datetime.now(UTC)) -> Tuple:
    access_payload = {
        'sub': str(user_id),
        'jti': str(uuid4()),
        'exp': current_time + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        'type': 'access'
    }

    refresh_payload = {
        'sub': str(user_id),
        'jti': str(uuid4()),
        'exp': current_time + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        'type': 'refresh'
    }

    access_token = encode(access_payload, settings.SECRET_KEY, settings.ALGORITHM)
    refresh_token = encode(refresh_payload, settings.SECRET_KEY, settings.ALGORITHM)

    return access_token, refresh_token

def decode_jwt_token(token: str, expected: Literal['access', 'refresh'], suppress: bool = False) -> Dict:
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail=f'{expected.capitalize()} token missing')

    try:
        payload = decode(token, settings.SECRET_KEY, settings.ALGORITHM, options={"verify_exp": not suppress})
        payload = Payload.model_validate(payload).model_dump()
        if payload['type'] != expected:
            raise ValueError

    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f'{expected.capitalize()} token form unadhered')

    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f'{expected.capitalize()} token expired')

    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f'Invalid {expected} token')

    return payload
