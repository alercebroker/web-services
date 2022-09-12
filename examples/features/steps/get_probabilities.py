from behave import when, then
from examples.features import environment
from examples.examples.api_request_example import probabilities_examples


@when("request all probabilities for {aid}")
def request_probabilities_for_classifier(context, aid):
    context.result = probabilities_examples.get_all_probabilities(aid)


@when("request probabilities for {classifier} classifier for {aid}")
def request_probabilities_for_classifier(context, classifier, aid):
    context.result = probabilities_examples.get_all_probabilities_with_classifier(aid, classifier)


@when("request probabilities for {classifier} classifier and version {version} for {aid}")
def request_probabilities_for_classifier_and_version(context, classifier, version, aid):
    context.result = probabilities_examples.get_all_probabilities_with_classifier_and_version(aid, classifier, version)


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
