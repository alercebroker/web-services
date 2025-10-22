import math
from typing import Optional

from pydantic import model_validator
from .lightcurve_item import BaseForcedPhotometry


class ZtfForcedPhotometry(BaseForcedPhotometry):
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

    def magnitude2flux(self, total: bool) -> float:
        mag = self.mag_corr if total else self.mag
        flux = 10 ** (-0.4 * (mag - 23.9))
        return flux * 1000  # convert to nJy

    def magnitude2flux_err(self, total: bool) -> float:
        err = self.e_mag_corr if total else self.e_mag
        return abs(err) * abs(self.magnitude2flux(total))

    def flux2magnitude(self, total: bool) -> float:
        return self.mag_corr if total else self.mag

    def flux2magnitude_err(self, total: bool) -> float:
        return self.e_mag_corr if total else self.e_mag


class LsstForcedPhotometry(BaseForcedPhotometry):
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
    scienceFlux: float
    scienceFluxErr: float
    band_map: dict[int, str] = {0: "u", 1: "g", 2: "r", 3: "i", 4: "z", 5: "y"}

    @model_validator(mode="before")
    @classmethod
    def set_defaults(cls, values: dict) -> dict:
        defaults = {
            "scienceFlux": 0.0,
            "scienceFluxErr": 0.0,
        }

        for field, default_value in defaults.items():
            if field in values and values[field] is None:
                values[field] = default_value

        return values

    def magnitude2flux(self, total: bool) -> float:
        return self.scienceFlux if total else self.psfFlux

    def magnitude2flux_err(self, total: bool) -> float:
        return self.scienceFluxErr if total else self.psfFluxErr

    def flux2magnitude(self, total: bool) -> float:
        flux = self.scienceFlux if total else self.psfFlux
        return -2.5 * math.log10(flux) + 23.9

    def flux2magnitude_err(self, total: bool) -> float:
        err = self.scienceFluxErr if total else self.psfFlux
        return err
