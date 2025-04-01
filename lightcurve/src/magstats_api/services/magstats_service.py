from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from core.exceptions import ObjectNotFound
from ..models.magstats import MagStats as MagStatsModel
from core.repository.queries.magstats import _query_sql_mag_stats

def get_mag_stats(
    oid: str, 
    session_factory: Callable[..., AbstractContextManager[Session]]
) -> list:
    try:

        first = _query_sql_mag_stats(oid=oid, session_factory=session_factory)
        mag_stats_objs = [row[0] for row in first]
        
        if len(mag_stats_objs) == 0:
            raise ObjectNotFound(oid)
        dict_list = []
        
        for mag in mag_stats_objs:
            dict_list.append(MagStatsModel(**mag.__dict__))
        
        return dict_list
    except ObjectNotFound:
        raise