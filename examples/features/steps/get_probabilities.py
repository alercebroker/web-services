import requests
from behave import when, then
from examples.features import environment


@when("request all probabilities for {aid}")
def request_limits(context, aid):
    url = f"{environment.BASE_URL}/objects/{aid}/probabilities"

    context.result = requests.get(url)


@when("request probabilities for {classifier} classifier for {aid}")
def request_limits(context, classifier, aid):
    params = {"classifier": classifier}
    url = f"{environment.BASE_URL}/objects/{aid}/probabilities"

    context.result = requests.get(url, params=params)


@when("request probabilities for {classifier} classifier and version {version} for {aid}")
def request_limits(context, classifier, version, aid):
    params = {"classifier": classifier, "classifier_version": version}
    url = f"{environment.BASE_URL}/objects/{aid}/probabilities"

    context.result = requests.get(url, params=params)


@then("retrieve classes {classes} with probabilities {probabilities}")
def retrieve_classes_for_objects(context, classes, probabilities):
    assert context.result.status_code == 200
    classes = classes.split(",")
    probabilities = [float(prob) for prob in probabilities.split(",")]
    for prob in context.result.json():
        assert prob["class_name"] in classes
        i = classes.index(prob["class_name"])
        assert prob["probability"] == probabilities[i]
        classes.pop(i)
        probabilities.pop(i)
    assert len(classes) == 0
    assert len(probabilities) == 0


@then("retrieve empty probabilities")
def retrieve_empty_probabilities(context):
    assert context.result.status_code == 200
    assert len(context.result.json()) == 0
