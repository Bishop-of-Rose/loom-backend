from uuid import UUID

from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

from ..models import User
from ..core.database import get_session
from ..core.dependencies import get_current_user
from ..core.password import hash_pw
from ..schemas import UserUpdate, UserResponse

router = APIRouter(
    prefix='/users',
    tags=['Users']
)

@router.get('/whoami', response_model=UserResponse)
def who_am_i(current_user = Depends(get_current_user)):
    return current_user

@router.get('/{user_id}', response_model=UserResponse)
def read_user(user_id: UUID,
              current_user: User = Depends(get_current_user),
              session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User not found')

    return user

@router.put('', response_model=UserResponse)
def update_user(edit: UserUpdate,
                session: Session = Depends(get_session),
                current_user: User = Depends(get_current_user)):
    current_user.username = current_user.username if edit.username is None else edit.username
    current_user.password = current_user.password if edit.password is None else hash_pw(edit.password)

    session.commit()
    return current_user

@router.delete('')
def delete_user(session: Session = Depends(get_session),
                current_user: User = Depends(get_current_user)):
    session.delete(current_user)
    session.commit()
    return