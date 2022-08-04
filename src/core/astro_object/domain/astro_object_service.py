from .list_object_payload import AstroObjectPayload


class AstroObjectService:
    def __init__(self, repo_list_object, repo_single_object, repo_limits):
        self.repo_list_object = repo_list_object
        self.repo_single_object = repo_single_object
        self.repo_limits = repo_limits

    def get_list_object(self, payload: AstroObjectPayload):
        return self.repo_list_object.get(payload)

    def get_single_object(self, payload: AstroObjectPayload):
        return self.repo_single_object.get(payload)

    def get_limits(self, payload: AstroObjectPayload):
        return self.repo_limits.get(payload)
