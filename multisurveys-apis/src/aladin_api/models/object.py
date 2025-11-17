from pydantic import BaseModel


class Object(BaseModel):
    oid: int
    ra: float
    dec: float
