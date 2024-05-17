from contextlib import AbstractContextManager
from typing import Any, Callable, Sequence, Tuple

from pymongo.database import Database
from pymongo.cursor import Cursor

from db_plugins.db.sql.models import Object
from sqlalchemy import Row, select, text
from sqlalchemy.orm import Session

from .exceptions import (
    AtlasNonDetectionError,
    DatabaseError,
    ObjectNotFound,
    SurveyIdError,
    ParseError,
)

import httpx

from .object_model import ObjectReduced as ObjectModel
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

    # with session_factory() as session:
    #     stmt = select(Object).where(Object.oid == oid)
    #     result = session.execute(stmt)
    #     object = result.first()

    # return object
    
    try:
        assert session_factory is not None
        with session_factory() as session:
            stmt = select(Object).where(Object.oid == oid)
            result = session.execute(stmt)
            first = result.all()[0]
            #print(first[0].__dict__)
            if first is None:
                raise ObjectNotFound(oid)
            return ObjectModel(**first[0].__dict__)
    except ObjectNotFound:
        raise
    except Exception as e:
        raise DatabaseError(e, database="PSQL")
    
async def get_host(ra, dec):
    async with httpx.AsyncClient() as client:
        url = f'http://localhost:8082/query_delight?ra={ra}&dec={dec}'
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            modifiedData = {
                "hostRa": data.get("ra"),
                "hostDec": data.get("dec")
            }
            return modifiedData
        else:
            raise Exception(f'Error: {response.status}')   







