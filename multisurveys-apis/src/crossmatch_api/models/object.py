from pydantic import BaseModel


class Object(BaseModel):
    meanra: float
    meandec: float