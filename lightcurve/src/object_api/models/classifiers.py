from pydantic import BaseModel

class ClassifierModel(BaseModel):
    classifier_name: str
    classifier_version: str
    classes: list


class ClassModel(BaseModel):
    name: str


