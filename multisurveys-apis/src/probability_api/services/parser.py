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

    for probability, taxonomy in probability_data:
        model_dict = {
            "oid": probability.oid,
            "class_id": probability.class_id,
            "classifier_id": probability.classifier_id,
            "probability": probability.probability,
            "ranking": probability.ranking,
            "class_name": taxonomy.class_name,
            "classifier_name": classifiers[probability.classifier_id],
            "classifier_version": probability.classifier_version,
        }

        parsed_probability.append(Probability(**model_dict))

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
        parsed_classifiers[row["classifier_id"]] = row["classifier_name"]

    return parsed_classifiers


def parse_grouped_probabilities(probabilities: list) -> dict:
    """
    Parses the probabilities into a dict grouped by classifier name for display in radar.

    Args:
        probabilities (list): List of Probability models.
    Returns:
        dict: Dictionary with classifier names as keys and lists of probabilities as values.
    """
    prob_list = [d.__dict__ for d in probabilities]

    unique_classifiers = []
    prob_dict = {}

    for d in prob_list:
        if d["classifier_name"] not in unique_classifiers:
            class_name = d["classifier_name"]
            unique_classifiers.append(class_name)
            prob_dict[class_name] = []
            del d["classifier_name"]
            prob_dict[class_name].append(d)
        else:
            class_name = d["classifier_name"]
            del d["classifier_name"]
            prob_dict[class_name].append(d)
    return prob_dict
