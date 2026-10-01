from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Profile, Post, Comment
from ..schemas import SearchResponse

def search_items(session: Session, Base: Profile | Post | Comment,
                 item_ids: List[UUID]) -> SearchResponse:
    stmt = select(Base).where(Base.id.in_(item_ids))
    items = list(session.scalars(stmt).all())

    old_item_ids = set(item_ids)
    new_item_ids = {item.id for item in items}
    diff = list(old_item_ids - new_item_ids)

    return SearchResponse(
        data=items,
        missing=diff
    )
