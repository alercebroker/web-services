from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class LsstDiaObjectSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    oid: int
    validityStartMjdTai: float
    ra: float
    raErr: Optional[float] = None
    dec: float
    decErr: Optional[float] = None
    ra_dec_Cov: Optional[float] = None
    u_psfFluxMean: Optional[float] = None
    u_psfFluxMeanErr: Optional[float] = None
    u_psfFluxSigma: Optional[float] = None
    u_psfFluxNdata: Optional[int] = None
    u_fpFluxMean: Optional[float] = None
    u_fpFluxMeanErr: Optional[float] = None
    g_psfFluxMean: Optional[float] = None
    g_psfFluxMeanErr: Optional[float] = None
    g_psfFluxSigma: Optional[float] = None
    g_psfFluxNdata: Optional[int] = None
    g_fpFluxMean: Optional[float] = None
    g_fpFluxMeanErr: Optional[float] = None
    r_psfFluxMean: Optional[float] = None
    r_psfFluxMeanErr: Optional[float] = None
    r_psfFluxSigma: Optional[float] = None
    r_psfFluxNdata: Optional[int] = None
    r_fpFluxMean: Optional[float] = None
    r_fpFluxMeanErr: Optional[float] = None
    i_psfFluxMean: Optional[float] = None
    i_psfFluxMeanErr: Optional[float] = None
    i_psfFluxSigma: Optional[float] = None
    i_psfFluxNdata: Optional[int] = None
    i_fpFluxMean: Optional[float] = None
    i_fpFluxMeanErr: Optional[float] = None
    z_psfFluxMean: Optional[float] = None
    z_psfFluxMeanErr: Optional[float] = None
    z_psfFluxSigma: Optional[float] = None
    z_psfFluxNdata: Optional[int] = None
    z_fpFluxMean: Optional[float] = None
    z_fpFluxMeanErr: Optional[float] = None
    y_psfFluxMean: Optional[float] = None
    y_psfFluxMeanErr: Optional[float] = None
    y_psfFluxSigma: Optional[float] = None
    y_psfFluxNdata: Optional[int] = None
    y_fpFluxMean: Optional[float] = None
    y_fpFluxMeanErr: Optional[float] = None
    u_scienceFluxMean: Optional[float] = None
    u_scienceFluxMeanErr: Optional[float] = None
    g_scienceFluxMean: Optional[float] = None
    g_scienceFluxMeanErr: Optional[float] = None
    r_scienceFluxMean: Optional[float] = None
    r_scienceFluxMeanErr: Optional[float] = None
    i_scienceFluxMean: Optional[float] = None
    i_scienceFluxMeanErr: Optional[float] = None
    z_scienceFluxMean: Optional[float] = None
    z_scienceFluxMeanErr: Optional[float] = None
    y_scienceFluxMean: Optional[float] = None
    y_scienceFluxMeanErr: Optional[float] = None
    u_psfFluxMin: Optional[float] = None
    u_psfFluxMax: Optional[float] = None
    u_psfFluxMaxSlope: Optional[float] = None
    u_psfFluxErrMean: Optional[float] = None
    g_psfFluxMin: Optional[float] = None
    g_psfFluxMax: Optional[float] = None
    g_psfFluxMaxSlope: Optional[float] = None
    g_psfFluxErrMean: Optional[float] = None
    r_psfFluxMin: Optional[float] = None
    r_psfFluxMax: Optional[float] = None
    r_psfFluxMaxSlope: Optional[float] = None
    r_psfFluxErrMean: Optional[float] = None
    i_psfFluxMin: Optional[float] = None
    i_psfFluxMax: Optional[float] = None
    i_psfFluxMaxSlope: Optional[float] = None
    i_psfFluxErrMean: Optional[float] = None
    z_psfFluxMin: Optional[float] = None
    z_psfFluxMax: Optional[float] = None
    z_psfFluxMaxSlope: Optional[float] = None
    z_psfFluxErrMean: Optional[float] = None
    y_psfFluxMin: Optional[float] = None
    y_psfFluxMax: Optional[float] = None
    y_psfFluxMaxSlope: Optional[float] = None
    y_psfFluxErrMean: Optional[float] = None
    firstDiaSourceMjdTai: Optional[float] = None
    lastDiaSourceMjdTai: Optional[float] = None
    nDiaSources: int
    created_date: Optional[datetime] = None


from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class LsstDiaObjectSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    oid: int
    validityStartMjdTai: float
    ra: float
    raErr: Optional[float] = None
    dec: float
    decErr: Optional[float] = None
    ra_dec_Cov: Optional[float] = None
    u_psfFluxMean: Optional[float] = None
    u_psfFluxMeanErr: Optional[float] = None
    u_psfFluxSigma: Optional[float] = None
    u_psfFluxNdata: Optional[int] = None
    u_fpFluxMean: Optional[float] = None
    u_fpFluxMeanErr: Optional[float] = None
    g_psfFluxMean: Optional[float] = None
    g_psfFluxMeanErr: Optional[float] = None
    g_psfFluxSigma: Optional[float] = None
    g_psfFluxNdata: Optional[int] = None
    g_fpFluxMean: Optional[float] = None
    g_fpFluxMeanErr: Optional[float] = None
    r_psfFluxMean: Optional[float] = None
    r_psfFluxMeanErr: Optional[float] = None
    r_psfFluxSigma: Optional[float] = None
    r_psfFluxNdata: Optional[int] = None
    r_fpFluxMean: Optional[float] = None
    r_fpFluxMeanErr: Optional[float] = None
    i_psfFluxMean: Optional[float] = None
    i_psfFluxMeanErr: Optional[float] = None
    i_psfFluxSigma: Optional[float] = None
    i_psfFluxNdata: Optional[int] = None
    i_fpFluxMean: Optional[float] = None
    i_fpFluxMeanErr: Optional[float] = None
    z_psfFluxMean: Optional[float] = None
    z_psfFluxMeanErr: Optional[float] = None
    z_psfFluxSigma: Optional[float] = None
    z_psfFluxNdata: Optional[int] = None
    z_fpFluxMean: Optional[float] = None
    z_fpFluxMeanErr: Optional[float] = None
    y_psfFluxMean: Optional[float] = None
    y_psfFluxMeanErr: Optional[float] = None
    y_psfFluxSigma: Optional[float] = None
    y_psfFluxNdata: Optional[int] = None
    y_fpFluxMean: Optional[float] = None
    y_fpFluxMeanErr: Optional[float] = None
    u_scienceFluxMean: Optional[float] = None
    u_scienceFluxMeanErr: Optional[float] = None
    g_scienceFluxMean: Optional[float] = None
    g_scienceFluxMeanErr: Optional[float] = None
    r_scienceFluxMean: Optional[float] = None
    r_scienceFluxMeanErr: Optional[float] = None
    i_scienceFluxMean: Optional[float] = None
    i_scienceFluxMeanErr: Optional[float] = None
    z_scienceFluxMean: Optional[float] = None
    z_scienceFluxMeanErr: Optional[float] = None
    y_scienceFluxMean: Optional[float] = None
    y_scienceFluxMeanErr: Optional[float] = None
    u_psfFluxMin: Optional[float] = None
    u_psfFluxMax: Optional[float] = None
    u_psfFluxMaxSlope: Optional[float] = None
    u_psfFluxErrMean: Optional[float] = None
    g_psfFluxMin: Optional[float] = None
    g_psfFluxMax: Optional[float] = None
    g_psfFluxMaxSlope: Optional[float] = None
    g_psfFluxErrMean: Optional[float] = None
    r_psfFluxMin: Optional[float] = None
    r_psfFluxMax: Optional[float] = None
    r_psfFluxMaxSlope: Optional[float] = None
    r_psfFluxErrMean: Optional[float] = None
    i_psfFluxMin: Optional[float] = None
    i_psfFluxMax: Optional[float] = None
    i_psfFluxMaxSlope: Optional[float] = None
    i_psfFluxErrMean: Optional[float] = None
    z_psfFluxMin: Optional[float] = None
    z_psfFluxMax: Optional[float] = None
    z_psfFluxMaxSlope: Optional[float] = None
    z_psfFluxErrMean: Optional[float] = None
    y_psfFluxMin: Optional[float] = None
    y_psfFluxMax: Optional[float] = None
    y_psfFluxMaxSlope: Optional[float] = None
    y_psfFluxErrMean: Optional[float] = None
    firstDiaSourceMjdTai: Optional[float] = None
    lastDiaSourceMjdTai: Optional[float] = None
    nDiaSources: int
    created_date: Optional[datetime] = None
