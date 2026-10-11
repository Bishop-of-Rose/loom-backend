from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import User

def get_user_by_id(session: Session, user_id: UUID) -> User | None:
    user = session.get(User, user_id)
    return user

def get_user_by_email(session: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    user = session.scalars(stmt).one_or_none()
    return user

def get_user_by_oauth(session: Session, oauth_id: str, provider: str) -> User | None:
    stmt = (select(User)
            .where(User.oauth_id == oauth_id)
            .where(User.provider == provider))
    user = session.scalars(stmt).one_or_none()
    return user