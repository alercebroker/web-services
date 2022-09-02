import requests
from behave import when, given, then
from examples.features.environment import insert_mongo_data, build_admin_token


BASE_URL = "http://alerts_api:5000/"
HEADER_ADMIN_TOKEN = {
    "AUTH-TOKEN": build_admin_token()
}


@given("the databases have ztf and atlas alerts")
def database_setup_ztf_atlas(context):
    insert_mongo_data(context)


@when("request {endpoint} endpoint for object {aid} in {survey_id} survey")
def request_to_endpoint(context, endpoint, aid, survey_id):
    res = requests.get(
        f"{BASE_URL}/objects/{aid}/{endpoint}?survey_id={survey_id.lower()}",
        headers=HEADER_ADMIN_TOKEN
    )
    if 200 <= res.status_code <= 400:
        # Handle successful requests
        context.result = res.json()
    else:
        context.result = res


@then(
    "the request should return detections and non detections for the object from {survey_id} data"
)
def check_lightcurve_response_for_survey(context, survey_id):
    assert isinstance(context.result, dict)
    if survey_id == "ZTF":
        assert len(context.result["detections"]) == 1
        assert context.result["detections"][0]["candid"] == "123"
        assert len(context.result["non_detections"]) == 1
        assert context.result["non_detections"][0]["mjd"] == 1
        assert context.result["non_detections"][0]["fid"] == 1
        assert context.result["non_detections"][0]["oid"] == "ZTF1"
    if survey_id == "ATLAS":
        assert len(context.result["detections"]) == 1
        assert context.result["detections"][0]["candid"] == "candid"
        assert len(context.result["non_detections"]) == 0


@then(
    "the request should return detections for the object from {survey_id} data"
)
def check_detections_response_for_survey(context, survey_id):
    assert isinstance(context.result, list)
    if survey_id == "ZTF":
        assert len(context.result) == 1
        assert context.result[0]["candid"] == "123"
    if survey_id == "ATLAS":
        assert len(context.result) == 1
        assert context.result[0]["candid"] == "candid"


@then(
    "the request should return non detections for the object from {survey_id} data"
)
def check_non_detections_response_for_survey(context, survey_id):
    assert isinstance(context.result, list)
    if survey_id == "ZTF":
        assert len(context.result) == 1
        assert context.result[0]["mjd"] == 1
        assert context.result[0]["fid"] == 1
        assert context.result[0]["oid"] == "ZTF1"


@then("the request should return {error_code} error")
def check_error_response(context, error_code):
    assert context.result.status_code == int(error_code)
