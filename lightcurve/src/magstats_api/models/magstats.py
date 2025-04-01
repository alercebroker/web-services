from typing import Optional

from pydantic import BaseModel


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