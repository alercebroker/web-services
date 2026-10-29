from contextlib import AbstractContextManager
from typing import Callable

from db_plugins.db.sql.models_pipeline import Feature, FeatureNameLut, FeatureVersionLut, Object
from sqlalchemy import and_, select
from sqlalchemy.orm import Session


def object_exists(oid: int, sid: int, session_factory: Callable[..., AbstractContextManager[Session]]) -> bool:
    with session_factory() as session:
        stmt = select(Object.oid).where(Object.oid == oid, Object.sid == sid).limit(1)
        return session.execute(stmt).first() is not None


def get_features(
    oid: int,
    sid: int,
    session_factory: Callable[..., AbstractContextManager[Session]],
    name: str | None = None,
    band: int | None = None,
    version: str | None = None,
):
    """The features of one object, with their names and versions resolved from the lookup tables.

    The feature table's key starts with oid, so this is an index lookup even on the full table.
    """
    stmt = (
        select(
            FeatureNameLut.feature_name.label("name"),
            Feature.value,
            Feature.band,
            FeatureVersionLut.version_name.label("version"),
        )
        .join(FeatureNameLut, and_(FeatureNameLut.feature_id == Feature.feature_id, FeatureNameLut.sid == Feature.sid))
        .outerjoin(
            FeatureVersionLut,
            and_(FeatureVersionLut.version_id == Feature.version, FeatureVersionLut.sid == Feature.sid),
        )
        .where(Feature.oid == oid, Feature.sid == sid)
        .order_by(FeatureNameLut.feature_name, Feature.band)
    )
    if name is not None:
        stmt = stmt.where(FeatureNameLut.feature_name == name)
    if band is not None:
        stmt = stmt.where(Feature.band == band)
    if version is not None:
        stmt = stmt.where(FeatureVersionLut.version_name == version)

    with session_factory() as session:
        return session.execute(stmt).mappings().all()
