from typing import Optional, Union, List

from pydantic import BaseModel, Field

class ObjectReduced(BaseModel):

    oid :              str
    corrected :        bool
    stellar :          bool
    ndet :             int
    meanra :           float
    meandec :          float
    firstmjd :         float
    lastmjd :          float

    pass

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

    pass

class Probability(BaseModel):

    classifier_name: str 
    classifier_version: str
    class_name: str
    probability: float
    ranking: int

    pass

class Taxonomy(BaseModel):

    classes: list
    classifier_name: str
    classifier_version: str

    pass

class Score(BaseModel):

    detector_name: str
    detector_version: str
    category_name: str
    score: str

    pass

class Distribution(BaseModel):

    detector_name: str
    detector_version: str
    category_name: str
    distribution_name: str
    distribution_version: str
    distribution_value: float

    pass
