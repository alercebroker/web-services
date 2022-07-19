import abc
from returns.result import Success, Failure
from db_plugins.db.mongo import models

from shared.error.exceptions import ClientErrorException, EmptyQuery
from shared.utils.repositories import MongoRepository
from .payload import LightCurvePayload


class _DetectionNonDetectionRepository(MongoRepository, abc.ABC):
    def _find_all_from_model(self, model, payload):
        return self.db.query().find_all(
            model=model,
            filter_by=payload.filter,
            paginate=False,
        )


class DetectionRepository(_DetectionNonDetectionRepository):
    def _query(self, payload: LightCurvePayload):
        return self._find_all_from_model(models.Detection, payload)

    def _wrap_results(self, result):
        detections = list(result)
        if len(detections):
            return Success(detections)
        return Failure(ClientErrorException(EmptyQuery()))


class NonDetectionRepository(_DetectionNonDetectionRepository):
    def _query(self, payload: LightCurvePayload):
        return self._find_all_from_model(models.NonDetection, payload)

    def _wrap_results(self, result):
        non_detections = list(result)
        if len(non_detections):
            return Success(non_detections)
        return Failure(ClientErrorException(EmptyQuery()))


class LightCurveRepository(_DetectionNonDetectionRepository):
    def _query(self, payload: LightCurvePayload):
        return (
            self._find_all_from_model(models.Detection, payload),
            self._find_all_from_model(models.NonDetection, payload),
        )

    def _wrap_results(self, result):
        detections, non_detections = [list(res) for res in result]
        if len(detections):
            return Success(
                {"detections": detections, "non_detections": non_detections}
            )
        return Failure(ClientErrorException(EmptyQuery()))
