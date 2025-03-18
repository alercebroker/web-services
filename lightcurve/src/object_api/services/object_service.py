from contextlib import AbstractContextManager
from typing import Callable

from db_plugins.db.sql.models import (Object, NonDetection, Detection)

from sqlalchemy import asc, func, select
from sqlalchemy.orm import Session

from core.exceptions import DatabaseError, ObjectNotFound
from ..models.object import ObjectReduced as ObjectModel

def get_object(
    oid: str, session_factory: Callable[..., AbstractContextManager[Session]]
) -> ObjectModel:
    try:
        assert session_factory is not None
        with session_factory() as session:
            stmt = select(Object).where(Object.oid == oid)
            result = session.execute(stmt)
            first = result.first()
            if first is None:
                raise ObjectNotFound(oid)

            return ObjectModel(**first[0].__dict__)
    except ObjectNotFound:
        raise
    except Exception as e:
        raise DatabaseError(e, database="PSQL")
    

def get_count_ndet(
    oid: str,
    session_factory: Callable[..., AbstractContextManager[Session]],
) -> int:
    try:
        assert session_factory is not None
        with session_factory() as session:
            stmt = (
                select(func.count())
                .select_from(NonDetection)
                .where(NonDetection.oid == oid)
            )
            result = session.execute(stmt)
            count = result.all()[0]
            if count is None:
                raise ObjectNotFound(oid)
            return count[0]
    except ObjectNotFound:
        raise
    except Exception as e:
        raise DatabaseError(e, database="PSQL")

def get_first_det_candid(
    oid: str,
    session_factory: Callable[..., AbstractContextManager[Session]],
) -> str:
    try:
        assert session_factory is not None
        with session_factory() as session:
            stmt = (
                select(Detection)
                .where(Detection.oid == oid)
                .where(Detection.has_stamp == True)
                .order_by(asc(Detection.mjd))
            )
            result = session.execute(stmt)
            first = result.first()
            if first is None:
                raise ObjectNotFound(oid)
            detection = first[0].__dict__
            if detection is None:
                raise ObjectNotFound(oid)
            return detection["candid"]
    except ObjectNotFound:
        raise
    except Exception as e:
        raise DatabaseError(e, database="PSQL")