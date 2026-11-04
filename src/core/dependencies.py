from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, APIKeyCookie
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import User
from ..util import store
from ..util.security import verify_access_token
from .database import get_session

jwt_scheme = HTTPBearer(auto_error=False, description='Enter your JWT Bearer Token')
session_scheme = APIKeyCookie(name='session_id', auto_error=False, description='Enter your Session ID')

def authenticate_user(
    jwt_auth: HTTPAuthorizationCredentials = Depends(jwt_scheme),
    session_auth: str = Depends(session_scheme)
) -> dict:
    if jwt_auth:
        user_info = verify_access_token(jwt_auth.credentials)
        return user_info

    if session_auth:
        user_info = store.get(session_auth)
        return user_info

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Not Authenticated'
    )

async def get_current_user(
    authenticated_user: dict = Depends(authenticate_user),
    session: AsyncSession = Depends(get_session),
) -> User:
    user_id = authenticated_user.get('sub')
    user = await session.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Current user not found'
        )

    return user

def get_refresh_token(request: Request) -> str:
    token = request.cookies.get('refresh_token')
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Refresh token not provided'
        )

    return token