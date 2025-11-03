def probability_parser(prob_list_raw: list) -> dict:

    prob_list = [d.__dict__ for d in prob_list_raw]

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
