from sqlalchemy import Engine

from core.infrastructure.orm import Base

def create_database(engine: Engine):
    Base.metadata.create_all(engine)

def delete_database(engine: Engine):
    Base.metadata.drop_all(engine)