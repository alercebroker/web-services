from typing import Optional

from pydantic import BaseModel


class Taxonomy(BaseModel):
    classes: list
    classifier_name: str
    classifier_version: str
