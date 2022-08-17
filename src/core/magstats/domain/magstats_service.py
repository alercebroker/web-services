from .magstats_payload import MagStatsPayload


class MagStatsService:
    def __init__(self, repo_magstats):
        self.repo_magstats = repo_magstats

    def get_magstats(self, payload: MagStatsPayload):
        return self.repo_magstats.get(payload)
