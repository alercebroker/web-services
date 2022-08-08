from .probabilities_payload import ProbabilitiesPayload


class ProbabilitiesService:
    def __init__(self, repo_probabilities):
        self.repo_probabilities = repo_probabilities

    def get_list_object(self, payload: ProbabilitiesPayload):
        return self.repo_probabilities.get(payload)
