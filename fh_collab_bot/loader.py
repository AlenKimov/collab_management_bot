import os

from aiogram import Bot
from aiogram import Dispatcher
from dotenv import load_dotenv

from definitions import DOT_ENV_FILEPATH


load_dotenv(DOT_ENV_FILEPATH)


TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = Bot(token=TELEGRAM_BOT_TOKEN, parse_mode='html')
dp = Dispatcher(bot)
