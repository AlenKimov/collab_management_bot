from pydantic import BaseSettings

from bot.definitions import DOT_ENV_FILEPATH


class Settings(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str = 'postgresql+psycopg://postgres:admin@localhost/collab_management'

    class Config:
        env_file = DOT_ENV_FILEPATH
        env_file_encoding = 'utf-8'


config = Settings()
