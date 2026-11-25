"""Read-only models for the multisurvey object association tables.

The association pipeline writes these tables; the APIs only read them. They aren't in db-plugins yet, so they
are declared here on their own metadata. Their schema comes from ``ASSOCIATION_SCHEMA``, read once at import
(``association`` when unset; the group panel is off then anyway, see lightcurve_api/services/group_service.py).

Objects are always named by ``(oid, sid)``. ``group_id`` is internal: it can change when groups merge or split.
"""

import os

from sqlalchemy import BigInteger, DateTime, Float, Integer, SmallInteger, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

ASSOCIATION_SCHEMA = os.getenv("ASSOCIATION_SCHEMA") or "association"


class AssociationBase(DeclarativeBase):
    pass


class AssociationMethod(AssociationBase):
    """One row per method version: the score and the grouping parameters it used."""

    __tablename__ = "association_method_lut"
    __table_args__ = {"schema": ASSOCIATION_SCHEMA}

    method_version: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    method_name: Mapped[str] = mapped_column(String)
    params: Mapped[dict] = mapped_column(JSONB)


class ObjectAssociation(AssociationBase):
    """A pair of objects that may be the same source. Stored once, with (sid_a, oid_a) < (sid_b, oid_b)."""

    __tablename__ = "object_association"
    __table_args__ = {"schema": ASSOCIATION_SCHEMA}

    oid_a: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    sid_a: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    oid_b: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    sid_b: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    method_version: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    dist: Mapped[float] = mapped_column(Float)  # arcseconds
    score: Mapped[float] = mapped_column(Float)  # probability that both are the same source
    computed_at = mapped_column(DateTime(timezone=True))


class ObjectGroup(AssociationBase):
    """Which group each object belongs to. Objects without a group have no row."""

    __tablename__ = "object_group"
    __table_args__ = {"schema": ASSOCIATION_SCHEMA}

    oid: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    sid: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    group_id: Mapped[int] = mapped_column(BigInteger, index=True)
    group_version: Mapped[int] = mapped_column(Integer)
    method_version: Mapped[int] = mapped_column(SmallInteger)
