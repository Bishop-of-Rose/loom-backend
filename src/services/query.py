from typing import Tuple, Literal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import Select
from sqlalchemy.orm import Session

from ..models import Profile, Post, Comment
from ..schemas import QueryResponse, QueryMeta
from ..util.cursor import decode_cursor, encode_cursor

def query_items(session: Session, Base: Profile | Post | Comment,
                stmt: Select[Tuple[Profile | Post | Comment]],
                cursor: str | None, direction: Literal['prev', 'next'],
                limit: int) -> QueryResponse[Profile | Post | Comment]:
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
        if direction == 'next':
            stmt = stmt.order_by(Base.id.desc())

        elif direction == 'prev':
            stmt = stmt.order_by(Base.id.asc())

    stmt = stmt.limit(limit + 1)
    result = list(session.scalars(stmt).all())

    has_more = len(result) > limit
    has_next = False
    has_prev = False
    next_cursor = None
    prev_cursor = None
    items = result[:limit]

    if direction == 'prev':
        items.reverse()

    if cursor is None:
        if direction == 'next':
            has_next = has_more

        elif direction == 'prev':
            has_prev = has_more

    elif direction == 'next':
        has_prev = True
        has_next = has_more

    elif direction == 'prev':
        has_prev = has_more
        has_next = True

    if items:
        if has_next:
            if direction == 'next':
                target = UUID(int=(int(result[-2].id) + int(result[-1].id)) // 2)
                next_cursor = encode_cursor(target)

            else:
                next_cursor = cursor

        if has_prev:
            if direction == 'prev':
                target = UUID(int=(int(result[-2].id) + int(result[-1].id)) // 2)
                prev_cursor = encode_cursor(target)

            else:
                prev_cursor = cursor

    return QueryResponse(
        data=items,
        meta=QueryMeta(
            count=len(items),
            prev_cursor=prev_cursor,
            next_cursor=next_cursor
        )
    )