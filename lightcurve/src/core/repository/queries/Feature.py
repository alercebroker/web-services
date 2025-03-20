import math
from contextlib import AbstractContextManager
from typing import Any, Callable, Sequence, Tuple

from db_plugins.db.sql.models import (
    Feature,
)
from returns.result import Failure, Result, Success
from sqlalchemy import Row, select, text
from sqlalchemy.orm import Session

from core.config.config import app_config

from ...exceptions import (
    DatabaseError,
)

from lightcurve_api.models.feature import Feature as FeatureModel

def _query_period_sql(
    oid: str,
    session_factory: Callable[..., AbstractContextManager[Session]] | None,
):
    try:
        assert session_factory is not None
        with session_factory() as session:
            stmt = (
                select(Feature)
                .where(Feature.oid == oid)
                .where(Feature.name == "Multiband_period")
            )
            result = session.execute(stmt).all()
            return result
    except Exception as e:
        return Failure(DatabaseError(e, database="PSQL"))

# def _get_period_sql(
#     oid: str,
#     session_factory: Callable[..., AbstractContextManager[Session]] | None,
# ) -> Result[FeatureModel, BaseException]:

#     result = _query_period_sql(oid, session_factory)
#     result = [FeatureModel(**res[0].__dict__) for res in result]
#     result = list(
#         filter(
#             lambda x: "23." not in x.version
#             and "25." not in x.version
#             and x.value != None,
#             result,
#         )
#     )
#     if len(result) == 0:
#         return Success(
#             FeatureModel(name="Multiband_period", value=0, fid=0, version="0")
#         )
#     return Success(result[0])