from shared.interface.command import Command, ResultHandler
from ..domain import AstroObjectService, LimitsAstroObjectPayload


class GetLimitsAstroObject(Command):
    def __init__(
        self,
        service: AstroObjectService,
        payload: LimitsAstroObjectPayload,
        handler: ResultHandler,
    ):
        super().__init__(service, payload, handler)
        self.action = "get_limits"
