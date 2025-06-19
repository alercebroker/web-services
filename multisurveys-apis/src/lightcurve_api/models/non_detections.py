from pydantic import BaseModel

class NonDetections(BaseModel):
    oid: int
    survey_id: str
    band: int
    mjd: float
    diffmaglim: float



class LsstNonDetection(BaseModel):
    oid: int
    survey_id: str
    ccdVisitId: int
    band: int
    mjd: float
    diaNoise: float