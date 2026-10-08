from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import User, Profile
from ..core.database import get_session
from ..core.dependencies import get_current_user
from ..schemas import ProfileInit, ProfileChange, ProfileResponse

router = APIRouter(
    prefix='/profiles',
    tags=['Profiles']
)

@router.post('', response_model=ProfileResponse)
def initialize_profile(profile: ProfileInit,
                       current_user: User = Depends(get_current_user),
                       session: Session = Depends(get_session)):
    if current_user.profile is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='Profile already initialized')

    current_user.profile = Profile(**profile.model_dump())
    session.commit()
    session.refresh(current_user)
    return current_user.profile