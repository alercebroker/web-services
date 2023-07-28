from fastapi import Query
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class GetAstroObjectsQuery(BaseModel):
    oid: List[str] = Field(Query([]))
    ranking: Optional[int] = 1
    count: Optional[bool] = False
    page: Optional[int] = 1
    perPage: Optional[int] = 10
    sortBy: Optional[str] = None
    ndet: Optional[int] = None
    probability: Optional[float] = None
    classifier_name: Optional[str] = None
    classifier_version: Optional[str] = None
    class_name: Optional[str] = None
    firstmjd: Optional[float] = None
    lastmjd: Optional[float] = None
    order_by: Optional[str] = None
    order_mode: Optional[str] = None
    ra: Optional[float] = None
    dec: Optional[float] = None
    radius: Optional[float] = None

class GetAstroObjectQuery(BaseModel):
    oid: str