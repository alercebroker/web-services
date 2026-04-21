from typing import Callable
from contextlib import AbstractContextManager
from db_plugins.db.sql.models import Taxonomy, Probability
from sqlalchemy.orm import Session, aliased
from sqlalchemy import select


def get_probability_by_oid(
    oid: str,
    classifier_id: int | None,
    session_factory: Callable[..., AbstractContextManager[Session]] | None = None,
):
    with session_factory() as session:
        TaxonomyAlias = aliased(Taxonomy, flat=True)

        stmt = select(Probability, TaxonomyAlias).join(
            TaxonomyAlias,
            (TaxonomyAlias.class_id == Probability.class_id)
            & (TaxonomyAlias.classifier_id == Probability.classifier_id),
        )

        if classifier_id:
            stmt = stmt.where(
                Probability.oid == oid,
                Probability.classifier_id == classifier_id,
            )
        else:
            stmt = stmt.where(Probability.oid == oid)

        stmt = stmt.order_by(TaxonomyAlias.order.asc())

        result = session.execute(stmt).all()
        return result
