from db_plugins.db.mongo import models
from returns.result import Success

from shared.utils.repositories import MongoRepository
from ..domain import LimitsAstroObjectPayload


class LimitsAstroObjectRepository(MongoRepository):
    def _query(self, payload: LimitsAstroObjectPayload):
        pipe = [
            {
                "$group": {
                    "_id": None,
                    "min_ndet": {"$min": "$ndet"},
                    "max_ndet": {"$max": "$ndet"},
                    "min_firstmjd": {"$min": "$firstmjd"},
                    "max_firstmjd": {"$max": "$firstmjd"},
                }
            }
        ]
        return self.db.query().find_all(
            model=models.Object, filter_by=pipe, paginate=False
        )

    def _wrap_results(self, result):
        result = result.next()
        result.pop("_id")
        return Success(result)
