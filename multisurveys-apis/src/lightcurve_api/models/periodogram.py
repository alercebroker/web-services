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

    def get_best_candidate_period(self):
        if len(self.best_periods_index) > 0:
            return round(self.periods[self.best_periods_index[0]], 7)
        elif len(self.scores) > 0 and len(self.periods) > 0:
            best_index = max(range(len(self.scores)), key=lambda i: self.scores[i])
            return round(self.periods[best_index], 7)
        else:
            raise NoPeriodError()

    def has_period(self):
        return len(self.best_periods_index) > 0

    def serialize(self):
        return {
            "periods": self.periods,
            "scores": self.scores,
            "best_periods": self.best_periods,
            "best_periods_index": self.best_periods_index,
        }
