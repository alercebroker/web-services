from .payload import LightCurvePayload


class LightCurveService:
    def __init__(self, repo_detections, repo_non_detections, repo_lightcurve):
        self.repo_detections = repo_detections
        self.repo_non_detections = repo_non_detections
        self.repo_lightcurve = repo_lightcurve

    def get_detections(self, payload: LightCurvePayload):
        return self.repo_detections.get(payload)

    def get_non_detections(self, payload: LightCurvePayload):
        return self.repo_non_detections.get(payload)

    def get_lightcurve(self, payload: LightCurvePayload):
        return self.repo_lightcurve.get(payload)
