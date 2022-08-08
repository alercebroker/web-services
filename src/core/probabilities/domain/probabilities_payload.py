from shared.utils.repositories import SingleObjectPayload


class ProbabilitiesPayload(SingleObjectPayload):
    def __init__(self, aid, classifier=None, classifier_version=None):
        super().__init__(aid, classifier=classifier, classifier_version=classifier_version)
