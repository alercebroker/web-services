from shared.utils.repositories import SingleObjectPayload


class FeaturesPayload(SingleObjectPayload):
    def __init__(self, aid, name=None, version=None, fid=None):
        super().__init__(aid, name=name, version=version, fid=fid)
