def update_filters(search_params, classes_list):
    if search_params.filter_args.classifier == "":
        return search_params
    for item in classes_list:
        if search_params.filter_args.classifier == item["classifier_name"]:
            classifier = item["classifier_id"]

        if (
            search_params.filter_args.class_name == item["class_name"]
            and search_params.filter_args.classifier == item["classifier_name"]
        ):
            class_name = item["class_id"]

    if search_params.filter_args.classifier is not None:
        search_params.filter_args.classifier = classifier

    if search_params.filter_args.class_name:
        search_params.filter_args.class_name = class_name

    return search_params


def match_and_update_item_class(items, classes_list):
    for item in items:
        for class_data in classes_list:
            if item["class_id"] == class_data["class_id"]:
                item["class_name"] = class_data["class_name"]
                item["classifier_name"] = class_data["classifier_name"]
                break

    return items
