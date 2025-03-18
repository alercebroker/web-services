from typing import Optional

from pydantic import BaseModel


class ObjectReduced(BaseModel):
    oid: str
    corrected: bool
    stellar: bool
    ndet: int
    meanra: float
    meandec: float
    firstmjd: float
    lastmjd: float