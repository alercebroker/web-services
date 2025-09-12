from typing import List


class ChartPoint:
    survey: str
    band: str
    x: float
    y: float

    def __init__(self, survey: str, band: str, x: float, y: float):
        self.survey = survey
        self.band = band
        self.x = x
        self.y = y

    def point(self) -> List[float]:
        return [self.x, self.y]
