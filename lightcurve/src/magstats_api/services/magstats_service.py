from contextlib import AbstractContextManager
from typing import Callable

from db_plugins.db.sql.models import (
    MagStats,
)

from sqlalchemy import asc, func, select
from sqlalchemy.orm import Session

from core.exceptions import DatabaseError, ObjectNotFound
from ..models.magstats import MagStats as MagStatsModel

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