from contextlib import AbstractContextManager
from typing import Callable
from .models import MagstatsModel
from pymongo.database import Database
from sqlalchemy.orm import Session
from werkzeug.exceptions import NotFound # no se si se puede cambiar
from .exceptions import DatabaseError, SurveyIdError

def get_magstats(
        oid: str,
        survey_id: str, # no se bien de donde sale
        session_factory: Callable[..., AbstractContextManager[Session]] = None,
        mongo_db: Database = None
        ):
    if survey_id == "ztf":
        result = _get_magstats_sql(session_factory,oid)
    elif survey_id == "atlas":
        result = _get_magstats_mongo(mongo_db,oid)
    else: 
        return SurveyIdError(survey_id)

    return result
        #error aun no implementado.

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
                return obj.magstats
            else:
                raise NotFound
    except Exception as e:
        return DatabaseError(e) # consultar sobre el Failiture
    
def _get_magstats_mongo(database: Database, oid: str):
    try:
        result = database["magstats"].find({"oid": oid})
        return [res for res in result] # preguntar que retornar.
    except Exception as e:
        return DatabaseError(e) # consultar sobre el Failiture
            
    
