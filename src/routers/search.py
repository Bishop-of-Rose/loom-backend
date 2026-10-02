from typing import List
from uuid import UUID

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from ..models import User, Profile, Post, Comment
from ..schemas import ProfileResponse, PostResponse, CommentResponse, SearchResponse
from ..services import search_items
from ..core.database import get_session
from ..core.dependencies import get_current_user

router = APIRouter(
    prefix='/search',
    tags = ['Search']
)

@router.post('/profiles', response_model=SearchResponse[ProfileResponse])
def search_profiles(profile_ids: List[UUID],
                    current_user: User = Depends(get_current_user),
                    session: Session = Depends(get_session)):
    response = search_items(session, Profile, profile_ids)
    return response

@router.post('/posts', response_model=SearchResponse[PostResponse])
def search_posts(post_ids: List[UUID],
                 current_user: User = Depends(get_current_user),
                 session: Session = Depends(get_session)):
    response = search_items(session, Post, post_ids)
    return response

@router.post('/comments', response_model=SearchResponse[CommentResponse])
def search_comments(comment_ids: List[UUID],
                    current_user: User = Depends(get_current_user),
                    session: Session = Depends(get_session)):
    response = search_items(session, Comment, comment_ids)
    return response