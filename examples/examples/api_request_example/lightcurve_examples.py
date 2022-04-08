import requests

BASE_URL = "http://alerts_api:5000/"


def get_lightcurve_from_ztf(object_id):
    res = requests.get(
        f"{BASE_URL}/objects/{object_id}/lightcurve?survey_id=ztf"
    )
    if res.status_code >= 200 and res.status_code < 400:
        # Handle successful requests
        return res.json()
    else:
        return res


def get_lightcurve_from_ztf_with_params(object_id):
    params = {"survey_id": "ztf"}
    res = requests.get(
        f"{BASE_URL}/objects/{object_id}/lightcurve", params=params
    )
    if res.status_code >= 200 and res.status_code < 400:
        # Handle successful requests
        return res.json()
    else:
        return res


def get_lightcurve_from_atlas(object_id):
    res = requests.get(
        f"{BASE_URL}/objects/{object_id}/lightcurve?survey_id=atlas"
    )
    if res.status_code >= 200 and res.status_code < 400:
        # Handle successful requests
        return res.json()
    else:
        return res
