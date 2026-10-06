from pydantic import BaseModel


class Probability(BaseModel):
    classifier_name: str | None = None
    classifier_version: int
    class_name: str
    probability: float
    ranking: int


class ObjectProbability(BaseModel):
    oid: int
    survey: str
    classifiers: dict
