from pydantic import BaseModel

class Classifiers(BaseModel):
    """
    Classifier model for the API.
    """
    classifier_name: str
    classifier_version: int
    classes: list[str]
