from db_plugins.db.mongo import models
from returns.result import Success, Failure

from shared.error.exceptions import ClientErrorException, EmptyQuery
from shared.utils.repositories import MongoRepository
from ..domain import AstroObjectPayload


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
