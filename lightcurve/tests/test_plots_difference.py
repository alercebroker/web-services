import api.plots.difference as diff


def test_hex2rgb():
    assert diff.hex2rgb("#000000") == "rgb(0, 0, 0)"
    assert diff.hex2rgb("#000000", 0.5) == "rgba(0, 0, 0, 0.5)"
    assert diff.hex2rgb("#000000", 2) == "rgba(0, 0, 0, 1)"
    assert diff.hex2rgb("#000000", -1) == "rgba(0, 0, 0, 0)"


def test_get_bands():
    items = [{"fid": 1}, {"fid": 2}]
    assert diff.get_bands(items) == [1, 2]
    items = [{"id": 1}, {"fid": 2}]
    try:
        diff.get_bands(items)
    except KeyError as e:
        assert (
            str(e)
            == "'Error getting bands from items. `fid` field should be present in the items'"
        )


def test_get_forced_photometry_series():
    forced_photometry = [
        {
            "fid": 1,
            "mjd": 1,
            "mag": 1,
            "e_mag": 1,
            "isdiffpos": 1,
            "extra_fields": {"distnr": 1},
        },
        {
            "fid": 2,
            "mjd": 2,
            "mag": 2,
            "e_mag": 2,
            "isdiffpos": 2,
            "extra_fields": {"distnr": 2},
        },
    ]
    bands = [1, 2]
    series = diff.get_forced_photometry_series(forced_photometry, bands)
    assert series == [
        {
            "name": "g forced photometry",
            "type": "scatter",
            "symbolSize": 6,
            "scale": True,
            "color": "rgb(86, 224, 58)",
            "symbol": "path://M0,0 L0,10 L10,10 L10,0 Z",
            "encode": {"x": 0, "y": 1},
            "data": [[1, 1, "no-candid", 1, 1]],
        },
        {
            "name": "r forced photometry",
            "type": "scatter",
            "symbolSize": 6,
            "scale": True,
            "color": "rgb(212, 47, 75)",
            "symbol": "path://M0,0 L0,10 L10,10 L10,0 Z",
            "encode": {"x": 0, "y": 1},
            "data": [[2, 2, "no-candid", 2, 2]],
        },
    ]

def test_get_forced_photometry_error_bands():
    forced_photometry = [
        {
            "fid": 1,
            "mjd": 1,
            "mag": 1,
            "e_mag": 1,
            "isdiffpos": 1,
            "extra_fields": {"distnr": 1},
        },
        {
            "fid": 2,
            "mjd": 2,
            "mag": 2,
            "e_mag": 2,
            "isdiffpos": 2,
            "extra_fields": {"distnr": 2},
        },
    ]
    bands = [1, 2]
    series = diff.get_error_bars_series(forced_photometry, bands, forced=True)
    assert series == [
        {
            "error_bars": True,
            "name": "g forced photometry",
            "type": "custom",
            "scale": True,
            "color": "rgb(86, 224, 58)",
            "data": [[1, 0, 2]],
        },
        {
            "error_bars": True,
            "name": "r forced photometry",
            "type": "custom",
            "scale": True,
            "color": "rgb(212, 47, 75)",
            "data": [[2, 0, 4]],
        },
    ]

def test_get_non_detections_series():
    non_detections = [
        {
            "fid": 1,
            "mjd": 1,
            "diffmaglim": 11,
        },
        {
            "fid": 2,
            "mjd": 2,
            "diffmaglim": 20,
        },
    ]
    bands = [1, 2]
    series = diff.get_non_detections_series(non_detections, bands)
    assert series == [
        {
            "name": "g non-detections",
            "type": "scatter",
            "symbolSize": 6,
            "scale": True,
            "color": "rgba(86, 224, 58, 0.5)",
            "symbol": "path://M0,49.017c0-13.824,11.207-25.03,25.03-25.03h438.017c13.824,0,25.029,11.207,25.029,25.03L262.81,455.745c0,0-18.772,18.773-37.545,0C206.494,436.973,0,49.017,0,49.017z",
            "data": [[1,11]],
        },
        {
            "name": "r non-detections",
            "type": "scatter",
            "symbolSize": 6,
            "scale": True,
            "color": "rgba(212, 47, 75, 0.5)",
            "symbol": "path://M0,49.017c0-13.824,11.207-25.03,25.03-25.03h438.017c13.824,0,25.029,11.207,25.029,25.03L262.81,455.745c0,0-18.772,18.773-37.545,0C206.494,436.973,0,49.017,0,49.017z",
            "data": [[2, 20]],
        },
    ]

def test_get_detections_series():
    detections = [
        {
            "candid": "1",
            "fid": 1,
            "mjd": 1,
            "mag": 1,
            "e_mag": 1,
            "isdiffpos": 1,
        },
        {
            "candid": "2",
            "fid": 2,
            "mjd": 2,
            "mag": 2,
            "e_mag": 2,
            "isdiffpos": 2,
        },
    ]
    bands = [1, 2]
    series = diff.get_detections_series(detections, bands)
    assert series == [
        {
            "name": "g",
            "type": "scatter",
            "symbolSize": 6,
            "scale": True,
            "color": "rgb(86, 224, 58)",
            "encode": {"x": 0, "y": 1},
            "data": [[1, 1, "1", 1, 1]],
        },
        {
            "name": "r",
            "type": "scatter",
            "symbolSize": 6,
            "scale": True,
            "color": "rgb(212, 47, 75)",
            "encode": {"x": 0, "y": 1},
            "data": [[2, 2, "2", 2, 2]],
        },
    ]

def test_get_detections_error_bars():
    detections = [
        {
            "candid": "1",
            "fid": 1,
            "mjd": 1,
            "mag": 1,
            "e_mag": 1,
            "isdiffpos": 1,
        },
        {
            "candid": "2",
            "fid": 2,
            "mjd": 2,
            "mag": 2,
            "e_mag": 2,
            "isdiffpos": 2,
        },
    ]
    bands = [1, 2]
    series = diff.get_error_bars_series(detections, bands)
    assert series == [
        {
            "error_bars": True,
            "name": "g",
            "type": "custom",
            "scale": True,
            "color": "rgb(86, 224, 58)",
            "data": [[1, 0, 2]],
        },
        {
            "error_bars": True,
            "name": "r",
            "type": "custom",
            "scale": True,
            "color": "rgb(212, 47, 75)",
            "data": [[2, 0, 4]],
        },
    ]
