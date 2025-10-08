from crossmatch_api.services.xwave_client.conesearch_result import ConesearchResponse
import requests


def conesearch(ra: float, dec: float, radius: float, neighbors: int, xwave_url: str) -> list[ConesearchResponse]:
    params = {
        "ra": ra,
        "dec": dec,
        "radius": radius,
        "nneighbor": neighbors,
        "getMetadata": "true",
    }
    response = requests.get(join_url(xwave_url, "v1/conesearch"), params=params)

    if response.status_code >= 400 and response.status_code < 500:
        raise ValueError(f"Error {response.status_code}: {response.text}")
    if response.status_code >= 500:
        raise RuntimeError(f"Error {response.status_code}: {response.text}")
    if response.status_code == 204:
        return []

    results: list[ConesearchResponse] = []
    for elem in response.json():
        results.append(ConesearchResponse.from_dict(elem))

    return results


def join_url(url: str, path: str) -> str:
    url = url.rstrip("/")
    path = path.lstrip("/")
    return url + "/" + path
