from typing import Dict
from uuid import UUID, uuid4
from datetime import datetime, UTC, timedelta

from jwt import encode, decode, ExpiredSignatureError, InvalidTokenError
from fastapi import status, HTTPException

from .config import settings

def encode_jwt_token(user_id: UUID, delta: timedelta) -> str:
    token = encode(
        {'sub': str(user_id),
         'jti': str(uuid4()),
         'exp': datetime.now(UTC) + delta},
        settings.SECRET_KEY,
        settings.ALGORITHM
    )
    return token

def decode_jwt_token(token: str, suppress: bool = False) -> Dict:
    try:
        payload = decode(token, settings.SECRET_KEY, settings.ALGORITHM, options={"verify_exp": not suppress})

    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Token expired')

    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid token')

    return payload
