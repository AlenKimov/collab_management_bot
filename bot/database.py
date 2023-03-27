from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker

from bot.config import config


# Во избежание этой ошибки:
# sqlalchemy.exc.InterfaceError: (psycopg.InterfaceError)
# Psycopg cannot use the 'ProactorEventLoop' to run in async mode.
# Please use a compatible event loop, for instance by setting
# 'asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())'
# (Background on this error at: https://sqlalche.me/e/20/rvf5)
import sys
import asyncio
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


engine = create_async_engine(config.DATABASE_URL, echo=False)
AsyncSessionmaker = async_sessionmaker(bind=engine, expire_on_commit=False)
