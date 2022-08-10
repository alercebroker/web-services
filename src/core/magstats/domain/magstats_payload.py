from shared.utils.repositories import SingleObjectPayload


class MagStatsPayload(SingleObjectPayload):
    def __init__(self, aid):
        super().__init__(aid)
