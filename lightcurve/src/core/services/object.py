from contextlib import AbstractContextManager
from typing import Callable

from db_plugins.db.sql.models import (
    Detection,
    MagStats,
    NonDetection,
    Object,
    Probability,
    Taxonomy,
)
from pymongo.database import Database
from sqlalchemy import asc, func, select
from sqlalchemy.orm import Session

from ..exceptions import DatabaseError, ObjectNotFound
from ..models.object import MagStats as MagStatsModel
from ..models.object import ObjectReduced as ObjectModel
from ..models.object import Probability as ProbabilityModel
from ..models.object import Taxonomy as TaxonomyModel


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


def get_mag_stats(
    oid: str, session_factory: Callable[..., AbstractContextManager[Session]]
) -> list:
    try:
        assert session_factory is not None
        with session_factory() as session:
            stmt = select(MagStats).where(MagStats.oid == oid)
            result = session.execute(stmt)
            first = result.all()
            mag_stats_objs = [row[0] for row in first]
            if len(mag_stats_objs) == 0:
                raise ObjectNotFound(oid)
            dict_list = []
            for mag in mag_stats_objs:
                dict_list.append(MagStatsModel(**mag.__dict__))
            return dict_list
    except ObjectNotFound:
        raise
    except Exception as e:
        raise DatabaseError(e, database="PSQL")


def get_probabilities(
    oid: str, session_factory: Callable[..., AbstractContextManager[Session]]
) -> list:
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
    session_factory: Callable[..., AbstractContextManager[Session]],
) -> list:
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
