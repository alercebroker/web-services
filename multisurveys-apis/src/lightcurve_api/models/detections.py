import math
from typing import Optional

from pydantic import model_validator
from .lightcurve_item import BaseDetection


class ztfDetection(BaseDetection):
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
    band_map: dict[int, str] = {1: "r", 2: "g", 3: "i"}

    @model_validator(mode="before")
    @classmethod
    def set_defaults(cls, values: dict) -> dict:
        defaults = {
            "pid": 0,
            "diffmaglim": 0,
            "isdiffpos": 0,
            "nid": 0,
            "magap": 0,
            "sigmagap": 0,
            "distnr": 0,
            "rb": 0,
            "rbversion": "0",
            "magapbig": 0,
            "sigmagapbig": 0,
            "magpsf_corr": 0,
            "sigmapsf_corr": 0,
            "sigmapsf_corr_ext": 0,
            "corrected": False,
            "dubious": False,
            "has_stamp": False,
        }

        for field, default_value in defaults.items():
            if field in values and values[field] is None:
                values[field] = default_value

        return values

    def magnitude2flux(self, difference: bool) -> float:
        mag = self.magpsf if difference else self.magpsf_corr
        partially_converted = 10 ** (-0.4 * (mag - 23.9))
        return partially_converted * self.isdiffpos if difference else partially_converted

    def magnitude2flux_err(self, difference: bool) -> float:
        err = self.sigmapsf if difference else self.sigmapsf_corr_ext
        return abs(err) * abs(self.magnitude2flux(difference))

    def flux2magnitude(self, difference: bool) -> float:
        return self.magpsf if difference else self.magpsf_corr

    def flux2magnitude_err(self, difference: bool) -> float:
        return self.sigmapsf if difference else self.sigmapsf_corr_ext


class LsstDetection(BaseDetection):
    oid: int
    survey_id: str
    measurement_id: int
    parentDiaSourceId: int | None
    psfFlux: float
    psfFluxErr: float
    psfFlux_flag: int
    psfFlux_flag_edge: int
    psfFlux_flag_noGoodPixels: int
    scienceFlux: float
    scienceFluxErr: float
    mjd: float
    ra: float
    dec: float
    band: int
    band_map: dict[int, str] = {0: "u", 1: "g", 2: "r", 3: "i", 4: "z", 5: "y"}

    @model_validator(mode="before")
    @classmethod
    def set_defaults(cls, values: dict) -> dict:
        defaults = {
            "parentDiaSourceId": -1,
            "psfFlux": 0.0,
            "psfFluxErr": 0.0,
            "psfFlux_flag": 0,
            "psfFlux_flag_edge": 0,
            "psfFlux_flag_noGoodPixels": 0,
            "scienceFlux": 0.0,
            "scienceFluxErr": 0.0,
            "mjd": 0.0,
            "ra": 0.0,
            "dec": 0.0,
            "band": 0,
        }

        for field, default_value in defaults.items():
            if field in values and values[field] is None:
                values[field] = default_value

        return values

    def magnitude2flux(self, difference: bool) -> float:
        return self.psfFlux if difference else self.scienceFlux

    def magnitude2flux_err(self, difference: bool) -> float:
        return self.psfFluxErr if difference else self.scienceFluxErr

    def flux2magnitude(self, difference: bool) -> float:
        mag = self.psfFlux if difference else self.scienceFlux
        return -2.5 * math.log10(mag) + 23.9

    def flux2magnitude_err(self, difference: bool) -> float:
        err = self.psfFluxErr if difference else self.scienceFluxErr
        return err  # TODO: compute actual err
