from shared.interface.command import Command, ResultHandler
from ..domain import FeaturesPayload, FeaturesService


class GetFeatures(Command):
    def __init__(
        self,
        service: FeaturesService,
        payload: FeaturesPayload,
        handler: ResultHandler,
    ):
        super().__init__(service, payload, handler)
        self.action = "get_features"
