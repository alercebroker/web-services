from typing import Optional, Union, List

from pydantic import BaseModel, Field


class Detection(BaseModel):
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


class NonDetection(BaseModel):
    aid: Optional[str] = None
    tid: str
    sid: Optional[str] = None
    oid: Optional[str] = None
    mjd: float
    fid: int
    diffmaglim: Optional[float] = None

    def __hash__(self):
        return hash((self.oid, self.fid, self.mjd))

    def __eq__(self, other):
        return (self.oid, self.fid, self.mjd) == (
            other.oid,
            other.fid,
            other.mjd,
        )


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


class Feature(BaseModel):
    name: str
    value: Optional[float] = None
    fid: int
    version: str


class DataReleaseDetection(BaseModel):
    mjd: float
    mag_corr: float
    e_mag_corr_ext: float
    fid: int
    field: int
    objectid: float
    corrected: Optional[bool] = True


class LightcurveModel(BaseModel):
    mjd: List[float | int]
    brightness: List[float | int]
    e_brightness: List[float | int]
    fid: List[str]

    
class LightcurveWithPeriod(LightcurveModel):
    period: float | int

