from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from core.exceptions import  ObjectNotFound
from core.repository.queries.object import query_psql_object
from core.repository.queries.non_detections import _query_count_non_detections_sql
from core.repository.queries.detections import _query_first_det_candid_sql

from ..models.object import ObjectReduced as ObjectModel

def get_object(
    oid: str, 
    session_factory: Callable[..., AbstractContextManager[Session]]
) -> ObjectModel:
    try:

        first = query_psql_object(oid=oid, session_factory=session_factory)

        return ObjectModel(**first.__dict__)
    except Exception:
        raise
    

def get_count_ndet(
    oid: str,
    session_factory: Callable[..., AbstractContextManager[Session]],
) -> int:
    
    try:
        count = _query_count_non_detections_sql(oid=oid, session_factory=session_factory)

        return count
    except Exception:
        raise

def get_first_det_candid(
    oid: str,
    session_factory: Callable[..., AbstractContextManager[Session]],
) -> str:
    try:
        first = _query_first_det_candid_sql(oid=oid, session_factory=session_factory)

        detection = first[0].__dict__
        
        if detection is None:
            raise ObjectNotFound(oid)
        
        return detection["candid"]
    except ObjectNotFound:
        raise