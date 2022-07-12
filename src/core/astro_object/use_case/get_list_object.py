from shared.interface.command import Command, ResultHandler
from core.astro_object.domain.astro_object_service import AstroObjectPayload


class GetListAstroObject(Command):
    def __init__(
            self,
            service,
            payload: AstroObjectPayload,
            handler: ResultHandler
    ):
        super().__init__(service, payload, handler)
        self.action = 'get_list_object'
