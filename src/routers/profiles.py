from typing import List, Literal
from uuid import UUID

from fastapi import Depends, APIRouter, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import User, Profile
from ..services import query_items, search_items
from ..core.database import get_session
from ..core.dependencies import get_current_user
from ..schemas import ProfileInit, ProfileResponse, QueryResponse, SearchResponse

router = APIRouter(
    prefix='/profiles',
    tags=['Profiles']
)

@router.get('', response_model=QueryResponse[ProfileResponse])
def query_profiles(current_user: User = Depends(get_current_user),
                   session: Session = Depends(get_session),
                   limit: int = Query(default=20, ge=1, le=100),
                   cursor: str | None = None,
                   direction: Literal['prev', 'next'] = 'next'):
    stmt = select(Profile)
    response = query_items(session, Profile, stmt, limit, cursor, direction)
    return response

@router.post('/search', response_model=SearchResponse[ProfileResponse])
def search_profiles(profile_ids: List[UUID],
                    current_user: User = Depends(get_current_user),
                    session: Session = Depends(get_session)):
    response = search_items(session, Profile, profile_ids)
    return response