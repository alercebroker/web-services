import json
from typing import List

from lightcurve_api.models.object import ApiObject
from pydantic import BaseModel

from lightcurve_api.models.detections import LsstDetection, ztfDetection
from lightcurve_api.models.force_photometry import LsstForcedPhotometry, ZtfForcedPhotometry
from lightcurve_api.models.lightcurve_item import BaseDetection, BaseForcedPhotometry, BaseNonDetection
from lightcurve_api.models.non_detections import ZtfNonDetections


class BandConfig(BaseModel):
    ztf: List[str]
    lsst: List[str]

    def all(self):
        return self.ztf + self.lsst


class ExternalSourceConfig(BaseModel):
    enabled: bool = False
    objects: list[ApiObject] = []
    selected_objects: list[str] = []


class ConfigState(BaseModel):
    bands: BandConfig = BandConfig(ztf=["g", "r", "i"], lsst=["u", "g", "r", "i", "z", "y"])
    flux: bool = False
    absolute: bool = False
    total: bool = False
    external_sources: ExternalSourceConfig = ExternalSourceConfig(enabled=False)
    fold: bool = False
    offset_bands: bool = False
    offset_num: int = 1
    offset_metric: str = "median"
    period: float = 0.05
    periodogram_enabled: bool = False

    # data types
    data_types: List[str] = ["detections", "non_detections", "forced_photometry"]

    # detections, non_detections and forced_photometry are sent as json strings
    # that need to be parsed
    detections: List[str] = []
    non_detections: List[str] = []
    forced_photometry: List[str] = []

    # additional context
    oid: str = ""
    survey_id: str = ""


def parse_detections(raw_detections: List[str]) -> List[BaseDetection]:
    detections: List[BaseDetection] = []
    for raw_det in raw_detections:
        parsed = json.loads(raw_det)
        assert "survey_id" in parsed
        if parsed["survey_id"].lower() == "ztf":
            detections.append(ztfDetection.model_validate(parsed))
        elif parsed["survey_id"].lower() == "lsst":
            detections.append(LsstDetection.model_validate(parsed))
        elif parsed["survey_id"].lower() == "ztf dr":
            continue
        else:
            raise ValueError(f"Unknown survey_id: {parsed['survey_id']}")

    return detections


def parse_non_detections(raw: List[str]) -> List[BaseNonDetection]:
    non_detections: List[BaseNonDetection] = []

    for raw_ndet in raw:
        parsed = json.loads(raw_ndet)
        assert "survey_id" in parsed
        if parsed["survey_id"].lower() == "ztf":
            non_detections.append(ZtfNonDetections.model_validate(parsed))
        else:
            raise ValueError(f"Unknown survey_id: {parsed['survey_id']}")

    return non_detections


def parse_forced_photometry(raw: List[str]) -> List[BaseForcedPhotometry]:
    forced_photometry: List[BaseForcedPhotometry] = []

    for raw_fphot in raw:
        parsed = json.loads(raw_fphot)
        assert "survey_id" in parsed
        if parsed["survey_id"].lower() == "lsst":
            forced_photometry.append(LsstForcedPhotometry.model_validate(parsed))
        elif parsed["survey_id"].lower() == "ztf":
            forced_photometry.append(ZtfForcedPhotometry.model_validate(parsed))
        else:
            raise ValueError(f"Unknown survey_id: {parsed['survey_id']}")

    return forced_photometry
