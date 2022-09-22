import requests
from .token_builder import build_admin_token, BASE_URL


HEADER_ADMIN_TOKEN = {"Authorization": f"bearer {build_admin_token()}"}


def get_all_detections_from_all_surveys(aid, as_admin=True):
    return requests.get(
        f"{BASE_URL}/objects/{aid}/detections",
        headers=HEADER_ADMIN_TOKEN if as_admin else None
    )


def get_all_detections_from_ztf(aid, as_admin=True):
    return requests.get(
        f"{BASE_URL}/objects/{aid}/detections?survey_id=ztf",
        headers=HEADER_ADMIN_TOKEN if as_admin else None
    )


def get_all_detections_from_atlas(aid, as_admin=True):
    return requests.get(
        f"{BASE_URL}/objects/{aid}/detections?survey_id=atlas",
        headers=HEADER_ADMIN_TOKEN if as_admin else None
    )


def get_first_detection_from_all_surveys(aid, as_admin=True):
    return requests.get(
        f"{BASE_URL}/objects/{aid}/detections?order_by=mjd&order_mode=ASC&page_size=1",
        headers=HEADER_ADMIN_TOKEN if as_admin else None
    )


def get_first_detection_from_ztf(aid, as_admin=True):
    return requests.get(
        f"{BASE_URL}/objects/{aid}/detections?survey_id=ztf&order_by=mjd&order_mode=ASC&page_size=1",
        headers=HEADER_ADMIN_TOKEN if as_admin else None
    )


def get_first_detection_from_atlas(aid, as_admin=True):
    return requests.get(
        f"{BASE_URL}/objects/{aid}/detections?survey_id=atlas&order_by=mjd&order_mode=ASC&page_size=1",
        headers=HEADER_ADMIN_TOKEN if as_admin else None
    )
