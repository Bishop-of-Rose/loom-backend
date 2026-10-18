from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import User

async def get_user_by_id(session: AsyncSession, user_id: UUID) -> User | None:
    user = await session.get(User, user_id)
    return user

async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    user = (await session.scalars(stmt)).one_or_none()
    return user

async def get_user_by_oauth(session: AsyncSession, oauth_id: str, provider: str) -> User | None:
    stmt = (select(User)
            .where(User.oauth_id == oauth_id)
            .where(User.provider == provider))
    user = (await session.scalars(stmt)).one_or_none()
    return user