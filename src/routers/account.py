from fastapi import APIRouter, Depends

from ..models import User
from ..schemas import UserResponse
from ..core.dependencies import get_current_user

router = APIRouter(
    prefix='/account',
    tags=['Account'],
)

@router.get('/me', response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user
