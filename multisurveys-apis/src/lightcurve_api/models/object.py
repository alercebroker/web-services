from pydantic import BaseModel


class ApiObject(BaseModel):
    objectId: str
    ra: float
    dec: float
