from typing import Optional

from pydantic import BaseModel


class Object(BaseModel):
    oid: str
    ndet: int
    meanra: float
    meandec: float
    firstmjd: float
    lastmjd: float

class ObjectWithProbability(BaseModel):
    oid: str
    ndet: int
    meanra: float
    meandec: float
    firstmjd: float
    lastmjd: float
    classifier_name: Optional[str] = None
    class_name: Optional[str] = None
    probability: Optional[float] = None


class AnomalyScore(BaseModel):

    oid: str
    Transient: float
    Stochastic: float
    Periodic: float

class AnomalyDistributions(BaseModel):
    name: str
    category: str
    value: float
