from typing import Optional, Union
from pydantic import BaseModel


class ForcedPhotometryMultistream(BaseModel):
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



class ZtfForcedPhotometry(BaseModel):
    oid: int
    survey_id: str
    measurement_id: int
    pid: int
    mag: float
    e_mag: float
    mag_corr: float
    e_mag_corr: float
    e_mag_corr_ext: float
    isdiffpos: int
    corrected: bool
    dubious: bool
    parent_candid: Optional[int] = None
    has_stamp: bool
    field: int
    rcid: int
    rfid: int
    sciinpseeing: float
    scibckgnd: float
    scisigpix: float
    magzpsci: float
    magzpsciunc: float
    magzpscirms: float
    clrcoeff: float
    clrcounc: float
    exptime: float
    adpctdif1: float
    adpctdif2: float
    diffmaglim: float
    programid: int
    procstatus: str
    distnr: float
    ranr: float
    decnr: float
    magnr: float
    sigmagnr: float
    chinr: float
    sharpnr: float


class LsstForcedPhotometry(BaseModel):
    oid: int
    measurement_id: int
    visit_id: int
    detector_id: int
    psf_flux: float
    psf_flux_err: float