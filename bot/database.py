from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker

from definitions import DATABASES_DIR

DATABASE_FILENAME = 'db.sqlite'
DATABASE_FILEPATH = DATABASES_DIR / DATABASE_FILENAME

engine = create_async_engine(URL.create('sqlite+aiosqlite', database=str(DATABASE_FILEPATH)), echo=False)
AsyncSessionMaker = async_sessionmaker(bind=engine)
