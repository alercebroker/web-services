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

    pass



