from .list_object_payload import ListAstroObjectPayload
from .single_object_payload import SingleAstroObjectPayload


class AstroObjectService:
    def __init__(self, repo_list_object, repo_single_object, repo_limits):
        self.repo_list_object = repo_list_object
        self.repo_single_object = repo_single_object
        self.repo_limits = repo_limits

    def get_list_object(self, payload: ListAstroObjectPayload):
        return self.repo_list_object.get(payload)

    def get_single_object(self, payload: SingleAstroObjectPayload):
        return self.repo_single_object.get(payload)

    def get_limits(self, payload: ListAstroObjectPayload):
        return self.repo_limits.get(payload)
