from contextlib import AbstractContextManager
from typing import Callable
from .models import MagstatsModel
from pymongo.database import Database
from sqlalchemy.orm import Session
from .exceptions import DatabaseError, OidError
from db_plugins.db.sql import models
from sqlalchemy import select, text


def default_handle_success(result):
    return result


def default_handle_error(error):
    raise error


def get_magstats(
        oid: str,
        session_factory: Callable[..., AbstractContextManager[Session]] = None,
        handle_success: Callable[..., dict] = default_handle_success,
        handle_error: Callable[Exception, None] = default_handle_error,        
        ):
    result = _get_magstats_sql(session_factory,oid,handle_error)
    if len(result) == 0:
        print("ohno error")
        handle_error(OidError(oid))
    else:
        print(result)
        print("entre al if jejej ")
        return handle_success(result)

    

def _get_magstats_sql(
    session_factory: Callable[..., AbstractContextManager[Session]],
    oid: str,
    handle_error: Callable[Exception, None] = default_handle_error, 
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
            return result

    except Exception as e:
        return handle_error(DatabaseError(e))
    
            
    
