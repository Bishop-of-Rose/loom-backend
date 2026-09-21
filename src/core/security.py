from typing import Tuple, Dict
from uuid import uuid4, UUID
from datetime import datetime, UTC, timedelta

from jwt import encode, decode, ExpiredSignatureError, InvalidTokenError
from fastapi import HTTPException, status

from .config import settings

def tokenize(user_id: UUID) -> Tuple[str, str]:
    sub = str(user_id)
    jti =  str(uuid4())
    current_time = datetime.now(UTC)
    access_exp = current_time + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_exp = current_time + timedelta(hours=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    access_payload = {
        "sub": sub,
        "jti": jti,
        "exp": access_exp,
        "type": "Access"
    }

    refresh_payload = {
        "sub": sub,
        "jti": jti,
        "exp": refresh_exp,
        "type": "Refresh"
    }

    access_token = encode(access_payload, settings.SECRET_KEY, settings.ALGORITHM)
    refresh_token = encode(refresh_payload, settings.SECRET_KEY, settings.ALGORITHM)

    return access_token, refresh_token

def detokenize(token: str, token_type: str, suppress: bool = False) -> Dict[str, str | int]:
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f'{token_type} token is missing')

    try:
        payload = decode(token, settings.SECRET_KEY, settings.ALGORITHM)
        if payload.get('type') != token_type:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail=f'Invalid {token_type} token')

    except ExpiredSignatureError:
        if not suppress:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f'{token_type} token has expired')

        payload = decode(token, settings.SECRET_KEY, settings.ALGORITHM, options={'verify_exp': False})
        if payload.get('type') != token_type:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail=f'Invalid {token_type} token')

    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f'Invalid {token_type} token')

    return payload