from numpy import isin
from returns.result import Success, Failure
from unittest.mock import patch
import pytest
from api.database_access.commands import InterfaceNotFound
from api.database_access.interfaces import (
    DBInterface,
    PSQLInterface,
    MongoInterface,
)
from api.result_handlers.exceptions import (
    ClientErrorException,
    ServerErrorException,
    ObjectNotFound,
)

ZTF_ID = "ztf"
ATLAS_ID = "atlas"


def test_get_light_curve_mongo(mongo_service, psql_service, client):
    result = MongoInterface.get_light_curve("ATLAS1").unwrap()

    assert len(result["detections"]) == 1
    assert result["detections"][0]["aid"] == "AID_ATLAS1"

    assert len(result["non_detections"]) == 1
    assert result["non_detections"][0]["aid"] == "AID_ATLAS1"

    result = MongoInterface.get_light_curve("ZTF2").unwrap()

    assert len(result["detections"]) == 1
    assert result["detections"][0]["aid"] == "AID_ATLAS2"

    assert len(result["non_detections"]) == 0
    assert result["non_detections"] == []


def test_get_light_curve_psql(mongo_service, psql_service, client):
    result = PSQLInterface.get_light_curve("ZTF1").unwrap()

    assert len(result["detections"]) == 1

    assert len(result["non_detections"]) == 1


def test_get_light_curve_not_found(mongo_service, psql_service, client):
    result = PSQLInterface.get_light_curve("ATLAS1")
    assert isinstance(result, Failure)
    assert isinstance(result.failure(), ClientErrorException)

    result = MongoInterface.get_light_curve("ZTF1")
    assert isinstance(result, Failure)
    assert isinstance(result.failure(), ClientErrorException)


def test_get_detections_mongo(mongo_service, psql_service, client):
    result = MongoInterface.get_detections("ATLAS1").unwrap()

    assert len(result) == 1


def test_get_detections_psql(mongo_service, psql_service, client):
    result = PSQLInterface.get_detections("ZTF1").unwrap()

    assert len(result) == 1


def test_get_detections_not_found(mongo_service, psql_service, client):
    result = PSQLInterface.get_detections("ATLAS1")
    assert isinstance(result, Failure)
    assert isinstance(result.failure(), ClientErrorException)

    result = MongoInterface.get_detections("ZTF1")
    assert isinstance(result, Failure)
    assert isinstance(result.failure(), ClientErrorException)


def test_get_non_detections_mongo(mongo_service, psql_service, client):
    result = MongoInterface.get_non_detections("ATLAS1").unwrap()

    assert len(result) == 1


def test_get_non_detections_psql(mongo_service, psql_service, client):
    result = PSQLInterface.get_non_detections("ZTF1").unwrap()

    assert len(result) == 1


def test_get_non_detections_not_found(mongo_service, psql_service, client):
    result = PSQLInterface.get_non_detections("ATLAS1")
    assert isinstance(result, Failure)
    assert isinstance(result.failure(), ClientErrorException)

    result = MongoInterface.get_non_detections("ZTF1")
    assert isinstance(result, Failure)
    assert isinstance(result.failure(), ClientErrorException)
    