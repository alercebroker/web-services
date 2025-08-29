from typing import Optional, Union

from pydantic import model_validator
from .lightcurve_item import BaseDetection


class ForcedPhotometryMultistream(BaseDetection):
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

    def magnitude2flux(self) -> float:
        return 0.0

    def magnitude2flux_err(self) -> float:
        return 0.0

    def flux2magnitude(self) -> float:
        return self.mag

    def flux2magnitude_err(self) -> float:
        return self.e_mag


class ZtfForcedPhotometry(BaseDetection):
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
    mjd: float
    ra: float
    dec: float
    band: int
    band_map: dict[int, str] = {1: "r", 2: "g", 3: "i"}

    @model_validator(mode="before")
    @classmethod
    def set_defaults(cls, values: dict) -> dict:
        defaults = {
            "pid": 0,
            "mag_corr": 0,
            "e_mag_corr": 0,
            "e_mag_corr_ext": 0,
        }

        for field, default_value in defaults.items():
            if field in values and values[field] is None:
                values[field] = default_value

        return values

    def magnitude2flux(self) -> float:
        return 0.0

    def magnitude2flux_err(self) -> float:
        return 0.0

    def flux2magnitude(self) -> float:
        return self.mag

    def flux2magnitude_err(self) -> float:
        return self.e_mag


class LsstForcedPhotometry(BaseDetection):
    oid: int
    measurement_id: int
    mjd: float
    ra: float
    dec: float
    band: int
    visit: int
    detector: int
    psfFlux: float
    psfFluxErr: float
    band_map: dict[int, str] = {0: "u", 1: "g", 2: "r", 3: "i", 4: "z", 5: "y"}

    @model_validator(mode="before")
    @classmethod
    def set_defaults(cls, values: dict) -> dict:
        defaults = {}

        for field, default_value in defaults.items():
            if field in values and values[field] is None:
                values[field] = default_value

        return values

    def magnitude2flux(self) -> float:
        return self.psfFlux

    def magnitude2flux_err(self) -> float:
        return self.psfFluxErr

    def flux2magnitude(self) -> float:
        return 0.0

    def flux2magnitude_err(self) -> float:
        return 0.0
