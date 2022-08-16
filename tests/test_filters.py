from src.api.filters import (
    filter_atlas_detection_non_detection,
    filter_atlas_lightcurve,
)

TEST_ATLAS_DETECTION = {
    "tid": "ATLAS",
    "mjd": 58372.27195600001,
    "candid": "618271950015010002",
    "fid": 1,
    "pid": 618271950015,
    "diffmaglim": 20.595707,
    "isdiffpos": -1,
    "nid": 618,
    "distnr": 0.08482515,
    "magpsf": 18.622025,
    "magpsf_corr": 17.906834,
    "magap": 18.5383,
    "sigmapsf": 0.09397929,
    "sigmapsf_corr": 0.042980175,
    "sigmapsf_corr_ext": 0.048635766,
    "sigmagap": 0.0627,
    "ra": 329.5708237,
    "dec": -19.1119961,
    "rb": 0.86333334,
    "rbversion": "t8_f5_c3",
    "drb": 0,
    "magapbig": 18.5364,
    "sigmagapbig": 0.0784,
    "rfid": 340120100,
    "has_stamp": False,
    "corrected": True,
    "dubious": False,
    "step_id_corr": "bulk_1.0.0",
    "parent_candid": 624294431315010000,
}
TEST_ZTF_DETECTION = {
    "tid": "ZTF",
    "mjd": 58372.27195600001,
    "candid": "618271950015010002",
    "fid": 1,
    "pid": 618271950015,
    "diffmaglim": 20.595707,
    "isdiffpos": -1,
    "nid": 618,
    "distnr": 0.08482515,
    "magpsf": 18.622025,
    "magpsf_corr": 17.906834,
    "magap": 18.5383,
    "sigmapsf": 0.09397929,
    "sigmapsf_corr": 0.042980175,
    "sigmapsf_corr_ext": 0.048635766,
    "sigmagap": 0.0627,
    "ra": 329.5708237,
    "dec": -19.1119961,
    "rb": 0.86333334,
    "rbversion": "t8_f5_c3",
    "drb": 0,
    "magapbig": 18.5364,
    "sigmagapbig": 0.0784,
    "rfid": 340120100,
    "has_stamp": False,
    "corrected": True,
    "dubious": False,
    "step_id_corr": "bulk_1.0.0",
    "parent_candid": 624294431315010000,
}
TEST_ATLAS_NON_DETECTION = {
    "tid": "ATLAS",
    "mjd": 58426.16753470013,
    "fid": 1,
    "diffmaglim": 19.7014,
}
TEST_ZTF_NON_DETECTION = {
    "tid": "ZTF",
    "mjd": 58426.16753470013,
    "fid": 1,
    "diffmaglim": 19.7014,
}


def test_filter_atlas_detections():
    result = filter_atlas_detection_non_detection(TEST_ATLAS_DETECTION)
    assert result == False

    result = filter_atlas_detection_non_detection(TEST_ZTF_DETECTION)
    assert result == True


def test_filter_atlas_non_detections():
    result = filter_atlas_detection_non_detection(TEST_ATLAS_NON_DETECTION)
    assert result == False

    result = filter_atlas_detection_non_detection(TEST_ZTF_NON_DETECTION)
    assert result == True


def test_filter_atlas_lightcurve():
    test_lightcurve = {
        "detections": [TEST_ATLAS_DETECTION, TEST_ZTF_DETECTION],
        "non_detections": [TEST_ATLAS_NON_DETECTION, TEST_ZTF_NON_DETECTION],
    }
    expected_lightcurve = {
        "detections": [TEST_ZTF_DETECTION],
        "non_detections": [TEST_ZTF_NON_DETECTION],
    }
    result = filter_atlas_lightcurve(test_lightcurve)
    assert result == True
    assert test_lightcurve == expected_lightcurve

    test_lightcurve = {
        "detections": [TEST_ATLAS_DETECTION, TEST_ATLAS_DETECTION],
        "non_detections": [TEST_ATLAS_NON_DETECTION, TEST_ATLAS_NON_DETECTION],
    }
    expected_lightcurve = {
        "detections": [TEST_ATLAS_DETECTION, TEST_ATLAS_DETECTION],
        "non_detections": [TEST_ATLAS_NON_DETECTION, TEST_ATLAS_NON_DETECTION],
    }
    result = filter_atlas_lightcurve(test_lightcurve)
    assert result == False
    assert test_lightcurve == expected_lightcurve
