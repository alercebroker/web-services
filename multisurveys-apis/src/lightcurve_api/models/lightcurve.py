from pydantic import BaseModel

from .lightcurve_item import (
    BaseDetection,
    BaseForcedPhotometry,
    BaseNonDetection,
)


class Lightcurve(BaseModel):
    detections: list[BaseDetection]
    non_detections: list[BaseNonDetection]
    forced_photometry: list[BaseForcedPhotometry]
