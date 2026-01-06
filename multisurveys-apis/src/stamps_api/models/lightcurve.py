from pydantic import BaseModel

class detection(BaseModel):
    mjd : float
    greg: str
    measurement_id: int
    band: str
    
    def to_json(self):
        return {
            "mjd": self.mjd,
            "greg": self.greg,
            "measurement_id": str(self.measurement_id),
            "band": self.band,
        }

class LightcurveModel(BaseModel):
    detections : list[detection] = []

class PostRequestInputModel(BaseModel):
    oid: str
    survey_id: str
    measurement_id: int
    detections_list: list[dict]
