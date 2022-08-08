from shared.utils.repositories import ObjectRepository


class ProbabilitiesRepository(ObjectRepository):
    field = "probabilities"

    def _post_process(self, result, **kwargs):
        if kwargs:
            return [elem for elem in result if all(elem[key] == value for key, value in kwargs.items())]
