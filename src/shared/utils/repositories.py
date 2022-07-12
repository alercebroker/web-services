import abc
from db_plugins.db.mongo.connection import MongoConnection

from .queries import PayloadFactory


class MongoRepository(abc.ABC):
    def __init__(self, db: MongoConnection):
        self.db = db

    @abc.abstractmethod
    def get(self, payload: PayloadFactory):
        pass
