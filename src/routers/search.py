from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_session
from ..models import Comment, Post, Profile
from ..schemas import CommentResponse, PostResponse, ProfileResponse, SearchResponse
from ..services import search_items

router = APIRouter(prefix='/search', tags=['Search'])

@router.post('/profiles', response_model=SearchResponse[ProfileResponse])
async def search_profiles(
    profile_ids: list[UUID], session: AsyncSession = Depends(get_session)
):
    response = await search_items(session, Profile, profile_ids)
    return response

@router.post('/posts', response_model=SearchResponse[PostResponse])
async def search_posts(
    post_ids: list[UUID], session: AsyncSession = Depends(get_session)
):
    response = await search_items(session, Post, post_ids)
    return response

@router.post('/comments', response_model=SearchResponse[CommentResponse])
async def search_comments(
    comment_ids: list[UUID], session: AsyncSession = Depends(get_session)
):
    response = await search_items(session, Comment, comment_ids)
    return response