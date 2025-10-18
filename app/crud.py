from models import ORM_CLS, ORM_OBJ
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException




async  def get_item_by_id(session: AsyncSession, orm_cls: ORM_CLS, item_id: int) -> ORM_OBJ:
    orm_obj = await session.get(orm_cls, item_id)
    if orm_obj is None:
        raise HTTPException(status_code=404, detail=f"Item not found")
    return orm_obj


async def add_item(session: AsyncSession, item: ORM_OBJ):
    session.add(item)
    try:
        await session.commit()
    except IntegrityError as err:
        raise HTTPException(status_code=409, detail='Item already exists')

async def delete_item(session: AsyncSession, item: ORM_OBJ):
    await session.delete(item)
    await session.commit()