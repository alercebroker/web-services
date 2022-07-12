from returns.result import Success, Failure
from db_plugins.db.mongo import models

from shared.error.exceptions import ClientErrorException, EmptyQuery
from shared.utils.repositories import MongoRepository
from .payload import AstroObjectPayload


class ListAstroObjectRepository(MongoRepository):
    def _query(self, payload: AstroObjectPayload):
        return self.db.query().find_all(
            model=models.Object,
            filter_by=payload.filter_by,
            paginate=True,
            count=False
        )

    def _wrap_results(self, result):
        if result.total is None or result.total > 0:
            return Success(result)
        else:
            return Failure(ClientErrorException(EmptyQuery()))


class SingleAstroObjectRepository(MongoRepository):
    def _query(self, payload: AstroObjectPayload):
        return self.db.query().find_one(
            model=models.Object,
            filter_by=payload.filter_by
        )

    def _wrap_results(self, result):
        if result:
            return Success(result)
        else:
            return Failure(ClientErrorException(EmptyQuery()))
