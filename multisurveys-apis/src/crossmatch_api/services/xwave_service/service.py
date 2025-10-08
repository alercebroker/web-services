from typing import Callable, TypeAlias

from crossmatch_api.services.xwave_client.conesearch_result import ConesearchResponse

ConesearchQuery: TypeAlias = Callable[[float, float, float, int, str], list[ConesearchResponse]]


def conesearch(ra: float, dec: float, radius: float, xwave_url: str, conesearch_query: ConesearchQuery) -> list[dict]:
    return _parse_response(conesearch_query(ra, dec, radius, 10, xwave_url), xwave_url)


def _parse_response(response: list[ConesearchResponse], xwave_url: str) -> list[dict]:
    results: list[dict] = []
    for obj in response:
        catalog = obj.catalog
        obj_dict = {}
        obj_dict[catalog] = {}
        # we only want the closest object of a catalog, so we get the first in the data array
        for field in obj.data[0].fields:
            obj_dict[catalog][field] = {"unit": "", "value": obj.data[0].fields[field].get_value()}
        obj_dict[catalog]["powered_by"] = {"name": "xwave", "url": xwave_url}
        results.append(obj_dict)

    return results
