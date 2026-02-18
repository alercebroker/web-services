from pydantic import BaseModel


class BaseDetection(BaseModel):
    band_map: dict[int, str]
    band: int
    mjd: float
    survey_id: str
    ra: float
    dec: float

    def magnitude2flux(self, total: bool, absolute: bool, redshift: float) -> float:
        """Convert magnitude to flux.

        Args:
            total: Whether to use corrected magnitude (True) or uncorrected (False)
            absolute: Whether to use absolute magnitude (True) or apparent magnitude (False)
            redshift: Redshift value for absolute magnitude calculation

        Returns:
            Calculated flux value
        """
        raise NotImplementedError

    def magnitude2flux_err(self, total: bool, absolute: bool, redshift: float) -> float:
        """Calculate flux error from magnitude error.

        Args:
            total: Whether to use corrected error (True) or uncorrected (False)
            absolute: Whether to use absolute magnitude (True) or apparent magnitude (False)
            redshift: Redshift value for absolute magnitude calculation

        Returns:
            Calculated flux error
        """
        raise NotImplementedError

    def flux2magnitude(self, total: bool, absolute: bool, redshift: float) -> float:
        """Convert flux to magnitude.

        Args:
            total: Whether to use corrected flux (True) or uncorrected (False)
            absolute: Whether to use absolute magnitude (True) or apparent magnitude (False)
            redshift: Redshift value for absolute magnitude calculation

        Returns:
            Calculated magnitude value
        """
        raise NotImplementedError

    def flux2magnitude_err(self, total: bool, absolute: bool, redshift: float) -> float:
        """Get magnitude error from flux error.

        Args:
            total: Whether to use corrected error (True) or uncorrected (False)
            absolute: Whether to use absolute magnitude (True) or apparent magnitude (False)
            redshift: Redshift value for absolute magnitude calculation

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

    def magnitude2flux(self, total: bool, absolute: bool, redshift: float) -> float:
        """Convert magnitude to flux.

        Args:
            total: Whether to use corrected magnitude (True) or uncorrected (False)
            absolute: Whether to use absolute magnitude (True) or apparent magnitude (False)
            redshift: Redshift value for absolute magnitude calculation

        Returns:
            Calculated flux value
        """
        raise NotImplementedError

    def magnitude2flux_err(self, total: bool, absolute: bool, redshift: float) -> float:
        """Calculate flux error from magnitude error.

        Args:
            total: Whether to use corrected error (True) or uncorrected (False)
            absolute: Whether to use absolute magnitude (True) or apparent magnitude (False)
            redshift: Redshift value for absolute magnitude calculation

        Returns:
            Calculated flux error
        """
        raise NotImplementedError

    def flux2magnitude(self, total: bool, absolute: bool, redshift: float) -> float:
        """Convert flux to magnitude.

        Args:
            total: Whether to use corrected flux (True) or uncorrected (False)
            absolute: Whether to use absolute magnitude (True) or apparent magnitude (False)
            redshift: Redshift value for absolute magnitude calculation

        Returns:
            Calculated magnitude value
        """
        raise NotImplementedError

    def flux2magnitude_err(self, total: bool, absolute: bool, redshift: float) -> float:
        """Get magnitude error from flux error.

        Args:
            total: Whether to use corrected error (True) or uncorrected (False)
            absolute: Whether to use absolute magnitude (True) or apparent magnitude (False)
            redshift: Redshift value for absolute magnitude calculation

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

    def flux_sign(self, total: bool, absolute: bool, redshift: float) -> str:
        """Get the flux sign."""
        raise NotImplementedError
