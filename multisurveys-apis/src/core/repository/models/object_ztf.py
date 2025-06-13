from pydantic import BaseModel


class objectZtf(BaseModel):
    oid: int
    g_r_max: float
    g_r_max_corr: float
    g_r_mean: float
    g_r_mean_corr: float
