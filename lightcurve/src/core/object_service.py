from contextlib import AbstractContextManager
from typing import Any, Callable, Sequence, Tuple

from pymongo.database import Database
from pymongo.cursor import Cursor

from db_plugins.db.sql.models import Object, MagStats
from sqlalchemy import Row, select, text
from sqlalchemy.orm import Session

from .exceptions import (
    AtlasNonDetectionError,
    DatabaseError,
    ObjectNotFound,
    SurveyIdError,
    ParseError,
)
from .object_model import ObjectReduced as ObjectModel, MagStats as MagStatsModel
from config import app_config

def default_handle_success(result):
    return result


def default_handle_error(error):
    raise error


def get_object( 
    oid: str,
    session_factory: Callable[..., AbstractContextManager[Session]] | None = None,
    mongo_db: Database | None = None,
    handle_success: Callable[[Any], Any] = default_handle_success,
    handle_error: Callable[[BaseException], None] = default_handle_error
    ) -> ObjectModel | None:
    
    try:
        assert session_factory is not None
        with session_factory() as session:
            stmt = select(Object).where(Object.oid == oid)
            result = session.execute(stmt)
            first = result.all()[0]
            if first is None:
                raise ObjectNotFound(oid)
            return ObjectModel(**first[0].__dict__)
    except ObjectNotFound:
        raise
    except Exception as e:
        raise DatabaseError(e, database="PSQL")
    
def get_mag_stats( 
    oid: str,
    session_factory: Callable[..., AbstractContextManager[Session]] | None = None,
    mongo_db: Database | None = None,
    handle_success: Callable[[Any], Any] = default_handle_success,
    handle_error: Callable[[BaseException], None] = default_handle_error
    ) -> list | None:
    
    try:
        assert session_factory is not None
        with session_factory() as session:
            stmt = select(MagStats).where(MagStats.oid == oid)
            result = session.execute(stmt)
            first = result.all()[0]
            if first is None:
                raise ObjectNotFound(oid)
            return MagStatsModel(**first[0].__dict__)
    except ObjectNotFound:
        raise
    except Exception as e:
        raise DatabaseError(e, database="PSQL")
    






