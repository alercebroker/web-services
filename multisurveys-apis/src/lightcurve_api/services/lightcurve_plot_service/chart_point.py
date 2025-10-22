from typing import List


class ChartPoint:
    survey: str
    band: str
    x: float
    y: float

    def __init__(self, survey: str, band: str, x: float, y: float, error: float):
        self.survey = survey
        self.band = band
        self.x = x
        self.y = y
        self.error = error

    def point(self) -> List[float]:
        return [self.x, self.y]

    def error_bar(self, limit=1) -> List[float]:
        err = self.error if self.error <= limit else limit

        return [self.x, self.y - err, self.y + err]
