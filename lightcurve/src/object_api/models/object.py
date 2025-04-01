from typing import Optional

from pydantic import BaseModel


class ObjectReduced(BaseModel):
    oid: str
    corrected: bool
    stellar: bool
    ndet: int
    meanra: float
    meandec: float
    firstmjd: float
    lastmjd: float


class ObjectReducedRest(BaseModel):
    oid: str
    ndethist: int | None = None
    ncovhist: int | None = None
    mjdstarthist: float | None = None
    mjdendhist: float | None = None
    corrected: bool | None = None
    stellar: bool| None = None
    ndet: int | None = None
    g_r_max: float | None = None
    g_r_max_corr: float | None = None
    g_r_mean: float | None = None
    g_r_mean_corr: float | None = None
    firstmjd: float | None = None
    lastmjd: float | None = None
    deltajd: float | None = None
    meanra: float | None = None
    meandec: float | None = None
    sigmara: float | None = None
    sigmadec: float | None = None
    step_id_corr: str | None = None