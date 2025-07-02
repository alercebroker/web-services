from pydantic import BaseModel


class ZtfObject(BaseModel):
    oid: int
    g_r_max: float | None = None
    g_r_max_corr: float | None = None
    g_r_mean: float | None = None
    g_r_mean_corr: float | None = None


class LsstObject(BaseModel):
    oid: int


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


class ObjectOutputModels():
    def __init__(self, survey: str, probability: bool = False):
        self.survey = survey
        self.probability = probability

    def get_model_by_survey(self):
        if self.probability:
            if self.survey == "ztf":
                return ZtfObjectProbability
            if self.survey == "lsst":
                return LsstObjectProbability
        else:
            if self.survey == "ztf":
                return ZtfObject
            elif self.survey == "lsst":
                return LsstObject
            
