from pydantic import BaseModel
from typing import Annotated
from fastapi import Query
from .pagination import Pagination, Order

class Filters(BaseModel):
    oid: Annotated[list[str] | None, Query()] = None
    classifier: str | None = None
    classifier_version: str | None = None
    class_name: str | None = None
    ranking: int | None = None
    ndet: list[int] | None = None
    probability: float | None = None
    firstmjd: list[float] | None = None
    lastmjd: float | None = None
    

class Consearch(BaseModel):
    dec: float | None = None
    ra: float | None = None
    radius: float | None = None


class SearchParams(BaseModel):
    filter_args: Filters
    conesearch_args: Consearch
    pagination_args: Pagination
    order_args: Order
