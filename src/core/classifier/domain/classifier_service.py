from .classifier_payload import ClassifierPayload


class ClassifierService:
    def __init__(self, repo_classifier):
        self.repo_classifier = repo_classifier

    def get_classifier(self, payload: ClassifierPayload):
        return self.repo_classifier.get(payload)
