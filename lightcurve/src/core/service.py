from contextlib import AbstractContextManager
from typing import Any, Callable

import httpx
from db_plugins.db.sql.models import (
    Detection,
    Feature,
    FeatureVersion,
    NonDetection,
)
from pymongo.database import Database
from returns.pipeline import is_successful
from returns.result import Failure, Result, Success
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from .exceptions import (
    AtlasNonDetectionError,
    DatabaseError,
    ObjectNotFound,
    SurveyIdError,
)
from .models import DataReleaseDetection as DataReleaseDetectionModel
from .models import Detection as DetectionModel
from .models import Feature as FeatureModel
from .models import NonDetection as NonDetectionModel


def default_handle_success(result):
    return result


def default_handle_error(error):
    raise error


def fail_from_list(failable_list: list):
    for el in failable_list:
        if not is_successful(el):
            return el.failure()


def get_lightcurve(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]] = None,
    mongo_db: Database = None,
    handle_success: Callable[[Any], Any] = default_handle_success,
    handle_error: Callable[[Exception], None] = default_handle_error,
) -> dict[str, list[DetectionModel] | list[NonDetectionModel]]:
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
    if survey_id in ["ztf", "atlas"]:
        detections = _get_all_unique_detections(
            oid, survey_id, session_factory=session_factory, mongo_db=mongo_db
        )
        non_detections = _get_all_unique_non_detections(
            oid, survey_id, session_factory=session_factory, mongo_db=mongo_db
        )
    else:
        handle_error(SurveyIdError(survey_id))
    failure = fail_from_list([detections, non_detections])
    if failure:
        handle_error(failure)
    if len(detections.unwrap()) == 0 and len(non_detections.unwrap()) == 0:
        handle_error(ObjectNotFound(oid))
    return handle_success(
        {
            "detections": detections.unwrap(),
            "non_detections": non_detections.unwrap(),
        }
    )


def get_detections(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]] = None,
    mongo_db: Database = None,
    handle_success: Callable[[Any], list] = default_handle_success,
    handle_error: Callable[[Exception], None] = default_handle_error,
) -> list[DetectionModel]:
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
    if survey_id in ["ztf", "atlas"]:
        detections_result = _get_all_unique_detections(
            oid, survey_id, session_factory=session_factory, mongo_db=mongo_db
        )
    else:
        handle_error(SurveyIdError(survey_id))

    if is_successful(detections_result):
        return handle_success(detections_result.unwrap())
    else:
        handle_error(detections_result.failure())


def _get_all_unique_detections(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]] = None,
    mongo_db: Database = None,
) -> Result[list[DetectionModel], BaseException]:
    try:
        sql_detections = _get_detections_sql(
            session_factory, oid, tid=survey_id
        )
    except ObjectNotFound:
        sql_detections = []
    except DatabaseError as e:
        return Failure(e)

    try:
        mongo_detections = _get_detections_mongo(mongo_db, oid, tid=survey_id)
    except ObjectNotFound:
        mongo_detections = []
    except DatabaseError as e:
        return Failure(e)

    detections = list(set(sql_detections + mongo_detections))

    return Success(detections)


def get_non_detections(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]] = None,
    mongo_db: Database = None,
    handle_success: Callable[[Any], list] = default_handle_success,
    handle_error: Callable[[Exception], None] = default_handle_error,
) -> list[NonDetectionModel]:
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
    if survey_id == "ztf":
        non_detections_result = _get_all_unique_non_detections(
            oid, survey_id, session_factory=session_factory, mongo_db=mongo_db
        )
    elif survey_id == "atlas":
        handle_error(AtlasNonDetectionError())
    else:
        handle_error(SurveyIdError(survey_id))

    if is_successful(non_detections_result):
        return handle_success(non_detections_result.unwrap())
    else:
        handle_error(non_detections_result.failure())


def get_period(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]] = None,
    mongo_db: Database = None,
    handle_success: Callable[[Any], list] = default_handle_success,
    handle_error: Callable[[Exception], None] = default_handle_error,
) -> FeatureModel:
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
    elif survey_id == "atlas":
        handle_error(NotImplementedError)
    else:
        handle_error(SurveyIdError(survey_id))

    if is_successful(period_results):
        return handle_success(period_results.unwrap())
    else:
        handle_error(period_results.failure())


def _get_all_unique_non_detections(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]] = None,
    mongo_db: Database = None,
) -> Result[list[NonDetectionModel], BaseException]:
    try:
        sql_non_detections = _get_non_detections_sql(
            session_factory, oid, tid=survey_id
        )
    except ObjectNotFound:
        sql_non_detections = []
    except DatabaseError as e:
        return Failure(e)

    try:
        mongo_non_detections = _get_non_detections_mongo(
            mongo_db, oid, tid=survey_id
        )
    except ObjectNotFound:
        mongo_non_detections = []
    except DatabaseError as e:
        return Failure(e)

    non_detections = list(set(sql_non_detections + mongo_non_detections))

    return Success(non_detections)


def _get_detections_sql(
    session_factory: Callable[..., AbstractContextManager[Session]],
    oid: str,
    tid: str,
) -> list[DetectionModel]:
    if tid == "atlas":
        return []
    try:
        with session_factory() as session:
            stmt = select(Detection, text("'ztf'")).filter(
                Detection.oid == oid
            )
            result = session.execute(stmt)
            result = [
                _ztf_detection_to_multistream(res[0].__dict__, tid=res[1])
                for res in result.all()
            ]
            return result
    except Exception as e:
        raise DatabaseError(e)


def _get_detections_mongo(
    database: Database, oid: str, tid: str
) -> list[DetectionModel]:
    try:
        obj = database["object"].find_one({"oid": oid}, {"_id": 1})
        if obj is None:
            raise ValueError()
        result = database["detection"].find(
            {"aid": obj["_id"], "oid": oid, "tid": tid}
        )
        result = [DetectionModel(**res, candid=res["_id"]) for res in result]
        return result
    except ValueError as e:
        raise ObjectNotFound(oid)
    except Exception as e:
        raise DatabaseError(e)


def _get_non_detections_sql(
    session_factory: Callable[..., AbstractContextManager[Session]],
    oid: str,
    tid: str,
) -> list[NonDetectionModel]:
    if tid == "atlas":
        return []
    try:
        with session_factory() as session:
            stmt = select(NonDetection, text("'ztf'")).where(
                NonDetection.oid == oid
            )
            result = session.execute(stmt)
            result = [
                _ztf_non_detection_to_multistream(res[0].__dict__, tid=res[1])
                for res in result.all()
            ]
            return result
    except Exception as e:
        raise DatabaseError(e)


def _get_non_detections_mongo(
    database: Database, oid: str, tid: str
) -> list[NonDetectionModel]:
    try:
        obj = database["object"].find_one({"oid": oid}, {"_id": 1})
        if obj is None:
            raise ValueError()
        result = database["non_detection"].find(
            {"aid": obj["_id"], "oid": oid, "tid": tid}
        )
        result = [NonDetectionModel(**res) for res in result]
        return result
    except ValueError as e:
        raise ObjectNotFound(oid)
    except Exception as e:
        raise DatabaseError(e)


async def get_data_release(
    ra: float, dec: float, radius: float = 1.5
) -> tuple[dict[str, Any], dict[str, list[DataReleaseDetectionModel]]]:
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


def _get_period_mongo():
    pass


def _get_period_sql(
    oid: str,
    session_factory: Callable[..., AbstractContextManager[Session]],
) -> Result[FeatureModel, BaseException]:
    try:
        with session_factory() as session:
            stmt = (
                select(Feature)
                .where(Feature.oid == oid)
                .where(Feature.name == "Multiband_period")
            )
            result = session.execute(stmt)
            result = [FeatureModel(**res[0].__dict__) for res in result.all()]
            return Success(result[0])
    except Exception as e:
        return Failure(DatabaseError(e))


def _ztf_detection_to_multistream(
    detection: dict[str, Any],
    tid: str,
) -> DetectionModel:
    """Converts a dictionary representing a detection in the ZTF schema
    to the Multistream schema defined in models.py. Separates every field
    that's without a correspondence in the schema into extra_fields.
    :param detection: Dictionary representing a detection.
    :param tid: Telescope id for this detection.
    :return: A Detection with the converted data."""
    fields = {
        "candid",
        "oid",
        "sid",
        "aid",
        "tid",
        "mjd",
        "fid",
        "ra",
        "e_ra",
        "dec",
        "e_dec",
        "magpsf",
        "sigmapsf",
        "magpsf_corr",
        "sigmapsf_corr",
        "sigmapsf_corr_ext",
        "isdiffpos",
        "corrected",
        "dubious",
        "parent_candid",
        "has_stamp",
    }

    extra_fields = {}
    for field, value in detection.items():
        if field not in fields and not field.startswith("_"):
            extra_fields[field] = value

    return DetectionModel(
        **detection,
        tid=tid,
        mag=detection["magpsf"],
        e_mag=detection["sigmapsf"],
        mag_corr=detection.get("magpsf_corr", None),
        e_mag_corr=detection.get("sigmapsf_corr", None),
        e_mag_corr_ext=detection.get("sigmapsf_corr_ext", None),
        extra_fields=extra_fields,
    )


def _ztf_non_detection_to_multistream(
    non_detections: dict[str, Any],
    tid: str,
) -> NonDetectionModel:
    """Converts a dictionary representing a non detection in the ZTF schema
    to the Multistream schema defined in models.py.
    :param non_detection: Dictionary representing a non_detection.
    :param tid: Telescope id for this detection.
    :return: A NonDetection with the converted data."""
    return NonDetectionModel(
        aid=non_detections.get("aid", None),
        tid=tid,
        mjd=non_detections["mjd"],
        fid=non_detections["fid"],
        oid=non_detections.get("oid", None),
        sid=non_detections.get("sid", None),
        diffmaglim=non_detections.get("diffmaglim", None),
    )
