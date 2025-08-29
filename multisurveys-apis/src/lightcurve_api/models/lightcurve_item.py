from typing import Tuple
from pydantic import BaseModel


class BaseDetection(BaseModel):
    band_map: dict[int, str]
    band: int
    mjd: float

    def magnitude2flux(self) -> float:
        raise NotImplementedError

    def magnitude2flux_err(self) -> float:
        raise NotImplementedError

    def flux2magnitude(self) -> float:
        raise NotImplementedError

    def flux2magnitude_err(self) -> float:
        raise NotImplementedError

    def band_name(self) -> str:
        return self.band_map[self.band]

    def get_point_magnitude(self) -> Tuple[float, float, float, str]:
        return (
            self.mjd,
            self.flux2magnitude(),
            self.flux2magnitude_err(),
            self.band_name(),
        )

    def get_point_flux(self) -> Tuple[float, float, float, str]:
        return (
            self.mjd,
            self.magnitude2flux(),
            self.magnitude2flux_err(),
            self.band_name(),
        )


class BaseNonDetection(BaseModel):
    band_map: dict[int, str]
    band: int

    def band_name(self) -> str:
        return self.band_map[self.band]

    def get_point(self) -> Tuple[float, float, float, str]:
        raise NotImplementedError


class BaseForcedPhotometry(BaseModel):
    band_map: dict[int, str]
    band: int
    mjd: float

    def magnitude2flux(self) -> float:
        raise NotImplementedError

    def magnitude2flux_err(self) -> float:
        raise NotImplementedError

    def flux2magnitude(self) -> float:
        raise NotImplementedError

    def flux2magnitude_err(self) -> float:
        raise NotImplementedError

    def band_name(self) -> str:
        return self.band_map[self.band]

    def get_point_magnitude(self) -> Tuple[float, float, float, str]:
        return (
            self.mjd,
            self.flux2magnitude(),
            self.flux2magnitude_err(),
            self.band_name(),
        )

    def get_point_flux(self) -> Tuple[float, float, float, str]:
        return (
            self.mjd,
            self.magnitude2flux(),
            self.magnitude2flux_err(),
            self.band_name(),
        )
