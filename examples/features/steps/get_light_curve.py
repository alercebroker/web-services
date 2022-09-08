from behave import when, given, then
from examples.features import environment
from examples.examples.api_request_example import detections_examples, non_detections_examples, lightcurve_examples


examples = {
    "detections": {
        "ZTF": detections_examples.get_all_detections_from_ztf,
        "ATLAS": detections_examples.get_all_detections_from_atlas,
        "all": detections_examples.get_all_detections_from_all_surveys,
    },
    "non detections": {
        "ZTF": non_detections_examples.get_all_non_detections_from_ztf,
        "ATLAS": non_detections_examples.get_all_non_detections_from_atlas,
        "all": non_detections_examples.get_all_non_detections_from_all_surveys,
    },
    "lightcurve": {
        "ZTF": lightcurve_examples.get_lightcurve_from_ztf,
        "ATLAS": lightcurve_examples.get_lightcurve_from_atlas,
        "all": lightcurve_examples.get_lightcurve_from_all_surveys,
    },
    "first detection": {
        "ZTF": detections_examples.get_first_detection_from_ztf,
        "ATLAS": detections_examples.get_first_detection_from_atlas,
        "all": detections_examples.get_first_detection_from_all_surveys,
    },
    "first non detection": {
        "ZTF": non_detections_examples.get_first_non_detection_from_ztf,
        "ATLAS": non_detections_examples.get_first_non_detection_from_atlas,
        "all": non_detections_examples.get_first_non_detection_from_all_surveys,
    },
}


@given("there are {model} for object {aid} with following parameters")
def insert_all_detections(context, model, aid):
    for row in context.table:
        kwargs = {heading: value for heading, value in zip(row.headings, row.cells)}
        kwargs["aid"] = aid
        environment.insert_in_database(context, model, **kwargs)


@when("request {endpoint} for object {aid} in {survey} survey as {user}")
def request_to_endpoint(context, endpoint, aid, survey, user):
    request = examples[endpoint][survey]
    as_admin = user == "admin"
    context.result = request(aid, as_admin=as_admin)


@then("retrieve detections with identifiers: {detections}; and non detections with identifiers: {non_detections}")
def check_output_candid(context, detections, non_detections):
    assert context.result.status_code == 200
    output = context.result.json()
    if detections == "none" and non_detections == "none":  # Special case for empty return
        assert output is None
        return
    actual_detections = output["detections"]
    actual_non_detections = output["non_detections"]

    detections = set(detections.split(","))
    for detection in actual_detections:
        assert detection["oid"] in detections
        detections.remove(detection["oid"])
    assert len(detections) == 0

    non_detections = set(non_detections.split(","))
    for non_detection in actual_non_detections:
        assert non_detection["oid"] in non_detections
        non_detections.remove(non_detection["oid"])
    assert len(non_detections) == 0


@then("retrieve results with identifiers: {expected}")
def check_output_candid(context, expected):
    assert context.result.status_code == 200
    output = context.result.json()
    if expected == "none":  # Special case for empty return
        assert len(output) == 0
        return
    expected = set(expected.split(","))
    for result in output:
        assert result["oid"] in expected
        expected.remove(result["oid"])
    assert len(expected) == 0


@then("retrieve error code {error_code:d}")
def check_error_code(context, error_code):
    assert context.result.status_code == error_code
