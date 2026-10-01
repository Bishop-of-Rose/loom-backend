from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from ..models import Post

def get_posts_by_id(session: Session, post_ids: List[UUID]) -> List[Post]:
    posts = session.get(Post, post_ids)
    return posts