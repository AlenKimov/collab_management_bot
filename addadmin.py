import asyncio
import argparse

from bot.database import AsyncSessionmaker
from bot.models import Manager


parser = argparse.ArgumentParser(description='Add new administrator')
parser.add_argument('telegram_id', type=int, help='Admin Telegram ID')
args = parser.parse_args()


async def add_manger(manager: Manager):
    async with AsyncSessionmaker() as session:
        session.add(manager)
        await session.commit()


if __name__ == '__main__':
    asyncio.run(add_manger(Manager(telegram_id=args.telegram_id, is_admin=True)))
