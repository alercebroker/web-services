from shared.interface.command import Command, ResultHandler
from core.astro_object.domain.astro_object_service import (
    GetObjectListPayload,
    AstroObjectService,
)


class GetObjectList(Command):
    def __init__(
        self,
        service: AstroObjectService,
        payload: GetObjectListPayload,
        handler: ResultHandler,
    ):
        super().__init__(service, payload, handler)
        self.action = "get_object_list"
