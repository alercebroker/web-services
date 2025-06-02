from enum import Enum

from pydantic import BaseModel


class Pagination(BaseModel):
    page: int
    page_size: int
    count: bool


class OrderMode(str, Enum):
    asc = "ASC"
    desc = "DESC"


class Order(BaseModel):
    order_by: str | None = "probability"
    order_mode: OrderMode = OrderMode.desc
