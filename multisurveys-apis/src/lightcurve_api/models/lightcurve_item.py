from pydantic import BaseModel


class BaseDetection(BaseModel):
    band_map: dict[int, str]
    band: int
    mjd: float
    survey_id: str

    def magnitude2flux(self, difference: bool) -> float:
        raise NotImplementedError

    def magnitude2flux_err(self, difference: bool) -> float:
        raise NotImplementedError

    def flux2magnitude(self, difference: bool) -> float:
        raise NotImplementedError

    def flux2magnitude_err(self, difference: bool) -> float:
        raise NotImplementedError

    def band_name(self) -> str:
        return self.band_map[self.band]


class BaseNonDetection(BaseModel):
    band_map: dict[int, str]
    band: int
    mjd: float
    survey_id: str

    def band_name(self) -> str:
        return self.band_map[self.band]

    def get_mag(self) -> float:
        raise NotImplementedError


class BaseForcedPhotometry(BaseModel):
    band_map: dict[int, str]
    band: int
    mjd: float
    survey_id: str

    def magnitude2flux(self, difference: bool) -> float:
        raise NotImplementedError

    def magnitude2flux_err(self, difference: bool) -> float:
        raise NotImplementedError

    def flux2magnitude(self, difference: bool) -> float:
        raise NotImplementedError

    def flux2magnitude_err(self, difference: bool) -> float:
        raise NotImplementedError

    def band_name(self) -> str:
        return self.band_map[self.band]
