from .payload import AstroObjectPayload


class AstroObjectService:
    def __init__(self, list_object_repository, single_object_repository):
        self.list_object_repository = list_object_repository
        self.single_object_repository = single_object_repository

    def get_list_object(self, payload: AstroObjectPayload):
        return self.list_object_repository.get(payload)

    def get_single_object(self, payload: AstroObjectPayload):
        return self.single_object_repository.get(payload)
