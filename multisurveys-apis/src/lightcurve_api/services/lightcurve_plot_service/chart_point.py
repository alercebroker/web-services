from typing import List


class ChartPoint:
    survey: str
    band: str
    x: float
    y: float
    measurement_id: str
    objectid: str
    field: str
    flux_sign: str


    def __init__(self, survey: str, band: str, x: float, y: float, error: float,  flux_sign: str, measurement_id: str = None, objectid: str = None, field: str = None):
        self.survey = survey
        self.band = band
        self.x = x
        self.y = y
        self.error = error
        self.flux_sign = flux_sign
        self.measurement_id = measurement_id
        self.objectid = objectid
        self.field = field


    def point(self, limit=1) -> List[float]:
        err = self.error if self.error <= limit else limit

        return [self.x, self.y, self.measurement_id, self.objectid, self.field, err, self.flux_sign]

    def error_bar(self, limit=1) -> List[float]:
        err = self.error if self.error <= limit else limit

        return [self.x, self.y - err, self.y + err]
