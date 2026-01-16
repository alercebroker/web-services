from pydantic import BaseModel

class detection(BaseModel):
    mjd : float
    greg: str
    measurement_id: int
    band: str
    has_stamp: bool
    def to_json(self):
        return {
            "mjd": self.mjd,
            "greg": self.greg,
            "measurement_id": str(self.measurement_id),
            "band": self.band,
            "has_stamp": self.has_stamp
        }

class LightcurveModel(BaseModel):
    detections : list[detection] = []

class PostRequestInputModel(BaseModel):
    oid: str
    survey_id: str
    measurement_id: int
    detections_list: list[dict]
