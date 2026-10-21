import secrets
import hashlib

from fastapi import APIRouter, Depends, status, Request, Response, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import load_only, noload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from asyncpg.exceptions import UniqueViolationError

from ..models import User
from ..schemas import RegistrationForm, LoginForm, UserResponse
from ..util import whitelist
from ..core.config import settings
from ..core.database import get_session
from ..core.dependencies import get_refresh_token
from ..core.limiter import limiter
from ..util.password import hash_pw, verify_pw
from ..util.security import create_access_token

router = APIRouter(
    prefix='/auth/jwt',
    tags=['JWT Authentication']
)

@router.post('/register' , status_code=status.HTTP_201_CREATED, response_model=UserResponse)
@limiter.limit('10/minute')
async def register(request: Request,
                   response: Response,
                   user: RegistrationForm,
                   session: AsyncSession = Depends(get_session)):
    user.password = hash_pw(user.password)
    user = User(**user.model_dump())
    try:
        session.add(user)
        await session.commit()
        await session.refresh(user)

    except IntegrityError as e:
        if isinstance(getattr(e.orig, '__cause__', None), UniqueViolationError):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail='User with that email already exists')

    return user

@router.post('/login')
@limiter.limit('10/minute')
async def login(request: Request,
                response: Response,
                data: LoginForm,
                session: AsyncSession = Depends(get_session)):
    stmt = select(User).where(User.email == data.email).options(load_only(User.id, User.password),
                                                                noload(User.profile))
    user = (await session.scalars(stmt)).one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid credentials')

    if user.password is None or not verify_pw(data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid credentials')

    access_token = create_access_token(user.id)
    refresh_token = secrets.token_hex(32)
    hashed = hashlib.sha256(refresh_token.encode()).hexdigest()
    whitelist.add(hashed, settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60, user.id)

    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return {'access_token': access_token}

@router.post('/logout')
def logout(response: Response,
           refresh_token: str = Depends(get_refresh_token)):
    hashed = hashlib.sha256(refresh_token.encode()).hexdigest()
    whitelist.remove(hashed)
    response.delete_cookie('refresh_token')
    return

@router.post('/refresh')
def refresh(response: Response,
            refresh_token: str = Depends(get_refresh_token)):
    hashed = hashlib.sha256(refresh_token.encode()).hexdigest()
    user_id = whitelist.get(hashed)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Refresh token expired or revoked')

    whitelist.remove(hashed)
    response.delete_cookie('refresh_token')

    access_token = create_access_token(user_id)
    refresh_token = secrets.token_hex(32)
    hashed = hashlib.sha256(refresh_token.encode()).hexdigest()
    whitelist.add(hashed, settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60, user_id)

    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return {'access_token': access_token}