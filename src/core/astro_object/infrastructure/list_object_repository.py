from db_plugins.db.mongo import models
from returns.result import Success

from shared.utils.repositories import MongoRepository
from ..domain import AstroObjectPayload


class ListAstroObjectRepository(MongoRepository):
    def _query(self, payload: AstroObjectPayload):
        return self._find_all(models.Object, payload)

    def _wrap_results(self, result):
        # There is no failure if query is empty in this case
        result = {
            "total": result.total,
            "page": result.page,
            "next": result.next_num,
            "has_next": result.has_next,
            "prev": result.prev_num,
            "has_prev": result.has_prev,
            "items": result.items,
        }
        return Success(result)
