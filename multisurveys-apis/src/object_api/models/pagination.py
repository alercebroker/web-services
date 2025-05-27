from pydantic import BaseModel, validator


class Pagination(BaseModel):
    page: int
    page_size: int
    count: bool


class Order(BaseModel):
    order_by: str | None = "probability"
    order_mode: str

    @validator('order_mode')
    def c_match(cls, v):
        if not v in ['ASC', 'DESC']:
            return "DESC"
        return v
