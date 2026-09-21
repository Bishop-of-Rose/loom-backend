from uuid import UUID

from sqlalchemy.orm import Session

from ..models import Post

def get_post_by_id(post_id: UUID, session: Session):
    post = session.get(Post, post_id)
    return post