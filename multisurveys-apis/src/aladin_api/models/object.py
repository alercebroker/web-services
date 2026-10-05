from pydantic import BaseModel, field_validator


class Object(BaseModel):
    oid: str
    sid: int
    meanra: float
    meandec: float

    @field_validator("oid", mode="before")
    @classmethod
    def oid_to_str(cls, v):
        return str(v)


class RawObjectsRequest(BaseModel):
    selected_oid: str
    sid: str
    objects: str | None = None
