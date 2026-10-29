from collections.abc import Sequence
from typing import Callable
from contextlib import AbstractContextManager
from db_plugins.db.sql.models_pipeline import Classifier, Taxonomy
from sqlalchemy.orm import Session
from sqlalchemy import RowMapping, select


def get_classifier_by_name(
    classifier_name: str,
    session_factory: Callable[..., AbstractContextManager[Session]],
) -> Sequence[RowMapping]:
    """
    Retrieves a classifier by its name.

    Args:
        classifier_name (str): The name of the classifier.
        session_factory (Callable[..., AbstractContextManager[Session]]): A factory function to create a database session.

    Returns:
        list: One row per (classifier, class) of the classifiers with that name.
    """
    with session_factory() as session:
        # The columns parse_classifiers reads, as in get_all_classifiers
        stmt = (
            select(
                Classifier.classifier_id,
                Classifier.classifier_name,
                Classifier.tid,
                Classifier.classifier_version,
                Taxonomy.order,
                Taxonomy.class_name,
                Taxonomy.class_id,
            )
            .join(
                Taxonomy,
                Classifier.classifier_id == Taxonomy.classifier_id,
            )
            .where(Classifier.classifier_name == classifier_name)
            .order_by(Taxonomy.order.asc())
        )
        return session.execute(stmt).mappings().all()


def get_all_classifiers(
    session_factory: Callable[..., AbstractContextManager[Session]],
) -> Sequence[RowMapping]:
    """
    Retrieves all classifiers.

    Args:
        session_factory (Callable[..., AbstractContextManager[Session]]): A factory function to create a database session.

    Returns:
        list: One row per (classifier, class).
    """
    with session_factory() as session:
        stmt = (
            select(
                Classifier.classifier_id,
                Classifier.classifier_name,
                Classifier.tid,
                Classifier.classifier_version,
                Taxonomy.classifier_id.label("taxonomy_classifier_id"),
                Taxonomy.order,
                Taxonomy.class_name,
                Taxonomy.class_id,
            )
            .join(
                Taxonomy,
                Classifier.classifier_id == Taxonomy.classifier_id,
            )
            .order_by(Classifier.classifier_name.asc(), Classifier.classifier_id.asc(), Taxonomy.order.asc())
        )
        result = session.execute(stmt)
        result = result.mappings().all()

        return result


def get_classes(
    classifier_name: str,
    classifier_version: str,
    session_factory: Callable[..., AbstractContextManager[Session]],
    sid: int | None = None,
) -> list[str] | None:
    """The class names of one classifier version, in taxonomy order. None if that classifier version doesn't exist.

    Name and version aren't unique (the same model can be registered for ZTF and LSST): `sid` picks the survey, and
    without it the classifier with the lowest id is used.
    """
    with session_factory() as session:
        stmt = select(Classifier.classifier_id).where(
            Classifier.classifier_name == classifier_name,
            Classifier.classifier_version == classifier_version,
        )
        if sid is not None:
            stmt = stmt.where(Classifier.tid == sid)
        classifier_id = session.execute(stmt.order_by(Classifier.classifier_id).limit(1)).scalar_one_or_none()
        if classifier_id is None:
            return None

        stmt = select(Taxonomy.class_name).where(Taxonomy.classifier_id == classifier_id).order_by(Taxonomy.order.asc())
        return list(session.execute(stmt).scalars().all())
