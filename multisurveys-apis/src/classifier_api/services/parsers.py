from ..models.classifiers import Classifiers


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

    # By id: a name isn't unique (several versions, or the same model for ZTF and LSST)
    for row in classifier_data:
        classifier_id = row["classifier_id"]
        class_name = row["class_name"]

        if classifier_id not in grouped_classifiers:
            grouped_classifiers[classifier_id] = {
                "classifier_name": row["classifier_name"],
                "classifier_version": row["classifier_version"],
                "classes": [class_name],
                "classifier_id": classifier_id,
                "survey_id": row["tid"],
            }
        else:
            grouped_classifiers[classifier_id]["classes"].append(class_name)

    for model_dict in grouped_classifiers.values():
        model_parsed = Classifiers(**model_dict)
        parsed_classifiers.append(model_parsed)

    return parsed_classifiers
