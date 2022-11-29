from db_plugins.db.mongo import models
from returns.result import Success

from shared.utils.repositories import MongoRepository
from ..domain import LimitsAstroObjectPayload


class LimitsAstroObjectRepository(MongoRepository):
    def _query(self, payload: LimitsAstroObjectPayload):
        query = self.db.query()
        query.init_collection(models.Object)
        return query.collection.find()

    def _wrap_results(self, result):
        result = {
            "min_ndet": result.sort([("ndet", 1)]).limit(1)[0]["ndet"],
            "max_ndet": result.sort([("ndet", -1)]).limit(1)[0]["ndet"],
            "min_firstmjd": result.sort([("firstmjd", 1)]).limit(1)[0][
                "firstmjd"
            ],
            "max_firstmjd": result.sort([("firstmjd", -1)]).limit(1)[0][
                "firstmjd"
            ],
        }
        return Success(result)
