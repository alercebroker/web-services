import requests
from behave import when, given, then
from examples.features import environment


@given("there is {model} for object {aid} with id {oid} from telescope {tid}")
def insert_all_detections(context, model, aid, oid, tid):
    environment.insert_in_database(context, model, aid=aid, oid=oid, tid=tid)


@when("request {endpoint} for object {aid} in {survey_id} survey {has} permission")
def request_to_endpoint(context, endpoint, aid, survey_id, has):
    req_string = f"{environment.BASE_URL}/objects/{aid}/{endpoint}"
    if survey_id != "both":
        req_string += f"?survey_id={survey_id.lower()}"

    if has == "with":
        context.result = requests.get(req_string, headers=environment.HEADER_ADMIN_TOKEN)
    elif has == "without":
        context.result = requests.get(req_string)


@then("retrieve detections with identifiers {oids}")
def check_output_candid(context, oids):
    assert context.result.status_code == 200
    if oids == "none":  # Special case for empty return
        assert len(context.result.json()) == 0
        return
    oids = set(oids.split(","))
    for detection in context.result.json():
        assert detection["oid"] in oids
        oids.remove(detection["oid"])
    assert len(oids) == 0
