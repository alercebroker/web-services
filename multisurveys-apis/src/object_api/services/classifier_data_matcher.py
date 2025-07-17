

def update_filters(search_params, classes_list):

    for item in classes_list:
        if search_params.filter_args.classifier == item["classifier_name"]:
            classifier = item["classifier_id"]
        
        if search_params.filter_args.class_name == item['class_name'] and search_params.filter_args.classifier == item["classifier_name"]:
            class_name = item['class_id']

    search_params.filter_args.classifier = classifier

    if search_params.filter_args.class_name:
        search_params.filter_args.class_name = class_name
        
    return search_params