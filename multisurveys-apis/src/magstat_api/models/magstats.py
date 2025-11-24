from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MagStat(BaseModel):
    oid: int
    sid: int
    band: int
    stellar: Optional[bool] = None
    corrected: Optional[bool] = None
    ndubious: Optional[int] = None
    dmdt_first: Optional[int] = None
    dm_first: Optional[int] = None
    sigmadm_first: Optional[int] = None
    dt_first: Optional[int] = None
    magmean: Optional[float] = None
    magmedian: Optional[float] = None
    magmax: Optional[float] = None
    magmin: Optional[float] = None
    magsigma: Optional[float] = None
    maglast: Optional[int] = None
    magfirst: Optional[int] = None
    magmean_corr: Optional[float] = None
    magmedian_corr: Optional[float] = None
    magmax_corr: Optional[float] = None
    magmin_corr: Optional[float] = None
    magsigma_corr: Optional[float] = None
    maglast_corr: Optional[float] = None
    magfirst_corr: Optional[float] = None
    step_id_corr: Optional[str] = None
    saturation_rate: Optional[float] = None
    updated_date: Optional[datetime] = None
