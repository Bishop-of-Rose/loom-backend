from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Comment, Post, Profile
from ..schemas import SearchMeta, SearchResponse

async def search_items(
    session: AsyncSession, Base: Profile | Post | Comment, item_ids: list[UUID]
) -> SearchResponse[Profile | Post | Comment]:
    stmt = select(Base).where(Base.id.in_(item_ids))
    items = list((await session.scalars(stmt)).all())

    old_item_ids = set(item_ids)
    new_item_ids = {item.id for item in items}
    diff = list(old_item_ids - new_item_ids)

    return SearchResponse(data=items, meta=SearchMeta(missing=diff))