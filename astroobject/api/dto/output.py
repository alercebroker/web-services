from pydantic import BaseModel, Field
from typing import Union

from core.domain.astroobject_model import AstroObject

class AstroObjectsResponse(BaseModel):
    oid: str
    ndethist: Union[int, None]
    ncovhist: Union[int, None]
    mjdstarthist: Union[float, None]
    mjdendhist: Union[float, None]
    corrected: Union[bool, None]
    stellar: Union[bool, None]
    ndet: Union[int, None]
    g_r_max: Union[float, None]
    g_r_max_corr: Union[float, None]
    g_r_mean: Union[float, None]
    g_r_mean_corr: Union[float, None]
    meanra: Union[float, None]
    meandec: Union[float, None]
    sigmara: Union[float, None]
    sigmadec: Union[float, None]
    deltajd: Union[float, None]
    firstmjd: Union[float, None]
    lastmjd: Union[float, None]
    step_id_corr: Union[str, None]
    class_name: str = Field(..., alias="class")
    classifier_name: str = Field(..., alias="classifier")
    probability: float

def astrooobjects_response_factory(astro: AstroObject):
    astro_dict = astro.model_dump(by_alias=True)
    rank_one = astro_dict["probabilities"][0]
    astro_dict.update({
        "class": rank_one["class_name"],
        "classifier": rank_one["classifier_name"],
        "probability": rank_one["probability"]
    }) # add ranking 1 prob
    return AstroObjectsResponse(**astro_dict)