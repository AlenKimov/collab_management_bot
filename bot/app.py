import asyncio

from aiogram import Bot, Dispatcher

from bot.logger import logger
from bot.handlers import admin, manager, user
from bot.config import config
from bot.ui_commands import set_ui_commands
from bot.middlewares import DbSessionMiddleware
from bot.database import AsyncSessionMaker


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
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info('Bot stopped!')
