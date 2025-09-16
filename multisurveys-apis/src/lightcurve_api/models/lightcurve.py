from pydantic import BaseModel
from .lightcurve_item import (
    BaseDetection,
    BaseNonDetection,
    BaseForcedPhotometry,
)


class Lightcurve(BaseModel):
    detections: list[BaseDetection]
    non_detections: list[BaseNonDetection]
    forced_photometry: list[BaseForcedPhotometry]
