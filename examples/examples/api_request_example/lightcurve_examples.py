import requests
from .token_builder import build_admin_token


BASE_URL = "http://alerts_api:5000/"
HEADER_ADMIN_TOKEN = {"AUTH-TOKEN": build_admin_token()}


def get_lightcurve_from_ztf(object_id):
    res = requests.get(
        f"{BASE_URL}/objects/{object_id}/lightcurve?survey_id=ztf",
        headers=HEADER_ADMIN_TOKEN,
    )
    if res.status_code >= 200 and res.status_code < 400:
        # Handle successful requests
        return res.json()
    else:
        return res


def get_lightcurve_from_ztf_with_params(object_id):
    params = {"survey_id": "ztf"}
    res = requests.get(
        f"{BASE_URL}/objects/{object_id}/lightcurve",
        params=params,
        headers=HEADER_ADMIN_TOKEN,
    )
    if res.status_code >= 200 and res.status_code < 400:
        # Handle successful requests
        return res.json()
    else:
        return res


def get_lightcurve_from_atlas(object_id):
    res = requests.get(
        f"{BASE_URL}/objects/{object_id}/lightcurve?survey_id=atlas",
        headers=HEADER_ADMIN_TOKEN,
    )
    if res.status_code >= 200 and res.status_code < 400:
        # Handle successful requests
        return res.json()
    else:
        return res
