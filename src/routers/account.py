from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import User
from ..schemas import ActivationRequestForm, UserResponse
from ..core.database import get_session
from ..core.dependencies import get_current_user

router = APIRouter(
    prefix='/account',
    tags=['Account'],
)

@router.get('/me', response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user
