from typing import Optional, Union
from pydantic import BaseModel

class Probability(BaseModel):
    oid: str
    class_name: str
    classifier_name: str
    probability: float
    ranking: int
