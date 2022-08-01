from returns.result import Success, Failure
from db_plugins.db.mongo import models

from shared.error.exceptions import ClientErrorException, EmptyQuery
from shared.utils.repositories import MongoRepository
from .domain import AstroObjectPayload


class ListAstroObjectRepository(MongoRepository):
    def _query(self, payload: AstroObjectPayload):
        return self.db.query().find_all(
            model=models.Object,
            filter_by=payload.filter,
            paginate=True,
            sort=payload.sort,
            **payload.paginate
        )

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


class SingleAstroObjectRepository(MongoRepository):
    def _query(self, payload: AstroObjectPayload):
        return self.db.query().find_one(
            model=models.Object, filter_by=payload.filter
        )

    def _wrap_results(self, result):
        if result:
            return Success(result)
        else:
            return Failure(ClientErrorException(EmptyQuery()))


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
