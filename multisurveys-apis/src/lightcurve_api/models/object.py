from pydantic import BaseModel


class AlerceObject(BaseModel):
    objectId: str
    ra: float
    dec: float
