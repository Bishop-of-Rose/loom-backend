from typing import List
from uuid import UUID

from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Profile, Post, Comment
from ..schemas import ProfileResponse, PostResponse, CommentResponse, SearchResponse
from ..services import search_items
from ..core.database import get_session

router = APIRouter(
    prefix='/search',
    tags = ['Search']
)

@router.post('/profiles', response_model=SearchResponse[ProfileResponse])
async def search_profiles(profile_ids: List[UUID],
                          session: AsyncSession = Depends(get_session)):
    response = await search_items(session, Profile, profile_ids)
    return response

@router.post('/posts', response_model=SearchResponse[PostResponse])
async def search_posts(post_ids: List[UUID],
                       session: AsyncSession = Depends(get_session)):
    response = await search_items(session, Post, post_ids)
    return response

@router.post('/comments', response_model=SearchResponse[CommentResponse])
async def search_comments(comment_ids: List[UUID],
                          session: AsyncSession = Depends(get_session)):
    response = await search_items(session, Comment, comment_ids)
    return response