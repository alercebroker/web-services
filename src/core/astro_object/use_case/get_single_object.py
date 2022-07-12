from shared.interface.command import Command, ResultHandler
from core.astro_object.domain.astro_object_service import AstroObjectService


class GetSingleAstroObject(Command):
    def __init__(
            self,
            service,
            payload: AstroObjectService,
            handler: ResultHandler
    ):
        super().__init__(service, payload, handler)
        self.action = 'get_single_object'
