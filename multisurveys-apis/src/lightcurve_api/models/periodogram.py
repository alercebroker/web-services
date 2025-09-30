from typing import List
from pydantic import BaseModel


class NoPeriodError(Exception):
    def __init__(self):
        super().__init__()


class Periodogram(BaseModel):
    periods: List[float]
    scores: List[float]
    best_periods: List[float]
    best_periods_index: List[int]

    def get_best_period(self):
        if len(self.best_periods_index) == 0:
            raise NoPeriodError()

        return round(self.periods[self.best_periods_index[0]], 7)

    def has_period(self):
        return len(self.best_periods_index) > 0

    def serialize(self):
        return {
            "periods": self.periods,
            "scores": self.scores,
            "best_periods": self.best_periods,
            "best_periods_index": self.best_periods_index,
        }
