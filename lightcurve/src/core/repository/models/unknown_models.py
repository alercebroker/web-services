from typing import Optional

from pydantic import BaseModel


class Score(BaseModel):
    detector_name: str
    detector_version: str
    category_name: str
    score: float


class Distribution(BaseModel):
    detector_name: str
    category_name: str
    distribution_name: str
    distribution_version: str
    distribution_value: float
