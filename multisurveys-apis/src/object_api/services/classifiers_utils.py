import re


def format_classifier_name(name):
    """
    Format the classifier name by replacing special characters with spaces and capitalizing each word.
    """

    name = re.sub(r'[$-/:-?{-~!"^_`]', " ", name)
    name = name.title()
    return name


def sort_classifiers(classifiers, survey_id):
    """
    Sort classifiers based on hard-coded priorities by survey.

    input: classifiers - list of classifier dictionaries, each containing a "classifier_id" key.
    input: survey_id - string representing the survey ID.
    """

    sort_arr_classifiers = [None] * 8
    priorities = get_priorities_by_survey(survey_id)

    for classifier in classifiers:
        if classifier["classifier_id"] in priorities:
            index = priorities[classifier["classifier_id"]]
            sort_arr_classifiers[index] = classifier

    return sort_arr_classifiers


def get_priorities_by_survey(survey_id):
    """
    Get the hard-coded priorities for classifiers based on the survey ID.

    input: survey_id - string representing the survey ID.
    output: dictionary mapping classifier IDs to their respective priorities.
    """

    if survey_id == "ztf":
        return {
            5: 0,
            4: 1,
            2: 2,
        }
    if survey_id == "lsst":
        return {
            3: 0,
            1: 1,
        }

    return {}