import asyncio

from aiogram.filters import BaseFilter
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fh_collab_bot.models import Manager
from fh_collab_bot.database import AsyncSessionMaker


admin_ids = []


# TODO Да это же какой-то костыль!
async def load_admin_ids():
    global admin_ids
    admin_ids.clear()
    async with AsyncSessionMaker() as session:
        async for admin in await session.stream_scalars(select(Manager).filter_by(is_admin=True)):
            admin_ids.append(admin.telegram_id)


asyncio.run(load_admin_ids())


class AdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in admin_ids
