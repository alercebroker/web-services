from pydantic import BaseModel

from .lightcurve_item import BaseNonDetection


class ZtfNonDetections(BaseNonDetection):
    oid: int
    survey_id: str
    band: int
    mjd: float
    diffmaglim: float
    band_map: dict[int, str] = {1: "g", 2: "r", 3: "i"}

    def get_mag(self) -> float:
        return self.diffmaglim


class ZtfNonDetectionsCsv(BaseModel):
    oid: str  # the ZTF object name (e.g. ZTF26abrmehv), not the internal master id
    survey_id: str
    mjd: float
    band: int
    band_name: str
    diffmaglim: float
