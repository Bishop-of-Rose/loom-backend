from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import User, Profile
from ..core.database import get_session
from ..core.dependencies import get_current_user
from ..schemas import ProfileInit, ProfileResponse

router = APIRouter(
    prefix='/profiles',
    tags=['Profiles']
)

@router.post('', response_model=ProfileResponse)
async def initialize_profile(profile: ProfileInit,
                             current_user: User = Depends(get_current_user),
                             session: AsyncSession = Depends(get_session)):
    if current_user.profile is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='Profile already initialized')

    current_user.profile = Profile(**profile.model_dump())
    await session.commit()
    await session.refresh(current_user)
    return current_user.profile