from returns.result import Success, Failure
from db_plugins.db.mongo import models

from shared.error.exceptions import ClientErrorException, EmptyQuery
from shared.utils.repositories import MongoRepository
from ..domain.astro_object_service import AstroObjectPayload


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
