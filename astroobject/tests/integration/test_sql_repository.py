import pytest

from core.domain.astroobject_repository import (
    AstroObject,
    AstroObjectRepository,
    GetAstroObjectsQuery,
    GetAstroObjectQuery,
)

@pytest.mark.asyncio
async def test_astro_respository_objects_query(psql_service, astro_repository: AstroObjectRepository):
    query = GetAstroObjectsQuery(
        oid=["ZTF123"],
        page=1,
        page_size=10,
        count=False,
        ranking=1,
        firstmjd=[],
        lastmjd=[]
    )

    result = await astro_repository.get_objects(query)
    print(result)
    assert len(result.items) == 2
    for item in result.items:
        assert item.probabilities[0].ranking == 1

@pytest.mark.asyncio
async def test_astro_repository_object_by_id(psql_service, astro_repository: AstroObjectRepository):
    query = GetAstroObjectQuery(oid="ZTF123")
    result = await astro_repository.get_object(query)
    assert result is not None
    assert isinstance(result, AstroObject)
    assert result.oid == "ZTF123"

@pytest.mark.asyncio
async def test_astro_repository_object_is_none(psql_service, astro_repository: AstroObjectRepository):
    query = GetAstroObjectQuery(oid="not_existant")
    result = await astro_repository.get_object(query)
    assert result is None