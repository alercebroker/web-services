from pydantic import BaseModel, Field, validator

class filters_model(BaseModel):
    oid: str | None = None
    classifier: str | None = None
    classifier_version: str | None = None
    class_name: str | None = Field(
        default=None, alias="class")
    ranking: int | None = None
    ndet: int | None = None
    probability: float | None = None
    firstmjd: float | None = None
    lastmjd: float | None = None
    

class conesearch_model(BaseModel):
    dec: float | None = None
    ra: float | None = None
    radius: float | None = None


class pagination_model(BaseModel):
    page: int
    page_size: int
    count: bool

class order_model(BaseModel):
    order_by: str | None = Field(default="probability")
    order_mode: str

    @validator('order_mode')
    def c_match(cls, v):
        if not v in ['ASC', 'DESC']:
            return "DESC"
        return v

  