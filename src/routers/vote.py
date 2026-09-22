from typing import Literal
from uuid import UUID

from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation, ForeignKeyViolation

from ..models import User, Vote
from ..core.database import get_session
from ..core.dependencies import get_current_user

router = APIRouter(
    prefix='/vote',
    tags=['Vote'],
)

@router.post('', status_code=status.HTTP_202_ACCEPTED)
def create_vote(vote_type: Literal['LIKE', 'DISLIKE'],
                post_id: UUID | None = None, comment_id: UUID | None = None,
                current_user: User = Depends(get_current_user),
                session: Session = Depends(get_session)):
    if post_id is None == comment_id is None:
        if comment_id is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                                detail='Vote attempted to refer using neither post_id and comment_id')
        else:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                                detail='Vote attempted to refer using both post_id and comment_id')

    vote = Vote(user_id=current_user.id, post_id=post_id, comment_id=comment_id, type=vote_type)
    ref_type = "post" if comment_id is None else "comment"

    try:
        session.add(vote)
        session.commit()

    except IntegrityError as e:
        print(e)
        if isinstance(e.orig, UniqueViolation):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'User already has a vote on this {ref_type}')

        elif isinstance(e.orig, ForeignKeyViolation):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'Vote reference {ref_type} not found')

    return {'message': f'{vote_type} created successfully'}

@router.put('', status_code=status.HTTP_202_ACCEPTED)
def update_vote(vote_type: Literal['LIKE', 'DISLIKE'],
                post_id: UUID | None = None, comment_id: UUID | None = None,
                current_user: User = Depends(get_current_user),
                session: Session = Depends(get_session)):
    if post_id is None == comment_id is None:
        if comment_id is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                                detail='Vote attempted to refer using neither post_id and comment_id')
        else:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                                detail='Vote attempted to refer using both post_id and comment_id')

    ref_type = "post" if comment_id is None else "comment"
    stmt = (select(Vote)
            .where(Vote.user_id == current_user.id)
            .where(Vote.post_id == post_id)
            .where(Vote.comment_id == comment_id)
            )

    vote = session.scalars(stmt).one_or_none()
    if vote is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'User has no vote on this {ref_type}')


    vote.type, vote_type = vote_type, vote.type
    session.commit()
    return {'message': f'{vote_type} updated to {vote.type} successfully'}

@router.delete('', status_code=status.HTTP_202_ACCEPTED)
def delete_vote(post_id: UUID | None = None, comment_id: UUID | None = None,
                current_user: User = Depends(get_current_user),
                session: Session = Depends(get_session)):
    if post_id is None == comment_id is None:
        if comment_id is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                                detail='Vote attempted to refer using neither post_id and comment_id')
        else:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                                detail='Vote attempted to refer using both post_id and comment_id')

    ref_type = "post" if comment_id is None else "comment"
    stmt = (select(Vote)
            .where(Vote.user_id == current_user.id)
            .where(Vote.post_id == post_id)
            .where(Vote.comment_id == comment_id)
            )

    vote = session.scalars(stmt).one_or_none()
    if vote is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'User has no vote on this {ref_type}')

    session.delete(vote)
    session.commit()
    return {'message': f'{vote.type} deleted successfully'}