from aiogram import Bot
from aiogram.types import BotCommandScopeAllPrivateChats, BotCommand


async def set_ui_commands(bot: Bot):
    """
    Sets bot commands in UI
    :param bot: Bot instance
    """
    commands = [
        BotCommand(command="my", description="Мои проекты"),
        BotCommand(command="best", description="Лучшие проекты"),
        BotCommand(command="new", description="Новые проекты"),
        BotCommand(command="set_username", description="Установить username"),
        BotCommand(command="help", description="Помощь"),
    ]
    await bot.set_my_commands(
        commands=commands,
        scope=BotCommandScopeAllPrivateChats()
    )
