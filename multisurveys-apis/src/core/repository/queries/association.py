"""Read queries on the object association tables (see core/repository/association_models.py)."""

from typing import Callable, ContextManager, Iterable

from db_plugins.db.sql.models_pipeline import Object
from sqlalchemy import Row, func, select, tuple_, union_all
from sqlalchemy.orm import Session

from core.repository.association_models import AssociationMethod, ObjectAssociation, ObjectGroup

SessionFactory = Callable[..., ContextManager[Session]]


def get_object_group(session_factory: SessionFactory, oid: int, sid: int) -> ObjectGroup | None:
    """The group row of one object, or None when the object has no group."""
    with session_factory() as session:
        stmt = select(ObjectGroup).where(ObjectGroup.oid == oid, ObjectGroup.sid == sid)
        return session.execute(stmt).scalar_one_or_none()


def get_group_members(session_factory: SessionFactory, group_id: int) -> list[tuple[int, int]]:
    """(oid, sid) of every member of a group."""
    with session_factory() as session:
        stmt = select(ObjectGroup.oid, ObjectGroup.sid).where(ObjectGroup.group_id == group_id)
        return [(row.oid, row.sid) for row in session.execute(stmt).all()]


def get_method(session_factory: SessionFactory, method_version: int | None = None) -> AssociationMethod | None:
    """One method version, or the newest one when none is given."""
    with session_factory() as session:
        stmt = select(AssociationMethod)
        if method_version is None:
            newest = select(func.max(AssociationMethod.method_version)).scalar_subquery()
            stmt = stmt.where(AssociationMethod.method_version == newest)
        else:
            stmt = stmt.where(AssociationMethod.method_version == method_version)
        return session.execute(stmt).scalar_one_or_none()


def get_pairs_touching(
    session_factory: SessionFactory, objects: Iterable[tuple[int, int]], method_version: int
) -> list[Row]:
    """Every pair, of one method version, with at least one side among ``objects`` ((oid, sid) tuples).

    Two selects, one per side, so each uses its own index: the primary key starts with (oid_a, sid_a), and
    (oid_b, sid_b) has an index of its own. A pair between two of the objects comes back once.
    """
    objects = list(objects)
    if not objects:
        return []
    columns = [
        ObjectAssociation.oid_a,
        ObjectAssociation.sid_a,
        ObjectAssociation.oid_b,
        ObjectAssociation.sid_b,
        ObjectAssociation.dist,
        ObjectAssociation.score,
    ]
    side_a = select(*columns).where(
        tuple_(ObjectAssociation.oid_a, ObjectAssociation.sid_a).in_(objects),
        ObjectAssociation.method_version == method_version,
    )
    side_b = select(*columns).where(
        tuple_(ObjectAssociation.oid_b, ObjectAssociation.sid_b).in_(objects),
        ObjectAssociation.method_version == method_version,
    )
    with session_factory() as session:
        rows = session.execute(union_all(side_a, side_b)).all()

    unique = {}
    for row in rows:
        unique[(row.oid_a, row.sid_a, row.oid_b, row.sid_b)] = row
    return list(unique.values())


def get_object_stats(session_factory: SessionFactory, objects: Iterable[tuple[int, int]]) -> dict[tuple[int, int], Row]:
    """n_det, firstmjd, lastmjd, meanra and meandec of each of ``objects`` ((oid, sid) tuples) found in the object table."""
    objects = list(objects)
    if not objects:
        return {}
    stmt = select(
        Object.oid, Object.sid, Object.n_det, Object.firstmjd, Object.lastmjd, Object.meanra, Object.meandec
    ).where(tuple_(Object.oid, Object.sid).in_(objects))
    with session_factory() as session:
        return {(row.oid, row.sid): row for row in session.execute(stmt).all()}
