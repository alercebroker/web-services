from db_plugins.db.mongo import models
from returns.result import Success, Failure

from shared.utils.repositories import MongoRepository
from shared.error.exceptions import ClientErrorException, EmptyQuery

from ..domain import ClassifiersPayload


class ClassesRepository(MongoRepository):
    def _query(self, payload: ClassifiersPayload):
        return self._find_one(models.Taxonomy, payload)

    def _wrap_results(self, result):
        if result:
            return Success([{"name": cls} for cls in result["classes"]])
        return Failure(ClientErrorException(EmptyQuery()))
