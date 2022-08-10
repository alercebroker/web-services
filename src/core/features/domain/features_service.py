from .features_payload import FeaturesPayload


class FeaturesService:
    def __init__(self, repo_features):
        self.repo_features = repo_features

    def get_probabilities(self, payload: FeaturesPayload):
        return self.repo_features.get(payload)
