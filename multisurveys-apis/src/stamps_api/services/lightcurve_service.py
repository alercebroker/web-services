from typing import Callable, ContextManager
from sqlalchemy.orm import Session
from core.repository.queries import detections
from .lightcurve_parser import parse_lightcurve

# get ligitcurve with oid and survey
# parse to get mjd, greg, and measurement_id

def get_detections(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., ContextManager[Session]],
):
    result = detections.get_ordered_detections_sql(oid, survey_id, session_factory=session_factory)

    result = parse_lightcurve(result)
    return result
