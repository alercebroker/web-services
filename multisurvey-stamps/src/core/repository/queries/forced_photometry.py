from typing import Any, Callable, ContextManager, List, Tuple, Sequence
from db_plugins.db.sql.models import (
    LsstForcedPhotometry,
    ZtfForcedPhotometry,
    ForcedPhotometry,
)
from sqlalchemy.orm import Session
from sqlalchemy import Row, select, and_


def get_unique_forced_photometry_sql(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., ContextManager[Session]],
):
    with session_factory() as session:
        if survey_id == "ztf":
            stmt = build_query(ZtfForcedPhotometry, oid)
        if survey_id == "lsst":
            stmt = build_query(LsstForcedPhotometry, oid)
        else:
            raise ValueError(f"Survey not supported {survey_id}")

        result = session.execute(stmt).all()

        return result


def build_query(model_id, oid):
    stmt = (
        select(model_id, ForcedPhotometry)
        .join(
            ForcedPhotometry,
            and_(
                model_id.oid == ForcedPhotometry.oid,
                model_id.measurement_id == ForcedPhotometry.measurement_id,
            ),
        )
        .where(model_id.oid == oid)
        .limit(10)
    )

    return stmt


def get_forced_photometry_by_list(
    session_factory: Callable[..., ContextManager[Session]],
):
    def _get(args: Tuple[List[int], str]) -> Tuple[Sequence[Row[Any]], str]:
        oids, survey_id = args
        if survey_id.lower() == "ztf":
            model = ZtfForcedPhotometry
        elif survey_id.lower() == "lsst":
            model = LsstForcedPhotometry
        else:
            raise ValueError("Survey not supported")

        with session_factory() as session:
            return (
                session.execute(
                    select(model, ForcedPhotometry)
                    .join(
                        ForcedPhotometry,
                        and_(
                            ForcedPhotometry.oid == model.oid,
                            ForcedPhotometry.measurement_id == model.measurement_id,
                        ),
                    )
                    .where(model.oid.in_(oids))
                ).all(),
                survey_id,
            )

    return _get
