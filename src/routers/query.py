from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_session
from ..models import Comment, Post, Profile
from ..schemas import CommentResponse, PostResponse, ProfileResponse, QueryResponse
from ..services import query_items

router = APIRouter(prefix='/query', tags=['Query'])

@router.get('/profiles', response_model=QueryResponse[ProfileResponse])
async def query_profiles(
    session: AsyncSession = Depends(get_session),
    cursor: str = None,
    direction: Literal['prev', 'next'] = 'next',
    limit: int = Query(default=20, ge=1, le=100),
):
    stmt = select(Profile)
    response = await query_items(session, Profile, stmt, cursor, direction, limit)
    return response

@router.get('/posts', response_model=QueryResponse[PostResponse])
async def query_posts(
    session: AsyncSession = Depends(get_session),
    author: UUID = None,
    cursor: str = None,
    direction: Literal['prev', 'next'] = 'next',
    limit: int = Query(default=20, ge=1, le=100),
):
    stmt = select(Post)
    if author is not None:
        stmt = stmt.where(Post.author_id == author)

    response = await query_items(session, Post, stmt, cursor, direction, limit)
    return response

@router.get('/comments', response_model=QueryResponse[CommentResponse])
async def query_comments(
    session: AsyncSession = Depends(get_session),
    author: UUID = None,
    commented: UUID = None,
    replied: UUID = None,
    cursor: str = None,
    direction: Literal['prev', 'next'] = 'next',
    limit: int = Query(default=20, ge=1, le=100),
):
    stmt = select(Comment)
    if author is not None:
        stmt = stmt.where(Comment.author_id == author)

    if commented is not None:
        stmt = stmt.where(Comment.commented == commented)

    if replied is not None:
        stmt = stmt.where(Comment.replied == replied)

    response = await query_items(session, Comment, stmt, cursor, direction, limit)
    return response