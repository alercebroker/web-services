from typing import Optional, Union
from pydantic import BaseModel

class MagStat(BaseModel):
    oid: int
    band: int
    stellar: bool
    corrected: bool
    ndubious: int
    dmdt_first: int
    dm_first: int
    sigmadm_first: int
    dt_first: int
    magmean: float
    magmedian: float
    magmax: float
    magmin: float
    magsigma: float
    maglast: int
    magfirst: int
    magmean_corr: float
    magmedian_corr: float
    magmax_corr: float
    magmin_corr: float
    magsigma_corr: float
    maglast_corr: float
    magfirst_corr: float
    saturation_rate: float
