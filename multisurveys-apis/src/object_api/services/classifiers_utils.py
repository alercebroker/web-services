import re


def format_classifier_name(name):
    # Replace special characters with spaces
    name = re.sub(r'[$-/:-?{-~!"^_`]', " ", name)
    # Capitalize the first letter of each word
    name = name.title()
    return name


def sort_classifiers(classifiers):
    sort_arr_classifiers = [None] * 7

    priorities = {
        "lc_classifier": 0,
        "lc_classifier_top": 1,
        "stamp_classifier": 2,
        "LC_classifier_ATAT_forced_phot": 3,
        "LC_classifier_BHRF_forced_phot": 4,
        "lc_classifier_lsst": 5,
        "rubin_stamp_1": 6,
    }

    # insertar por prioridad
    for classifier in classifiers:
        if classifier["classifier_name"] in priorities:
            index = priorities[classifier["classifier_name"]]
            sort_arr_classifiers[index] = classifier

    return sort_arr_classifiers
