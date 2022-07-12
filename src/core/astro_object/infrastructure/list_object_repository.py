from returns.result import Success, Failure
from db_plugins.db.mongo import models

from shared.error.exceptions import (
    ServerErrorException,
    ClientErrorException,
    EmptyQuery
)
from shared.utils.repositories import MongoRepository
from ..domain.astro_object_service import AstroObjectPayload


class ListAstroObjectRepository(MongoRepository):
    def _query(self, payload: AstroObjectPayload):
        return self.db.query().find_all(
            model=models.Object,
            filter_by=payload.filter_by,
            paginate=True
        )

    def _wrap_results(self, result):
        if result.total > 0:
            return Success(list(result))
        else:
            return Failure(ClientErrorException(EmptyQuery()))
