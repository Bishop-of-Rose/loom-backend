from typing import List, Literal
from uuid import UUID

from fastapi import Depends, APIRouter, status, Query, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import User
from ..core.cursor import encode_cursor, decode_cursor
from ..core.database import get_session
from ..core.dependencies import get_current_user
from ..core.password import hash_pw
from ..schemas import UserUpdate, UserResponse, QueryResponse, SearchResponse

router = APIRouter(
    prefix='/users',
    tags=['Users']
)

@router.get('', response_model=QueryResponse[UserResponse])
def query_users(current_user: User = Depends(get_current_user),
                session: Session = Depends(get_session),
                limit: int = Query(default=5, ge=1, le=20),
                cursor: str | None = None,
                direction: Literal['prev', 'next'] = 'next'):
    stmt = select(User)
    if cursor is not None:
        try:
            target_id = decode_cursor(cursor)
            if direction == 'next':
                stmt = stmt.where(User.id < target_id).order_by(User.id.desc())

            elif direction == 'prev':
                stmt = stmt.where(User.id > target_id).order_by(User.id.asc())

        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Invalid cursor')

    else:
        stmt = stmt.order_by(User.id.desc())

    stmt = stmt.limit(limit + 1)
    result = list(session.scalars(stmt).all())

    has_more = len(result) > limit
    has_next = False
    has_prev = False
    users = result[:limit]

    if direction == 'prev':
        users.reverse()

    if cursor is None:
        has_prev = False
        has_next = has_more

    elif direction == 'next':
        has_prev = True
        has_next = has_more

    elif direction == 'prev':
        has_prev = has_more
        has_next = True

    next_cursor = None
    prev_cursor = None

    if users:
        if has_next:
            next_cursor = encode_cursor(users[-1].id)

        if has_prev:
            prev_cursor = encode_cursor(users[0].id)

    return QueryResponse(
        data=users,
        next_cursor=next_cursor,
        prev_cursor=prev_cursor
    )

@router.post('/search', response_model=SearchResponse[UserResponse])
def search_users(user_ids: List[UUID],
                 current_user: User = Depends(get_current_user),
                 session: Session = Depends(get_session)):
    stmt = select(User).where(User.id.in_(user_ids))
    users = list(session.scalars(stmt).all())

    old_user_ids = set(user_ids)
    new_user_ids = {user.id for user in users}
    diff = list(old_user_ids - new_user_ids)

    return SearchResponse(
        data=users,
        missing=diff
    )
@router.put('', response_model=UserResponse)
def update_user(edit: UserUpdate,
                session: Session = Depends(get_session),
                current_user: User = Depends(get_current_user)):
    current_user.username = current_user.username if edit.username is None else edit.username
    current_user.password = current_user.password if edit.password is None else hash_pw(edit.password)

    session.commit()
    return current_user

@router.delete('', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(session: Session = Depends(get_session),
                current_user: User = Depends(get_current_user)):
    session.delete(current_user)
    session.commit()
    return