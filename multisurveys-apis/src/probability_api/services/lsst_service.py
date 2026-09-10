def classifier_name_parser(classifier_dict):
    return [{name: name.replace("_", " ").title()} for name in classifier_dict.values()]


def sort_classifiers(classifiers, priorities):
    sorted_items = sorted(
        ((k, v) for k, v in classifiers.items() if k in priorities), key=lambda item: priorities[item[0]]
    )

    return dict(sorted_items)


def priorities_by_survey(survey):
    if survey == "ztf":
        priorities_by_survey = {
            5: 0,
            4: 1,
            2: 2,
        }
    elif survey == "lsst":
        priorities_by_survey = {
            3: 0,
            1: 1,
        }
    else:
        priorities_by_survey = {}

    return priorities_by_survey
