from db_plugins.db.mongo import models
from returns.result import Success

from shared.utils.repositories import MongoRepository
from ..domain import ClassifiersPayload


class ClassifiersRepository(MongoRepository):
    def _query(self, payload: ClassifiersPayload):
        return self._find_all(models.Taxonomy, payload)

    def _wrap_results(self, result):
        return Success(list(result))
