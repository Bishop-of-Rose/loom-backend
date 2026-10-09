from typing import Tuple

from fastapi import HTTPException, status
from sqlalchemy import Select
from sqlalchemy.orm import Session

from ..models import Profile, Post, Comment
from ..schemas import QueryResponse
from ..core.cursor import decode_cursor, encode_cursor

def query_items(session: Session, Base: Profile | Post | Comment,
                stmt: Select[Tuple[Profile | Post | Comment]],
                cursor: str | None, limit: int) -> QueryResponse:
    if cursor is not None:
        try:
            target_id = decode_cursor(cursor)
            stmt = stmt.where(Base.id < target_id).order_by(Base.id.desc())

        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Invalid cursor')

    else:
        stmt = stmt.order_by(Base.id.desc())

    stmt = stmt.limit(limit + 1)
    result = list(session.scalars(stmt).all())
    items = result[:limit]

    has_more = len(result) > limit
    cursor = None

    if items and has_more:
        cursor = encode_cursor(items[-1].id)

    return QueryResponse(
        data=items,
        cursor=cursor
    )