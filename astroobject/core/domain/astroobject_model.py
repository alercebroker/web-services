from pydantic import BaseModel
from typing import List

class Probability(BaseModel):
    oid: str
    class_name: str
    classifier_name: str
    classifier_version: str
    probability: float
    ranking: int

class AstroObject(BaseModel):
    oid: str
    ndethist: int
    ncovhist: int
    mjdstarthist: float
    mjdendhist: float
    corrected: bool
    stellar: bool
    ndet: int
    g_r_max: float
    g_r_max_corr: float
    g_r_mean: float
    g_r_mean_corr: float
    meanra: float
    meandec: float
    sigmara: float
    sigmadec: float
    deltajd: float
    firstmjd: float
    lastmjd: float
    step_id_corr: str
    diffpos: bool
    reference_change: bool
    probabilities: List[Probability] = []