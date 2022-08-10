from shared.interface.command import Command, ResultHandler
from ..domain import ProbabilitiesPayload, ProbabilitiesService


class GetProbabilities(Command):
    def __init__(
        self,
        service: ProbabilitiesService,
        payload: ProbabilitiesPayload,
        handler: ResultHandler,
    ):
        super().__init__(service, payload, handler)
        self.action = "get_probabilities"
