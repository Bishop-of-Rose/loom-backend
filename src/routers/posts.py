from typing import Literal, List
from uuid import UUID

from fastapi import Depends, HTTPException, status, APIRouter, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import User, Post
from ..schemas import PostCreate, PostUpdate, PostResponse, QueryResponse, SearchResponse
from ..services import query_items, search_items
from ..core.database import get_session
from ..core.dependencies import get_current_user

router = APIRouter(
    prefix='/posts',
    tags = ['Posts']
)

@router.get('', response_model=QueryResponse[PostResponse])
def query_posts(current_user: User = Depends(get_current_user),
                session: Session = Depends(get_session),
                author: UUID | None = None,
                limit: int = Query(default=20, ge=1, le=100),
                cursor: str | None = None,
                direction: Literal['prev', 'next'] = 'next'):
    stmt = select(Post)
    if author is not None:
        stmt = stmt.where(Post.author_id == author)

    response = query_items(session, Post, stmt, limit, cursor, direction)
    return response

@router.post('', status_code=status.HTTP_201_CREATED, response_model=PostResponse)
def create_post(post: PostCreate,
                current_user: User = Depends(get_current_user),
                session: Session = Depends(get_session)):
    post = Post(**post.model_dump())
    post.author_id = current_user.id

    session.add(post)
    session.commit()
    session.refresh(post)
    return post

@router.post('/search', response_model=SearchResponse[PostResponse])
def search_posts(post_ids: List[UUID],
                 current_user: User = Depends(get_current_user),
                 session: Session = Depends(get_session)):
    response = search_items(session, Post, post_ids)
    return response

@router.put('/{post_id}', response_model=PostResponse)
def update_post(post_id: UUID, edit: PostUpdate,
                current_user: User = Depends(get_current_user),
                session: Session = Depends(get_session)):
    post = session.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Post not found')

    if post.author_id != current_user.id:
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
    post = session.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Post not found')

    if post.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Unauthorised to delete this post')

    session.delete(post)
    session.commit()
    return