import json
from typing import Any, Dict

from core.models import Detection, NonDetection
from core.service import (
    _ztf_detection_to_multistream,
    _ztf_non_detection_to_multistream,
)


def get_dummy_data() -> (list[Detection], list[NonDetection]):
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
