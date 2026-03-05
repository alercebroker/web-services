import re


def format_classifier_name(name):
    # Replace special characters with spaces
    name = re.sub(r'[$-/:-?{-~!"^_`]', " ", name)
    # Capitalize the first letter of each word
    name = name.title()
    return name


def sort_classifiers(classifiers):
    sort_arr_classifiers = [None] * 8
    # priorities explanation: 
    ## classifier_id:priority
    priorities = {
        1: 0,
    }

    # insertar por prioridad
    for classifier in classifiers:
        if classifier["classifier_id"] in priorities:
            index = priorities[classifier["classifier_id"]]
            sort_arr_classifiers[index] = classifier

    return sort_arr_classifiers
