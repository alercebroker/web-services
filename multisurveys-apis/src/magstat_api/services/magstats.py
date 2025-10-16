from typing import Callable
from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from core.repository.queries.magstats import get_magstats_by_oid
from .parsers import parse_magstats, parse_lsst_dia_objects


def get_magstats(
    oid,
    survey_id,
    session_factory: Callable[..., AbstractContextManager[Session]] | None = None,
):  
    result = get_magstats_by_oid(oid, survey_id, session_factory=session_factory)
    
    if survey_id == "ztf":
        parsed_result = parse_magstats(result)
    elif survey_id == "lsst":
        parsed_result = parse_lsst_dia_objects(result)
    else:
        raise ValueError(f"Unsupported survey: {survey_id}")

    return parsed_result
