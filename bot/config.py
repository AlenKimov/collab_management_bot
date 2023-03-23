from pydantic import BaseSettings, SecretStr

from definitions import DOT_ENV_FILEPATH


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr

    class Config:
        env_file = DOT_ENV_FILEPATH
        env_file_encoding = 'utf-8'


config = Settings()
