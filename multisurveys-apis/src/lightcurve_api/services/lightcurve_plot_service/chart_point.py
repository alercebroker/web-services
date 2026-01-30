from typing import List


class ChartPoint:
    survey: str
    band: str
    x: float
    y: float
    measurement_id: str

    def __init__(self, survey: str, band: str, x: float, y: float, error: float, measurement_id: str = None):
        self.survey = survey
        self.band = band
        self.x = x
        self.y = y
        self.error = error
        self.measurement_id = measurement_id

    def point(self) -> List[float]:
        return [self.x, self.y, self.measurement_id]

    def error_bar(self, limit=1) -> List[float]:
        err = self.error if self.error <= limit else limit

        return [self.x, self.y - err, self.y + err]
