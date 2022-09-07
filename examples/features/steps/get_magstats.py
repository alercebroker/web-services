import requests
from behave import when, given, then
from examples.features import environment


@given("object {aid} is in the database with magstats for fid {fids}")
def insert_object_with_magstats(context, aid, fids):
    magstats = []
    for fid in fids.split(","):
        magstat = {"fid": int(fid)}
        magstats.append(magstat)
    environment.insert_in_database(context, "objects", aid=aid, magstats=magstats)


@when("request magstats for {aid}")
def request_magstats(context, aid):
    url = f"{environment.BASE_URL}/objects/{aid}/magstats"

    context.result = requests.get(url)


@then("retrieve magstats with fid {fids}")
def retrieve_classes_for_objects(context, fids):
    assert context.result.status_code == 200
    fids = {int(fid) for fid in fids.split(",")}
    for magstat in context.result.json():
        assert magstat["fid"] in fids
        fids.remove(magstat["fid"])
    assert len(fids) == 0
