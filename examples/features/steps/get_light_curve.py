from behave import when, given, then
from examples.features.environment import insert_mongo_data, insert_psql_data
from examples.examples.api_request_example.detections_examples import (
    get_detections_from_ztf,
    get_detections_from_ztf_with_params,
    get_detections_from_atlas,
)
from examples.examples.api_request_example.non_detections_examples import (
    get_non_detections_from_ztf,
    get_non_detections_from_ztf_with_params,
)
from examples.examples.api_request_example.lightcurve_examples import (
    get_lightcurve_from_ztf,
    get_lightcurve_from_ztf_with_params,
    get_lightcurve_from_atlas,
)

examples = {
    "detections": {
        "ZTF": [
            get_detections_from_ztf,
            get_detections_from_ztf_with_params,
        ],
        "ATLAS": [get_detections_from_atlas],
    },
    "non_detections": {
        "ZTF": [
            get_non_detections_from_ztf,
            get_non_detections_from_ztf_with_params,
        ],
    },
    "lightcurve": {
        "ZTF": [
            get_lightcurve_from_ztf,
            get_lightcurve_from_ztf_with_params,
        ],
        "ATLAS": [get_lightcurve_from_atlas],
    },
}


@given("the databases have ztf and altas alerts")
def database_setup_ztf_atlas(context):
    insert_psql_data(context)
    insert_mongo_data(context)


@when("request {endpoint} endpoint for Object {oid} in {survey_id} survey")
def request_to_endpoint(context, endpoint, oid, survey_id):
    for request in examples[endpoint][survey_id]:
        result = request(oid)
    context.result = result


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
        assert context.result["detections"][0]["candid"] == "candid2"
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
