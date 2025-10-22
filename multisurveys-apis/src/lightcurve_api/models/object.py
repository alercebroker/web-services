from pydantic import BaseModel


class ApiObject(BaseModel):
    objectId: str
    survey_id: str
    ra: float
    dec: float


class ZtfDrObject(ApiObject):
    survey_id: str = "ztf dr"
    filterid: int
    nepochs: int
    fieldid: int
    rcid: int
