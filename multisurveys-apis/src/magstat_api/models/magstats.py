from pydantic import BaseModel
from typing import Optional

class MagStat(BaseModel):
    oid: int
    sid: int
    band: int
    stellar: bool
    corrected: bool
    ndubious: Optional[float] = None #int
    dmdt_first: Optional[float] = None #int
    dm_first: Optional[float] = None #int
    sigmadm_first: Optional[float] = None #int
    dt_first: Optional[float] = None #int
    magmean: Optional[float] = None
    magmedian: Optional[float] = None
    magmax: Optional[float] = None
    magmin: Optional[float] = None
    magsigma: Optional[float] = None
    maglast: Optional[float] = None #int
    magfirst: Optional[float] = None #int
    magmean_corr: Optional[float] = None
    magmedian_corr: Optional[float] = None
    magmax_corr: Optional[float] = None
    magmin_corr: Optional[float] = None
    magsigma_corr: Optional[float] = None
    maglast_corr: Optional[float] = None
    magfirst_corr: Optional[float] = None
    saturation_rate: Optional[float] = None