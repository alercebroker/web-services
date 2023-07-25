from ..domain.astroobject_queries import GetAstroObjectsQuery, GetAstroObjectQuery
from ..domain.astroobject_repository import AstroObjectRepository

class AstroObjectService:
    def __init__(self, astroobject_repository: AstroObjectRepository):
        self.repository = astroobject_repository

    def get_objects(self, query: GetAstroObjectsQuery):
        return self.get_objects(query)
    
    def get_object(self, query: GetAstroObjectQuery):
        return self.get_object(query)