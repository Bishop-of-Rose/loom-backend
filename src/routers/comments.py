from uuid import UUID

from fastapi import Depends, HTTPException, status, APIRouter
from psycopg2.errors import ForeignKeyViolation
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models import User, Comment
from ..schemas import CommentCreate, CommentUpdate, CommentResponse
from ..core.database import get_session
from ..core.dependencies import get_current_user

router = APIRouter(
    prefix='/comments',
    tags=['Comments'],
)

@router.post('', status_code=status.HTTP_201_CREATED, response_model=CommentResponse)
def create_comment(comment: CommentCreate,
                   current_user: User = Depends(get_current_user),
                   session: Session = Depends(get_session)):
    comment = Comment(**comment.model_dump())
    comment.author_id = current_user.id

    try:
        session.add(comment)
        session.commit()
        session.refresh(comment)

    except IntegrityError as e:
        print(e)
        if isinstance(e.orig, ForeignKeyViolation):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Target not found')

    return comment

@router.put('/{comment_id}', response_model=CommentResponse)
def update_comment(comment_id: UUID,
                   edit: CommentUpdate,
                   current_user: User = Depends(get_current_user),
                   session: Session = Depends(get_session)):
    comment = session.get(Comment, comment_id)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Comment not found')

    if comment.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Unauthorised to update comment')

    comment.content = edit.content
    session.commit()
    session.refresh(comment)
    return comment

@router.delete('/{comment_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: UUID,
                   current_user: User = Depends(get_current_user),
                   session: Session = Depends(get_session)):
    comment = session.get(Comment, comment_id)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Comment not found')

    if comment.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Unauthorised to delete comment')

    session.delete(comment)
    session.commit()
    return