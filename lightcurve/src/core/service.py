from contextlib import AbstractContextManager
from typing import Any, Callable

import httpx
from db_plugins.db.sql.models import (
    Detection,
    Feature,
    ForcedPhotometry,
    NonDetection,
)
from pymongo.database import Database
from pymongo.cursor import Cursor
from returns.pipeline import is_successful
from returns.result import Failure, Result, Success
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from .exceptions import (
    AtlasNonDetectionError,
    DatabaseError,
    ObjectNotFound,
    SurveyIdError,
    ParseError
)
from .models import DataReleaseDetection as DataReleaseDetectionModel
from .models import Detection as DetectionModel
from .models import Feature as FeatureModel
from .models import ForcedPhotometry as ForcedPhotometryModel
from .models import NonDetection as NonDetectionModel
from config import app_config
import math


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
    survey_id: str = "all",
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
    else:
        handle_error(SurveyIdError(survey_id, "lightcurve"))
    failure = fail_from_list([detections, non_detections, forced_photometry])
    if failure:
        handle_error(failure)
    return handle_success(
        {
            "detections": detections.unwrap(),
            "non_detections": non_detections.unwrap(),
            "forced_photometry": forced_photometry.unwrap(),
        }
    )


def get_detections(
    oid: str,
    survey_id: str = "all",
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
    config = app_config()
    if survey_id in config["tid"]:
        detections_result = _get_all_unique_detections(
            oid, survey_id, session_factory=session_factory, mongo_db=mongo_db
        )
    else:
        handle_error(SurveyIdError(survey_id, "detections"))
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
    detections = {d.candid: d for d in sql_detections + mongo_detections}
    return Success(list(detections.values()))


def get_non_detections(
    oid: str,
    survey_id: str = "all",
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
    if survey_id in ["ztf", "all"]:
        survey_id = "ztf"
        non_detections_result = _get_all_unique_non_detections(
            oid, survey_id, session_factory=session_factory, mongo_db=mongo_db
        )
    elif survey_id == "atlas":
        handle_error(AtlasNonDetectionError())
    else:
        handle_error(SurveyIdError(survey_id, "non detections"))

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
        handle_error(SurveyIdError(survey_id, "period"))

    if is_successful(period_results):
        return handle_success(period_results.unwrap())
    else:
        handle_error(period_results.failure())


def get_forced_photometry(
    oid: str,
    survey_id: str = "all",
    session_factory: Callable[..., AbstractContextManager[Session]] = None,
    mongo_db: Database = None,
    handle_success: Callable[[Any], Any] = default_handle_success,
    handle_error: Callable[[Exception], None] = default_handle_error,
) -> list[ForcedPhotometryModel]:
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
    else:
        handle_error(SurveyIdError(survey_id, "forced photometry"))

    if is_successful(forced_photometry):
        return handle_success(forced_photometry.unwrap())
    else:
        handle_error(forced_photometry.failure())


def _get_unique_forced_photometry(
    oid: str,
    survey_id: str,
    session_factory: Callable[..., AbstractContextManager[Session]] = None,
    mongo_db: Database = None,
) -> Result[list[ForcedPhotometryModel], BaseException]:
    try:
        sql_forced_photometry = _get_forced_photometry_sql(
            session_factory, oid, tid=survey_id
        )
        mongo_forced_photometry = _get_forced_photometry_mongo(
            mongo_db, oid, tid=survey_id
        )
    except DatabaseError as e:
        return Failure(e)
    except ObjectNotFound:
        return Success([])

    forced_photometry = {
        (fp.oid, fp.pid): fp
        for fp in sql_forced_photometry + mongo_forced_photometry
    }
    forced_photometry = list(forced_photometry.values())
    return Success(forced_photometry)


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

    non_detections = {
        (n.oid, n.fid, n.mjd): n
        for n in sql_non_detections + mongo_non_detections
    }

    return Success(list(non_detections.values()))

def _query_detections_sql(session_factory: Callable[..., AbstractContextManager[Session]], oid: str) -> list:
    try:
        with session_factory() as session:
            stmt = select(Detection, text("'ztf'")).filter(
                Detection.oid == oid
            )
            return session.execute(stmt).all()
    except Exception as e:
        raise DatabaseError(e, database="PSQL")

def _parse_sql_detection(result: list) -> list[DetectionModel]:
    try: 
        return [
            _ztf_detection_to_multistream(res[0].__dict__, tid=res[1])
            for res in result
        ]
    except Exception as e:
        raise ParseError(e, "sql detection")


def _get_detections_sql(
    session_factory: Callable[..., AbstractContextManager[Session]],
    oid: str,
    tid: str,
) -> list[DetectionModel]:
    if tid == "atlas":
        return []
    result = _query_detections_sql(session_factory, oid)
    result = _parse_sql_detection(result)
    return result

def _clean_extra_fields(extra_fields: dict[str, Any]) -> dict[str, Any]:
    if "magpsf_corr" in extra_fields and math.isnan(extra_fields.get("magpsf_corr", None)):
        extra_fields["magpsf_corr"] = None
    if "sigmapsf_corr" in extra_fields and math.isnan(extra_fields.get("sigmapsf_corr", None)):
        extra_fields["sigmapsf_corr"] = None
    if "sigmapsf_corr_ext" in extra_fields and math.isnan(extra_fields.get("sigmapsf_corr_ext", None)):
        extra_fields["sigmapsf_corr_ext"] = None
        

def _get_candid(result: dict[str, Any]) -> str:
    """Get the candid from a result dict. If the candid is not present, use the _id field.

    This handles the old and new schema for the candid field in the mongo database.

    :param result: A result dict from the mongo database.
    :type result: dict[str, Any]
    :return: The candid for the result.
    :rtype: str
    """
    candid = result.pop("candid", None)
    if not candid:
        candid = result["_id"]
    return str(candid)

def _clean_parent_candid(result: dict[str, Any]) -> None:
    """Sets the parent_candid to None if it's NaN.

    Note that this modifies the result in place.

    :param result: A result dict from the mongo database.
    :type result: dict[str, Any]
    """
    if result["parent_candid"] is None:
        return
    if math.isnan(result["parent_candid"]):
        result["parent_candid"] = None
    else:
        result["parent_candid"] = int(result["parent_candid"])

def _parse_mongo_detection(res: dict[str, Any]) -> DetectionModel:
    try:
        candid = _get_candid(res)
        _clean_parent_candid(res)
        _clean_extra_fields(res.get("extra_fields", {}))
        return DetectionModel(**res, candid=candid)
    except Exception as e:
        raise ParseError(e, "mongo detection")

def _query_mongo_object(database: Database, oid: str) -> dict[str, Any]:
    obj = database["object"].find_one({"oid": oid})
    if obj is None:
        raise ObjectNotFound(oid)
    return obj

def _query_detections_by_aid(database: Database, aid: str, tid: str = "all") -> Cursor:
    if tid == "all":
        mongo_filter = {"aid": aid}
    elif tid == "atlas" or tid == "ztf":
        mongo_filter = {
            "aid": aid,
            "tid": {"$regex": f"{tid}*", "$options": "i"},
        }
    try:
        return database["detection"].find(mongo_filter)
    except Exception as e:
        raise DatabaseError(e, database="MONGO")

def _get_aid_from_object(obj: dict[str, Any]) -> str:
    return obj["_id"]

def _get_detections_mongo(
    database: Database, oid: str, tid: str
) -> list[DetectionModel]:
    obj = _query_mongo_object(database, oid)
    result = _query_detections_by_aid(database, _get_aid_from_object(obj), tid)
    result = [_parse_mongo_detection(res) for res in result]
    return result


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
        raise DatabaseError(e, database="PSQL")


def _get_non_detections_mongo(
    database: Database, oid: str, tid: str
) -> list[NonDetectionModel]:
    try:
        obj = database["object"].find_one({"oid": oid}, {"_id": 1})
        if obj is None:
            raise ValueError()
        if tid == "all":
            mongo_filter = {"aid": obj["_id"]}
        else:
            mongo_filter = {
                "aid": obj["_id"],
                "tid": {"$regex": f"{tid}*", "$options": "i"},
            }
        result = database["non_detection"].find(mongo_filter)
        result = [NonDetectionModel(**res) for res in result]
        return result
    except ValueError:
        raise ObjectNotFound(oid)
    except Exception as e:
        raise DatabaseError(e, database="MONGO")


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
    except Exception as e:
        return Failure(DatabaseError(e, database="PSQL"))
    if len(result) == 0:
        return Success(FeatureModel(name="Multiband_period", value=0, fid=0, version="0"))
    return Success(result[0])


def _get_forced_photometry_mongo(
    mongo_db: Database,
    oid: str,
    tid: str,
) -> list[ForcedPhotometryModel]:
    try:
        obj = mongo_db["object"].find_one({"oid": oid}, {"_id": 1})
        if obj is None:
            raise ValueError()
        if tid == "all":
            mongo_filter = {"aid": obj["_id"]}
        else:
            mongo_filter = {
                "aid": obj["_id"],
                "tid": {"$regex": f"{tid}*", "$options": "i"},
            }
        result = mongo_db["forced_photometry"].find(mongo_filter)
    except ValueError:
        raise ObjectNotFound(oid)
    except Exception as e:
        raise DatabaseError(e, database="MONGO")
    result = [ForcedPhotometryModel(**res) for res in result]
    return result


def _get_forced_photometry_sql(
    session_factory: Callable[..., AbstractContextManager[Session]],
    oid: str,
    tid: str,
) -> list[ForcedPhotometryModel]:
    if tid == "atlas":
        return []
    try:
        with session_factory() as session:
            stmt = select(ForcedPhotometry, text("'ztf'")).where(
                ForcedPhotometry.oid == oid
            )
            result = session.execute(stmt)
            result = [
                _ztf_forced_photometry_to_multistream(
                    res[0].__dict__, tid=res[1]
                )
                for res in result.all()
            ]
            return result
    except Exception as e:
        raise DatabaseError(e, database="PSQL")


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
    candid = detection.pop("candid")
    return DetectionModel(
        **detection,
        candid=str(candid),
        tid=tid,
        sid=tid,
        mag=detection.pop("magpsf"),
        e_mag=detection.pop("sigmapsf"),
        mag_corr=detection.pop("magpsf_corr", None),
        e_mag_corr=detection.pop("sigmapsf_corr", None),
        e_mag_corr_ext=detection.pop("sigmapsf_corr_ext", None),
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


def _ztf_forced_photometry_to_multistream(
    forced_photometry: dict[str, Any],
    tid: str,
) -> ForcedPhotometryModel:
    """Converts a dictionary representing a forced photometry in the ZTF schema
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
    for field, value in forced_photometry.items():
        if field not in fields and not field.startswith("_"):
            extra_fields[field] = value

    fid_map = {1: "g", 2: "r", 0: None, 12: "gr"}

    forced_photometry["fid"] = fid_map[forced_photometry["fid"]]

    return ForcedPhotometryModel(
        **forced_photometry,
        tid=tid,
        candid=forced_photometry["oid"] + str(forced_photometry["pid"]),
        extra_fields=extra_fields,
    )
