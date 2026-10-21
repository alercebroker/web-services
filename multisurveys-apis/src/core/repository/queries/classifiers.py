from typing import Callable
from contextlib import AbstractContextManager
from db_plugins.db.sql.models_pipeline import Classifier, Taxonomy
from sqlalchemy.orm import Session
from sqlalchemy import select


def get_classifier_by_name(
    classifier_name: str,
    session_factory: Callable[..., AbstractContextManager[Session]] | None = None,
):
    """
    Retrieves a classifier by its name.

    Args:
        classifier_name (str): The name of the classifier.
        session_factory (Callable[..., AbstractContextManager[Session]] | None, optional): A factory function to create a database session. Defaults to None.

    Returns:
        list: List of classifiers matching the given name.
    """
    with session_factory() as session:
        stmt = (
            select(Classifier, Taxonomy)
            .join(
                Taxonomy,
                Classifier.classifier_id == Taxonomy.classifier_id,
            )
            .where(Classifier.classifier_name == classifier_name)
            .order_by(Taxonomy.order.asc())
        )
        result = session.execute(stmt).all()
        return result


def get_all_classifiers(
    session_factory: Callable[..., AbstractContextManager[Session]] | None = None, survey_id: str | None = None
):
    """
    Retrieves all classifiers.

    Args:
        session_factory (Callable[..., AbstractContextManager[Session]] | None, optional): A factory function to create a database session. Defaults to None.
        survey_id (str | None, optional): The survey ID to filter classifiers. Defaults to None.

    Returns:
        list: List of all classifiers.
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
            .order_by(Classifier.classifier_name.asc(), Taxonomy.order.asc())
        )
        result = session.execute(stmt)
        result = result.mappings().all()

        return result


def get_classes(
    classifier_name: str,
    classifier_version: str,
    session_factory: Callable[..., AbstractContextManager[Session]],
) -> list[str] | None:
    """The class names of one classifier version, in taxonomy order. None if that classifier version doesn't exist."""
    with session_factory() as session:
        classifier_id = session.execute(
            select(Classifier.classifier_id).where(
                Classifier.classifier_name == classifier_name,
                Classifier.classifier_version == classifier_version,
            )
        ).scalar_one_or_none()
        if classifier_id is None:
            return None

        stmt = select(Taxonomy.class_name).where(Taxonomy.classifier_id == classifier_id).order_by(Taxonomy.order.asc())
        return list(session.execute(stmt).scalars().all())
