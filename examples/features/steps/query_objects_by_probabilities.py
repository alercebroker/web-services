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


@then("retrieve empty items")
def retrieve_empty_items(context):
    assert context.result.status_code == 200
    print(context.result.json()["items"])
    assert len(context.result.json()["items"]) == 0
