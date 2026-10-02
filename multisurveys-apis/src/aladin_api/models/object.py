from pydantic import BaseModel


class Object(BaseModel):
    oid: str
    sid: int
    meanra: float
    meandec: float


class RawObjectsRequest(BaseModel):
    selected_oid: str
    sid: str
    objects: str
