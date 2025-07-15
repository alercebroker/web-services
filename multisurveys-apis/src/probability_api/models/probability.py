from pydantic import BaseModel

class Probability(BaseModel):
    classifier_name: str
    classifier_version: str
    class_name: str
    probability: float
    ranking: int
