from pydantic import BaseModel


class Object(BaseModel):
    oid: int
    tid: int
    sid: int
    meanra: float
    meandec: float
    sigmara: float
    sigmadec: float
    firstmjd: float
    lastmjd: float
    deltamjd: float
    n_det: int
    n_force: int
    n_non_det: int
    corrected: bool
    stella: bool
