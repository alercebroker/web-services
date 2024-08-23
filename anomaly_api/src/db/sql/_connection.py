from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Base
from contextlib import contextmanager
from typing import Callable, ContextManager
import logging


def get_db_url(config: dict):
    return f"postgresql://{config['USER']}:{config['PASSWORD']}@{config['HOST']}:{config['PORT']}/{config['DB_NAME']}"


def wrapper_url_maker(credentials: dict):
    return get_db_url(credentials)

class MockerDatabase:
    def __init__(self, engine=None, credentials=None, **kwargs) -> None:
        """provide an engine or create a new one whit credentials"""
        self._engine = (
            engine
            if engine is not None
            else create_engine(wrapper_url_maker(credentials))
        )
        self._session_factory = sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine
        )

    def create_db(self):
        Base.metadata.create_all(self._engine)

    def drop_db(self):
        Base.metadata.drop_all(self._engine)

    @contextmanager
    def session(self):
        session: Session = self._session_factory()
        try:
            """ session """
            yield session
        except Exception as e:
            """ exception """
            print(e)
        finally:
            """ finally close session created """
            session.close()
