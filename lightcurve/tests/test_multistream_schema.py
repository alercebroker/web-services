from core.models import Detection as DetectionModel
from core.models import NonDetection as NonDetectionModel
from core.service import (
    _get_detections_sql,
    _get_non_detections_sql,
    _ztf_detection_to_multistream,
    _ztf_non_detection_to_multistream,
)


def test_psql_detections_to_multistream():
    psql_detection = {
        "candid": 123,
        "oid": "oid1",
        "mjd": 59000.0,
        "fid": 1,
        "pid": 1,
        "isdiffpos": True,
        "ra": 10.0,
        "dec": 20.0,
        "magpsf": 15,
        "sigmapsf": 0.5,
        "corrected": False,
        "dubious": False,
        "has_stamp": False,
        "step_id_corr": "test",
        "_InstanceState": "non serializable data",
    }

    expected_multistream_detection = {
        "candid": 123,
        "oid": "oid1",
        "sid": None,
        "aid": None,
        "tid": "0",
        "mjd": 59000.0,
        "fid": 1,
        "ra": 10.0,
        "e_ra": None,
        "dec": 20,
        "e_dec": None,
        "mag": 15,
        "e_mag": 0.5,
        "mag_corr": None,
        "e_mag_corr": None,
        "e_mag_corr_ext": None,
        "parent_candid": None,
        "corrected": False,
        "dubious": False,
        "has_stamp": False,
        "isdiffpos": True,
        "extra_fields": {
            "pid": 1,
            "step_id_corr": "test",
        },
    }
    multistream_detection = _ztf_detection_to_multistream(
        psql_detection, tid="0"
    )

    assert isinstance(multistream_detection, DetectionModel)
    assert multistream_detection.__dict__ == expected_multistream_detection


def test_psql_non_detections_to_multistream():
    psql_non_detection = {
        "oid": "oid1",
        "mjd": 59000,
        "fid": 1,
    }
    expected_multistream_non_detection = {
        "aid": None,
        "tid": "0",
        "sid": None,
        "oid": "oid1",
        "mjd": 59000,
        "fid": 1,
        "diffmaglim": None,
    }
    multistream_non_detection = _ztf_non_detection_to_multistream(
        psql_non_detection, tid="0"
    )

    assert isinstance(multistream_non_detection, NonDetectionModel)
    assert (
        multistream_non_detection.__dict__
        == expected_multistream_non_detection
    )
