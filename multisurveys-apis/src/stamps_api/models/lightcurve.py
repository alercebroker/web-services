from pydantic import BaseModel

class detection(BaseModel):
    mjd : float
    greg: str
    measurement_id: int

class LightcurveModel(BaseModel):
    detections : list[detection] = []