from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .blacklist import check
from .database import get_session
from .security import detokenize
from ..models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

def get_current_user(access_token: str = Depends(oauth2_scheme),
                     session: Session = Depends(get_session)):
    access_payload = detokenize(access_token, 'Access')
    access_jti = access_payload.get('jti')

    if check(access_jti):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='User already logged out')

    user_id = access_payload.get('sub')
    user = session.get(User, user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User authenticated but not found')

    return user