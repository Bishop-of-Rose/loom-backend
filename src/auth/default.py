from datetime import datetime, UTC

from fastapi import APIRouter, Depends, status, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

from ..models import User
from ..schemas import RegistrationRequestForm, LoginForm, UserResponse
from ..core import blacklist
from ..core.config import settings
from ..core.database import get_session
from ..core.dependencies import get_access_token, get_refresh_token
from ..core.limiter import limiter
from ..core.password import hash_pw, verify_pw
from ..core.security import create_tokens, decode_jwt_token

router = APIRouter(
    prefix='/auth',
    tags=['Authentication']
)

@router.post('/register' , status_code=status.HTTP_201_CREATED, response_model=UserResponse)
@limiter.limit('10/minute')
def register(request: Request,
             response: Response,
             user: RegistrationRequestForm,
             session: Session = Depends(get_session)):
    user.password = hash_pw(user.password)
    user = User(**user.model_dump())
    try:
        session.add(user)
        session.commit()
        session.refresh(user)

    except IntegrityError as e:
        if isinstance(e.orig, UniqueViolation):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail='User with that email already exists')

    return user

@router.post('/login')
@limiter.limit('10/minute')
def login(request: Request,
          response: Response,
          data: LoginForm,
          session: Session = Depends(get_session)):
    stmt = select(User).where(User.email == data.email)
    user = session.scalars(stmt).one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid credentials')

    if not verify_pw(data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid credentials')

    access_token, refresh_token = create_tokens(user.id)
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite='lax',
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return {'access_token': access_token}

@router.post('/logout')
def logout(response: Response,
           access_token: str = Depends(get_access_token),
           refresh_token: str = Depends(get_refresh_token)):
    access_payload = decode_jwt_token(access_token, 'access')
    refresh_payload = decode_jwt_token(refresh_token, 'refresh')
    access_jti, access_ttl = access_payload.get('jti'), int(access_payload.get('exp') - datetime.now(UTC).timestamp())
    refresh_jti, refresh_ttl = refresh_payload.get('jti'), int(refresh_payload.get('exp') - datetime.now(UTC).timestamp())
    blacklist.ban(access_jti, access_ttl)
    blacklist.ban(refresh_jti, refresh_ttl)
    response.delete_cookie('refresh_token')
    return

@router.post('/refresh')
def refresh(response: Response,
            access_token: str = Depends(get_access_token),
            refresh_token: str = Depends(get_refresh_token)):
    access_payload = decode_jwt_token(access_token, 'access')
    refresh_payload = decode_jwt_token(refresh_token, 'refresh')
    refresh_jti = refresh_payload.get('jti')
    refresh_ttl = int(refresh_payload.get('exp') - datetime.now(UTC).timestamp())
    if blacklist.check(refresh_jti):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Refresh token revoked')

    blacklist.ban(refresh_jti, refresh_ttl)
    response.delete_cookie('refresh_token')

    user_id = access_payload.get('sub')
    access_token, refresh_token = create_tokens(user_id)
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite='lax',
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return {'access_token': access_token}