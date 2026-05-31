from typing import Callable

from pydantic import BaseModel


def build_plot_variants(
    magnitude: Callable[[bool], float],
    magnitude_err: Callable[[bool], float],
    flux: Callable[[bool], float],
    flux_err: Callable[[bool], float],
    sign: Callable[[bool], str],
) -> dict:
    """Precompute the plotted (y, err, sign) for every flux/total toggle combination.

    The lightcurve widget only ever shows one of four states -- magnitude or flux,
    crossed with difference or total -- so the server emits all four up front and the
    browser merely looks up the one matching the current toggles (see
    lightcurve-app.js). This keeps the magnitude<->flux conversion (zero points, error
    propagation, sign handling) defined in exactly one place: the model methods passed
    in here. There is no parallel copy in JavaScript to drift out of sync.

    Each callable takes the ``total`` flag (corrected vs uncorrected) and returns the
    converted value for that mode.
    """
    return {
        "mag_diff": {"y": magnitude(False), "err": abs(magnitude_err(False)), "sign": sign(False)},
        "mag_total": {"y": magnitude(True), "err": abs(magnitude_err(True)), "sign": sign(True)},
        "flux_diff": {"y": flux(False), "err": abs(flux_err(False)), "sign": sign(False)},
        "flux_total": {"y": flux(True), "err": abs(flux_err(True)), "sign": sign(True)},
    }


class BaseDetection(BaseModel):
    band_map: dict[int, str]
    band: int
    mjd: float
    survey_id: str
    ra: float
    dec: float

    def magnitude2flux(self, total: bool, absolute: bool) -> float:
        """Convert magnitude to flux.

        Args:
            total: Whether to use corrected magnitude (True) or uncorrected (False)

        Returns:
            Calculated flux value
        """
        raise NotImplementedError

    def magnitude2flux_err(self, total: bool, absolute: bool) -> float:
        """Calculate flux error from magnitude error.

        Args:
            total: Whether to use corrected error (True) or uncorrected (False)

        Returns:
            Calculated flux error
        """
        raise NotImplementedError

    def flux2magnitude(self, total: bool, absolute: bool) -> float:
        """Convert flux to magnitude.

        Args:
            total: Whether to use corrected flux (True) or uncorrected (False)

        Returns:
            Calculated magnitude value
        """
        raise NotImplementedError

    def flux2magnitude_err(self, total: bool, absolute: bool) -> float:
        """Get magnitude error from flux error.

        Args:
            total: Whether to use corrected error (True) or uncorrected (False)

        Returns:
            Magnitude error value
        """
        raise NotImplementedError

    def flux_sign(self, total: bool, absolute: bool) -> str:
        """Sign of the measurement ('+'/'-' or, for ZTF, the raw isdiffpos)."""
        raise NotImplementedError

    def band_name(self) -> str:
        """Get the string representation of the band."""
        return self.band_map[self.band]

    def phase(self, period: float) -> float:
        """Calculate the phase for the given period"""
        return (self.mjd % period) / period

    def plot_variants(self) -> dict:
        """All (flux, total) variants for this detection. See build_plot_variants."""
        return build_plot_variants(
            lambda total: self.flux2magnitude(total, False),
            lambda total: self.flux2magnitude_err(total, False),
            lambda total: self.magnitude2flux(total, False),
            lambda total: self.magnitude2flux_err(total, False),
            lambda total: self.flux_sign(total, False),
        )


class BaseNonDetection(BaseModel):
    band_map: dict[int, str]
    band: int
    mjd: float
    survey_id: str

    def band_name(self) -> str:
        """Get the string representation of the band."""
        return self.band_map[self.band]

    def get_mag(self) -> float:
        """Get magnitude."""
        raise NotImplementedError


class BaseForcedPhotometry(BaseModel):
    band_map: dict[int, str]
    band: int
    mjd: float
    survey_id: str

    def magnitude2flux(self, total: bool) -> float:
        """Convert magnitude to flux.

        Args:
            total: Whether to use corrected magnitude (True) or uncorrected (False)

        Returns:
            Calculated flux value
        """
        raise NotImplementedError

    def magnitude2flux_err(self, total: bool) -> float:
        """Calculate flux error from magnitude error.

        Args:
            total: Whether to use corrected error (True) or uncorrected (False)

        Returns:
            Calculated flux error
        """
        raise NotImplementedError

    def flux2magnitude(self, total: bool) -> float:
        """Convert flux to magnitude.

        Args:
            total: Whether to use corrected flux (True) or uncorrected (False)

        Returns:
            Calculated magnitude value
        """
        raise NotImplementedError

    def flux2magnitude_err(self, total: bool) -> float:
        """Get magnitude error from flux error.

        Args:
            total: Whether to use corrected error (True) or uncorrected (False)

        Returns:
            Magnitude error value
        """
        raise NotImplementedError

    def band_name(self) -> str:
        """Get the string representation of the band."""
        return self.band_map[self.band]

    def phase(self, period: float) -> float:
        """Calculate the phase for the given period"""
        return (self.mjd % period) / period

    def plot_variants(self) -> dict:
        """All (flux, total) variants for this point. See build_plot_variants."""
        raise NotImplementedError
