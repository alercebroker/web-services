class LightcurveService:
    def __init__(
        self, detection_repository_factory, non_detection_repository_factory
    ):
        self.detection_repository_factory = detection_repository_factory
        self.non_detection_repository_factory = (
            non_detection_repository_factory
        )

    def get_detections(self, payload: dict) -> list:
        repository = self.detection_repository_factory(
            payload.get("survey_id")
        )
        return repository.get(payload.get("oid"))

    def get_non_detections(self, payload: dict) -> list:
        repository = self.non_detection_repository_factory(
            payload.get("survey_id")
        )
        return repository.get(payload.get("oid"))

    def get_lightcurve(self, payload) -> dict:
        detections = self.get_detections(payload)
        non_detections = self.get_non_detections(payload)
        return {"detections": detections, "non_detections": non_detections}
