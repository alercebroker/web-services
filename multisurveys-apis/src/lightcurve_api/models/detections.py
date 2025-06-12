from typing import Optional, Union
from pydantic import BaseModel, Field

class ztfDetection(BaseModel):
    oid: int
    survey_id: str
    measurement_id: int
    pid: int
    diffmaglim: float
    isdiffpos: int
    nid: int
    magpsf: float
    sigmapsf: float
    magap: float
    sigmagap: float
    distnr: float
    rb: float
    rbversion: str
    drb: float
    drbversion: str
    magapbig: float
    sigmagapbig: float
    rfid: int
    magpsf_corr: float
    sigmapsf_corr: float
    sigmapsf_corr_ext: float
    corrected: bool
    dubious: bool
    parent_candid: Optional[int] = None
    has_stamp: bool


class DetectionMultistream(BaseModel):
    candid: str
    tid: str
    sid: Optional[str] = Field(default=None)
    aid: str = Field(default=None)
    pid: int = Field(default=None)
    oid: str
    mjd: float
    fid: int
    ra: float
    e_ra: float = Field(default=None)
    dec: float
    e_dec: float = Field(default=None)
    mag: float
    e_mag: float
    mag_corr: Optional[float] = Field(default=None)
    e_mag_corr: Optional[float] = Field(default=None)
    e_mag_corr_ext: Optional[float] = Field(default=None)
    isdiffpos: Union[bool, int]
    corrected: bool
    dubious: bool = Field(default=None)
    parent_candid: Optional[int] = Field(default=None)
    has_stamp: bool = Field(default=None)
    extra_fields: dict = Field(default={})

    def __hash__(self):
        return hash(self.candid)

    def __eq__(self, other):
        return self.candid == other.candid
    