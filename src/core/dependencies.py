from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .blacklist import check
from .database import get_session
from .security import decode_jwt_token
from ..models import User

bearer_scheme = HTTPBearer()

def get_access_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> str:
    token = credentials.credentials
    return token

def get_refresh_token(request: Request) -> str:
    token = request.cookies.get('refresh_token')
    return token

def get_current_user(token: str = Depends(get_access_token),
                     session: Session = Depends(get_session)) -> User:
    payload = decode_jwt_token(token, 'access')
    jti = payload.get('jti')
    if check(jti):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail='User already logged out')

    user_id = payload.get('sub')
    user = session.get(User, user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail='Current user not found')

    return user