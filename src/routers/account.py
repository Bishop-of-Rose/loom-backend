from fastapi import APIRouter, Depends

from ..core.dependencies import get_current_user
from ..models import User
from ..schemas import UserResponse

router = APIRouter(
    prefix='/account',
    tags=['Account'],
)

@router.get('/me', response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user