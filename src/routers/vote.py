from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation, ForeignKeyViolation

from ..models import User, Vote
from ..schemas import VoteCreate, VoteUpdate, VoteBase
from ..core.database import get_session
from ..core.dependencies import get_current_user

router = APIRouter(
    prefix='/vote',
    tags=['Vote'],
)

@router.post('', status_code=status.HTTP_201_CREATED)
def create_vote(vote: VoteCreate,
                current_user: User = Depends(get_current_user),
                session: Session = Depends(get_session)):
    vote = Vote(**vote.model_dump())
    vote.user_id = current_user.id
    ref_type = "post" if vote.comment_id is None else "comment"

    try:
        session.add(vote)
        session.commit()
        session.refresh(vote)

    except IntegrityError as e:
        if isinstance(e.orig, UniqueViolation):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'User already has a vote on this {ref_type}')

        elif isinstance(e.orig, ForeignKeyViolation):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'Vote reference {ref_type} not found')

    return

@router.put('', status_code=status.HTTP_202_ACCEPTED)
def update_vote(vote: VoteUpdate,
                current_user: User = Depends(get_current_user),
                session: Session = Depends(get_session)):
    ref_type = "post" if vote.comment_id is None else "comment"
    stmt = (select(Vote)
            .where(Vote.user_id == current_user.id)
            .where(Vote.post_id == vote.post_id)
            .where(Vote.comment_id == vote.comment_id)
            )

    result = session.scalars(stmt).one_or_none()
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'User has no vote on this {ref_type}')

    result.type = vote.type
    session.commit()
    return

@router.delete('', status_code=status.HTTP_202_ACCEPTED)
def delete_vote(vote: VoteBase,
                current_user: User = Depends(get_current_user),
                session: Session = Depends(get_session)):
    ref_type = "post" if vote.comment_id is None else "comment"
    stmt = (select(Vote)
            .where(Vote.user_id == current_user.id)
            .where(Vote.post_id == vote.post_id)
            .where(Vote.comment_id == vote.comment_id)
            )

    vote = session.scalars(stmt).one_or_none()
    if vote is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'User has no vote on this {ref_type}')

    session.delete(vote)
    session.commit()
    return