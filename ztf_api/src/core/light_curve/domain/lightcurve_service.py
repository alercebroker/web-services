from dataclasses import dataclass
from returns.result import Success
from shared.utils.result_helpers import get_failure_from_list
from core.light_curve.infrastructure.detection_repository import (
    DetectionRepository,
)


@dataclass
class LightcurveServicePayload:
    oid: str
    survey_id: str


class LightcurveService:
    def __init__(
        self, detection_repository_factory, non_detection_repository_factory
    ):
        self.detection_repository_factory = detection_repository_factory
        self.non_detection_repository_factory = (
            non_detection_repository_factory
        )

    def get_detections(self, payload: LightcurveServicePayload) -> list:
        repository: DetectionRepository = self.detection_repository_factory(
            payload.survey_id
        )
        return repository.get(payload.oid, payload.survey_id)

    def get_non_detections(self, payload: LightcurveServicePayload) -> list:
        repository = self.non_detection_repository_factory(payload.survey_id)
        return repository.get(payload.oid, payload.survey_id)

    def get_lightcurve(self, payload: LightcurveServicePayload) -> dict:
        detections = self.get_detections(payload)
        non_detections = self.get_non_detections(payload)
        light_curve_data = [detections, non_detections]
        failure = get_failure_from_list(results_list=light_curve_data)
        if failure:
            return failure
        else:
            light_curve = {
                "detections": light_curve_data[0].unwrap(),
                "non_detections": light_curve_data[1].unwrap(),
            }

            return Success(light_curve)
