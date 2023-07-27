from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class Filters(BaseModel):
    classifier: str = ""
    class_: str = Field(default="", alias="class")
    ndet: str = ""
    firstmjd: str = ""
    lastmjd: str = ""
    probability: str = ""
    ranking: str = ""
    classifier_version: str = ""
    oid: str = ""

class GetAstroObjectsQuery(BaseModel):
    oids: List[str]
    page: int
    page_size: int
    count: bool
    order_by: Optional[str] = None
    order_mode: Optional[str] = None
    filters: Filters
    conesearch: Dict
    classifier: Optional[str] = None
    version: Optional[str] = None
    ranking: Optional[int] = None

class GetAstroObjectQuery(BaseModel):
    oid: str