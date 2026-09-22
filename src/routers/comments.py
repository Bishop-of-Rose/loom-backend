from typing import List, Literal
from uuid import UUID

from fastapi import Depends, HTTPException, status, APIRouter, Query
from psycopg2.errors import ForeignKeyViolation
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models import User, Comment
from ..schemas import CommentCreate, CommentUpdate, CommentResponse, QueryResponse, SearchResponse
from ..core.cursor import decode_cursor, encode_cursor
from ..core.database import get_session
from ..core.dependencies import get_current_user

router = APIRouter(
    prefix='/comments',
    tags=['Comments'],
)

@router.get('', response_model=QueryResponse[CommentResponse])
def query_comments(current_user: User = Depends(get_current_user),
                   session: Session = Depends(get_session),
                   commented: UUID | None = None,
                   limit: int = Query(default=20, ge=1, le=100),
                   cursor: str | None = None,
                   direction: Literal['prev', 'next'] = 'next'):
    stmt = select(Comment)
    if commented is not None:
        stmt = stmt.where(Comment.post_id == commented)

    if cursor is not None:
        try:
            target_id = decode_cursor(cursor)
            if direction == 'next':
                stmt = stmt.where(Comment.id < target_id).order_by(Comment.id.desc())

            elif direction == 'prev':
                stmt = stmt.where(Comment.id > target_id).order_by(Comment.id.asc())

        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Invalid cursor')

    else:
        stmt = stmt.order_by(Comment.id.desc())

    stmt = stmt.limit(limit + 1)
    result = list(session.scalars(stmt).all())

    has_more = len(result) > limit
    has_next = False
    has_prev = False
    comments = result[:limit]

    if direction == 'prev':
        comments.reverse()

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

    if comments:
        if has_next:
            next_cursor = encode_cursor(comments[-1].id)

        if has_prev:
            prev_cursor = encode_cursor(comments[0].id)

    return QueryResponse(
        data=comments,
        next_cursor=next_cursor,
        prev_cursor=prev_cursor
    )

@router.post('', status_code=status.HTTP_201_CREATED, response_model=CommentResponse)
def create_comment(comment: CommentCreate,
                   current_user: User = Depends(get_current_user),
                   session: Session = Depends(get_session)):
    comment = Comment(**comment.model_dump())
    comment.user_id = current_user.id

    try:
        session.add(comment)
        session.commit()
        session.refresh(comment)

    except IntegrityError as e:
        if isinstance(e.orig, ForeignKeyViolation):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Post not found')

    return comment

@router.post('/search', response_model=SearchResponse[CommentResponse])
def search_comments(comment_ids: List[UUID],
                    current_user: User = Depends(get_current_user),
                    session: Session = Depends(get_session)):
    stmt = select(Comment).where(Comment.id.in_(comment_ids))
    comments = list(session.scalars(stmt).all())

    old_comment_ids = set(comment_ids)
    new_comment_ids = {comment.id for comment in comments}
    diff = list(old_comment_ids - new_comment_ids)

    return SearchResponse(
        data=comments,
        missing=diff
    )

@router.put('/{comment_id}', status_code=status.HTTP_202_ACCEPTED, response_model=CommentResponse)
def update_comment(comment_id: UUID,
                   edit: CommentUpdate,
                   current_user: User = Depends(get_current_user),
                   session: Session = Depends(get_session)):
    comment = session.get(Comment, comment_id)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Comment not found')

    if comment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Unauthorised to update comment')

    comment.content = edit.content
    session.commit()
    session.refresh(comment)
    return comment

@router.delete('/{comment_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: UUID,
                   current_user: User = Depends(get_current_user),
                   session: Session = Depends(get_session)):
    comment = session.get(Comment, comment_id)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Comment not found')

    if comment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Unauthorised to delete comment')

    session.delete(comment)
    session.commit()
    return