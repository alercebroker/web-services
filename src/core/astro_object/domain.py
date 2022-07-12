from .payload import AstroObjectPayload


class AstroObjectService:
    def __init__(self, list_repository, single_repository):
        self.list_repository = list_repository
        self.single_repository = single_repository

    def get_list_object(self, payload: AstroObjectPayload):
        return self.list_repository.get(payload)

    def get_single_object(self, payload: AstroObjectPayload):
        return self.single_repository.get(payload)
