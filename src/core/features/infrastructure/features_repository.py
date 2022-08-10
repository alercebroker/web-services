from shared.utils.repositories import ObjectRepository


class FeaturesRepository(ObjectRepository):
    field = "features"

    def _post_process(self, result, **kwargs):
        return [elem for elem in result if self.__check(elem, kwargs)]

    @staticmethod
    def __check(elem, filters):
        return elem["name"] == (
            filters["name"] or elem["name"]
        ) and elem["version"] == (
            filters["version"] or elem["version"]
        ) and elem["fid"] == (
            filters["fid"] or elem["fid"]
        )
