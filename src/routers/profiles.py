from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import User, Profile
from ..core.database import get_session
from ..core.dependencies import get_current_user
from ..schemas import ProfileInit, ProfileResponse

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

    unique_name = profile.username.lower()
    stmt = select(Profile.unique_name).where(Profile.unique_name.startswith(unique_name)).order_by(Profile.unique_name.asc())
    result = list(session.scalars(stmt).all())
    if result:
        final = result[-1]
        b = len(final) - 1
        while b > 0:
            if final[b].isdigit():
                b -= 1
                continue
            b += 1
            break

        digit = int(final[b:]) + 1 if final[b:].isdigit() else 1
        unique_name += '_' + str(digit)

    profile = Profile(**profile.model_dump(), id=current_user.id, unique_name=unique_name)
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile