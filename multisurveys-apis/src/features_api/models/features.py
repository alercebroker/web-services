from pydantic import BaseModel, Field


class Feature(BaseModel):
    name: str = Field(description="Feature name.")
    value: float | None = Field(description="Feature value. null when it couldn't be computed.")
    band: int = Field(description="Band the feature was computed on (for ZTF: 1=g, 2=r, 3=i).")
    version: str | None = Field(description="Version of the feature computation.")
