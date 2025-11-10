from pydantic import BaseModel


class Classifiers(BaseModel):
    """
    Classifier model for the API.
    """

    classifier_name: str
    classifier_version: str
    classes: list[str]
