from behave import when, given, then
from examples.features import environment
from examples.examples.api_request_example import features_examples


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
    environment.insert_in_database(context, "objects", _id=aid, features=features)


@when("request all features for {aid}")
def request_all_features(context, aid):
    context.result = features_examples.get_all_features(aid)


@when("request features with fid {fid:d} for {aid}")
def request_all_features_with_fid(context, fid, aid):
    context.result = features_examples.get_all_features_with_fid(aid, fid)


@when("request features with version {version} for {aid}")
def request_all_features_with_version(context, version, aid):
    context.result = features_examples.get_all_features_with_version(aid, version)


@when("request features with fid {fid:d} and version {version} for {aid}")
def request_all_features_with_fid_and_version(context, fid, version, aid):
    context.result = features_examples.get_all_features_with_fid_and_version(aid, fid, version)


@when("request feature {feature} with fid {fid:d} for {aid}")
def request_feature_with_fid(context, feature, fid, aid):
    context.result = features_examples.get_feature_with_fid(aid, feature, fid)


@when("request feature {feature} with version {version} for {aid}")
def request_feature_with_version(context, feature, version, aid):
    context.result = features_examples.get_feature_with_version(aid, feature, version)


@when("request feature {feature} with fid {fid:d} and version {version} for {aid}")
def request_feature_with_fid_and_version(context, feature, fid, version, aid):
    context.result = features_examples.get_feature_with_fid_and_version(aid, feature, fid, version)


@when("request feature {feature} for {aid}")
def request_feature(context, feature, aid):
    context.result = features_examples.get_feature(aid, feature)


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
