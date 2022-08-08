from shared.utils.repositories import ObjectRepository


class SingleAstroObjectRepository(ObjectRepository):
    def _post_process(self, result, **kwargs):
        return result
