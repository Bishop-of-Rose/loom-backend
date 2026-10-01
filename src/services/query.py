from typing import Tuple, Literal

from fastapi import HTTPException, status
from sqlalchemy import Select
from sqlalchemy.orm import Session

from ..models import Profile, Post, Comment
from ..schemas import QueryResponse
from ..core.cursor import decode_cursor, encode_cursor

def query_items(session: Session, Base: Profile | Post | Comment,
                stmt: Select[Tuple[Profile | Post | Comment]],
                limit: int, cursor: str | None = None, direction: Literal['prev', 'next'] = 'next') -> QueryResponse:
    if cursor is not None:
        try:
            target_id = decode_cursor(cursor)
            if direction == 'next':
                stmt = stmt.where(Base.id < target_id).order_by(Base.id.desc())

            elif direction == 'prev':
                stmt = stmt.where(Base.id > target_id).order_by(Base.id.asc())

        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Invalid cursor')

    else:
        stmt = stmt.order_by(Base.id.desc())

    stmt = stmt.limit(limit + 1)
    result = list(session.scalars(stmt).all())

    has_more = len(result) > limit
    has_next = False
    has_prev = False
    items = result[:limit]

    if direction == 'prev':
        items.reverse()

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

    if items:
        if has_next:
            next_cursor = encode_cursor(items[-1].id)

        if has_prev:
            prev_cursor = encode_cursor(items[0].id)

    return QueryResponse(
        data=items,
        next_cursor=next_cursor,
        prev_cursor=prev_cursor
    )