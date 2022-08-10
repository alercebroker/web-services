from shared.interface.command import Command, ResultHandler
from ..domain import MagStatsService, MagStatsPayload


class GetMagStats(Command):
    def __init__(
        self,
        service: MagStatsService,
        payload: MagStatsPayload,
        handler: ResultHandler,
    ):
        super().__init__(service, payload, handler)
        self.action = "get_magstats"
