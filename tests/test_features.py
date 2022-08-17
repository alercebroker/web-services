def test_get_features(client):
    rv = client.get("objects/ALERCE1/features")
    assert rv.status_code == 200
    rv = client.get("objects/ALERCE1/features/testfeature")
    assert rv.status_code == 200


def test_get_features_filter_by_fid(client):
    rv = client.get("objects/ALERCE1/features?fid=1")
    assert rv.status_code == 200
    rv = client.get("objects/ALERCE1/features/testfeature?fid=1")
    assert rv.status_code == 200


def test_get_features_filter_by_version(client):
    rv = client.get("objects/ALERCE1/features?version=1.0.0-test")
    assert rv.status_code == 200
    rv = client.get("objects/ALERCE1/features/testfeature?version=1.0.0-test")
    assert rv.status_code == 200


def test_get_features_not_found(client):
    rv = client.get("objects/NOTFOUND/features")
    assert rv.status_code == 404
    rv = client.get("objects/NOTFOUND/features/testfeature")
    assert rv.status_code == 404
