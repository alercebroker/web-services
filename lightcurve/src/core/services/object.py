from contextlib import AbstractContextManager
from typing import Any, Callable, Sequence, Tuple

from pymongo.database import Database
from pymongo.cursor import Cursor

from db_plugins.db.sql.models import Object, MagStats, Probability, Taxonomy
from sqlalchemy import Row, select, text
from sqlalchemy.orm import Session

from .exceptions import (
    AtlasNonDetectionError,
    DatabaseError,
    ObjectNotFound,
    SurveyIdError,
    ParseError,
)
from .object_model import ObjectReduced as ObjectModel, MagStats as MagStatsModel, Probability as ProbabilityModel, Taxonomy as  TaxonomyModel
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
            first = result.all()
            mag_stats_objs = [row[0] for row in first]
            dict_list = []
            for mag in mag_stats_objs:
                dict_list.append(MagStatsModel(**mag.__dict__))
            if first is None:
                raise ObjectNotFound(oid)
            return dict_list
    except ObjectNotFound:
        raise
    except Exception as e:
        raise DatabaseError(e, database="PSQL")
    
def get_probabilities( 
    oid: str,
    session_factory: Callable[..., AbstractContextManager[Session]] | None = None,
    mongo_db: Database | None = None,
    handle_success: Callable[[Any], Any] = default_handle_success,
    handle_error: Callable[[BaseException], None] = default_handle_error
    ) -> list | None:
    try:
        assert session_factory is not None
        with session_factory() as session:
            stmt = select(Probability).where(Probability.oid == oid)
            result = session.execute(stmt)
            prob_list = result.all()
            get_prob_data = [row[0] for row in prob_list]
            get_prob_list = []
            for prob in get_prob_data:
                get_prob_list.append(ProbabilityModel(**prob.__dict__))
            if prob_list is None:
                raise ObjectNotFound(oid)
            return get_prob_list
    except ObjectNotFound:
        raise
    except Exception as e:
        raise DatabaseError(e, database="PSQL")
    
def get_taxonomies(
    session_factory: Callable[..., AbstractContextManager[Session]] | None = None,
    mongo_db: Database | None = None,
    handle_success: Callable[[Any], Any] = default_handle_success,
    handle_error: Callable[[BaseException], None] = default_handle_error
    ) -> list | None:
    try:
        assert session_factory is not None
        with session_factory() as session:
            stmt = select(Taxonomy)
            result = session.execute(stmt)
            taxonomy_list = result.all()
            get_taxonomy_data = [row[0] for row in taxonomy_list]
            get_taxonomy_list = []
            for prob in get_taxonomy_data:
                get_taxonomy_list.append(TaxonomyModel(**prob.__dict__))
            return get_taxonomy_list
    except ObjectNotFound:
        raise
    except Exception as e:
        raise DatabaseError(e, database="PSQL")
