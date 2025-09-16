from .lightcurve_item import BaseNonDetection
from typing import Tuple


class ZtfNonDetections(BaseNonDetection):
    oid: int
    survey_id: str
    band: int
    mjd: float
    diffmaglim: float
    band_map: dict[int, str] = {1: "r", 2: "g", 3: "i"}

    def get_point(self) -> Tuple[float, float, float, str]:
        band = self.band_name()
        return (self.mjd, self.diffmaglim, 0, band)


class LsstNonDetection(BaseNonDetection):
    oid: int
    survey_id: str
    ccdVisitId: int
    band: int
    mjd: float
    diaNoise: float
    band_map: dict[int, str] = {0: "u", 1: "g", 2: "r", 3: "i", 4: "z", 5: "y"}

    def get_point(self) -> Tuple[float, float, float, str]:
        band = self.band_name()
        return (self.mjd, self.diaNoise, 0, band)
