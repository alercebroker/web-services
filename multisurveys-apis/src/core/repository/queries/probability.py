from typing import Callable
from contextlib import AbstractContextManager
from db_plugins.db.sql.models import Taxonomy_ms, Probability_ms
from sqlalchemy.orm import Session
from sqlalchemy import select


def get_probability_by_oid(
    oid: str,
    classifier_id: int | None,
    session_factory: Callable[..., AbstractContextManager[Session]]
    | None = None,
):
    with session_factory() as session:
        stmt = select(Probability_ms, Taxonomy_ms).join(
            Taxonomy_ms, Taxonomy_ms.class_id == Probability_ms.class_id
        )

        if classifier_id:
            stmt = stmt.where(
                Probability_ms.oid == oid,
                Probability_ms.classifier_id == classifier_id,
            )
        else:
            stmt = stmt.where(Probability_ms.oid == oid)

        stmt = stmt.order_by(Taxonomy_ms.order.asc())

        result = session.execute(stmt).all()
        return result
