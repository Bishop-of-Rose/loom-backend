from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .blacklist import check
from .database import get_session
from .security import decode_jwt_token
from ..models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

def get_refresh_token(request: Request):
    token = request.cookies.get('refresh_token')
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail='Token missing')

    return token

def get_current_user(token: str = Depends(oauth2_scheme),
                     session: Session = Depends(get_session)):
    payload = decode_jwt_token(token)
    jti = payload.get('jti')

    if check(jti):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail='User already logged out')

    user_id = payload.get('sub')
    user = session.get(User, user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail='Not authenticated')

    return user