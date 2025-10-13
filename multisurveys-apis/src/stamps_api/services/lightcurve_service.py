from typing import Callable, ContextManager, List, Tuple, cast
from sqlalchemy.orm import Session
from core.repository.queries import detections

# get ligitcurve with oid and survey
# parse to get mjd, greg, and measurement_id

def get_detections(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., ContextManager[Session]],
):
    result = detections.get_all_unique_detections_sql(oid, survey_id, session_factory=session_factory)

    result = parse_sql_detection(result)

    return result

def parse_sql_detection(sql_data):
    pass