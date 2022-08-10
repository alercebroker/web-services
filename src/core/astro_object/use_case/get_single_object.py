from shared.interface.command import Command, ResultHandler
from ..domain import AstroObjectService, SingleAstroObjectPayload


class GetSingleAstroObject(Command):
    def __init__(
        self,
        service: AstroObjectService,
        payload: SingleAstroObjectPayload,
        handler: ResultHandler,
    ):
        super().__init__(service, payload, handler)
        self.action = "get_single_object"
