import pytest

from core.domain.astroobject_model import AstroObject
from core.domain.astroobject_queries import (
    GetAstroObjectQuery,
    GetAstroObjectsQuery,
)
from core.shared.sql import Pagination
from core.application.astroobject_service import (
    AstroObjectService,
    AstroObjectRepository,
)

dict_object = {
    "oid": "ZTF123",
    "ndethist": 1,
    "ncovhist": 1,
    "mjdstarthist": 1.0,
    "mjdendhist": 1.0,
    "corrected": False,
    "stellar": False,
    "ndet": 5,
    "g_r_max": 1.0,
    "g_r_max_corr": 1.0,
    "g_r_mean": 1.0,
    "g_r_mean_corr": 1.0,
    "meanra": 33.0,
    "meandec": 133.0,
    "sigmara": 3.0,
    "sigmadec": 1.0,
    "deltajd": 0.5,
    "firstmjd": 55555.0,
    "lastmjd": 555556.0,
    "step_id_corr": "asd",
    "diffpos": False,
    "reference_change": False,
    "probabilities": [
        {
            "oid": "ZTF123",
            "class_name": "SNIa",
            "classifier_name": "classifier",
            "classifier_version": "classifier_v1",
            "probability": 0.99,
            "ranking": 1,
        }
    ],
}

class MockAstroObjectRepository(AstroObjectRepository):
    async def get_object(self, query: GetAstroObjectQuery) -> AstroObject:
        if query.oid == "ZTF123":
            return AstroObject(**dict_object)
        return None

    async def get_objects(self, query: GetAstroObjectsQuery) -> Pagination[AstroObject]:
        items = [AstroObject(**dict_object)]
        return Pagination(None, 1, 10, 1, items)


mock_service = AstroObjectService(astroobject_repository=MockAstroObjectRepository())

@pytest.mark.asyncio
async def test_get_objects():
    query_dict = {
        "oids": ["oid1", "ZTF123"],
        "page": 1,
        "page_size": 10,
        "count": True,
        "order_by": "lol",
        "order_mode": "ASC",
        "filters": {},
        "conesearch": {},
    }
    result = await mock_service.get_objects(GetAstroObjectsQuery(**query_dict))
    assert len(result.items) == 1

@pytest.mark.asyncio
async def test_get_single_object():
    result = await mock_service.get_object(GetAstroObjectQuery(oid="ZTF123"))
    assert result.model_dump() == dict_object