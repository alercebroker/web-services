from pydantic import BaseModel


class ZtfObject(BaseModel):
    oid: int
    g_r_max: float | None = None
    g_r_max_corr: float | None = None
    g_r_mean: float | None = None
    g_r_mean_corr: float | None = None