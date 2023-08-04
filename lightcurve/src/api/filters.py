def update_config_dict(config_dict):
    config_dict["FILTERS_MAP"] = {
        "filter_atlas_detections": filter_atlas_detection_non_detection,
        "filter_atlas_non_detections": filter_atlas_detection_non_detection,
        "filter_atlas_lightcurve": filter_atlas_lightcurve,
    }


def get_filters_map():
    return {
        "filter_atlas_detections": filter_atlas_detection_non_detection,
        "filter_atlas_non_detections": filter_atlas_detection_non_detection,
        "filter_atlas_lightcurve": filter_atlas_lightcurve,
    }


def filter_atlas_detection_non_detection(lc_object):
    if lc_object["tid"] == "atlas":
        return False
    return True


def filter_atlas_lightcurve(lc_object):
    non_filtered_detections = []
    non_filtered_non_detections = []

    for detection in lc_object["detections"]:
        if filter_atlas_detection_non_detection(detection):
            non_filtered_detections.append(detection)
    for non_detecton in lc_object["non_detections"]:
        if filter_atlas_detection_non_detection(non_detecton):
            non_filtered_non_detections.append(non_detecton)

    if (
        len(non_filtered_detections) > 0
        or len(non_filtered_non_detections) > 0
    ):
        lc_object["detections"] = non_filtered_detections
        lc_object["non_detections"] = non_filtered_non_detections
        return True
    else:
        return False