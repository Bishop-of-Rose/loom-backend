from fastapi import APIRouter, Request, Response, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import load_only, raiseload
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_session
from ..core.limiter import limiter
from ..models import User
from ..schemas import LoginForm
from ..util import store
from ..util.password import verify_pw

router = APIRouter(prefix='/auth/session', tags=['Session Authentication'])

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

    session_data = {
        'sub': str(user.id),
        'email': user.email
    }
    session_id = store.add(session_data)
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