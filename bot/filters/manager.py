import asyncio

from aiogram.filters import BaseFilter
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Manager
from bot.database import AsyncSessionMaker


manager_ids = []


# TODO Да это же какой-то костыль!
async def load_manager_ids():
    global manager_ids
    manager_ids.clear()
    async with AsyncSessionMaker() as session:
        async for manager in await session.stream_scalars(select(Manager)):
            manager_ids.append(manager.telegram_id)


asyncio.run(load_manager_ids())


class ManagerFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in manager_ids
