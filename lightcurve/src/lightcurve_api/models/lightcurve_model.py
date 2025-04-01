from typing import List, Optional, Union

from pydantic import BaseModel, Field


class DataReleaseDetection(BaseModel):
    mjd: float
    mag_corr: float
    e_mag_corr_ext: float
    fid: int
    field: int
    objectid: float
    corrected: Optional[bool] = True


class LightcurveModel(BaseModel):
    mjd: List[float | int]
    brightness: List[float | int]
    e_brightness: List[float | int]
    fid: List[str]


class LightcurveWithPeriod(LightcurveModel):
    period: float | int
