from core.domain.astroobject_queries import GetAstroObjectsQuery, GetAstroObjectQuery
from core.domain.astroobject_repository import AstroObjectRepository

class AstroObjectService:
    def __init__(self, astroobject_repository: AstroObjectRepository):
        self.repository = astroobject_repository

    async def get_objects(self, query: GetAstroObjectsQuery):
        return self.repository.get_objects(query)
    
    async def get_object(self, query: GetAstroObjectQuery):
        return self.repository.get_object(query)