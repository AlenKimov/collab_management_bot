from aiogram.types import Message

from logger import logger
from loader import dp, bot


@dp.message_handler(commands="start")
async def start_message(message: Message):
    """welcome message."""
    await bot.send_message(message.chat.id, "ℹ [About]\n Ну привет")