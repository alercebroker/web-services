from shared.interface.command import Command, ResultHandler
from ..domain.magstats_service import MagStatsServicePayload


class GetMagStats(Command):
    def __init__(
        self,
        service,
        payload: MagStatsServicePayload,
        handler: ResultHandler,
    ):
        super().__init__(service, payload, handler)
        self.action = "get_magstats"
