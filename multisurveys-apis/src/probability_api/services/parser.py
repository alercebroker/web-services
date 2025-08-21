from ..models.probability import Probability


def parse_probability(probability_data, classifiers):
    """
    Parses the probability data from the database response into a list of Probability models.

    Args:
        probability_data (list): List of SQLAlchemy model instances representing magstats.

    Returns:
        list: List of Probability models.
    """
    parsed_probability = []

    for row in probability_data:
        probability_dict = row[0].__dict__.copy()
        taxonomy_list = row[1].__dict__.copy()

        model_dict = {**probability_dict, **taxonomy_list}
        model_dict["classifier_name"] = classifiers[
            model_dict["classifier_id"]
        ]

        model_parsed = Probability(**model_dict)
        parsed_probability.append(model_parsed)

    return parsed_probability


def parse_classifiers(classifiers_data):
    """
    Parses the classifiers data from the database response into a list of classifier IDs.

    Args:
        classifiers_data (list): List of SQLAlchemy model instances representing classifiers.

    Returns:
        list: List of classifier IDs.
    """
    parsed_classifiers = {}

    for row in classifiers_data:
        model_dict = row[0].__dict__.copy()
        parsed_classifiers[model_dict["classifier_id"]] = model_dict[
            "classifier_name"
        ]

    return parsed_classifiers
