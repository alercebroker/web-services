from shared.interface.command import Command, ResultHandler
from ..domain import AstroObjectService, AstroObjectPayload


class GetLimits(Command):
    def __init__(
        self,
        service: AstroObjectService,
        payload: AstroObjectPayload,
        handler: ResultHandler,
    ):
        super().__init__(service, payload, handler)
        self.action = "get_limits"
