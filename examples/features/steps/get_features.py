import requests
from behave import when, given, then
from examples.features import environment


@given("object {aid} is in the database with following features")
def insert_object_with_features(context, aid):
    features = []
    for row in context.table:
        feature = {
            "name": row["name"],
            "fid": int(row["fid"]),
            "value": float(row["value"]),
            "version": row["version"],
        }
        features.append(feature)
    environment.insert_in_database(context, "objects", aid=aid, features=features)


@when("request all {endpoint} for {aid}")
def request_all_from_endpoint(context, endpoint, aid):
    url = f"{environment.BASE_URL}/objects/{aid}/{endpoint}"

    context.result = requests.get(url)


@when("request features with fid {fid:d} for {aid}")
def request_all_features_with_fid(context, fid, aid):
    params = {"fid": fid}
    url = f"{environment.BASE_URL}/objects/{aid}/features"

    context.result = requests.get(url, params=params)


@when("request features with version {version} for {aid}")
def request_all_features_with_version(context, version, aid):
    params = {"version": version}
    url = f"{environment.BASE_URL}/objects/{aid}/features"

    context.result = requests.get(url, params=params)


@when("request features with fid {fid:d} and version {version} for {aid}")
def request_all_features_with_fid_and_version(context, fid, version, aid):
    params = {"fid": fid, "version": version}
    url = f"{environment.BASE_URL}/objects/{aid}/features"

    context.result = requests.get(url, params=params)


@when("request feature {feature} with fid {fid:d} for {aid}")
def request_feature_with_fid(context, feature, fid, aid):
    params = {"fid": fid}
    url = f"{environment.BASE_URL}/objects/{aid}/features/{feature}"

    context.result = requests.get(url, params=params)


@when("request feature {feature} with version {version} for {aid}")
def request_feature_with_version(context, feature, version, aid):
    params = {"version": version}
    url = f"{environment.BASE_URL}/objects/{aid}/features/{feature}"

    context.result = requests.get(url, params=params)


@when("request feature {feature} with fid {fid:d} and version {version} for {aid}")
def request_feature_with_fid_and_version(context, feature, fid, version, aid):
    params = {"fid": fid, "version": version}
    url = f"{environment.BASE_URL}/objects/{aid}/features/{feature}"

    context.result = requests.get(url, params=params)


@when("request feature {feature} for {aid}")
def request_feature(context, feature, aid):
    url = f"{environment.BASE_URL}/objects/{aid}/features/{feature}"

    context.result = requests.get(url)


@then("retrieve following features")
def retrieve_features(context):
    assert context.result.status_code == 200
    names, fids, values, versions = [], [], [], []
    for row in context.table:
        names.append(row["name"])
        versions.append(row["version"])
        fids.append(int(row["fid"]))
        values.append(float(row["value"]))
    for feature in context.result.json():
        idx = [i for i, (name, ver, fid, value) in enumerate(zip(names, versions, fids, values))
               if feature["name"] == name and feature["version"] == ver
               and feature["fid"] == fid and feature["value"] == value]
        assert len(idx) == 1
        names.pop(idx[0])
        versions.pop(idx[0])
        fids.pop(idx[0])
        values.pop(idx[0])
    assert len(names) == 0
    assert len(versions) == 0
    assert len(fids) == 0
    assert len(values) == 0


@then("retrieve empty features")
def retrieve_features(context):
    assert context.result.status_code == 200
    assert len(context.result.json()) == 0
