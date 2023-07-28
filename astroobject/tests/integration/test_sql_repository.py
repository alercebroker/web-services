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
        ranking=1
    )

    result = astro_repository.get_objects(query)
    for item in result.items:
        print(item.model_dump())
