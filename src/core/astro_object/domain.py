from .payload import AstroObjectPayload


class AstroObjectService:
    def __init__(self, repo_object_list, repo_single_object, repo_limits):
        self.repo_object_list = repo_object_list
        self.repo_single_object = repo_single_object
        self.repo_limits = repo_limits

    def get_list_object(self, payload: AstroObjectPayload):
        return self.repo_object_list.get(payload)

    def get_single_object(self, payload: AstroObjectPayload):
        return self.repo_single_object.get(payload)

    def get_limits(self, payload: AstroObjectPayload):
        return self.repo_limits.get(payload)
