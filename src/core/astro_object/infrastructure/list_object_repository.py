from returns.result import Success, Failure
from db_plugins.db.mongo import models

from shared.error.exceptions import (
    ServerErrorException,
    ClientErrorException,
    EmptyQuery
)
from shared.utils.repositories import MongoRepository


class ListAstroObjectRepository(MongoRepository):
    def get(self, payload):
        try:
            result = self.db.query().find_all(
                model=models.Object,
                filter_by=payload.filter_by,
                paginate=True
            )
        except Exception as e:
            return Failure(ServerErrorException(e))

        if result.total > 0:
            return Success(list(result))
        else:
            return Failure(ClientErrorException(EmptyQuery()))
