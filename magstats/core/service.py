from contextlib import AbstractContextManager
from typing import Callable
from .models import MagstatsModel
from pymongo.database import Database
from sqlalchemy.orm import Session
from .exceptions import DatabaseError, OidError
from api.result_handler import handle_error, handle_success
from db_plugins.db.sql import models
from sqlalchemy import select, text

def get_magstats(
        oid: str,
        session_factory: Callable[..., AbstractContextManager[Session]] = None,
        mongo_db: Database = None
        ):
    result = _get_magstats_sql(session_factory,oid)

    if result is None: #revisar que pasa cuando el oid no esta en la bd
        handle_error(OidError(oid))

    return handle_success(result)
    

def _get_magstats_sql(
    session_factory: Callable[..., AbstractContextManager[Session]], oid: str
):
    try:
        with session_factory() as session:
            stmt = select(models.MagStats, text("'ztf'")).filter(
                models.MagStats.oid == oid
            )
            result = session.execute(stmt)
            result = [
                MagstatsModel(**ob[0].__dict__, tid=ob[1])
                for ob in result.all()
            ]
            return handle_success(result)

    except Exception as e:
        return handle_error(DatabaseError(e))
    
            
    
