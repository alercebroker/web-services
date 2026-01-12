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
