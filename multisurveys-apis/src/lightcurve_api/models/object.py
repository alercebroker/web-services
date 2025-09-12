from pydantic import BaseModel


class ApiObject(BaseModel):
    objectId: str
    survey_id: str
    ra: float
    dec: float
