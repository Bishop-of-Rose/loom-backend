import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import load_only, noload
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import User
from ..schemas import LoginForm
from ..util import store
from ..core.database import get_session
from ..core.limiter import limiter
from ..util.password import verify_pw

router = APIRouter(
    prefix="/auth/session",
)

@router.post('/login')
@limiter.limit('10/minute')
async def login(request: Request,
                response: Response,
                data: LoginForm,
                session: AsyncSession = Depends(get_session)):
    stmt = select(User).where(User.email == data.email).options(load_only(User.id, User.email, User.password),
                                                                noload(User.profile))
    user = (await session.scalars(stmt)).one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid credentials')

    if user.password is None or not verify_pw(data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid credentials')

    session_id = secrets.token_urlsafe(64)
    unique_id = str(user.id)
    real_ip = request.headers.get('X-FORWARDED-FOR', getattr(request.client, 'host', '127.0.0.1'))
    session_data = {
        'user_id': str(user.id),
        'email': user.email
    }

    if store.match(real_ip, unique_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='User already logged in')

    store.add(real_ip, unique_id, session_id, session_data)

    response.set_cookie(
        key='session_id',
        value=session_id,
        httponly=True,
        max_age=3600
    )

    return {'message': 'Logged in successfully'}

@router.post('/logout')
async def logout(request: Request,
                 response: Response):
    session_id = request.cookies.get('session_id')
    store.remove(session_id)
    response.delete_cookie('session_id')
    return {'message': 'Logged out successfully'}