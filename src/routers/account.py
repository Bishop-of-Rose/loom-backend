from asyncpg.exceptions import UniqueViolationError
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_session
from ..core.dependencies import get_current_user
from ..core.limiter import limiter
from ..models import User, Profile
from ..schemas import RegistrationRequestForm, UserResponse
from ..util.password import hash_pw

router = APIRouter(
    prefix='/account',
    tags=['Account'],
)

@router.post('/register', status_code=status.HTTP_201_CREATED, response_model=UserResponse)
@limiter.limit('10/minute')
async def register(request: Request,
                   response: Response,
                   user: RegistrationRequestForm,
                   session: AsyncSession = Depends(get_session)):
    user.password = hash_pw(user.password)
    user = User(**user.model_dump())
    user.profile = Profile(username=user.email.split('@')[0])
    try:
        session.add(user)
        await session.commit()
        await session.refresh(user)

    except IntegrityError as e:
        if isinstance(getattr(e.orig, '__cause__', None), UniqueViolationError):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='User with that email already exists',
            )

    return user

@router.get('/whoami', response_model=UserResponse)
def who_am_i(current_user: User = Depends(get_current_user)):
    return current_user