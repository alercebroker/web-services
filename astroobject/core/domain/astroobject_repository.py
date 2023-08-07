from abc import ABC, abstractmethod
from .astroobject_model import AstroObject
from .astroobject_queries import GetAstroObjectQuery, GetAstroObjectsQuery
from core.shared.sql import Pagination


class AstroObjectRepository(ABC):
    @abstractmethod
    async def get_objects(self, query: GetAstroObjectsQuery) -> Pagination[AstroObject]:
        pass

    @abstractmethod
    async def get_object(self, query: GetAstroObjectQuery) -> AstroObject:
        pass
