import re


def update_config_dict(config_dict):
    config_dict["FILTERS_MAP"] = {
        "filter_atlas_detections": filter_atlas_detection_non_detection,
        "filter_atlas_non_detections": filter_atlas_detection_non_detection,
        "filter_atlas_lightcurve": filter_atlas_lightcurve,
        "filter_atlas_forced_photometry": filter_atlas_detection_non_detection,
    }


def get_filters_map():
    return {
        "filter_atlas_detections": filter_atlas_detection_non_detection,
        "filter_atlas_non_detections": filter_atlas_detection_non_detection,
        "filter_atlas_lightcurve": filter_atlas_lightcurve,
        "filter_atlas_forced_photometry": filter_atlas_detection_non_detection,
    }


def filter_atlas_detection_non_detection(lc_object):
    pattern = re.compile("atlas*", re.IGNORECASE)
    if pattern.match(lc_object["tid"]):
        return False
    return True


def filter_atlas_lightcurve(lc_object):
    non_filtered_detections = []
    non_filtered_non_detections = []
    non_filtered_forced_photometry = []

    for detection in lc_object["detections"]:
        if filter_atlas_detection_non_detection(detection):
            non_filtered_detections.append(detection)
    for non_detecton in lc_object["non_detections"]:
        if filter_atlas_detection_non_detection(non_detecton):
            non_filtered_non_detections.append(non_detecton)
    for forced_photometry in lc_object["forced_photometry"]:
        if filter_atlas_detection_non_detection(forced_photometry):
            non_filtered_forced_photometry.append(forced_photometry)

    lc_object["detections"] = non_filtered_detections
    lc_object["non_detections"] = non_filtered_non_detections
    lc_object["forced_photometry"] = non_filtered_forced_photometry
    return True