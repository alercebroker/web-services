import api.plots.apparent as ap

def test_get_forced_photometry_series():
    forced_photometry = [
        {
            "fid": 1,
            "mjd": 1,
            "mag_corr": 1,
            "e_mag_corr_ext": 1,
            "isdiffpos": 1,
            "extra_fields": {"distnr": 1},
        },
        {
            "fid": 2,
            "mjd": 2,
            "mag_corr": 2,
            "e_mag_corr_ext": 2,
            "isdiffpos": 2,
            "extra_fields": {"distnr": 2},
        },
    ]
    bands = [1, 2]
    series = ap.get_forced_photometry_series(forced_photometry, bands)
    assert series == [
        {
            "name": "g forced photometry",
            "type": "scatter",
            "symbolSize": 6,
            "scale": True,
            "color": "rgb(86, 224, 58)",
            "symbol": "path://M0,0 L0,10 L10,10 L10,0 Z",
            "encode": {"x": 0, "y": 1},
            "data": [
                [1, 1, "no-candid", 1, 1],
            ],
        },
        {
            "name": "r forced photometry",
            "type": "scatter",
            "symbolSize": 6,
            "scale": True,
            "color": "rgb(212, 47, 75)",
            "symbol": "path://M0,0 L0,10 L10,10 L10,0 Z",
            "encode": {"x": 0, "y": 1},
            "data": [
                [2, 2, "no-candid", 2, 2],
            ],
        },
    ]

def test_get_error_bars_series_for_forced_photometry():
    forced_photometry = [
        {
            "fid": 1,
            "mjd": 1,
            "mag_corr": 1,
            "e_mag_corr_ext": 1,
            "isdiffpos": 1,
            "extra_fields": {"distnr": 1},
            "corrected": True,
        },
        {
            "fid": 1,
            "mjd": 1,
            "mag_corr": 1,
            "e_mag_corr_ext": 1,
            "isdiffpos": 1,
            "extra_fields": {"distnr": 1},
            "corrected": False,
        },
        {
            "fid": 2,
            "mjd": 2,
            "mag_corr": 2,
            "e_mag_corr_ext": 2,
            "isdiffpos": 2,
            "extra_fields": {"distnr": 2},
            "corrected": True,
        },
    ]
    bands = [1, 2]
    series = ap.get_error_bars_series(forced_photometry, bands, forced=True)
    assert series == [
        {
            "error_bars": True,
            "name": "g forced photometry",
            "type": "custom",
            "scale": True,
            "color": "rgb(86, 224, 58)",
            "data": [
                [1, 0, 2],
            ],
            "error_bars": True,
        },
        {
            "error_bars": True,
            "name": "r forced photometry",
            "type": "custom",
            "scale": True,
            "color": "rgb(212, 47, 75)",
            "data": [
                [2, 0, 4],
            ],
            "error_bars": True,
        },
    ]

def test_get_detection_series():
    detections = [
        {
            "candid": "1",
            "fid": 1,
            "mjd": 1,
            "mag_corr": 1,
            "e_mag_corr_ext": 1,
            "isdiffpos": 1,
        },
        {
            "candid": "2",
            "fid": 2,
            "mjd": 2,
            "mag_corr": 2,
            "e_mag_corr_ext": 2,
            "isdiffpos": 2,
        },
    ]
    bands = [1, 2]
    series = ap.get_detections_series(detections, bands)
    assert series == [
        {
            "name": "g",
            "type": "scatter",
            "scale": True,
            "color": "rgb(86, 224, 58)",
            "symbolSize": 6,
            "symbol": "circle",
            "encode": {"x": 0, "y": 1},
            "zlevel": 10,
            "data": [[1, 1, "1", 1, 1]],
        },
        {
            "name": "r",
            "type": "scatter",
            "scale": True,
            "color": "rgb(212, 47, 75)",
            "symbolSize": 6,
            "symbol": "circle",
            "encode": {"x": 0, "y": 1},
            "zlevel": 10,
            "data": [[2, 2, "2", 2, 2]],
        },
    ]

def test_get_detection_series_with_data_release():
    detections = [
        {
            "objectid": "1",
            "fid": 101,
            "mjd": 1,
            "mag_corr": 1,
            "e_mag_corr_ext": 1,
            "field": 1,
        },
        {
            "objectid": "2",
            "fid": 102,
            "mjd": 2,
            "mag_corr": 2,
            "e_mag_corr_ext": 2,
            "field": 2,
        },
        {
            "objectid": "3",
            "fid": 103,
            "mjd": 3,
            "mag_corr": 3,
            "e_mag_corr_ext": 3,
            "field": 3,
        },
    ]
    bands = [101, 102, 103]
    series = ap.get_detections_series(detections, bands)
    assert series == [
        {
            "name": "g DR5",
            "type": "scatter",
            "scale": True,
            "color": "rgb(173, 163, 163)",
            "symbolSize": 3,
            "symbol": "square",
            "encode": {"x": 0, "y": 1},
            "zlevel": 0,
            "data": [[1, 1, "1", 1, 1]],
        },
        {
            "name": "r DR5",
            "type": "scatter",
            "scale": True,
            "color": "rgb(55, 126, 184)",
            "symbolSize": 3,
            "symbol": "square",
            "encode": {"x": 0, "y": 1},
            "zlevel": 0,
            "data": [[2, 2, "2", 2, 2]],
        },
        {
            "name": "i DR5",
            "type": "scatter",
            "scale": True,
            "color": ap.hex2rgb("#FF7F00"),
            "symbolSize": 3,
            "symbol": "square",
            "encode": {"x": 0, "y": 1},
            "zlevel": 0,
            "data": [[3, 3, "3", 3, 3]],
        },
    ]
