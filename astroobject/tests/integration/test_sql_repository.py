from core.domain.astroobject_repository import (
    AstroObjectRepository,
    GetAstroObjectsQuery,
)


def test_astro_respository_objects_query(psql_service, astro_repository: AstroObjectRepository):
    query = GetAstroObjectsQuery(
        oid=["ZTF123"],
        page=1,
        page_size=10,
        count=False,
        ranking=1,
        firstmjd=[],
        lastmjd=[]
    )

    result = astro_repository.get_objects(query)
    assert len(result.items) == 2
    for item in result.items:
        assert item.probabilities[0].ranking == 1
