import httpx

from typing import Any, Callable, Sequence, Tuple
from contextlib import AbstractContextManager

from core.config.config import app_config

from returns.pipeline import is_successful
from pymongo.database import Database
from returns.result import Failure, Result, Success
from sqlalchemy.orm import Session

from core.exceptions import (
    AtlasNonDetectionError,
    DatabaseError,
    ObjectNotFound,
    ParseError,
    SurveyIdError,
)

from ..models.forcephotometry import ForcedPhotometry as ForcedPhotometryModel
from ..models.nondetection import NonDetection as NonDetectionModel
from ..models.detection import Detection as DetectionModel
from ..models.feature import Feature as FeatureModel
from ..models.lightcurve_model import DataReleaseDetection as DataReleaseDetectionModel

from .lighcurve_get_queries import _get_non_detections_sql, _get_forced_photometry_sql, _get_period_sql, _get_detections_sql


def default_handle_success(result):
    return result


def default_handle_error(error):
    raise error


def fail_from_list(failable_list: list):
    for el in failable_list:
        if not is_successful(el):
            return el.failure()


def get_detections(
    oid: str,
    survey_id: str = "all",
    session_factory: Callable[..., AbstractContextManager[Session]]
    | None = None,
    mongo_db: Database | None = None,
    handle_success: Callable[[Any], list] = default_handle_success,
    handle_error: Callable[[BaseException], None] = default_handle_error,
) -> list[dict] | None:
    """Retrieves all unique detections from the databases for a given
    object in a given survey.

    :param oid: oid for the object.
    :type oid: str
    :param survey_id: id for the survey, can be "ztf" or "atlas"
    :type survey_id: str
    :param session_factory: Session factory for SQL requests.
    :type session_factory: Callable[..., AbstractContextManager[Session]]
    :param mongo_db: Mongo database for mongo requests.
    :type mongo_db: Database
    :param handle_success: Callback for handling a success.
    :type handle_success: Callable[[Any], list]
    :param handle_error: Callback for handling failure.
    :type handle_error: Callable[Exception, None]
    :return: The result of calling handle_success with a list containing
    all unique Detection objects in the databases.
    :rtype: list[DetectionModel]
    """
    config = app_config()
    if survey_id in config["tid"]:
        detections_result = _get_all_unique_detections(
            oid, survey_id, session_factory=session_factory, mongo_db=mongo_db
        )
        if is_successful(detections_result):
            return handle_success(detections_result.unwrap())
        else:
            handle_error(detections_result.failure())
    else:
        handle_error(SurveyIdError(survey_id, "detections"))


def get_non_detections(
    oid: str,
    survey_id: str = "all",
    session_factory: Callable[..., AbstractContextManager[Session]]
    | None = None,
    mongo_db: Database | None = None,
    handle_success: Callable[[Any], list] = default_handle_success,
    handle_error: Callable[[BaseException], None] = default_handle_error,
) -> list[NonDetectionModel] | None:
    """Retrieves all unique non-detections from the databases for a given
    object in a given survey.

    :param oid: oid for the object.
    :type oid: str
    :param survey_id: id for the survey, can be "ztf" or "atlas"
    :type survey_id: str
    :param session_factory: Session factory for SQL requests.
    :type session_factory: Callable[..., AbstractContextManager[Session]]
    :param mongo_db: Mongo database for mongo requests.
    :type mongo_db: Database
    :param handle_success: Callback for handling a success.
    :type handle_success: Callable[[Any], list]
    :param handle_error: Callback for handling failure.
    :type handle_error: Callable[[Exception], None]
    :return: The result of calling handle_success with a list containing
    all unique NonDetection objects in the databases.
    :rtype: list[NonDetectionModel]
    """
    if survey_id in ["ztf", "all"]:
        survey_id = "ztf"
        non_detections_result = _get_all_unique_non_detections(
            oid, survey_id, session_factory=session_factory, mongo_db=mongo_db
        )
        if is_successful(non_detections_result):
            return handle_success(non_detections_result.unwrap())
        else:
            handle_error(non_detections_result.failure())
    elif survey_id == "atlas":
        handle_error(AtlasNonDetectionError())
    else:
        handle_error(SurveyIdError(survey_id, "non detections"))


def get_forced_photometry(
    oid: str,
    survey_id: str = "all",
    session_factory: Callable[..., AbstractContextManager[Session]]
    | None = None,
    mongo_db: Database | None = None,
    handle_success: Callable[[Any], Any] = default_handle_success,
    handle_error: Callable[[BaseException], None] = default_handle_error,
) -> list[ForcedPhotometryModel] | None:
    """Retrieves the forced photometry from an object

    :param oid: oid for the object.
    :type oid: str
    :param survey_id: id for the survey, can be "ztf" or "atlas"
    :type survey_id: str
    :param session_factory: Session factory for SQL requests.
    :type session_factory: Callable[..., AbstractContextManager[Session]]
    :param mongo_db: Mongo database for mongo requests.
    :type mongo_db: Database
    :param handle_success: Callback for handling a success.
    :type handle_success: Callable[[Any], list]
    :param handle_error: Callback for handling failure.
    :type handle_error: Callable[[Exception], None]
    :return: The result of calling handle_success with a dictionary
    containing all detections and non_detections with removed duplicates.
    :rtype: list[ForcedPhotometryModel]
    """
    config = app_config()
    if survey_id in config["tid"]:
        forced_photometry = _get_unique_forced_photometry(
            oid, survey_id, session_factory, mongo_db
        )
        if is_successful(forced_photometry):
            return handle_success(forced_photometry.unwrap())
        else:
            handle_error(forced_photometry.failure())
    else:
        handle_error(SurveyIdError(survey_id, "forced photometry"))


def get_period(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]]
    | None = None,
    handle_success: Callable[[Any], FeatureModel] = default_handle_success,
    handle_error: Callable[[BaseException], None] = default_handle_error,
) -> FeatureModel | None:
    """Retrieves the period feature from a given object. Currently only works for
    ZTF on the SQL DB.

    If multiple verions of the feature are presents, returns the first one.

    :param oid: oid for the object.
    :type oid: str
    :param survey_id: id for the survey, can be "ztf" or "atlas"
    :type survey_id: str
    :param session_factory: Session factory for SQL requests.
    :type session_factory: Callable[..., AbstractContextManager[Session]]
    :param mongo_db: Mongo database for mongo requests.
    :type mongo_db: Database
    :param handle_success: Callback for handling a success.
    :type handle_success: Callable[[Any], list]
    :param handle_error: Callback for handling failure.
    :type handle_error: Callable[[Exception], None]
    :return: The result of calling handle_success with a Feature corresponding the the period.
    :rtype: FetureModel
    """
    if survey_id == "ztf":
        period_results = _get_period_sql(oid, session_factory)
        if is_successful(period_results):
            return handle_success(period_results.unwrap())
        else:
            handle_error(period_results.failure())
    elif survey_id == "atlas":
        handle_error(NotImplementedError())
    else:
        handle_error(SurveyIdError(survey_id, "period"))


def get_lightcurve(
    oid: str,
    survey_id: str = "all",
    session_factory: Callable[..., AbstractContextManager[Session]]
    | None = None,
    mongo_db: Database | None = None,
    handle_success: Callable[[Any], Any] = default_handle_success,
    handle_error: Callable[[BaseException], None] = default_handle_error,
) -> dict[str, list[DetectionModel] | list[NonDetectionModel]] | None:
    """Retrieves both unique detections and non detections for a given object in
    a given survey.

    :param oid: oid for the object.
    :type oid: str
    :param survey_id: id for the survey, can be "ztf" or "atlas"
    :type survey_id: str
    :param session_factory: Session factory for SQL requests.
    :type session_factory: Callable[..., AbstractContextManager[Session]]
    :param mongo_db: Mongo database for mongo requests.
    :type mongo_db: Database
    :param handle_success: Callback for handling a success.
    :type handle_success: Callable[[Any], list]
    :param handle_error: Callback for handling failure.
    :type handle_error: Callable[[Exception], None]
    :return: The result of calling handle_success with a dictionary
    containing all detections and non_detections with removed duplicates.
    :rtype: dict[str, list[DetectionModel] | list[NonDetectionModel]]
    """
    config = app_config()
    if survey_id in config["tid"]:
        detections = _get_all_unique_detections(
            oid, survey_id, session_factory=session_factory, mongo_db=mongo_db
        )
        non_detections = _get_all_unique_non_detections(
            oid, survey_id, session_factory=session_factory, mongo_db=mongo_db
        )
        forced_photometry = _get_unique_forced_photometry(
            oid, survey_id, session_factory, mongo_db
        )
        failure = fail_from_list(
            [detections, non_detections, forced_photometry]
        )
        if failure:
            handle_error(failure)
        return handle_success(
            {
                "detections": detections.unwrap(),
                "non_detections": non_detections.unwrap(),
                "forced_photometry": forced_photometry.unwrap(),
            }
        )
    else:
        handle_error(SurveyIdError(survey_id, "lightcurve"))


async def get_data_release(
    ra: float, dec: float, radius: float = 1.5
) -> tuple[list[dict[str, Any]], dict[str, list[DataReleaseDetectionModel]]]:
    dr_params = {
        "ra": ra,
        "dec": dec,
        "radius": radius,
    }
    datareleases = []
    detections = {}
    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.get(
            "https://api.alerce.online/ztf/dr/v1/light_curve/",
            params=dr_params,
        )
        datareleases = [
            {
                k: dr_data[k]
                for k in ("_id", "filterid", "nepochs", "fieldid", "rcid")
            }
            for dr_data in resp.json()
        ]
        for datarelease in datareleases:
            datarelease["checked"] = False
        detections = {
            dr_data["_id"]: [
                DataReleaseDetectionModel(
                    mjd=dr_data["hmjd"][i],
                    mag_corr=dr_data["mag"][i],
                    e_mag_corr_ext=dr_data["magerr"][i],
                    fid=dr_data["filterid"] + 100,
                    field=dr_data["fieldid"],
                    objectid=dr_data["_id"],
                    corrected=True,
                )
                for i in range(dr_data["nepochs"])
            ]
            for dr_data in resp.json()
        }
    return datareleases, detections

def remove_duplicate_forced_photometry_by_pid(
    detections: list, forced_photometry: list
):
    new_forced_photometry = []
    pids = {}
    size = max(len(detections), len(forced_photometry))
    for i in range(size):
        try:
            dpid = detections[i]["pid"]
            if dpid not in pids:
                pids[dpid] = None
            else:
                if pids[dpid] is not None:
                    new_forced_photometry.pop(pids[dpid])
        except IndexError:
            pass
        try:
            fpid = forced_photometry[i]["pid"]
            if fpid not in pids:
                pids[fpid] = i
                new_forced_photometry.append(forced_photometry[i])
        except IndexError:
            pass
    return new_forced_photometry


def _get_all_unique_detections(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]]
    | None = None,
    mongo_db: Database | None = None,
) -> Result[list[DetectionModel], BaseException]:
    try:
        assert session_factory is not None
        sql_detections = _get_detections_sql(
            session_factory, oid, tid=survey_id
        )
        return Success(sql_detections)
    except ObjectNotFound:
        sql_detections = []
        return Success(sql_detections)
    except DatabaseError as e:
        return Failure(e)


def _get_all_unique_non_detections(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]]
    | None = None,
    mongo_db: Database | None = None,
) -> Result[list[NonDetectionModel], BaseException]:
    try:
        assert session_factory is not None
        sql_non_detections = _get_non_detections_sql(
            session_factory, oid, tid=survey_id
        )
        return Success(sql_non_detections)
    except ObjectNotFound:
        sql_non_detections = []
        return Success(sql_non_detections)
    except DatabaseError as e:
        return Failure(e)
    

def _get_unique_forced_photometry(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]]
    | None = None,
    mongo_db: Database | None = None,
) -> Result[list[ForcedPhotometryModel], BaseException]:
    try:
        assert session_factory is not None
        sql_forced_photometry = _get_forced_photometry_sql(
            session_factory, oid, tid=survey_id
        )
        return Success(sql_forced_photometry)
    except ObjectNotFound:
        sql_forced_photometry = []
        return Success(sql_forced_photometry)
    except DatabaseError as e:
        return Failure(e)