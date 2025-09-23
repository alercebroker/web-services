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
        """Set default values for None fields to ensure data consistency."""

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

    def magnitude2flux(self, total: bool) -> float:
        """Convert magnitude to flux.

        Args:
            total: Whether to use corrected magnitude (True) or uncorrected (False)

        Returns:
            Calculated flux value
        """

        mag = self.magpsf_corr if total else self.magpsf
        partially_converted = 10 ** (-0.4 * (mag - 23.9))
        return partially_converted if total else partially_converted * self.isdiffpos

    def magnitude2flux_err(self, total: bool) -> float:
        """Calculate flux error from magnitude error.

        Args:
            total: Whether to use corrected error (True) or uncorrected (False)

        Returns:
            Calculated flux error
        """
        err = self.sigmapsf_corr_ext if total else self.sigmapsf
        return abs(err) * abs(self.magnitude2flux(total))

    def flux2magnitude(self, total: bool) -> float:
        """Convert flux to magnitude.

        Args:
            total: Whether to use corrected flux (True) or uncorrected (False)

        Returns:
            Calculated magnitude value
        """

        return self.magpsf_corr if total else self.magpsf

    def flux2magnitude_err(self, total: bool) -> float:
        """Get magnitude error from flux error.

        Args:
            total: Whether to use corrected error (True) or uncorrected (False)

        Returns:
            Magnitude error value
        """
        return self.sigmapsf_corr_ext if total else self.sigmapsf


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

    def magnitude2flux(self, total: bool) -> float:
        """Convert magnitude to flux.

        Args:
            total: Whether to use corrected magnitude (True) or uncorrected (False)

        Returns:
            Calculated flux value
        """
        return self.scienceFlux if total else self.psfFlux

    def magnitude2flux_err(self, total: bool) -> float:
        """Calculate flux error from magnitude error.

        Args:
            total: Whether to use corrected error (True) or uncorrected (False)

        Returns:
            Calculated flux error
        """
        return self.scienceFluxErr if total else self.psfFluxErr

    def flux2magnitude(self, total: bool) -> float:
        """Convert flux to magnitude.

        Args:
            total: Whether to use corrected flux (True) or uncorrected (False)

        Returns:
            Calculated magnitude value
        """
        mag = self.scienceFlux if total else self.psfFlux
        return -2.5 * math.log10(mag) + 23.9

    def flux2magnitude_err(self, total: bool) -> float:
        """Get magnitude error from flux error.

        Args:
            total: Whether to use corrected error (True) or uncorrected (False)

        Returns:
            Magnitude error value
        """
        return self.scienceFluxErr if total else self.psfFluxErr


class ZtfDataReleaseDetection(BaseDetection):
    mjd: float
    survey_id: str = "ztf dr"
    mag_corr: float
    e_mag_corr_ext: float
    fid: int
    field: int
    objectid: float
    corrected: bool = True
    band_map: dict[int, str] = {1: "r", 2: "g", 3: "i"}

    def magnitude2flux(self, total: bool) -> float:
        """Convert magnitude to flux.

        Args:
            total: Total is always used for ZTF DR

        Returns:
            Calculated flux value
        """
        return 10 ** (-0.4 * (self.mag_corr - 23.9))

    def magnitude2flux_err(self, total: bool) -> float:
        """Calculate flux error from magnitude error.

        Args:
            total: Total is always used for ZTF DR

        Returns:
            Calculated flux error
        """
        return abs(self.e_mag_corr_ext) * abs(self.magnitude2flux(total))

    def flux2magnitude(self, total: bool) -> float:
        """Convert flux to magnitude.

        Args:
            total: Total is always used for ZTF DR

        Returns:
            Calculated magnitude value
        """
        return self.mag_corr

    def flux2magnitude_err(self, total: bool) -> float:
        """Get magnitude error from flux error.

        Args:
            total: Total is always used for ZTF DR

        Returns:
            Magnitude error value
        """
        return self.e_mag_corr_ext
