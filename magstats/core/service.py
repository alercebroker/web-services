from contextlib import AbstractContextManager
from typing import Callable
from .models import MagstatsModel
from pymongo.database import Database
from sqlalchemy.orm import Session
from .exceptions import DatabaseError, SurveyIdError
from api.result_handler import handle_error, handle_success

def get_magstats(
        oid: str,
        survey_id: str, 
        session_factory: Callable[..., AbstractContextManager[Session]] = None,
        mongo_db: Database = None
        ):
    if survey_id == "ztf":
        result = _get_magstats_sql(session_factory,oid)
    elif survey_id == "atlas":
        result = _get_magstats_mongo(mongo_db,oid)
    else: 
        return handle_error(SurveyIdError(survey_id))

    return handle_success(result)
    

def _get_magstats_sql(
    session_factory: Callable[..., AbstractContextManager[Session]], oid: str
):
    try:
        with session_factory() as session:
            obj = (
                session.query(MagstatsModel.Object)
                .filter(MagstatsModel.Object.oid == id)
                .one_or_none()
            )
            if obj:
                return handle_success(obj.magstats)
            else:
                raise # que tipo de error mostrar? en Flask era de tipo NotFound
    except Exception as e:
        return handle_error(DatabaseError(e))
    
def _get_magstats_mongo(database: Database, oid: str):
    try:
        result = database["magstats"].find({"oid": oid})
        return [res for res in result] 
    except Exception as e:
        return handle_error(DatabaseError(e))
            
    
