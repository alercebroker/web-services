from behave import when, given, then
from examples.features import environment
from examples.examples.api_request_example import objects_examples


range_examples = {
    "ndet": objects_examples.get_objects_in_range_of_ndet,
    "firstmjd": objects_examples.get_objects_in_range_of_first_mjd,
    "lastmjd": objects_examples.get_objects_in_range_of_last_mjd,
}

probabilities_examples = {
    "classifier": objects_examples.get_objects_by_classifier,
    "ranking": objects_examples.get_objects_by_ranking,
    "probability": objects_examples.get_objects_by_probability,
    "classifier_version": objects_examples.get_objects_by_classifier_version,
    "class": objects_examples.get_objects_by_class,
}

sorting_examples = {
    "probability": {
        "ascending": objects_examples.get_objects_sorted_by_probability_ascending,
        "descending": objects_examples.get_objects_sorted_by_probability_descending,
    },
    "ndet": {
        "ascending": objects_examples.get_objects_sorted_by_number_of_detections_ascending,
        "descending": objects_examples.get_objects_sorted_by_number_of_detections_descending,
    },
    "firstmjd": {
        "ascending": objects_examples.get_objects_sorted_by_first_detection_date_ascending,
        "descending": objects_examples.get_objects_sorted_by_first_detection_date_descending,
    },
    "lastmjd": {
        "ascending": objects_examples.get_objects_sorted_by_last_detection_date_ascending,
        "descending": objects_examples.get_objects_sorted_by_last_detection_date_descending,
    }
}


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
    environment.insert_in_database(context, "objects", _id=aid, probabilities=probabilities)


@given("objects are in the database with following parameters")
def insert_object(context):
    for row in context.table:
        kwargs = {heading: value for heading, value in zip(row.headings, row.cells)}
        if "oid" in kwargs:
            kwargs["oid"] = kwargs["oid"].split(",")
        environment.insert_in_database(context, "objects", **kwargs)


@when("request objects with identifiers {oids}")
def request_objects_by_id(context, oids):
    context.result = objects_examples.get_objects_by_identifiers(*oids.split(","))


@when("request objects with {parameter} between {minimum} and {maximum}")
def request_ranged_parameter(context, parameter, minimum, maximum):
    context.result = range_examples[parameter](minimum, maximum)


@when("request objects with {parameter} {value}")
def request_parameter_with_value(context, parameter, value):
    context.result = probabilities_examples[parameter](value)


@when("request objects sorted by {parameter} in {direction} order")
def request_sorted_objects(context, parameter, direction):
    context.result = sorting_examples[parameter][direction]()


@when("request objects within {radius} arcsec of {ra}/{dec}")
def request_conesearch(context, radius, ra, dec):
    context.result = objects_examples.get_objects_with_conesearch(ra, dec, radius)


@when("request object with AID {aid}")
def request_single_object(context, aid):
    context.result = objects_examples.get_single_object(aid)


@when("request limit values")
def request_limits(context):
    context.result = objects_examples.get_limits()


@then("ensure {field} is {value}")
def retrieve_fields(context, field, value):
    result = context.result.json()
    assert field in result
    if value == "present":  # Only used for nested subfields
        assert isinstance(result[field], list)
    elif field == "oid":
        assert result[field] == value.split(",")
    else:
        assert result[field] == value


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


@then("retrieve classes {classes} for objects {objects}, respectively, in that order")
def retrieve_classes_for_objects(context, classes, objects):
    assert context.result.status_code == 200
    classes = classes.split(",")
    objects = objects.split(",")
    for i, obj in enumerate(context.result.json()["items"]):
        assert obj["aid"] == objects[i]
        assert obj["class_name"] == classes[i]
    assert len(objects) == len(context.result.json()["items"])
    assert len(classes) == len(context.result.json()["items"])


@then("retrieve objects {objects}, in that order")
def retrieve_ordered_objects(context, objects):
    assert context.result.status_code == 200
    objects = objects.split(",")
    items = context.result.json()["items"]
    assert len(items) == len(objects)
    for expected, actual in zip(objects, items):
        assert actual["aid"] == expected


@then("retrieve {field} with value {value}")
def check_field_value(context, field, value):
    assert context.result.status_code == 200
    result = context.result.json()
    value = int(value) if "ndet" in field else float(value)
    assert result[field] == value


@then("retrieve objects {objects}")
def retrieve_unordered_classes(context, objects):
    assert context.result.status_code == 200
    objects = objects.split(",")
    for obj in context.result.json()["items"]:
        assert obj["aid"] in objects
        i = objects.index(obj["aid"])
        objects.pop(i)
    assert len(objects) == 0


@then("retrieve empty items")
def retrieve_empty_items(context):
    assert context.result.status_code == 200
    assert len(context.result.json()["items"]) == 0
