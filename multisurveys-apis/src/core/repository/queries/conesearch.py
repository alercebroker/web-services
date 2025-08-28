from typing import Callable, ContextManager, List, Tuple
from db_plugins.db.sql.models import Object
from numpy import int64
from sqlalchemy import asc, select, text
from sqlalchemy.orm import Session, aliased


def conesearch_coordinates(
    session_factory: Callable[..., ContextManager[Session]],
):
    def _conesearch(args: Tuple[float, float, float, int]) -> List[Object]:
        ra, dec, radius, neighbors = args
        stmt = _build_statement_coordinates(neighbors)
        with session_factory() as session:
            result = session.execute(
                stmt, {"ra": ra, "dec": dec, "radius": radius}
            ).all()
            return [row[0] for row in result]

    return _conesearch


def _build_statement_coordinates(neighbors: int):
    return (
        select(Object)
        .where(text("q3c_radial_query(meanra, meandec, :ra, :dec, :radius)"))
        .order_by(asc(text("q3c_dist(meanra, meandec, :ra, :dec)")))
        .limit(neighbors)
    )


def conesearch_oid(session_factory: Callable[..., ContextManager[Session]]):
    def _conesearch(args: Tuple[int64, float, int]) -> List[Object]:
        oid, radius, neighbors = args
        stmt = _build_statement_oid(oid, neighbors)
        with session_factory() as session:
            result = session.execute(stmt, {"radius": radius}).all()
            return [row[0] for row in result]

    return _conesearch


def _build_statement_oid(oid: int64, neighbors: int):
    # Create aliases for the Object table
    center_obj = aliased(Object, name="center")
    target_obj = aliased(Object, name="target")

    # Build the query using q3c_radial_query function
    return (
        select(target_obj.oid, target_obj.meanra, target_obj.meandec)
        .select_from(center_obj, target_obj)
        .where(center_obj.oid == oid.item())
        .where(
            text(
                "q3c_radial_query(target.meanra, target.meandec, center.meanra, center.meandec, :radius)"
            )
        )
        .order_by(
            asc(
                text(
                    "q3c_dist(target.meanra, target.meandec, center.meanra, center.meandec)"
                )
            )
        )
        .limit(neighbors)
    )
