from .payload import LightCurvePayload


class LightCurveService:
    def __init__(self, repo_detection, repo_non_detection, repo_lightcurve):
        self.repo_detection = repo_detection
        self.repo_non_detection = repo_non_detection
        self.repo_lightcurve = repo_lightcurve

    def get_detections(self, payload: LightCurvePayload):
        return self.repo_detection.get(payload)

    def get_non_detections(self, payload: LightCurvePayload):
        return self.repo_non_detection.get(payload)

    def get_lightcurve(self, payload: LightCurvePayload):
        return self.repo_lightcurve.get(payload)
