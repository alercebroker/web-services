import json
from typing import Any, Dict

from core.models import Detection, Feature, NonDetection
from core.service import (
    _ztf_detection_to_multistream,
    _ztf_non_detection_to_multistream,
)


def get_dummy_lc() -> (list[Detection], list[NonDetection]):
    data = {}
    with open("tests/data/aaelulu.json") as file:
        data: Dict[str, Dict[str, Any]] = json.load(file)
    detections = [
        _ztf_detection_to_multistream(detection, tid="ztf")
        for detection in data["detections"]
    ]
    non_detections = [
        _ztf_non_detection_to_multistream(non_detection, tid="ztf")
        for non_detection in data["non_detections"]
    ]

    return detections, non_detections


def get_dummy_features() -> list[Feature]:
    data = {}
    with open("tests/data/aaelulu.json") as file:
        data: Dict[str, Dict[str, Any]] = json.load(file)
    features = [Feature(**feat) for feat in data["features"]]
    return features


def get_forced_mongo() -> dict[str, Any]:
    with open("tests/data/forced_mongo.json") as file:
        return json.load(file)


def get_forced_sql() -> dict[str, Any]:
    with open("tests/data/forced_photometry_202311301515.json") as file:
        return json.load(file)["forced_photometry"]
