from typing import Literal
from uuid import UUID

from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import ForeignKeyViolation

from ..models import User, Vote
from ..core.database import get_session
from ..core.dependencies import get_current_user

router = APIRouter(
    prefix='/vote',
    tags=['Vote'],
)

@router.post('')
def toggle_vote(vote_type: Literal['LIKE', 'DISLIKE'] | None = None,
                post_id: UUID | None = None,
                comment_id: UUID | None = None,
                current_user: User = Depends(get_current_user),
                session: Session = Depends(get_session)):
    if post_id is None == comment_id is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                            detail='Votes should either refer to a post or a comment')

    stmt = select(Vote).where(Vote.author_id == current_user.id, Vote.post_id == post_id, Vote.comment_id == comment_id)
    vote = session.scalars(stmt).one_or_none()
    if vote is None:
        if vote_type is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                                detail='Vote type not specified for vote creation')

        vote = Vote(author_id=current_user.id, post_id=post_id, comment_id=comment_id, type=vote_type)
        session.add(vote)
        message = f'{vote.type} successfully created'

    else:
        if vote_type is not None:
            vote.type, vote_type = vote_type, vote.type
            message = f'{vote_type} successfully updated to {vote.type}'

        else:
            session.delete(vote)
            message = f'{vote.type} successfully deleted'

    try:
        session.commit()

    except IntegrityError as e:
        if isinstance(e.orig, ForeignKeyViolation):
            ref = 'post' if post_id is not None else 'comment'
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f'Vote reference {ref} not found')

    return {'message': message}