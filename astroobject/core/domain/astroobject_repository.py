from abc import ABC, abstractmethod
from typing import List
from .astroobject_model import AstroObject
from .astroobject_queries import GetAstroObjectQuery, GetAstroObjectsQuery

class AstroObjectRepository(ABC):
    @abstractmethod
    def get_objects(self, query: GetAstroObjectsQuery) -> List[AstroObject]:
        pass

    @abstractmethod
    def get_object(self, query: GetAstroObjectQuery) -> AstroObject:
        pass