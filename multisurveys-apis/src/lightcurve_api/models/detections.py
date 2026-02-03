import math
import traceback
import pprint
from typing import Dict, Optional

from pydantic import BaseModel, computed_field, model_validator
from toolz.functoolz import return_none
from .lightcurve_item import BaseDetection
from astropy.coordinates import Distance
import astropy.units as u

REDSHIFT = (
    0.23  # TODO: Instead of a hardcoded REDSHIFT, use the redshift from the object
)



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
    band_map: dict[int, str] = {1: "g", 2: "r", 3: "i"}
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

    def magnitude2flux(self, total: bool, absolute: bool) -> float:
        """Convert magnitude to flux.

        Args:
            total: Whether to use corrected magnitude (True) or uncorrected (False)
            absolute: Whether to use absolute magnitude (True) or apparent magnitude (False)

        Returns:
            Calculated flux value
        """
        d = Distance(REDSHIFT, unit=u.lyr)  # type: ignore
        mag = self.magpsf_corr if total else self.magpsf
        # m = M + mu; where M is absolute magnitude
        mag = mag - d.distmod.value if absolute else mag
        partially_converted = 10 ** (-0.4 * (mag - 23.9))
        flux = partially_converted if total else partially_converted * self.isdiffpos
        return flux * 1000  # convert to nJy

    def magnitude2flux_err(self, total: bool, absolute: bool) -> float:
        """Calculate flux error from magnitude error.

        Args:
            total: Whether to use corrected error (True) or uncorrected (False)

        Returns:
            Calculated flux error
        """
        err = self.sigmapsf_corr_ext if total else self.sigmapsf
        return abs(err) * abs(self.magnitude2flux(total, absolute))

    def flux2magnitude(self, total: bool, absolute: bool) -> float:
        """Convert flux to magnitude.

        Args:
            total: Whether to use corrected flux (True) or uncorrected (False)

        Returns:
            Calculated magnitude value
        """
        d = Distance(REDSHIFT, unit=u.lyr)  # type: ignore
        mag = self.magpsf_corr if total else self.magpsf
        return mag - d.distmod.value if absolute else mag

    def flux2magnitude_err(self, total: bool, absolute: bool) -> float:
        """Get magnitude error from flux error.

        Args:
            total: Whether to use corrected error (True) or uncorrected (False)

        Returns:
            Magnitude error value
        """
        return self.sigmapsf_corr_ext if total else self.sigmapsf

    def flux_sign(self, total: bool, absolute: bool) -> str:
        return str(self.isdiffpos)


class LsstDetection(BaseDetection):
    oid: int
    survey_id: str
    measurement_id: int
    parentDiaSourceId: int | None
    diaObjectId: int | None
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
    band_map: dict[int, str] = {6: "u", 1: "g", 2: "r", 3: "i", 4: "z", 5: "y"}
    has_stamp: bool
    visit: int
    detector: int
    ssObjectId: int | None = None
    raErr: float | None = None
    decErr: float | None = None
    ra_dec_Cov: float | None = None
    x: float
    xErr: float | None = None
    y: float
    yErr: float | None = None
    centroid_flag: bool | None = None
    apFlux: float | None = None
    apFluxErr: float | None = None
    apFlux_flag: bool | None = None
    apFlux_flag_apertureTruncated: bool | None = None
    isNegative: bool | None = None
    snr: float | None = None
    psfLnL: float | None = None
    psfChi2: float | None = None
    psfNdata: int | None = None
    trailFlux: float | None = None
    trailFluxErr: float | None = None
    trailRa: float | None = None
    trailRaErr: float | None = None
    trailDec: float | None = None
    trailDecErr: float | None = None
    trailLength: float | None = None
    trailLengthErr: float | None = None
    trailAngle: float | None = None
    trailAngleErr: float | None = None
    trailChi2: float | None = None
    trailNdata: int | None = None
    trail_flag_edge: bool | None = None
    dipoleMeanFlux: float | None = None
    dipoleMeanFluxErr: float | None = None
    dipoleFluxDiff: float | None = None
    dipoleFluxDiffErr: float | None = None
    dipoleLength: float | None = None
    dipoleAngle: float | None = None
    dipoleChi2: float | None = None
    dipoleNdata: int | None = None
    forced_PsfFlux_flag: bool | None = None
    forced_PsfFlux_flag_edge: bool | None = None
    forced_PsfFlux_flag_noGoodPixels: bool | None = None
    templateFlux: float | None = None
    templateFluxErr: float | None = None
    ixx: float | None = None
    iyy: float | None = None
    ixy: float | None = None
    ixxPSF: float | None = None
    iyyPSF: float | None = None
    ixyPSF: float | None = None
    shape_flag: bool | None = None
    shape_flag_no_pixels: bool | None = None
    shape_flag_not_contained: bool | None = None
    shape_flag_parent_source: bool | None = None
    extendedness: float | None = None
    reliability: float | None = None
    isDipole: bool | None = None
    dipoleFitAttempted: bool | None = None
    timeProcessedMjdTai: float
    timeWithdrawnMjdTai: float | None = None
    bboxSize: int | None = None
    pixelFlags: bool | None = None
    pixelFlags_bad: bool | None = None
    pixelFlags_cr: bool | None = None
    pixelFlags_crCenter: bool | None = None
    pixelFlags_edge: bool | None = None
    pixelFlags_nodata: bool | None = None
    pixelFlags_nodataCenter: bool | None = None
    pixelFlags_interpolated: bool | None = None
    pixelFlags_interpolatedCenter: bool | None = None
    pixelFlags_offimage: bool | None = None
    pixelFlags_saturated: bool | None = None
    pixelFlags_saturatedCenter: bool | None = None
    pixelFlags_suspect: bool | None = None
    pixelFlags_suspectCenter: bool | None = None
    pixelFlags_streak: bool | None = None
    pixelFlags_streakCenter: bool | None = None
    pixelFlags_injected: bool | None = None
    pixelFlags_injectedCenter: bool | None = None
    pixelFlags_injected_template: bool | None = None
    pixelFlags_injected_templateCenter: bool | None = None
    glint_trail: bool | None = None

    @model_validator(mode="before")
    @classmethod
    def set_defaults(cls, values: dict) -> dict:
        defaults = {
            "parentDiaSourceId": -1,
            "diaObjectId": -1,
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

    def magnitude2flux(self, total: bool, absolute: bool) -> float:
        """Convert magnitude to flux.

        Args:
            total: Whether to use corrected magnitude (True) or uncorrected (False)

        Returns:
            Calculated flux value
        """
        flux = self.scienceFlux if total else self.psfFlux

        if absolute:
            d = Distance(REDSHIFT, unit=u.lyr)  # type: ignore
            flux = self.scienceFlux if total else self.psfFlux
            absflux = math.fabs(flux)
            sign = absflux / flux
            magnitude = 31.4 - 2.5 * math.log10(absflux) - d.distmod.value
            flux = 10**(-(magnitude - 31.4) / 2.5) * sign

        return flux


    def magnitude2flux_err(self, total: bool, absolute: bool) -> float:
        """Calculate flux error from magnitude error.

        Args:
            total: Whether to use corrected error (True) or uncorrected (False)

        Returns:
            Calculated flux error
        """

        flux = self.magnitude2flux(total, absolute)
        magnitude_error = self.flux2magnitude_err(total, absolute)

        return math.log(10.0)  * math.fabs(flux) / 2.5 * magnitude_error        
        
        
    def flux2magnitude(self, total: bool, absolute: bool) -> float:
        """Convert flux to magnitude.

        Args:
            total: Whether to use corrected flux (True) or uncorrected (False)

        Returns:
            Calculated magnitude value
        """
        try:
            d = Distance(REDSHIFT, unit=u.lyr)  # type: ignore
            flux = self.scienceFlux if total else self.psfFlux

            if flux < 0:
                flux = math.fabs(flux)
                if total == True:
                    flux = flux * -1


            if flux < 0:
                raise ValueError("Flux no puede ser negativo para cálculo de magnitud")
                
            mag = 31.4 - 2.5 * math.log10(flux)

        except ValueError as e:
            traceback.print_exc()
            return 0

        return mag - d.distmod.value if absolute else mag

    def flux2magnitude_err(self, total: bool, absolute: bool) -> float:
        """Get magnitude error from flux error.

        Args:
            total: Whether to use corrected error (True) or uncorrected (False)

        Returns:
            Magnitude error value
        """
        try:
            flux = self.scienceFlux if total else self.psfFlux
            flux_err = self.scienceFluxErr if total else self.psfFluxErr

            if flux < 0:
                flux = math.fabs(flux)
            
            if flux_err < 0: 
                flux_err = math.fabs(flux_err)
            
            magnitude_error = (2.5 * flux_err) / (math.log(10.0) * flux)

        except ValueError as e:
            traceback.print_exc()
            return 0


        return magnitude_error

    def flux_sign(self, total: bool, absolute: bool) -> str:
        flux = self.scienceFlux if total else self.psfFlux

        return '-' if flux < 0 else '+'


class ZtfDataReleaseDetection(BaseDetection):
    mjd: float
    survey_id: str = "ztf dr"
    mag_corr: float
    e_mag_corr_ext: float
    fid: int
    field: int
    objectid: float
    corrected: bool = True
    band_map: dict[int, str] = {1: "g", 2: "r", 3: "i"}

    def magnitude2flux(self, total: bool, absolute: bool) -> float:
        """Convert magnitude to flux.

        Args:
            total: Total is always used for ZTF DR

        Returns:
            Calculated flux value
        """
        d = Distance(REDSHIFT, unit=u.lyr)  # type: ignore
        flux = 10 ** (-0.4 * (self.mag_corr - 23.9))
        flux = flux - d.distmod.value if absolute else flux
        return flux * 1000  # convert to nJy

    def magnitude2flux_err(self, total: bool, absolute: bool) -> float:
        """Calculate flux error from magnitude error.

        Args:
            total: Total is always used for ZTF DR

        Returns:
            Calculated flux error
        """
        return abs(self.e_mag_corr_ext) * abs(self.magnitude2flux(total, absolute))

    def flux2magnitude(self, total: bool, absolute: bool) -> float:
        """Convert flux to magnitude.

        Args:
            total: Total is always used for ZTF DR

        Returns:
            Calculated magnitude value
        """
        d = Distance(REDSHIFT, unit=u.lyr)  # type: ignore
        return self.mag_corr - d.distmod.value if absolute else self.mag_corr

    def flux2magnitude_err(self, total: bool, absolute: bool) -> float:
        """Get magnitude error from flux error.

        Args:
            total: Total is always used for ZTF DR

        Returns:
            Magnitude error value
        """
        return self.e_mag_corr_ext

    def flux_sign(self, total: bool, absolute: bool) -> str:
        flux = self.magnitude2flux(total, absolute)

        return '-' if flux < 0 else '+'


class ZTFDetectionCSV(BaseModel):
    oid: int
    survey_id: str
    measurement_id: int
    has_stamp: bool
    mjd: float
    ra: float  # Validación de rango
    dec: float
    band: int
    @model_validator(mode="before")
    @classmethod
    def set_defaults(cls, values: dict) -> dict:
        """Set default values for None fields to ensure data consistency."""

        defaults = {
            "has_stamp": False,
        }

        for field, default_value in defaults.items():
            if field in values and values[field] is None:
                values[field] = default_value

        return values



class LsstDetectionCsv(BaseModel):
    oid: int
    measurement_id: int
    mjd: float 
    ra: float  
    dec: float  
    band: int | None = None
    band_name: str | None = None
    psfFlux: float | None = None
    psfFluxErr: float | None = None
    scienceFlux: float | None = None
    scienceFluxErr: float | None = None
    snr: float | None = None
    visit: int
    detector: int
    diaObjectId: int | None = None
    ssObjectId: int | None = None
    parentDiaSourceId: int | None = None
    raErr: float | None = None
    decErr: float | None = None
    ra_dec_Cov: float | None = None
    x: float
    xErr: float | None = None
    y: float
    yErr: float | None = None
    centroid_flag: bool | None = None
    apFlux: float | None = None
    apFluxErr: float | None = None
    apFlux_flag: bool | None = None
    apFlux_flag_apertureTruncated: bool | None = None
    isNegative: bool | None = None
    psfLnL: float | None = None
    psfChi2: float | None = None
    psfNdata: int | None = None
    psfFlux_flag: bool | None = None
    psfFlux_flag_edge: bool | None = None
    psfFlux_flag_noGoodPixels: bool | None = None
    trailFlux: float | None = None
    trailFluxErr: float | None = None
    trailRa: float | None = None
    trailRaErr: float | None = None
    trailDec: float | None = None
    trailDecErr: float | None = None
    trailLength: float | None = None
    trailLengthErr: float | None = None
    trailAngle: float | None = None
    trailAngleErr: float | None = None
    trailChi2: float | None = None
    trailNdata: int | None = None
    trail_flag_edge: bool | None = None
    dipoleMeanFlux: float | None = None
    dipoleMeanFluxErr: float | None = None
    dipoleFluxDiff: float | None = None
    dipoleFluxDiffErr: float | None = None
    dipoleLength: float | None = None
    dipoleAngle: float | None = None
    dipoleChi2: float | None = None
    dipoleNdata: int | None = None
    forced_PsfFlux_flag: bool | None = None
    forced_PsfFlux_flag_edge: bool | None = None
    forced_PsfFlux_flag_noGoodPixels: bool | None = None
    templateFlux: float | None = None
    templateFluxErr: float | None = None
    ixx: float | None = None
    iyy: float | None = None
    ixy: float | None = None
    ixxPSF: float | None = None
    iyyPSF: float | None = None
    ixyPSF: float | None = None
    shape_flag: bool | None = None
    shape_flag_no_pixels: bool | None = None
    shape_flag_not_contained: bool | None = None
    shape_flag_parent_source: bool | None = None
    extendedness: float | None = None
    reliability: float | None = None
    isDipole: bool | None = None
    dipoleFitAttempted: bool | None = None
    timeProcessedMjdTai: float
    timeWithdrawnMjdTai: float | None = None
    bboxSize: int | None = None
    pixelFlags: bool | None = None
    pixelFlags_bad: bool | None = None
    pixelFlags_cr: bool | None = None
    pixelFlags_crCenter: bool | None = None
    pixelFlags_edge: bool | None = None
    pixelFlags_nodata: bool | None = None
    pixelFlags_nodataCenter: bool | None = None
    pixelFlags_interpolated: bool | None = None
    pixelFlags_interpolatedCenter: bool | None = None
    pixelFlags_offimage: bool | None = None
    pixelFlags_saturated: bool | None = None
    pixelFlags_saturatedCenter: bool | None = None
    pixelFlags_suspect: bool | None = None
    pixelFlags_suspectCenter: bool | None = None
    pixelFlags_streak: bool | None = None
    pixelFlags_streakCenter: bool | None = None
    pixelFlags_injected: bool | None = None
    pixelFlags_injectedCenter: bool | None = None
    pixelFlags_injected_template: bool | None = None
    pixelFlags_injected_templateCenter: bool | None = None
    glint_trail: bool | None = None
    has_stamp: bool | None = None
    survey_id: str 