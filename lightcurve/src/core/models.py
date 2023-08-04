from pydantic import BaseModel
from typing import Optional, Union


class Detection(BaseModel):
    candid: Union[str, int]
    oid: str
    tid: str
    mjd: float
    fid: int
    pid: float
    diffmaglim: Optional[float] = None
    isdiffpos: int
    nid: Optional[int] = None
    ra: float
    dec: float
    magpsf: float
    sigmapsf: float
    magap: Optional[float] = None
    sigmagap: Optional[float] = None
    distnr: Optional[float] = None
    rb: Optional[float] = None
    rbversion: Optional[str] = None
    drb: Optional[float] = None
    drbversion: Optional[str] = None
    magapbig: Optional[float] = None
    sigmagapbig: Optional[float] = None
    rfid: Optional[int] = None
    magpsf_corr: Optional[float] = None
    sigmapsf_corr: Optional[float] = None
    sigmapsf_corr_ext: Optional[float] = None
    corrected: bool
    dubious: bool
    parent_candid: Optional[int] = None
    has_stamp: bool
    step_id_corr: str


class NonDetection(BaseModel):
    oid: str
    fid: int
    tid: str
    mjd: float
    diffmaglim: Optional[float] = None
