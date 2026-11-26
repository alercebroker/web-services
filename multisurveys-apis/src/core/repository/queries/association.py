"""Read queries on the object association tables (see core/repository/association_models.py).

Each function is one statement: every query is a round trip to a distant database.
"""

from typing import Callable, ContextManager, Iterable

from db_plugins.db.sql.models_pipeline import Object
from sqlalchemy import BigInteger, Row, SmallInteger, and_, func, literal, or_, select, true, tuple_, union
from sqlalchemy.orm import Session, aliased

from core.repository.association_models import AssociationMethod, ObjectAssociation, ObjectGroup

SessionFactory = Callable[..., ContextManager[Session]]


def get_counterpart_rows(session_factory: SessionFactory, objects: Iterable[tuple[int, int]]) -> list[Row]:
    """Every other member of the groups of ``objects`` ((oid, sid) tuples).

    One row per (listed object, member): ``listed_oid``, ``listed_sid``, ``oid``, ``sid``, the ``dist`` and
    ``score`` of their direct pair (None when the member joined the group through another member) and the
    member's ``n_det``, ``meanra`` and ``meandec`` (None when it isn't in the object table). Objects without a
    group give no rows.

    A pair is stored once, in either order, so it is looked up in both: each join uses its own index (the
    primary key starts with (oid_a, sid_a); (oid_b, sid_b) has an index of its own).
    """
    objects = list(objects)
    if not objects:
        return []
    listed = aliased(ObjectGroup)
    member = aliased(ObjectGroup)
    forward = aliased(ObjectAssociation)
    backward = aliased(ObjectAssociation)

    def pair_between(pair, a, b):
        return and_(
            pair.oid_a == a.oid,
            pair.sid_a == a.sid,
            pair.oid_b == b.oid,
            pair.sid_b == b.sid,
            pair.method_version == listed.method_version,
        )

    stmt = (
        select(
            listed.oid.label("listed_oid"),
            listed.sid.label("listed_sid"),
            member.oid,
            member.sid,
            func.coalesce(forward.dist, backward.dist).label("dist"),
            func.coalesce(forward.score, backward.score).label("score"),
            Object.n_det,
            Object.meanra,
            Object.meandec,
        )
        .join(member, and_(member.group_id == listed.group_id, or_(member.oid != listed.oid, member.sid != listed.sid)))
        .outerjoin(forward, pair_between(forward, listed, member))
        .outerjoin(backward, pair_between(backward, member, listed))
        .outerjoin(Object, and_(Object.oid == member.oid, Object.sid == member.sid))
        .where(tuple_(listed.oid, listed.sid).in_(objects))
    )
    with session_factory() as session:
        return session.execute(stmt).all()


def get_group_neighbourhood(session_factory: SessionFactory, oid: int, sid: int) -> list[Row]:
    """What the light curve's group panel shows about one object: its group, and the pairs around it.

    The neighbourhood is the object, the other members of its group, and every object paired with a member. One
    row per object of the neighbourhood and pair with that object on its ``a`` side, so each pair comes once:

    - the object: ``oid``, ``sid``, ``is_member``, and its ``n_det``, ``firstmjd`` and ``lastmjd`` (None when it
      isn't in the object table);
    - the pair: ``oid_a``, ``sid_a``, ``oid_b``, ``sid_b``, ``dist``, ``score`` (None when the object has no pair
      on its ``a`` side);
    - on every row, the group's ``group_id`` and ``group_version`` (None without a group) and the
      ``method_version`` and ``params`` of its method, or of the newest one for an object without a group.

    No rows when there is no method at all.
    """
    viewed = (
        select(ObjectGroup.group_id, ObjectGroup.group_version, ObjectGroup.method_version)
        .where(ObjectGroup.oid == oid, ObjectGroup.sid == sid)
        .cte("viewed")
    )
    newest_method = select(func.max(AssociationMethod.method_version)).correlate(None).scalar_subquery()
    method = (
        select(AssociationMethod.method_version, AssociationMethod.params)
        .where(
            AssociationMethod.method_version
            == func.coalesce(select(viewed.c.method_version).scalar_subquery(), newest_method)
        )
        .cte("method")
    )
    members = union(
        select(ObjectGroup.oid, ObjectGroup.sid).where(
            ObjectGroup.group_id == select(viewed.c.group_id).scalar_subquery()
        ),
        select(literal(oid, BigInteger).label("oid"), literal(sid, SmallInteger).label("sid")),
    ).cte("members")

    # Pairs with a member on either side, of the method's version. Each side joins through its own index.
    pair = ObjectAssociation
    pair_columns = [pair.oid_a, pair.sid_a, pair.oid_b, pair.sid_b, pair.dist, pair.score]
    of_method = pair.method_version == select(method.c.method_version).scalar_subquery()
    pairs = union(
        select(*pair_columns)
        .join(members, and_(pair.oid_a == members.c.oid, pair.sid_a == members.c.sid))
        .where(of_method),
        select(*pair_columns)
        .join(members, and_(pair.oid_b == members.c.oid, pair.sid_b == members.c.sid))
        .where(of_method),
    ).cte("pairs")

    nodes = union(
        select(members.c.oid, members.c.sid),
        select(pairs.c.oid_a, pairs.c.sid_a),
        select(pairs.c.oid_b, pairs.c.sid_b),
    ).cte("nodes")
    member = members.alias("member")

    stmt = (
        select(
            nodes.c.oid,
            nodes.c.sid,
            member.c.oid.is_not(None).label("is_member"),
            Object.n_det,
            Object.firstmjd,
            Object.lastmjd,
            pairs.c.oid_a,
            pairs.c.sid_a,
            pairs.c.oid_b,
            pairs.c.sid_b,
            pairs.c.dist,
            pairs.c.score,
            viewed.c.group_id,
            viewed.c.group_version,
            method.c.method_version,
            method.c.params,
        )
        .select_from(nodes)
        .join(method, true())
        .outerjoin(viewed, true())
        .outerjoin(member, and_(member.c.oid == nodes.c.oid, member.c.sid == nodes.c.sid))
        .outerjoin(Object, and_(Object.oid == nodes.c.oid, Object.sid == nodes.c.sid))
        .outerjoin(pairs, and_(pairs.c.oid_a == nodes.c.oid, pairs.c.sid_a == nodes.c.sid))
    )
    with session_factory() as session:
        return session.execute(stmt).all()
