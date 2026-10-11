from typing import Literal
from uuid import UUID

from fastapi import Depends, APIRouter, Query, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import User, Profile, Post, Comment
from ..schemas import ProfileResponse, PostResponse, CommentResponse, QueryResponse
from ..services import query_items
from ..core.database import get_session
from ..core.dependencies import get_current_user
from ..core.limiter import limiter

router = APIRouter(
    prefix='/query',
    tags = ['Query']
)

@router.get('/profiles', response_model=QueryResponse[ProfileResponse])
@limiter.limit('10/minute')
def query_profiles(request: Request,
                   response: Response,
                   current_user: User = Depends(get_current_user),
                   session: Session = Depends(get_session),
                   cursor: str = None,
                   direction: Literal['prev', 'next'] = 'next',
                   limit: int = Query(default=20, ge=1, le=100)):
    stmt = select(Profile)
    response = query_items(session, Profile, stmt, cursor, direction, limit)
    return response

@router.get('/posts', response_model=QueryResponse[PostResponse])
@limiter.limit('10/minute')
def query_posts(request: Request,
                response: Response,
                current_user: User = Depends(get_current_user),
                session: Session = Depends(get_session),
                author: UUID = None,
                cursor: str = None,
                direction: Literal['prev', 'next'] = 'next',
                limit: int = Query(default=20, ge=1, le=100)):
    stmt = select(Post)
    if author is not None:
        stmt = stmt.where(Post.author_id == author)

    response = query_items(session, Post, stmt, cursor, direction, limit)
    return response

@router.get('/comments', response_model=QueryResponse[CommentResponse])
@limiter.limit('10/minute')
def query_comments(request: Request,
                   response: Response,
                   current_user: User = Depends(get_current_user),
                   session: Session = Depends(get_session),
                   author: UUID = None,
                   commented: UUID = None,
                   replied: UUID = None,
                   cursor: str = None,
                   direction: Literal['prev', 'next'] = 'next',
                   limit: int = Query(default=20, ge=1, le=100)):
    stmt = select(Comment)
    if author is not None:
        stmt = stmt.where(Comment.author_id == author)

    if commented is not None:
        stmt = stmt.where(Comment.commented == commented)

    if replied is not None:
        stmt = stmt.where(Comment.replied == replied)

    response = query_items(session, Comment, stmt, cursor, direction, limit)
    return response