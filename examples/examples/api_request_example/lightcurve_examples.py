import requests
from .token_builder import build_admin_token, BASE_URL


HEADER_ADMIN_TOKEN = {"AUTH-TOKEN": build_admin_token()}


def get_lightcurve_from_all_surveys(aid, as_admin=True):
    return requests.get(
        f"{BASE_URL}/objects/{aid}/lightcurve",
        headers=HEADER_ADMIN_TOKEN if as_admin else None
    )


def get_lightcurve_from_ztf(aid, as_admin=True):
    return requests.get(
        f"{BASE_URL}/objects/{aid}/lightcurve?survey_id=ztf",
        headers=HEADER_ADMIN_TOKEN if as_admin else None
    )


def get_lightcurve_from_atlas(aid, as_admin=True):
    return requests.get(
        f"{BASE_URL}/objects/{aid}/lightcurve?survey_id=atlas",
        headers=HEADER_ADMIN_TOKEN if as_admin else None
    )
