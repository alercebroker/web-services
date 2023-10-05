from pydantic import BaseModel
from typing import Optional, Union


class Detection(BaseModel):
    candid: Union[str, int]
    tid: str
    sid: Optional[str] = None
    aid: Optional[str] = None
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
    isdiffpos: bool
    corrected: bool
    dubious: bool
    parent_candid: Optional[int] = None
    has_stamp: bool
    extra_fields: Optional[dict] = {}

    def __hash__(self):
        return hash(str(self.candid))
    def __eq__(self, other):
        return str(self.candid)==str(other.candid)


class NonDetection(BaseModel):
    aid: Optional[str] = None
    tid: str
    sid: Optional[str] = None
    oid: str
    mjd: float
    fid: int
    diffmaglim: Optional[float] = None

    def __hash__(self):
        return hash((self.oid, self.fid, self.mjd))
    def __eq__(self, other):
        return (self.oid, self.fid, self.mjd) ==\
                (other.oid, other.fid, other.mjd)
