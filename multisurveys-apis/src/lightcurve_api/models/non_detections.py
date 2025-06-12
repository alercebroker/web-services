from pydantic import BaseModel

class NonDetections(BaseModel):
    oid: int
    survey_id: str
    band: int
    mjd: float
    diffmaglim: float


class nonDectectionMultistream(BaseModel):
    aid: int | None = None
    tid: str | None = None
    mjd: float | None = None
    fid: int | None = None
    oid: int | None = None
    sid: int | None = None
    diffmaglim: float | None = None
