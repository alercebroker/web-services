import requests
from behave import when, given, then
from examples.features import environment


@given("there are {model} in database with following parameters")
def insert_all_detections(context, model):
    for row in context.table:
        kwargs = {heading: value for heading, value in zip(row.headings, row.cells)}
        environment.insert_in_database(context, model, **kwargs)


@when("request first {endpoint} for object {aid} in {survey_id} survey {has} permission")
def request_to_endpoint(context, endpoint, aid, survey_id, has):
    req_string = f"{environment.BASE_URL}/objects/{aid}/{endpoint}s?order_by=mjd&order_mode=ASC&page_size=1"
    if survey_id != "both":
        req_string += f"&survey_id={survey_id.lower()}"

    kwargs = {}
    if has == "with":
        kwargs["headers"] = environment.HEADER_ADMIN_TOKEN
    context.result = requests.get(req_string, **kwargs)


@when("request {endpoint} for object {aid} in {survey_id} survey {has} permission")
def request_to_endpoint(context, endpoint, aid, survey_id, has):
    req_string = f"{environment.BASE_URL}/objects/{aid}/{endpoint}"
    if survey_id != "both":
        req_string += f"?survey_id={survey_id.lower()}"

    kwargs = {}
    if has == "with":
        kwargs["headers"] = environment.HEADER_ADMIN_TOKEN
    context.result = requests.get(req_string, **kwargs)


@then("retrieve {results} with identifiers {oids}")
def check_output_candid(context, results, oids):
    assert context.result.status_code == 200
    if results == "results":
        output = context.result.json()
    else:
        output = context.result.json()[results]
    if oids == "none":  # Special case for empty return
        assert len(output) == 0
        return
    oids = set(oids.split(","))
    for detection in output:
        assert detection["oid"] in oids
        oids.remove(detection["oid"])
    assert len(oids) == 0
