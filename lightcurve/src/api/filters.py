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
    if lc_object["tid"].lower().startswith("atlas"):
        return False
    return True


def filter_atlas_lightcurve(lc_object):
    detections = []
    non_detections = []

    for detection in lc_object["detections"]:
        if filter_atlas_detection_non_detection(detection):
            detections.append(detection)
    for non_detecton in lc_object["non_detections"]:
        if filter_atlas_detection_non_detection(non_detecton):
            non_detections.append(non_detecton)

    lc_object["detections"] = detections
    print("filter", lc_object["detections"])
    lc_object["non_detections"] = non_detections
    return True
