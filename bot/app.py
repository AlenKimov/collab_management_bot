import asyncio

from aiogram import Bot, Dispatcher

from handlers import admin, manager, user
from config import config
from ui_commands import set_ui_commands
from middlewares import DbSessionMiddleware
from database import AsyncSessionMaker


async def main():
    bot = Bot(token=config.BOT_TOKEN.get_secret_value(), parse_mode='HTML')

    dp = Dispatcher()
    dp.update.middleware(DbSessionMiddleware(session_pool=AsyncSessionMaker))
    dp.include_router(admin.router)
    dp.include_router(manager.router)
    dp.include_router(user.router)

    await set_ui_commands(bot)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
