import abc
from db_plugins.db.mongo.connection import MongoConnection
from returns.pipeline import is_successful
from returns.result import Success, Failure
from ..error.exceptions import ServerErrorException


class MongoRepository(abc.ABC):
    def __init__(self, db: MongoConnection):
        self.db = db

    def get(self, filter_args, order_args=None, paginate_args=None):
        try:
            query = self._filter(filter_args)
            if is_successful(query):
                query = query.unwrap()
            else:
                return query

            if order_args:
                query = self._order(query, order_args)
            if paginate_args:
                query = self._paginate(query, paginate_args)
            return Success(query)
        except Exception as e:
            return Failure(ServerErrorException(e))

    @abc.abstractmethod
    def _filter(self, filter_args):
        pass

    @staticmethod
    def _paginate(query, paginate_args):
        n, page = paginate_args.get('page_size'), paginate_args.get('page')
        return query.skip((page - 1) * n).limit(n)

    @staticmethod
    def _order(query, order_args):
        by, mode = order_args.get('order_by'), order_args.get('order_mode')
        return query.order([by, -1 if mode == 'DESC' else 1])
