import hashlib
import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only, raiseload

from ..core.config import settings
from ..core.database import get_session
from ..core.dependencies import get_refresh_token
from ..core.limiter import limiter
from ..models import User
from ..schemas import LoginForm
from ..util import whitelist
from ..util.password import verify_pw
from ..util.security import create_access_token

router = APIRouter(prefix='/auth/jwt', tags=['JWT Authentication'])

@router.post('/login')
@limiter.limit('10/minute')
async def login(request: Request,
                response: Response,
                data: LoginForm,
                session: AsyncSession = Depends(get_session)):
    stmt = (
        select(User)
        .where(User.email == data.email)
        .options(load_only(User.id, User.email, User.password), raiseload(User.profile))
    )
    user = (await session.scalars(stmt)).one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials'
        )

    if user.password is None or not verify_pw(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials'
        )

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
def logout(response: Response, refresh_token: str = Depends(get_refresh_token)):
    hashed = hashlib.sha256(refresh_token.encode()).hexdigest()
    whitelist.remove(hashed)
    response.delete_cookie('refresh_token')

@router.post('/refresh')
def refresh(response: Response, refresh_token: str = Depends(get_refresh_token)):
    hashed = hashlib.sha256(refresh_token.encode()).hexdigest()
    user_id = whitelist.get(hashed)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Refresh token expired or revoked',
        )

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