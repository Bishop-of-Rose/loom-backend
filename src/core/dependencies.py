from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_session
from ..models import User
from ..util.security import verify_access_token

bearer_scheme = HTTPBearer()

def get_refresh_token(request: Request) -> str:
    token = request.cookies.get('refresh_token')
    if token is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Refresh token is missing')

    return token

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
                           session: AsyncSession = Depends(get_session)) -> User:
    token = credentials.credentials
    payload = verify_access_token(token)

    user_id = payload.get('sub')
    user = await session.get(User, user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail='Current user not found')

    return user