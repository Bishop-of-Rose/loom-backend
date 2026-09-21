from datetime import datetime, UTC

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

from ..models import User
from ..schemas import UserCreate, UserResponse
from ..core.blacklist import ban, check
from ..core.config import settings
from ..core.database import get_session
from ..core.dependencies import oauth2_scheme
from ..core.password import hash_pw, verify_pw
from ..core.security import tokenize, detokenize

router = APIRouter(
    prefix='/auth',
    tags=['Authentication']
)

@router.post('/register' , status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def register(user: UserCreate,
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
def login(response: Response,
          credentials: OAuth2PasswordRequestForm = Depends(),
          session: Session = Depends(get_session)):
    stmt = select(User).where(User.email == credentials.username)
    user = session.scalars(stmt).one_or_none()

    if user is None or not verify_pw(credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Invalid Credentials')

    if not verify_pw(credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Invalid Credentials')

    access_token, refresh_token = tokenize(user.id)
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite='none',
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return {'access_token': access_token}

@router.post('/logout')
def logout(request: Request,
           response: Response,
           access_token: str = Depends(oauth2_scheme)):
    refresh_token = request.cookies.get('refresh_token')
    
    access_payload = detokenize(access_token, 'Access', suppress=True)
    refresh_payload = detokenize(refresh_token, 'Refresh', suppress=True)
    access_jti = access_payload.get('jti')
    refresh_jti = refresh_payload.get('jti')

    if access_jti != refresh_jti:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Access token and refresh token do not match')

    if check(access_jti):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Already logged out')

    remaining_ttl = int(access_payload.get('exp') - datetime.now(UTC).timestamp())
    if remaining_ttl > 0:
        ban(access_jti, remaining_ttl)

    response.delete_cookie('refresh_token')
    return

@router.post('/refresh')
def refresh(request: Request,
            response: Response,
            access_token: str = Depends(oauth2_scheme)):
    refresh_token = request.cookies.get('refresh_token')

    access_payload = detokenize(access_token, 'Access', suppress=True)
    refresh_payload = detokenize(refresh_token, 'Refresh')
    access_jti = access_payload.get('jti')
    refresh_jti = refresh_payload.get('jti')

    if access_jti != refresh_jti:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Access token and refresh token do not match')

    if check(access_jti):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Already logged out')

    remaining_ttl = int(refresh_payload.get('exp') - datetime.now(UTC).timestamp())
    if remaining_ttl > 0:
        ban(access_jti, remaining_ttl)

    user_id = access_payload.get('sub')
    access_token, refresh_token = tokenize(user_id)

    response.delete_cookie('refresh_token')
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite='none',
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return {'access_token': access_token}
