from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import User

def get_user_by_id(session: Session, user_id: UUID):
    user = session.get(User, user_id)
    return user

def get_user_by_email(session: Session, email: str):
    stmt = select(User).where(User.email == email)
    user = session.scalars(stmt).one_or_none()
    return user

def get_user_by_oauth_id(session: Session, oauth_id: str):
    stmt = select(User).where(User.oauth_id == oauth_id)
    user = session.scalars(stmt).one_or_none()
    return user