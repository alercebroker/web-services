from ..models.classifiers import Classifiers

import pprint
def parse_classifiers(classifier_data: list) -> list:
    """
    Parses the classifiers data from the database response into a list of Classifiers models.

    Args:
        classifier_dat (list): List of SQLAlchemy model instances representing classifiers.

    Returns:
        list: List of Classifiers models.
    """
    grouped_classifiers = {}
    parsed_classifiers = []

    for row in classifier_data:
        classifier_dict = row[0].__dict__.copy()
        taxonomy_dict = row[1].__dict__.copy()
        classifier_name = classifier_dict["classifier_name"]
        class_name = taxonomy_dict["class_name"]

        if classifier_name not in grouped_classifiers.keys():
            grouped_classifiers[classifier_name] = {
                "classifier_name": classifier_name,
                "classifier_version": classifier_dict["classifier_version"],
                "classes": [class_name],
            }
        else:
            grouped_classifiers[classifier_name]["classes"].append(class_name)

    for model_dict in grouped_classifiers.values():
        model_parsed = Classifiers(**model_dict)
        parsed_classifiers.append(model_parsed)

    return parsed_classifiers
