from shared.interface.command import Command, ResultHandler
from ..domain import ClassifierService, ClassifiersPayload


class GetClasses(Command):
    def __init__(
        self,
        service: ClassifierService,
        payload: ClassifiersPayload,
        handler: ResultHandler,
    ):
        super().__init__(service, payload, handler)
        self.action = "get_classes"
