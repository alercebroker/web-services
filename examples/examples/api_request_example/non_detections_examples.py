import requests

BASE_URL = "http://alerts_api:5000/"


def get_non_detections_from_ztf(object_id):
    res = requests.get(
        f"{BASE_URL}/objects/{object_id}/non_detections?survey_id=ztf"
    )
    if res.status_code > 200 and res.status_code < 400:
        # Handle successful requests
        return res.json()
    else:
        return res


def get_non_detections_from_ztf_with_params(object_id):
    params = {"survey_id": "ztf"}
    res = requests.get(
        f"{BASE_URL}/objects/{object_id}/non_detections", params=params
    )
    if res.status_code >= 200 and res.status_code < 400:
        # Handle successful requests
        return res.json()
    else:
        return res
