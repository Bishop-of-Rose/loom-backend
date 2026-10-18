from uuid import UUID

from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from asyncpg.exceptions import ForeignKeyViolationError

from ..models import User, Comment
from ..schemas import CommentCreate, CommentUpdate, CommentResponse
from ..core.database import get_session
from ..core.dependencies import get_current_user

router = APIRouter(
    prefix='/comments',
    tags=['Comments'],
)

@router.post('', status_code=status.HTTP_201_CREATED, response_model=CommentResponse)
async def create_comment(comment: CommentCreate,
                         current_user: User = Depends(get_current_user),
                         session: AsyncSession = Depends(get_session)):
    comment = Comment(**comment.model_dump())
    comment.author_id = current_user.id

    try:
        session.add(comment)
        await session.commit()
        await session.refresh(comment)

    except IntegrityError as e:
        if isinstance(getattr(e.orig, '__cause__', None), ForeignKeyViolationError):
            ref = 'post' if comment.commented is not None else 'comment'
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f'Comment reference {ref} not found')

    return comment

@router.put('/{comment_id}', response_model=CommentResponse)
async def update_comment(comment_id: UUID,
                         edit: CommentUpdate,
                         current_user: User = Depends(get_current_user),
                         session: AsyncSession = Depends(get_session)):
    comment = await session.get(Comment, comment_id)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Comment not found')

    if comment.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Unauthorised to update comment')

    comment.content = edit.content
    await session.commit()
    await session.refresh(comment)
    return comment

@router.delete('/{comment_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(comment_id: UUID,
                         current_user: User = Depends(get_current_user),
                         session: AsyncSession = Depends(get_session)):
    comment = await session.get(Comment, comment_id)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Comment not found')

    if comment.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Unauthorised to delete comment')

    await session.delete(comment)
    await session.commit()
    return