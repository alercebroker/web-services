from returns.result import Success, Failure
from db_plugins.db.mongo import models

from shared.error.exceptions import ClientErrorException, EmptyQuery
from shared.utils.repositories import MongoRepository
from ..domain import LightCurvePayload


class DetectionRepository(MongoRepository):
    def _query(self, payload: LightCurvePayload):
        return self._find_all(models.Detection, payload)

    def _wrap_results(self, result):
        try:
            detections = list(result)
        except TypeError:  # Pagination is being used
            detections = result.items
        if len(detections):
            return Success(detections)
        return Failure(ClientErrorException(EmptyQuery()))
