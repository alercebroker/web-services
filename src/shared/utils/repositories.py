import abc
from db_plugins.db.mongo.connection import MongoConnection
from returns.result import Failure

from .queries import Payload
from ..error.exceptions import ServerErrorException


class MongoRepository(abc.ABC):
    def __init__(self, db: MongoConnection):
        self.db = db

    def get(self, payload: Payload):
        try:
            result = self._query(payload)
        except Exception as e:
            return Failure(ServerErrorException(e))

        return self._wrap_results(result)

    @abc.abstractmethod
    def _query(self, payload: Payload):
        pass

    @abc.abstractmethod
    def _wrap_results(self, result):
        pass
