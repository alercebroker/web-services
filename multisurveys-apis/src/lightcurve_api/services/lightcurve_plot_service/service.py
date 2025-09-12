import copy
from collections import defaultdict
from typing import Any, Callable, ContextManager, List, Tuple, cast

from sqlalchemy.orm.session import Session
from toolz import pipe

from lightcurve_api.models.lightcurve import Lightcurve
from lightcurve_api.models.lightcurve_item import (
    BaseDetection,
    BaseForcedPhotometry,
    BaseNonDetection,
)

from ..conesearch.conesearch import conesearch_oid_lightcurve
from .chart_point import ChartPoint
from .result import Result

DEFAULT_RADIUS = 30
DEFAULT_NEIGHBORS = 2
DETECTION = "det"
NON_DETECTION = "lim. mag"
FORCED_PHOTOMETRY = "f. phot"
COLORS = {
    "ztf": {"g": "#56E03A", "r": "#D42F4B", "i": "#F4D617"},
    "lsst": {"u": "#1600EA", "g": "#31DE1F", "r": "#B52626", "i": "#370201", "z": "#BA52FF", "y": "#61A2B3"},
}
SYMBOLS = {
    "ztf": {DETECTION: "circle", NON_DETECTION: "triangle", FORCED_PHOTOMETRY: "rect"},
    "lsst": {DETECTION: "roundRect", NON_DETECTION: "diamond", FORCED_PHOTOMETRY: "arrow"},
}


def default_config_state():
    return {
        "ztf_bands": ["g", "r", "i"],
        "lsst_bands": ["u", "g", "r", "i", "z", "y"],
        "flux": False,
        "magnitude": True,
        "apparent": True,
        "absolute": False,
        "difference": True,
        "total": False,
        "external_sources": [],
        "external_sources_enabled": False,
        "offset_bands": False,
    }


def create_series(name: str, survey: str, band: str, data: List[List[float]]) -> dict:
    return {
        "name": name + " " + survey.upper() + ": " + band,
        "type": "scatter",
        "data": data,
        "color": COLORS[survey][band],
        "symbol": SYMBOLS[survey][name],
    }


def default_echarts_options():
    return {
        "tooltip": {},
        "grid": {"right": "21%", "left": "5%", "bottom": "10%"},
        "legend": {
            "right": 0,
            "top": 80,
            "orient": "vertical",
            "selectedMode": False,
            "itemWidth": 15,
        },
        "xAxis": {"type": "value", "name": "MJD", "scale": True},
        "yAxis": {"type": "value", "name": "Magnitude", "scale": True},
        "series": [],
    }


def lightcurve_plot(
    oid: str, survey_id: str, session_factory: Callable[..., ContextManager[Session]]
) -> Tuple[Result, dict[str, Any]]:
    result = Result({}, Lightcurve(detections=[], non_detections=[], forced_photometry=[]))
    return cast(
        Tuple[Result, dict],
        pipe(
            get_lightcurve(oid, result, survey_id, session_factory),
            create_echart_options,
            set_chart_options_detections,
            set_chart_options_non_detections,
            set_chart_options_forced_photometry,
        ),
    )


def get_lightcurve(oid: str, result: Result, survey_id: str, session_factory: Callable[..., ContextManager[Session]]):
    return Result(
        copy.deepcopy(result.echart_options),
        conesearch_oid_lightcurve(
            oid,
            DEFAULT_RADIUS,
            DEFAULT_NEIGHBORS,
            survey_id,
            session_factory,
        ),
    )


def create_echart_options(result: Result) -> Tuple[Result, dict[str, Any]]:
    result_copy = result.copy()
    chart_options = default_echarts_options()
    result_copy.echart_options = chart_options
    config_state = default_config_state()
    return result_copy, config_state


def set_chart_options_detections(args: Tuple[Result, dict[str, Any]]) -> Tuple[Result, dict[str, Any]]:
    result, config_state = args

    result_copy = result.copy()
    config_state_copy = copy.deepcopy(config_state)
    detections_grouped: dict[str, dict[str, List[List[float]]]] = defaultdict(lambda: defaultdict(lambda: []))

    # Group detections by survey and band
    for chart_point in create_chart_detections(result_copy.lightcurve.detections, config_state_copy):
        detections_grouped[chart_point.survey][chart_point.band].append(chart_point.point())

    # Create echart series for each survey and band
    for survey in detections_grouped:
        for band, data in detections_grouped[survey].items():
            result_copy.echart_options["series"].append(create_series(DETECTION, survey, band, data))

    return result_copy, config_state_copy


def set_chart_options_non_detections(args: Tuple[Result, dict[str, Any]]) -> Tuple[Result, dict[str, Any]]:
    result, config_state = args

    result_copy = result.copy()
    config_state_copy = copy.deepcopy(config_state)
    grouped: dict[str, dict[str, List[List[float]]]] = defaultdict(lambda: defaultdict(lambda: []))

    # Group non detections by survey and band
    for chart_point in create_chart_non_detections(result_copy.lightcurve.non_detections, config_state_copy):
        grouped[chart_point.survey][chart_point.band].append(chart_point.point())

    # Create echart series for each survey and band
    for survey in grouped:
        for band, data in grouped[survey].items():
            result_copy.echart_options["series"].append(create_series(NON_DETECTION, survey, band, data))

    return result_copy, config_state_copy


def set_chart_options_forced_photometry(args: Tuple[Result, dict[str, Any]]) -> Tuple[Result, dict[str, Any]]:
    result, config_state = args

    result_copy = result.copy()
    config_state_copy = copy.deepcopy(config_state)
    grouped: dict[str, dict[str, List[List[float]]]] = defaultdict(lambda: defaultdict(lambda: []))

    # Group forced photometry by survey and band
    for chart_point in create_chart_forced_photometry(result_copy.lightcurve.forced_photometry, config_state_copy):
        grouped[chart_point.survey][chart_point.band].append(chart_point.point())

    # Create echart series for each survey and band
    for survey in grouped:
        for band, data in grouped[survey].items():
            result_copy.echart_options["series"].append(create_series(FORCED_PHOTOMETRY, survey, band, data))

    return result_copy, config_state_copy


def create_chart_detections(detections: List[BaseDetection], config_state: dict[str, Any]) -> List[ChartPoint]:
    result = []
    for det in detections:
        if det.band_name() not in config_state["ztf_bands"] + config_state["lsst_bands"]:
            continue

        result.append(
            ChartPoint(
                det.survey_id,
                det.band_name(),
                det.mjd,
                det.magnitude2flux(config_state["difference"])
                if config_state["flux"]
                else det.flux2magnitude(config_state["difference"]),
            )
        )

    return result


def create_chart_non_detections(
    non_detections: List[BaseNonDetection], config_state: dict[str, Any]
) -> List[ChartPoint]:
    result = []
    for ndet in non_detections:
        if ndet.band_name() not in config_state["ztf_bands"] + config_state["lsst_bands"]:
            continue

        result.append(ChartPoint(ndet.survey_id, ndet.band_name(), ndet.mjd, ndet.get_mag()))

    return result


def create_chart_forced_photometry(
    forced_photometry: List[BaseForcedPhotometry], config_state: dict[str, Any]
) -> List[ChartPoint]:
    result = []
    for fphot in forced_photometry:
        if fphot.band_name() not in config_state["ztf_bands"] + config_state["lsst_bands"]:
            continue

        result.append(
            ChartPoint(
                fphot.survey_id,
                fphot.band_name(),
                fphot.mjd,
                fphot.magnitude2flux(config_state["difference"])
                if config_state["flux"]
                else fphot.flux2magnitude(config_state["difference"]),
            )
        )
    return result
