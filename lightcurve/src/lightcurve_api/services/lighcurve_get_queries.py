from typing import Any, Callable, Sequence, Tuple
from contextlib import AbstractContextManager

from sqlalchemy.orm import Session
from returns.result import Failure, Result, Success

from lightcurve_api.models.nondetection import NonDetection as NonDetectionModel
from lightcurve_api.models.forcephotometry import ForcedPhotometry as ForcedPhotometryModel
from lightcurve_api.models.feature import Feature as FeatureModel
from lightcurve_api.models.detection import Detection as DetectionModel

from lightcurve_api.parser.lightcurve_parser import _ztf_non_detection_to_multistream, _ztf_forced_photometry_to_multistream, _parse_sql_detection

from core.repository.queries.non_detections import _query_non_detections_sql
from core.repository.queries.force_photometry import _query_forced_photometry_sql
from core.repository.queries.Feature import _query_period_sql
from core.repository.queries.detections import _query_detections_sql

def _get_non_detections_sql(
    session_factory: Callable[..., AbstractContextManager[Session]],
    oid: str,
    tid: str,
) -> list[NonDetectionModel]:
    if tid == "atlas":
        return []

    result = _query_non_detections_sql(session_factory, oid, tid)
    result = [
        _ztf_non_detection_to_multistream(res[0].__dict__, tid=res[1])
        for res in result
    ]
    return result

def _get_forced_photometry_sql(
    session_factory: Callable[..., AbstractContextManager[Session]],
    oid: str,
    tid: str,
) -> list[ForcedPhotometryModel]:
    if tid == "atlas":
        return []
    
    result = _query_forced_photometry_sql(session_factory, oid, tid)
    result = [
        _ztf_forced_photometry_to_multistream(
            res[0].__dict__, tid=res[1]
        )
        for res in result
    ]
    return result

def _get_period_sql(
    oid: str,
    session_factory: Callable[..., AbstractContextManager[Session]] | None,
) -> Result[FeatureModel, BaseException]:

    result = _query_period_sql(oid, session_factory)
    result = [FeatureModel(**res[0].__dict__) for res in result]
    result = list(
        filter(
            lambda x: "23." not in x.version
            and "25." not in x.version
            and x.value != None,
            result,
        )
    )
    if len(result) == 0:
        return Success(
            FeatureModel(name="Multiband_period", value=0, fid=0, version="0")
        )
    return Success(result[0])

def _get_detections_sql(
    session_factory: Callable[..., AbstractContextManager[Session]],
    oid: str,
    tid: str,
) -> list[DetectionModel]:
    if tid == "atlas":
        return []
    result = list(_query_detections_sql(session_factory, oid))
    result = _parse_sql_detection(result)
    return result