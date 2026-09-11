from pydantic import BaseModel


class Object(BaseModel):
    meanra: float
    meandec: float


class ObjectInformation(BaseModel):
    oid: str
    survey: str
