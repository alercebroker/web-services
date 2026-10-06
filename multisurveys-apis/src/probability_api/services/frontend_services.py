from src.probability_api.services.lsst_service import priorities_by_survey
from ..models.probability import ObjectProbability


def get_classifiers_names_for_front(object: ObjectProbability, group_prob: dict) -> list:
    priorities = priorities_by_survey(object.survey)
    order_classifiers = order_classifiers_front(priorities, object.classifiers)
    filter_classifiers = filter_classifiers_by_probabilities(order_classifiers, group_prob)
    classifiers_names = prepare_classifier_names(filter_classifiers)

    return classifiers_names


def order_classifiers_front(priorities: dict, classifier_list: list) -> list:
    """
    Order classifiers based on the priorities defined in the priorities dictionary.
    """

    classifiers_sorted = [None] * 10
    for priority, index in priorities.items():
        if priority in classifier_list:
            classifiers_sorted[index] = classifier_list[priority]

    return [classifier for classifier in classifiers_sorted if classifier is not None]


def filter_classifiers_by_probabilities(classifiers: list, probabilites: dict) -> list:
    """
    Filter classifiers based on the probabilities return by the query.
    """

    return [c for c in classifiers if c in probabilites.keys()]


def prepare_classifier_names(classifiers: list) -> list:
    result = []
    for classifier_name in classifiers:
        parsed_name = classifier_name.replace("_", " ").title()
        aux_dict = {classifier_name: parsed_name}
        result.append(aux_dict)

    return result
