from typing import Callable
from contextlib import AbstractContextManager
from db_plugins.db.sql.models import Probability
from sqlalchemy.orm import Session
from sqlalchemy import select


def get_probability_by_oid(
    oid: str,
    classifier: str | None = None,
    session_factory: Callable[..., AbstractContextManager[Session]]
    | None = None,
):
    with session_factory() as session:
        stmt = (
            select(Probability)
            .where(Probability.oid==oid)
            .order_by(Probability.probabilty())
        )

        if classifier:
            stmt = stmt.where(Probability.classifier_name == classifier)

        result = session.execute(stmt).all()

        return result
