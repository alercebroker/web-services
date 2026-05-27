

def classifier_name_parser(classifier_dict):
    return [{name: name.replace("_", " ").title()} for name in classifier_dict.values()]


def sort_classifiers(classifiers):
    # priorities explanation:
    ## classifier_id:priority
    priorities = {
        3: 0,
        1: 1,
    }

    sorted_items = sorted(
        ((k, v) for k, v in classifiers.items() if k in priorities), key=lambda item: priorities[item[0]]
    )

    return dict(sorted_items)
