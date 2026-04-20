def update_filters(search_params, classes_list):
    requested_classifier_name = search_params.filter_args.classifier
    requested_class_name = search_params.filter_args.class_name

    # If no classifier name is provided, return the original search_params
    if requested_classifier_name is None:
        return search_params

    # Find the corresponding IDs for the requested classifier and class names
    classifier_id = None
    class_name_id = None
    for item in classes_list:
        if requested_classifier_name == item["classifier_name"]:
            classifier_id = item["classifier_id"]

            if requested_class_name == item["class_name"]:
                class_name_id = item["class_id"]
                break

    if classifier_id is None:
        raise ValueError(f"Classifier name '{requested_classifier_name}' not found.")

    search_params.filter_args.classifier = classifier_id
    if search_params.filter_args.class_name is not None:
        search_params.filter_args.class_name = class_name_id

    return search_params

def match_and_update_item_class(items, classes_list):
    for item in items:
        matched_class = find_match_class(item, classes_list)

        if matched_class is not None:
            item["class_name"] = matched_class["class_name"]
            item["classifier_name"] = matched_class["classifier_name"]
            item["classifier_version"] = matched_class["classifier_version"]
        
        item["classifier_version"] = str(item["classifier_version"])

    return items

def find_match_class(item, classes_list):
    for class_data in classes_list:
        if check_classifier_match(item, class_data) and check_class_match(item, class_data):
            return class_data
        
    return None

def check_classifier_match(item, class_data):
    if item["classifier_id"] == class_data["classifier_id"]:
        return True
    
    return False

def check_class_match(item, class_data):
    if item["class_id"] == class_data["class_id"]:
        return True
    
    return False