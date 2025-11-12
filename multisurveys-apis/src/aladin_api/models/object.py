from pydantic import BaseModel


class Object(BaseModel):
    oid: int
    meanra: float
    meandec: float