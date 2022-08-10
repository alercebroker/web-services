from shared.interface.command import Command, ResultHandler
from ..domain import AstroObjectService, ListAstroObjectPayload


class GetListAstroObject(Command):
    def __init__(
        self,
        service: AstroObjectService,
        payload: ListAstroObjectPayload,
        handler: ResultHandler,
    ):
        super().__init__(service, payload, handler)
        self.action = "get_list_object"
