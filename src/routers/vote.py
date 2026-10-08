from typing import Literal

from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import ForeignKeyViolation

from ..models import User, Vote
from ..schemas import VoteBase
from ..core.database import get_session
from ..core.dependencies import get_current_user

router = APIRouter(
    prefix='/vote',
    tags=['Vote'],
)

@router.post('')
def toggle_vote(target: VoteBase,
                choice: Literal['LIKE', 'DISLIKE'],
                current_user: User = Depends(get_current_user),
                session: Session = Depends(get_session)):
    stmt = select(Vote).where(Vote.author_id == current_user.id, Vote.post_id == target.post_id, Vote.comment_id == target.comment_id)
    vote = session.scalars(stmt).one_or_none()
    if vote is None:
        vote = Vote(**target.model_dump(), author_id=current_user.id, type=choice)
        session.add(vote)
        message = f'{vote.type} successfully created'

    else:
        if choice != vote.type:
            vote.type, choice = choice, vote.type
            message = f'{choice} successfully updated to {vote.type}'

        else:
            session.delete(vote)
            message = f'{vote.type} successfully deleted'

    try:
        session.commit()

    except IntegrityError as e:
        if isinstance(e.orig, ForeignKeyViolation):
            ref = 'post' if target.post_id is not None else 'comment'
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f'Vote reference {ref} not found')

    return {'message': message}