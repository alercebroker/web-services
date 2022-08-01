from db_plugins.db.mongo import models
from returns.result import Success

from shared.utils.repositories import MongoRepository
from ..domain import AstroObjectPayload


class LimitsRepository(MongoRepository):
    def _query(self, payload: AstroObjectPayload):
        return self.db.query().find_all(model=models.Object, paginate=False)

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
