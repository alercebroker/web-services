from typing import Optional
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

    def magnitude2flux(self) -> float:
        return 0.0

    def magnitude2flux_err(self) -> float:
        return 0.0

    def flux2magnitude(self) -> float:
        return self.magpsf_corr

    def flux2magnitude_err(self) -> float:
        return self.sigmapsf_corr


class LsstDetection(BaseDetection):
    oid: int
    measurement_id: int
    parentDiaSourceId: int | None
    psfFlux: float
    psfFluxErr: float
    psfFlux_flag: int
    psfFlux_flag_edge: int
    psfFlux_flag_noGoodPixels: int
    mjd: float
    ra: float
    dec: float
    band: int
    band_map: dict[int, str] = {0: "u", 1: "g", 2: "r", 3: "i", 4: "z", 5: "y"}

    def magnitude2flux(self) -> float:
        return self.psfFlux

    def magnitude2flux_err(self) -> float:
        return self.psfFluxErr

    def flux2magnitude(self) -> float:
        return 0.0

    def flux2magnitude_err(self) -> float:
        return 0.0
