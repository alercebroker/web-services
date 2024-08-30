from typing import Optional

from pydantic import BaseModel


class ObjectReduced(BaseModel):
    oid: str
    corrected: bool
    stellar: bool
    ndet: int
    meanra: float
    meandec: float
    firstmjd: float
    lastmjd: float


class MagStats(BaseModel):
    stellar: bool
    corrected: bool
    ndet: int
    ndubious: int
    magmean: float
    magmedian: float
    magmax: float
    magmin: float
    magsigma: Optional[float] = None
    maglast: float
    magfirst: float
    firstmjd: float
    lastmjd: float
    step_id_corr: str
    fid: int


class Probability(BaseModel):
    classifier_name: str
    classifier_version: str
    class_name: str
    probability: float
    ranking: int


class Taxonomy(BaseModel):
    classes: list
    classifier_name: str
    classifier_version: str


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
