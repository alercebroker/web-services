from pydantic import BaseModel, Extra
from typing import List, Union

class Probability(BaseModel):
    oid: str
    class_name: str
    classifier_name: str
    classifier_version: str
    probability: float
    ranking: int

class AstroObject(BaseModel):
    oid: str
    ndethist: Union[int, None]
    ncovhist: Union[int, None]
    mjdstarthist: Union[float, None]
    mjdendhist: Union[float, None]
    corrected: Union[bool, None]
    stellar: Union[bool, None]
    ndet: Union[int, None]
    g_r_max: Union[float, None]
    g_r_max_corr: Union[float, None]
    g_r_mean: Union[float, None]
    g_r_mean_corr: Union[float, None]
    meanra: Union[float, None]
    meandec: Union[float, None]
    sigmara: Union[float, None]
    sigmadec: Union[float, None]
    deltajd: Union[float, None]
    firstmjd: Union[float, None]
    lastmjd: Union[float, None]
    step_id_corr: Union[str, None]
    diffpos: Union[bool, None]
    reference_change: Union[bool, None]
    probabilities: List[Probability] = []