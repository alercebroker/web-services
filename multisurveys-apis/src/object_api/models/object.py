from pydantic import BaseModel
from datetime import datetime


class ZtfObject(BaseModel):
    oid: int
    g_r_max: float | None = None
    g_r_max_corr: float | None = None
    g_r_mean: float | None = None
    g_r_mean_corr: float | None = None


class ObjectPlusZtfObject(BaseModel):
    oid: int

    tid: int
    sid: int
    meanra: float
    meandec: float
    sigmara: float | None = None
    sigmadec: float | None = None
    firstmjd: float
    lastmjd: float
    deltamjd: float = 0.0
    n_det: int = 1
    n_forced: int = 1
    n_non_det: int = 1
    corrected: bool = False
    stellar: bool | None = None

    g_r_max: float | None = None
    g_r_max_corr: float | None = None
    g_r_mean: float | None = None
    g_r_mean_corr: float | None = None


class LsstObject(BaseModel):
    oid: int
    validityStartMjdTai: float
    ra: float
    raErr: float | None = None
    dec: float
    decErr: float | None = None
    ra_dec_Cov: float | None = None
    u_psfFluxMean: float | None = None
    u_psfFluxMeanErr: float | None = None
    u_psfFluxSigma: float | None = None
    u_psfFluxNdata: int | None = None
    u_fpFluxMean: float | None = None
    u_fpFluxMeanErr: float | None = None
    g_psfFluxMean: float | None = None
    g_psfFluxMeanErr: float | None = None
    g_psfFluxSigma: float | None = None
    g_psfFluxNdata: int | None = None
    g_fpFluxMean: float | None = None
    g_fpFluxMeanErr: float | None = None
    r_psfFluxMean: float | None = None
    r_psfFluxMeanErr: float | None = None
    r_psfFluxSigma: float | None = None
    r_psfFluxNdata: int | None = None
    r_fpFluxMean: float | None = None
    r_fpFluxMeanErr: float | None = None
    i_psfFluxMean: float | None = None
    i_psfFluxMeanErr: float | None = None
    i_psfFluxSigma: float | None = None
    i_psfFluxNdata: int | None = None
    i_fpFluxMean: float | None = None
    i_fpFluxMeanErr: float | None = None
    z_psfFluxMean: float | None = None
    z_psfFluxMeanErr: float | None = None
    z_psfFluxSigma: float | None = None
    z_psfFluxNdata: int | None = None
    z_fpFluxMean: float | None = None
    z_fpFluxMeanErr: float | None = None
    y_psfFluxMean: float | None = None
    y_psfFluxMeanErr: float | None = None
    y_psfFluxSigma: float | None = None
    y_psfFluxNdata: int | None = None
    y_fpFluxMean: float | None = None
    y_fpFluxMeanErr: float | None = None
    u_scienceFluxMean: float | None = None
    u_scienceFluxMeanErr: float | None = None
    g_scienceFluxMean: float | None = None
    g_scienceFluxMeanErr: float | None = None
    r_scienceFluxMean: float | None = None
    r_scienceFluxMeanErr: float | None = None
    i_scienceFluxMean: float | None = None
    i_scienceFluxMeanErr: float | None = None
    z_scienceFluxMean: float | None = None
    z_scienceFluxMeanErr: float | None = None
    y_scienceFluxMean: float | None = None
    y_scienceFluxMeanErr: float | None = None
    u_psfFluxMin: float | None = None
    u_psfFluxMax: float | None = None
    u_psfFluxMaxSlope: float | None = None
    u_psfFluxErrMean: float | None = None
    g_psfFluxMin: float | None = None
    g_psfFluxMax: float | None = None
    g_psfFluxMaxSlope: float | None = None
    g_psfFluxErrMean: float | None = None
    r_psfFluxMin: float | None = None
    r_psfFluxMax: float | None = None
    r_psfFluxMaxSlope: float | None = None
    r_psfFluxErrMean: float | None = None
    i_psfFluxMin: float | None = None
    i_psfFluxMax: float | None = None
    i_psfFluxMaxSlope: float | None = None
    i_psfFluxErrMean: float | None = None
    z_psfFluxMin: float | None = None
    z_psfFluxMax: float | None = None
    z_psfFluxMaxSlope: float | None = None
    z_psfFluxErrMean: float | None = None
    y_psfFluxMin: float | None = None
    y_psfFluxMax: float | None = None
    y_psfFluxMaxSlope: float | None = None
    y_psfFluxErrMean: float | None = None
    firstDiaSourceMjdTai: float | None = None
    lastDiaSourceMjdTai: float | None = None
    nDiaSources: int
    created_date: datetime | None = None


class ObjectPlusLsstObject(BaseModel):
    oid: int

    tid: int
    sid: int
    meanra: float
    meandec: float
    sigmara: float | None = None
    sigmadec: float | None = None
    firstmjd: float
    lastmjd: float
    deltamjd: float = 0.0
    n_det: int = 1
    n_forced: int = 1
    n_non_det: int = 1
    corrected: bool = False
    stellar: bool | None = None

    validityStartMjdTai: float
    ra: float
    raErr: float | None = None
    dec: float
    decErr: float | None = None
    ra_dec_Cov: float | None = None
    u_psfFluxMean: float | None = None
    u_psfFluxMeanErr: float | None = None
    u_psfFluxSigma: float | None = None
    u_psfFluxNdata: int | None = None
    u_fpFluxMean: float | None = None
    u_fpFluxMeanErr: float | None = None
    g_psfFluxMean: float | None = None
    g_psfFluxMeanErr: float | None = None
    g_psfFluxSigma: float | None = None
    g_psfFluxNdata: int | None = None
    g_fpFluxMean: float | None = None
    g_fpFluxMeanErr: float | None = None
    r_psfFluxMean: float | None = None
    r_psfFluxMeanErr: float | None = None
    r_psfFluxSigma: float | None = None
    r_psfFluxNdata: int | None = None
    r_fpFluxMean: float | None = None
    r_fpFluxMeanErr: float | None = None
    i_psfFluxMean: float | None = None
    i_psfFluxMeanErr: float | None = None
    i_psfFluxSigma: float | None = None
    i_psfFluxNdata: int | None = None
    i_fpFluxMean: float | None = None
    i_fpFluxMeanErr: float | None = None
    z_psfFluxMean: float | None = None
    z_psfFluxMeanErr: float | None = None
    z_psfFluxSigma: float | None = None
    z_psfFluxNdata: int | None = None
    z_fpFluxMean: float | None = None
    z_fpFluxMeanErr: float | None = None
    y_psfFluxMean: float | None = None
    y_psfFluxMeanErr: float | None = None
    y_psfFluxSigma: float | None = None
    y_psfFluxNdata: int | None = None
    y_fpFluxMean: float | None = None
    y_fpFluxMeanErr: float | None = None
    u_scienceFluxMean: float | None = None
    u_scienceFluxMeanErr: float | None = None
    g_scienceFluxMean: float | None = None
    g_scienceFluxMeanErr: float | None = None
    r_scienceFluxMean: float | None = None
    r_scienceFluxMeanErr: float | None = None
    i_scienceFluxMean: float | None = None
    i_scienceFluxMeanErr: float | None = None
    z_scienceFluxMean: float | None = None
    z_scienceFluxMeanErr: float | None = None
    y_scienceFluxMean: float | None = None
    y_scienceFluxMeanErr: float | None = None
    u_psfFluxMin: float | None = None
    u_psfFluxMax: float | None = None
    u_psfFluxMaxSlope: float | None = None
    u_psfFluxErrMean: float | None = None
    g_psfFluxMin: float | None = None
    g_psfFluxMax: float | None = None
    g_psfFluxMaxSlope: float | None = None
    g_psfFluxErrMean: float | None = None
    r_psfFluxMin: float | None = None
    r_psfFluxMax: float | None = None
    r_psfFluxMaxSlope: float | None = None
    r_psfFluxErrMean: float | None = None
    i_psfFluxMin: float | None = None
    i_psfFluxMax: float | None = None
    i_psfFluxMaxSlope: float | None = None
    i_psfFluxErrMean: float | None = None
    z_psfFluxMin: float | None = None
    z_psfFluxMax: float | None = None
    z_psfFluxMaxSlope: float | None = None
    z_psfFluxErrMean: float | None = None
    y_psfFluxMin: float | None = None
    y_psfFluxMax: float | None = None
    y_psfFluxMaxSlope: float | None = None
    y_psfFluxErrMean: float | None = None
    firstDiaSourceMjdTai: float | None = None
    lastDiaSourceMjdTai: float | None = None
    nDiaSources: int
    created_date: datetime | None = None


class ZtfObjectProbability(BaseModel):
    oid: int
    g_r_max: float | None = None
    g_r_max_corr: float | None = None
    g_r_mean: float | None = None
    g_r_mean_corr: float | None = None
    tid: int
    sid: int
    meanra: float
    meandec: float
    sigmara: float | None = None
    sigmadec: float | None = None
    firstmjd: float
    lastmjd: float
    deltamjd: float
    n_det: int
    n_forced: int
    n_non_det: int
    corrected: bool
    stellar: bool
    class_name: str
    classifier_name: str
    classfier_version: str | None = None
    probability: float
    ranking: int


class LsstObjectProbability(BaseModel):
    oid: int
    tid: int
    sid: int
    meanra: float
    meandec: float
    sigmara: float | None = None
    sigmadec: float | None = None
    firstmjd: float
    lastmjd: float
    deltamjd: float
    n_det: int
    n_forced: int
    n_non_det: int
    corrected: bool
    stellar: bool
    class_name: str | None = None
    classifier_name: str | None = None
    classfier_version: str | None = None
    probability: float | None = None
    ranking: int | None = None


class Object(BaseModel):
    oid: int
    tid: int
    sid: int
    meanra: float
    meandec: float
    sigmara: float | None = None
    sigmadec: float | None = None
    firstmjd: float
    lastmjd: float
    deltamjd: float = 0.0
    n_det: int = 1
    n_forced: int = 1
    n_non_det: int = 1
    corrected: bool = False
    stellar: bool | None = None


class ExportModel:
    def __init__(self, survey: str, model_variant: str = "basic"):
        self.survey = survey
        self.model_variant = model_variant

    def get_model(self):
        if self.model_variant == "probability":
            if self.survey == "ztf":
                return ZtfObjectProbability
            elif self.survey == "lsst":
                return LsstObjectProbability
        elif self.model_variant == "basic":
            if self.survey == "ztf":
                return Object
            elif self.survey == "lsst":
                return Object
        elif self.model_variant == "with_extra":
            if self.survey == "ztf":
                return ObjectPlusZtfObject
            elif self.survey == "lsst":
                return ObjectPlusLsstObject
        else:
            raise ValueError("Invalid model variant")
