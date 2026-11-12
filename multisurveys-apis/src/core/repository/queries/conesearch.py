from typing import Callable, ContextManager, List, Tuple
from db_plugins.db.sql.models_pipeline import Object
from sqlalchemy import asc, select, text
from sqlalchemy.orm import Session, aliased


# TODO: takes its inputs as one positional tuple so it fits a toolz pipe. That is error-prone: ra, dec and radius
# are all floats, so swapping two of them raises no error and the type checker can't catch it. Change it to named
# parameters, like conesearch_oid below.
def conesearch_coordinates(
    session_factory: Callable[..., ContextManager[Session]],
):
    def _conesearch(args: Tuple[float, float, float, int]) -> List[Object]:
        ra, dec, radius, neighbors = args
        stmt = _build_statement_coordinates(neighbors)
        with session_factory() as session:
            result = session.execute(stmt, {"ra": ra, "dec": dec, "radius": radius}).all()
            return [row[0] for row in result]

    return _conesearch


def _build_statement_coordinates(neighbors: int):
    return (
        select(Object)
        .where(text("q3c_radial_query(meanra, meandec, :ra, :dec, :radius)"))
        .order_by(asc(text("q3c_dist(meanra, meandec, :ra, :dec)")))
        .limit(neighbors)
    )


# The oid searches take the object's (oid, sid): an object is identified by both, and the same oid can be an object
# in more than one survey. Parameters are keyword-only, so ids, radius and neighbors can't be swapped by position.


def conesearch_oid(
    session_factory: Callable[..., ContextManager[Session]],
    *,
    oid: int,
    sid: int,
    radius: float,
    neighbors: int,
) -> List[Object]:
    """Objects of any survey within `radius` of the object (oid, sid), nearest first, at most `neighbors`.

    Not used by the API yet: the routes use dummy_conesearch_oid.
    """
    stmt = _build_statement_oid(oid, sid, neighbors)
    with session_factory() as session:
        result = session.execute(stmt, {"radius": radius}).all()
        return [row[0] for row in result]


def dummy_conesearch_oid(
    session_factory: Callable[..., ContextManager[Session]],
    *,
    oid: int,
    sid: int,
) -> List[Object]:
    """Placeholder for conesearch_oid: returns only the object (oid, sid) itself, no neighbors."""
    stmt = select(Object).where(Object.oid == oid, Object.sid == sid)
    with session_factory() as session:
        result = session.execute(stmt).all()
        return [row[0] for row in result]


def _build_statement_oid(oid: int, sid: int, neighbors: int):
    # Create aliases for the Object table
    center_obj = aliased(Object, name="center")
    target_obj = aliased(Object, name="target")

    # Build the query using q3c_radial_query function
    return (
        select(target_obj)
        .select_from(center_obj, target_obj)
        .where(center_obj.oid == oid, center_obj.sid == sid)
        .where(text("q3c_radial_query(target.meanra, target.meandec, center.meanra, center.meandec, :radius)"))
        .order_by(asc(text("q3c_dist(target.meanra, target.meandec, center.meanra, center.meandec)")))
        .limit(neighbors)
    )
