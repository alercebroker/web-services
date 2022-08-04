from shared.interface.command import Command, ResultHandler
from .domain import LightCurveService
from core.light_curve.domain.light_curve_payload import LightCurvePayload


class GetDetections(Command):
    def __init__(
        self,
        service: LightCurveService,
        payload: LightCurvePayload,
        handler: ResultHandler,
    ):
        super().__init__(service, payload, handler)
        self.action = "get_detections"


class GetNonDetections(Command):
    def __init__(
        self,
        service: LightCurveService,
        payload: LightCurvePayload,
        handler: ResultHandler,
    ):
        super().__init__(service, payload, handler)
        self.action = "get_non_detections"


class GetLightCurve(Command):
    def __init__(
        self,
        service: LightCurveService,
        payload: LightCurvePayload,
        handler: ResultHandler,
    ):
        super().__init__(service, payload, handler)
        self.action = "get_lightcurve"
