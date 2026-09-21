from typing import Literal, List
from uuid import UUID

from fastapi import Depends, HTTPException, status, APIRouter, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import User, Post
from ..schemas import PostCreate, PostUpdate, PostResponse, CursorPage
from ..services import get_post_by_id
from ..core.cursor import encode_cursor, decode_cursor
from ..core.database import get_session
from ..core.dependencies import get_current_user

router = APIRouter(
    prefix='/posts',
    tags = ['Posts']
)

@router.get('', response_model=List[PostResponse])
def query_posts(current_user: User = Depends(get_current_user),
                session: Session = Depends(get_session),
                cursor: str | None = None, limit: int = Query(default=20, ge=1, le=100),
                direction: Literal['prev', 'next'] = 'next'):
    stmt = select(Post)
    if cursor is not None:
        try:
            target_id = decode_cursor(cursor)
            if direction == 'next':
                stmt = stmt.where(Post.id < target_id).order_by(Post.id.desc())

            elif direction == 'prev':
                stmt = stmt.where(Post.id > target_id).order_by(Post.id.asc())

        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Invalid cursor')

    else:
        stmt = stmt.order_by(Post.id.desc())

    stmt = stmt.limit(limit + 1)
    result = list(session.scalars(stmt).all())

    has_more = len(result) > limit
    has_next = False
    has_prev = False
    posts = result[:limit]

    if direction == 'prev':
        posts.reverse()

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

    if posts:
        if has_next:
            next_cursor = encode_cursor(posts[-1].id)

        if has_prev:
            prev_cursor = encode_cursor(posts[0].id)

    """return CursorPage(
        data=posts,
        next_cursor=next_cursor,
        prev_cursor=prev_cursor
    )"""

    return posts

@router.post('', status_code=status.HTTP_201_CREATED, response_model=PostResponse)
def create_post(post: PostCreate,
                current_user: User = Depends(get_current_user),
                session: Session = Depends(get_session)):
    post = Post(**post.model_dump())
    post.user_id = current_user.id

    session.add(post)
    session.commit()
    session.refresh(post)
    return post

@router.get('/{post_id}', response_model=PostResponse)
def read_post(post_id: UUID,
              current_user: User = Depends(get_current_user),
              session: Session = Depends(get_session)):
    post = get_post_by_id(post_id, session)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Post not found')

    return post

@router.put('/{post_id}', status_code=status.HTTP_202_ACCEPTED, response_model=PostResponse)
def update_post(post_id: UUID, edit: PostUpdate,
                current_user: User = Depends(get_current_user),
                session: Session = Depends(get_session)):
    post = get_post_by_id(post_id, session)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Post not found')

    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Unauthorised to update this post')

    post.content = edit.content
    session.commit()
    session.refresh(post)
    return post

@router.delete('/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: UUID,
                current_user: User = Depends(get_current_user),
                session: Session = Depends(get_session)):
    post = get_post_by_id(post_id, session)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Post not found')

    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Unauthorised to delete this post')

    session.delete(post)
    session.commit()
    return