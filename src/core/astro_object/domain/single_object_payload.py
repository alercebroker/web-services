from shared.utils.repositories import SingleObjectPayload


class SingleAstroObjectPayload(SingleObjectPayload):
    def __init__(self, aid):
        super().__init__(aid)
