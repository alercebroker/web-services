
def test_non_detections_from_ztf(
    test_client,
    insert_ztf_1_oid_per_aid,
):
    res = test_client.get("/non_detections/oid1", params={"survey_id": "ztf"})
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_non_detections_from_ztf_multiple_oid_per_aid(
    test_client,
    insert_ztf_many_oid_per_aid,
):
    res = test_client.get("/non_detections/oid1", params={"survey_id": "ztf"})
    assert res.status_code == 200
    assert len(res.json()) == 3


def test_non_detections_from_atlas(
    test_client,
    insert_ztf_1_oid_per_aid,
):
    res = test_client.get(
        "/non_detections/oid1", params={"survey_id": "atlas"}
    )
    assert res.status_code == 400
    assert (
        res.json()["detail"]
        == "Can't retrieve non detections: ATLAS does not provide non_detections"
    )


def test_non_detections_multistream(
    test_client,
    insert_many_aid_ztf_and_atlas_detections,
):
    res = test_client.get("/non_detections/oid1", params={"survey_id": "ztf"})
    assert res.status_code == 200
    assert len(res.json()) == 1
    res = test_client.get(
        "/non_detections/oid1", params={"survey_id": "atlas"}
    )
    assert res.status_code == 400
    res = test_client.get("/non_detections/oid1")
    assert res.status_code == 200
    assert len(res.json()) == 2
