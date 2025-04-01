
from typing import Any
from ..models.detection import Detection as DetectionModel
from ..models.forcephotometry import ForcedPhotometry as ForcedPhotometryModel
from ..models.nondetection import NonDetection as NonDetectionModel

from core.exceptions import (
    ParseError,
)

def _parse_sql_detection(result: list) -> list[DetectionModel]:
    try:
        return [
            _ztf_detection_to_multistream(res[0].__dict__, tid=res[1])
            for res in result
        ]
    except Exception as e:
        raise ParseError(e, "sql detection")
    
def _ztf_detection_to_multistream(
    detection: dict[str, Any],
    tid: str,
) -> DetectionModel:
    """Converts a dictionary representing a detection in the ZTF schema
    to the Multistream schema defined in models.py. Separates every field
    that's without a correspondence in the schema into extra_fields.
    :param detection: Dictionary representing a detection.
    :param tid: Telescope id for this detection.
    :return: A Detection with the converted data."""
    fields = {
        "candid",
        "oid",
        "sid",
        "aid",
        "pid",
        "tid",
        "mjd",
        "fid",
        "ra",
        "e_ra",
        "dec",
        "e_dec",
        "magpsf",
        "sigmapsf",
        "magpsf_corr",
        "sigmapsf_corr",
        "sigmapsf_corr_ext",
        "isdiffpos",
        "corrected",
        "dubious",
        "parent_candid",
        "has_stamp",
    }

    extra_fields = {}
    for field, value in detection.items():
        if field not in fields and not field.startswith("_"):
            extra_fields[field] = value
    candid = detection.pop("candid")
    pid = detection.pop("pid")
    return DetectionModel(
        **detection,
        candid=str(candid),
        tid=tid,
        sid=tid,
        mag=detection.pop("magpsf"),
        e_mag=detection.pop("sigmapsf"),
        mag_corr=detection.pop("magpsf_corr", None),
        e_mag_corr=detection.pop("sigmapsf_corr", None),
        e_mag_corr_ext=detection.pop("sigmapsf_corr_ext", None),
        pid=pid,
        extra_fields=extra_fields,
    )


def _ztf_forced_photometry_to_multistream(
    forced_photometry: dict[str, Any],
    tid: str,
) -> ForcedPhotometryModel:
    """Converts a dictionary representing a forced photometry in the ZTF schema
    to the Multistream schema defined in models.py. Separates every field
    that's without a correspondence in the schema into extra_fields.
    :param detection: Dictionary representing a detection.
    :param tid: Telescope id for this detection.
    :return: A Detection with the converted data."""
    fields = {
        "candid",
        "oid",
        "sid",
        "aid",
        "tid",
        "mjd",
        "fid",
        "ra",
        "e_ra",
        "dec",
        "e_dec",
        "magpsf",
        "sigmapsf",
        "magpsf_corr",
        "sigmapsf_corr",
        "sigmapsf_corr_ext",
        "isdiffpos",
        "corrected",
        "dubious",
        "parent_candid",
        "has_stamp",
    }
    extra_fields = {}
    for field, value in forced_photometry.items():
        if field not in fields and not field.startswith("_"):
            extra_fields[field] = value
    return ForcedPhotometryModel(
        **forced_photometry,
        tid=tid,
        candid=forced_photometry["oid"] + str(forced_photometry["pid"]),
        extra_fields=extra_fields,
    )


def _ztf_non_detection_to_multistream(
    non_detections: dict[str, Any],
    tid: str,
) -> NonDetectionModel:
    """Converts a dictionary representing a non detection in the ZTF schema
    to the Multistream schema defined in models.py.
    :param non_detection: Dictionary representing a non_detection.
    :param tid: Telescope id for this detection.
    :return: A NonDetection with the converted data."""
    return NonDetectionModel(
        aid=non_detections.get("aid", None),
        tid=tid,
        mjd=non_detections["mjd"],
        fid=non_detections["fid"],
        oid=non_detections.get("oid", None),
        sid=non_detections.get("sid", None),
        diffmaglim=non_detections.get("diffmaglim", None),
    )