from typing import Callable
from contextlib import AbstractContextManager
from db_plugins.db.sql.models import NonDetection, Object
from sqlalchemy.orm import Session
from sqlalchemy import select


def get_all_unique_non_detections_sql(
    filters: dict,
    session_factory: Callable[..., AbstractContextManager[Session]]
    | None = None,
):
    with session_factory() as session:

        stmt = (
            select(NonDetection)
            .where(*filters.values())
            .order_by(NonDetection.mjd.desc())
            .limit(10)
        )

        result = session.execute(stmt).all()

        return result
    
