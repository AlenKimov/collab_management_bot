from sqlalchemy import URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from definitions import DATABASES_DIR

DATABASE_FILENAME = 'db.sqlite'
DATABASE_FILEPATH = DATABASES_DIR / DATABASE_FILENAME

engine = create_engine(URL.create('sqlite', database=str(DATABASE_FILEPATH)), echo=True)
DatabaseSession = sessionmaker(bind=engine)
