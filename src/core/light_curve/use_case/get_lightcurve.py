from shared.interface.command import Command, ResultHandler
from core.light_curve.domain.lightcurve_service import LightcurveServicePayload


class GetLightcurve(Command):
    def __init__(
        self,
        service,
        payload: LightcurveServicePayload,
        handler: ResultHandler,
    ):
        super().__init__(service, payload, handler)
        self.action = "get_lightcurve"
