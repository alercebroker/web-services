from typing import List, Optional, Union
from pydantic import BaseModel, Field


class ForcedPhotometry(BaseModel):
    candid: str
    tid: str
    sid: Optional[str] = None
    aid: Optional[str] = None
    pid: int
    oid: str
    mjd: float
    fid: int
    ra: float
    e_ra: Optional[float] = None
    dec: float
    e_dec: Optional[float] = None
    mag: float
    e_mag: float
    mag_corr: Optional[float] = None
    e_mag_corr: Optional[float] = None
    e_mag_corr_ext: Optional[float] = None
    isdiffpos: Union[bool, int]
    corrected: bool
    dubious: bool
    parent_candid: Optional[int] = None
    has_stamp: Optional[bool] = None
    extra_fields: Optional[dict] = {}

    def __hash__(self):
        return hash(str(f"{self.oid}_{self.pid}"))

    def __eq__(self, other):
        return self.oid == other.oid and self.pid == other.pid
