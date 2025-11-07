from pydantic import BaseModel

class detection(BaseModel):
    mjd : float
    greg: str
    measurement_id: int

    def to_json(self):
        return {
            "mjd": self.mjd,
            "greg": self.greg,
            "measurement_id": str(self.measurement_id,)
        }

class LightcurveModel(BaseModel):
    detections : list[detection] = []