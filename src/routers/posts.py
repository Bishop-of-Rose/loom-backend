from uuid import UUID

from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import User, Post
from ..schemas import PostCreate, PostUpdate, PostResponse
from ..core.database import get_session
from ..core.dependencies import get_current_user

router = APIRouter(
    prefix='/posts',
    tags = ['Posts']
)

@router.post('', status_code=status.HTTP_201_CREATED, response_model=PostResponse)
async def create_post(post: PostCreate,
                      current_user: User = Depends(get_current_user),
                      session: AsyncSession = Depends(get_session)):
    post = Post(**post.model_dump())
    post.author_id = current_user.id

    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post

@router.put('/{post_id}', response_model=PostResponse)
async def update_post(post_id: UUID, edit: PostUpdate,
                      current_user: User = Depends(get_current_user),
                      session: AsyncSession = Depends(get_session)):
    post = await session.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Post not found')

    if post.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Unauthorised to update this post')

    post.content = edit.content
    await session.commit()
    await session.refresh(post)
    return post

@router.delete('/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: UUID,
                current_user: User = Depends(get_current_user),
                session: AsyncSession = Depends(get_session)):
    post = await session.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Post not found')

    if post.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Unauthorised to delete this post')

    await session.delete(post)
    await session.commit()
    return