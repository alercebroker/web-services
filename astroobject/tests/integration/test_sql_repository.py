from core.domain.astroobject_repository import (
    AstroObjectRepository,
    GetAstroObjectsQuery,
)


def test_astro_respository_objects_query(psql_service ,astro_repository: AstroObjectRepository):
    query = GetAstroObjectsQuery(
        oids=["ZTF123"],
        page=1,
        page_size=10,
        count=False,
        filters={},
        conesearch={},
    )

    result = astro_repository.get_objects(query)
    for item in result.items:
        print(item[0].__dict__)
        print(item[1].__dict__)
