import abc
from db_plugins.db.mongo.connection import MongoConnection
from returns.result import Failure

from .queries import MongoPayload
from ..error.exceptions import ServerErrorException


class MongoRepository(abc.ABC):
    """Base class for mongo repositories.

    Subclasses must define the methods `_query` and `_wrap_results`. The
    first contains the query for the database, while the second generates
    the desired results based on the query and wraps them in either `Success`
    or `Failure`.

    The `get` method already handles server errors, while `_wrap_results`
    should handle client errors if needed.

    Attributes
    ----------
    db : MongoConnection
        Connection to mongo database
    """

    def __init__(self, db: MongoConnection):
        """
        Parameters
        ----------
        db : MongoConnection
            Connection to mongo database
        """
        self.db = db

    def get(self, payload: MongoPayload):
        """Makes a request to the repository.

        Parameters
        ----------
        payload : MongoPayload
            Payload used to query the database

        Returns
        -------
        Success or Failure:
            Output or error from database query
        """
        try:
            result = self._query(payload)
        except Exception as e:
            return Failure(ServerErrorException(e))
        return self._wrap_results(result)

    @abc.abstractmethod
    def _query(self, payload: MongoPayload):
        pass

    @abc.abstractmethod
    def _wrap_results(self, result):
        pass

    def _find_all(self, model, payload: MongoPayload):
        paginate = True if payload.paginate else False
        return self.db.query().find_all(
            model=model,
            filter_by=payload.filter,
            paginate=paginate,
            sort=payload.sort,
            **payload.paginate
        )

    def _find_one(self, model, payload: MongoPayload):
        return self.db.query().find_one(model=model, filter_by=payload.filter)
