from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import User
from ..util.security import verify_access_token
from .database import get_session

jwt_scheme = HTTPBearer(description='Enter your JWT Bearer Token')

def authenticate_user(
    jwt_auth: HTTPAuthorizationCredentials = Depends(jwt_scheme),
) -> dict:
    user_info = verify_access_token(jwt_auth.credentials)
    return user_info

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