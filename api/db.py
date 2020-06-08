#from db_plugins.db.sql import get_scoped_session, start_db
from . import app
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
# session = get_scoped_session(app.config["DATABASE"]["SQL"])

engine = create_engine(app.config["DATABASE"]["SQL"], convert_unicode=True)
session = scoped_session(sessionmaker(autocommit=False,autoflush=False,bind=engine))
# Base = declarative_base()
# Base.query = session.query_property()

def init_db():
    from db_plugins.db.sql.models import Base, Class
    Base.metadata.create_all(bind=engine)
    # start_db(app.config["DATABASE"]["SQL"])
