from returns.result import Success, Failure
from db_plugins.db.mongo import models

from shared.error.exceptions import ClientErrorException, EmptyQuery
from shared.utils.repositories import MongoRepository
from .payload import LightCurvePayload


class DetectionRepository(MongoRepository):
    def _query(self, payload: LightCurvePayload):
        return self.db.query().find_all(
            model=models.Detection,
            filter_by=payload.filter,
            paginate=False,
        )

    def _wrap_results(self, result):
        detections = list(result)
        if len(detections):
            return Success(detections)
        return Failure(ClientErrorException(EmptyQuery()))


class NonDetectionRepository(MongoRepository):
    def _query(self, payload: LightCurvePayload):
        return self.db.query().find_all(
            model=models.NonDetection,
            filter_by=payload.filter,
            paginate=False,
        )

    def _wrap_results(self, result):
        detections = list(result)
        if len(detections):
            return Success(detections)
        return Failure(ClientErrorException(EmptyQuery()))
