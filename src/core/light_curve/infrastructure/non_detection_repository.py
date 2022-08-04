from returns.result import Success, Failure
from db_plugins.db.mongo import models

from shared.error.exceptions import ClientErrorException, EmptyQuery
from shared.utils.repositories import MongoRepository
from ..domain import LightCurvePayload


class NonDetectionRepository(MongoRepository):
    def _query(self, payload: LightCurvePayload):
        return self._find_all(models.NonDetection, payload)

    def _wrap_results(self, result):
        non_detections = list(result)
        if len(non_detections):
            return Success(non_detections)
        return Failure(ClientErrorException(EmptyQuery()))
