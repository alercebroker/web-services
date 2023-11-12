from pydantic import BaseModel, Field


class MagstatsModel(BaseModel):
    fid: int = Field(description="Filter ID (1=g; 2=r, 3=i)")
    stellar: bool = Field(
        description="Whether the object appears to be unresolved in the given band"
    )
    corrected: bool = Field(
        description="Whether the corrected photometry should be used"
    )
    ndet: int = Field(description="Number of detections in the given band")
    ndubious: int = Field(description="Number of dubious corrections")
    magmean: float = Field(description="The mean magnitude for the given fid")
    magmedian: float = Field(
        description="The median magnitude for the given fid"
    )
    magmax: float = Field(description="The max magnitude for the given fid")
    magmin: float = Field(description="The min magnitude for the given fid")
    magsigma: float = Field(
        description="Magnitude standard deviation for the given fid"
    )
    maglast: float = Field(description="The last magnitude for the given fid")
    magfirst: float = Field(
        description="The first magnitude for the given fid"
    )
    firstmjd: float = Field(
        description="The time of the first detection in the given fid"
    )
    lastmjd: float = Field(
        description="The time of the last detection in the given fid"
    )
    step_id_corr: str = Field(description="Correction step pipeline version")
