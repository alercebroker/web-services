import abc
from returns.result import Success, Failure
from db_plugins.db.mongo import models

from shared.error.exceptions import ClientErrorException, EmptyQuery
from shared.utils.repositories import MongoRepository
from .payload import LightCurvePayload


class _DetectionNonDetectionRepository(MongoRepository, abc.ABC):
    def _find_all(self, model, payload):
        return self.db.query().find_all(
            model=model,
            filter_by=payload.filter,
            paginate=False,
        )


class DetectionRepository(_DetectionNonDetectionRepository):
    def _query(self, payload: LightCurvePayload):
        if self.check_object_exists(payload.raw_filter["aid"]):
            return self._find_all(models.Detection, payload)
        return None

    def _wrap_results(self, result):
        try:
            detections = list(result)
            if len(detections):
                return Success(detections)
        except TypeError:
            pass
        return Failure(ClientErrorException(EmptyQuery()))


class NonDetectionRepository(_DetectionNonDetectionRepository):
    def _query(self, payload: LightCurvePayload):
        if self.check_object_exists(payload.raw_filter["aid"]):
            return self._find_all(models.NonDetection, payload)
        return None

    def _wrap_results(self, result):
        try:
            return Success(list(result))
        except TypeError:
            pass
        return Failure(ClientErrorException(EmptyQuery()))


class LightCurveRepository(_DetectionNonDetectionRepository):
    def _query(self, payload: LightCurvePayload):
        if self.check_object_exists(payload.raw_filter["aid"]):
            return (
                self._find_all(models.Detection, payload),
                self._find_all(models.NonDetection, payload),
            )
        return None

    def _wrap_results(self, result):
        try:
            detections, non_detections = [list(res) for res in result]
            if len(detections):
                return Success({
                    "detections": detections,
                    "non_detections": non_detections
                })
        except TypeError:
            pass
        return Failure(ClientErrorException(EmptyQuery()))
