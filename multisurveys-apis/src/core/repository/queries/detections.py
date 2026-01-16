from typing import Callable, ContextManager, List, Tuple
from db_plugins.db.sql.models import ZtfDetection, Detection, LsstDetection
from sqlalchemy.orm import Session
from sqlalchemy import select, text, and_, desc


def get_all_unique_detections_sql(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., ContextManager[Session]],
):
    with session_factory() as session:
        if survey_id == "ztf":
            stmt = build_statement(ZtfDetection, oid)
        elif survey_id == "lsst":
            stmt = build_statement(LsstDetection, oid)
        else:
            stmt = text("")

        return session.execute(stmt).all()


def build_statement(model_id, oid):
    stmt = (
        select(model_id, Detection)
        .join(
            Detection,
            and_(
                Detection.oid == model_id.oid,
                Detection.measurement_id == model_id.measurement_id,
            ),
        )
        .where(model_id.oid == oid)
        .limit(10)
    )

    return stmt


def get_detections_by_list(
    session_factory: Callable[..., ContextManager[Session]],
):
    def _get_detections_by_list(args: Tuple[List[int], str]):
        oids, survey_id = args

        if survey_id.lower() == "ztf":
            detection_model = ZtfDetection
        elif survey_id.lower() == "lsst":
            detection_model = LsstDetection
        else:
            raise ValueError("Survey not supported")
        stmt = (
            select(detection_model, Detection)
            .join(
                Detection,
                and_(
                    Detection.oid == detection_model.oid,
                    Detection.measurement_id == detection_model.measurement_id,
                ),
            )
            .where(detection_model.oid.in_(oids))
        )
        with session_factory() as session:
            return (
                session.execute(stmt).all(),
                survey_id,
            )  # we are passing this to a pipe expecting the rows and survey_id

    return _get_detections_by_list

def get_ordered_detections_sql(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., ContextManager[Session]],
):
    with session_factory() as session:
        if survey_id.lower() == "ztf":
            detection_model = ZtfDetection
        elif survey_id.lower() == "lsst":
            detection_model = LsstDetection
        else:
            raise ValueError("Survey not supported")

        stmt = (
            select(detection_model, Detection)
            .join(
                Detection,
                and_(
                    Detection.oid == detection_model.oid,
                    Detection.measurement_id == detection_model.measurement_id,
                ),
            )
            .where(
                detection_model.oid == oid
            ).order_by(desc(Detection.mjd))
        )

        return session.execute(stmt).all()
    
