from fastapi import HTTPException

from .lsst import LSSTS3Handler
from .ztf import ZTFS3Handler

SURVEYS_HANDLERS = {
    "lsst": LSSTS3Handler,
    "ztf": ZTFS3Handler,
}


def handler_selector(survey_id: str):
    try:
        return SURVEYS_HANDLERS[survey_id]
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Incorrect survey identifier {survey_id}, valid surveys are {list(SURVEYS_HANDLERS.keys())}",
        )
