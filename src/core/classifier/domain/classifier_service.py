from .classifier_payload import ClassifiersPayload


class ClassifierService:
    def __init__(self, repo_classifiers, repo_classes):
        self.repo_classifiers = repo_classifiers
        self.repo_classes = repo_classes

    def get_classifiers(self, payload: ClassifiersPayload):
        return self.repo_classifiers.get(payload)

    def get_classes(self, payload: ClassifiersPayload):
        return self.repo_classes.get(payload)
