from typing import Optional, Union

from pydantic import BaseModel


class Detection(BaseModel):
    candid: Union[str, int]
    tid: str
    sid: Optional[str] = None
    aid: Optional[str] = None
    oid: Optional[str] = None
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


class NonDetection(BaseModel):
    aid: Optional[str] = None
    tid: str
    sid: Optional[str] = None
    oid: Optional[str] = None
    mjd: float
    fid: int
    diffmaglim: Optional[float] = None
