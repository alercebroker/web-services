from shared.interface.command import Command, ResultHandler
from ..domain import LightCurveService, LightCurvePayload


class GetDetections(Command):
    def __init__(
        self,
        service: LightCurveService,
        payload: LightCurvePayload,
        handler: ResultHandler,
    ):
        super().__init__(service, payload, handler)
        self.action = "get_detections"
