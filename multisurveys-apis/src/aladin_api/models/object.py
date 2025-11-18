from pydantic import BaseModel


class Object(BaseModel):
    oid: str
    meanra: float
    meandec: float
