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
