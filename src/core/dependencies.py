from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_session
from ..models import User
from ..util import blacklist
from ..util.security import decode_jwt_token

bearer_scheme = HTTPBearer()

def get_access_token(request: Request) -> str:
    auth_header = request.headers.get('Authorization')
    if auth_header is None or not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Not Authenticated')

    token = auth_header.split()[1]
    return token

def get_refresh_token(request: Request) -> str:
    token = request.cookies.get('refresh_token')
    return token

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
                           session: AsyncSession = Depends(get_session)) -> User:
    token = credentials.credentials
    payload = decode_jwt_token(token, 'access')
    jti = payload.get('jti')
    if blacklist.check(jti):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail='User already logged out')

    user_id = payload.get('sub')
    user = await session.get(User, user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail='Current user not found')

    return user