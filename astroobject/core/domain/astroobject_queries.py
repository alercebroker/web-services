from pydantic import BaseModel
from typing import Any, Dict, List, Optional

class GetAstroObjectsQuery(BaseModel):
    oids: List[str]
    page: int
    page_size: int
    count: bool
    order_by: str
    order_mode: str
    filters: Dict
    conesearch_args: Dict
    conesearch: Dict
    default_classifier: Optional[str]
    default_version: Optional[str]
    default_ranking: Optional[int]

class GetAstroObjectQuery(BaseModel):
    oid: str