import requests
from behave import when, given, then
from examples.features import environment


@given("object {aid} is in the database with following probabilities")
def insert_object_with_probabilities(context, aid):
    probabilities = []
    for row in context.table:
        probability = {
            "classifier_name": row["classifier_name"],
            "classifier_version": row["classifier_version"],
            "class_name": row["class_name"],
            "probability": float(row["probability"]),
            "ranking": int(row["ranking"]),
        }
        probabilities.append(probability)
    environment.insert_in_database(context, "objects", aid=aid, probabilities=probabilities)


@given("objects are in the database with following probabilities")
def insert_object(context):
    for row in context.table:
        kwargs = {heading: value for heading, value in zip(row.headings, row.cells)}
        if "oid" in kwargs:
            kwargs["oid"] = kwargs["oid"].split(",")
        environment.insert_in_database(context, "objects", **kwargs)


@when("request objects with identifiers {oids} in {direction} order by {sort}")
def request_objects_by_id(context, oids, direction, sort):
    params = {"oid": oids.split(","), "order_by": sort, "order_mode": direction}
    url = f"{environment.BASE_URL}/objects"

    context.result = requests.get(url, params=params)


@when("request objects with {parameter} between {minimum} and {maximum} in {direction} order by {sort}")
def request_range_with_sort(context, parameter, minimum, maximum, direction, sort):
    params = {parameter: [minimum, maximum], "order_by": sort, "order_mode": direction}
    url = f"{environment.BASE_URL}/objects"

    context.result = requests.get(url, params=params)


@when("request objects with {parameter} {value} and classifier {classifier} in {direction} order by {sort}")
def request_parameter_and_classifier(context, parameter, value, classifier, direction, sort):
    params = {}
    if value != "all":
        params[parameter] = value
    if classifier != "all":
        params["classifier"] = classifier
    params.update({"order_by": sort, "order_mode": direction})
    url = f"{environment.BASE_URL}/objects"

    context.result = requests.get(url, params=params)


@when("request objects with {parameter} {value} and classifier {classifier}")
def request_parameter_and_classifier(context, parameter, value, classifier):
    params = {}
    if value != "all":
        params[parameter] = value
    if classifier != "all":
        params["classifier"] = classifier
    url = f"{environment.BASE_URL}/objects"

    context.result = requests.get(url, params=params)


@then("retrieve classes {classes} for objects {objects}, respectively")
def retrieve_classes_for_objects(context, classes, objects):
    assert context.result.status_code == 200
    classes = classes.split(",")
    objects = objects.split(",")
    for obj in context.result.json()["items"]:
        assert obj["aid"] in objects
        i = objects.index(obj["aid"])
        assert obj["class_name"] == classes[i]
        objects.pop(i)
        classes.pop(i)
    assert len(objects) == 0
    assert len(classes) == 0


@then("retrieve objects {objects} in that order")
def retrieve_ordered_classes(context, objects):
    assert context.result.status_code == 200
    objects = objects.split(",")
    items = context.result.json()["items"]
    assert len(items) == len(objects)
    for expected, actual in zip(objects, items):
        assert actual["aid"] == expected


@then("retrieve empty items")
def retrieve_empty_items(context):
    assert context.result.status_code == 200
    assert len(context.result.json()["items"]) == 0
