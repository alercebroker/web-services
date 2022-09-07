import requests
from behave import when, given, then
from examples.features import environment


@given("following classifiers are in database")
def insert_classifiers(context):
    for row in context.table:
        classifier = {
            "classifier_name": row["classifier_name"],
            "classifier_version": row["classifier_version"],
            "classes": row["classes"].split(","),
        }
        environment.insert_in_database(context, "taxonomy", **classifier)


@when("request all classifiers")
def request_all_classifiers(context):
    url = f"{environment.BASE_URL}/classifiers"

    context.result = requests.get(url)


@when("request classes for classifier {classifier} and version {version}")
def request_all_classifiers(context, classifier, version):
    url = f"{environment.BASE_URL}/classifiers/{classifier}/{version}/classes"

    context.result = requests.get(url)


@then("retrieve following classifiers")
def retrieve_classifiers(context):
    assert context.result.status_code == 200
    classifiers, versions, classes = [], [], []
    for row in context.table:
        classifiers.append(row["classifier_name"])
        versions.append(row["classifier_version"])
        classes.append(row["classes"].split(","))
    for classifier in context.result.json():
        idx, = [i for i, (cls, ver) in enumerate(zip(classifiers, versions))
                if classifier["classifier_name"] in cls and classifier["classifier_version"] in ver]
        assert classifier["classes"] == classes[idx]
        classifiers.pop(idx)
        versions.pop(idx)
        classes.pop(idx)
    assert len(classifiers) == 0
    assert len(versions) == 0
    assert len(classes) == 0


@then("retrieve classes with names {classes}")
def retrieve_classes(context, classes):
    assert context.result.status_code == 200
    classes = classes.split(",")
    for result in context.result.json():
        assert result["name"] in classes
        classes.pop(classes.index(result["name"]))
    assert len(classes) == 0

