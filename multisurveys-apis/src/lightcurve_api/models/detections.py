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
    drb: float | None = None
    drbversion: str | None = None
    magapbig: float
    sigmagapbig: float
    rfid: int | None = None
    magpsf_corr: float
    sigmapsf_corr: float
    sigmapsf_corr_ext: float
    corrected: bool
    dubious: bool
    parent_candid: Optional[int] = None
    has_stamp: bool
    mjd: float
    ra: float
    dec: float
    band: int


class LsstDetection(BaseModel):
    oid: int
    measurement_id: int
    parentDiaSourceId: int
    psfFlux: float
    psfFluxErr: float
    psfFlux_flag: bool
    psfFlux_flag_edge: bool
    psfFlux_flag_noGoodPixels: bool
    mjd: float
    ra: float
    dec: float
    band: int