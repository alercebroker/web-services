from shared.utils.repositories import ObjectRepository


class ProbabilitiesRepository(ObjectRepository):
    field = "probabilities"

    def _post_process(self, result, **kwargs):
        return [elem for elem in result if self.__check(elem, kwargs)]

    @staticmethod
    def __check(elem, filters):
        return elem["classifier_name"] == (
            filters["classifier"] or elem["classifier_name"]
        ) and elem["classifier_version"] == (
            filters["classifier_version"] or elem["classifier_version"]
        )
