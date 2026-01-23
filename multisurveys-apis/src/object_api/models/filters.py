from pydantic import BaseModel
from .pagination import PaginationArgs, Order


class Filters(BaseModel):
    oids: list[int] | None = None
    survey: str | None = None
    classifier: str | None = None
    class_name: str | None = None
    ranking: int | None = None
    n_det: list[int] | None = None
    probability: float | None = None
    firstmjd: list[float] | None = None
    lastmjd: list[float] | None = None


class Consearch(BaseModel):
    dec: float | None = None
    ra: float | None = None
    radius: float | None = None


class SearchParams(BaseModel):
    filter_args: Filters
    conesearch_args: Consearch
    pagination_args: PaginationArgs
    #order_args: Order
